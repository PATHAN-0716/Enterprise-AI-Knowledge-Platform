
import json
import logging
import os
import re
import time
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

from backend.app.services.document_processor import extract_document


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma_db"
CHUNKS_FILE = Path(__file__).resolve().parent / "chunks.json"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_TIMEOUT_SECONDS = 60
MAX_GEMINI_ATTEMPTS = 3

logger.info("Loading embedding model...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

logger.info("Loading reranker model...")
reranker = CrossEncoder(RERANKER_MODEL_NAME)

logger.info("Initializing ChromaDB...")
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = chroma_client.get_or_create_collection(
    name="document_chunks"
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
    separators=["\n\n", "\n", ". ", " ", ""],
)


# --------------------------------------------------
# Chunk metadata storage
# --------------------------------------------------

def load_chunks() -> list[dict]:
    if not CHUNKS_FILE.exists():
        return []

    return json.loads(
        CHUNKS_FILE.read_text(encoding="utf-8")
    )


def save_chunks(chunks: list[dict]) -> None:
    CHUNKS_FILE.parent.mkdir(parents=True, exist_ok=True)

    CHUNKS_FILE.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# --------------------------------------------------
# Document indexing
# --------------------------------------------------

def index_document(
    file_path: Path,
    document_id: str,
    original_filename: str,
) -> dict:
    logger.info("Extracting document: %s", original_filename)

    extracted = extract_document(file_path)
    new_chunks = []

    for page in extracted["pages"]:
        page_text = page["text"]

        if not page_text.strip():
            continue

        pieces = splitter.split_text(page_text)

        for piece in pieces:
            chunk_index = len(new_chunks)

            new_chunks.append({
                "id": f"{document_id}-{chunk_index}",
                "text": piece,
                "document_id": document_id,
                "filename": original_filename,
                "page_number": page["page_number"],
                "chunk_index": chunk_index,
            })

    if not new_chunks:
        raise ValueError(
            "No extractable text found. The document may be scanned or empty."
        )

    logger.info("Creating embeddings for %d chunks...", len(new_chunks))

    vectors = embedding_model.encode(
        [chunk["text"] for chunk in new_chunks],
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()

    collection.add(
        ids=[chunk["id"] for chunk in new_chunks],
        documents=[chunk["text"] for chunk in new_chunks],
        embeddings=vectors,
        metadatas=[
            {
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "page_number": chunk["page_number"] or 0,
                "chunk_index": chunk["chunk_index"],
            }
            for chunk in new_chunks
        ],
    )

    all_chunks = load_chunks()
    all_chunks.extend(new_chunks)
    save_chunks(all_chunks)

    logger.info(
        "Indexed %d chunks for %s",
        len(new_chunks),
        original_filename,
    )

    return {
        "document_id": document_id,
        "filename": original_filename,
        "chunks_created": len(new_chunks),
    }


# --------------------------------------------------
# Hybrid retrieval
# BM25 + vector search + cross-encoder reranking
# --------------------------------------------------

def hybrid_search(question: str, top_k: int = 5) -> list[dict]:
    start = time.perf_counter()
    logger.info("Starting hybrid search...")

    chunks = load_chunks()

    if not chunks:
        logger.warning("No chunks found in the chunk registry.")
        return []

    # 1. Keyword retrieval
    tokenized_chunks = [
        re.findall(r"\w+", chunk["text"].lower())
        for chunk in chunks
    ]
    tokenized_question = re.findall(r"\w+", question.lower())

    bm25 = BM25Okapi(tokenized_chunks)
    bm25_scores = bm25.get_scores(tokenized_question)

    bm25_order = sorted(
        range(len(chunks)),
        key=lambda index: bm25_scores[index],
        reverse=True,
    )[:20]

    # 2. Semantic vector retrieval
    query_vector = embedding_model.encode(
        [question],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0].tolist()

    vector_count = collection.count()

    if vector_count == 0:
        logger.warning("ChromaDB contains no vectors.")
        return []

    vector_results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(20, vector_count),
        include=["documents", "metadatas"],
    )

    # 3. Reciprocal rank fusion
    fused_scores = {}
    chunk_by_id = {
        chunk["id"]: chunk for chunk in chunks
    }

    for rank, index in enumerate(bm25_order, start=1):
        chunk_id = chunks[index]["id"]
        fused_scores[chunk_id] = (
            fused_scores.get(chunk_id, 0) + 1 / (60 + rank)
        )

    vector_ids = vector_results["ids"][0]

    for rank, chunk_id in enumerate(vector_ids, start=1):
        fused_scores[chunk_id] = (
            fused_scores.get(chunk_id, 0) + 1 / (60 + rank)
        )

    candidate_ids = sorted(
        fused_scores,
        key=fused_scores.get,
        reverse=True,
    )[:20]

    candidates = [
        chunk_by_id[chunk_id]
        for chunk_id in candidate_ids
        if chunk_id in chunk_by_id
    ]

    if not candidates:
        logger.warning("No retrieval candidates found.")
        return []

    # 4. Cross-encoder reranking
    logger.info("Reranking %d candidates...", len(candidates))

    pairs = [
        (question, chunk["text"])
        for chunk in candidates
    ]

    scores = reranker.predict(
        pairs,
        show_progress_bar=False,
    )

    ranked = sorted(
        zip(candidates, scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    results = [
        {**chunk, "rerank_score": float(score)}
        for chunk, score in ranked[:top_k]
    ]

    logger.info(
        "Hybrid search finished in %.2f seconds; retrieved %d chunks.",
        time.perf_counter() - start,
        len(results),
    )

    return results


# --------------------------------------------------
# Gemini call with limited retries
# --------------------------------------------------

def generate_gemini_answer(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(
        api_key=api_key,
        http_options={
            "timeout": GEMINI_TIMEOUT_SECONDS * 1000,
        },
    )

    for attempt in range(1, MAX_GEMINI_ATTEMPTS + 1):
        try:
            logger.info(
                "Calling Gemini model %s (attempt %d/%d)...",
                GEMINI_MODEL,
                attempt,
                MAX_GEMINI_ATTEMPTS,
            )

            start = time.perf_counter()

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )

            logger.info(
                "Gemini completed in %.2f seconds.",
                time.perf_counter() - start,
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text.strip()

        except errors.APIError as exc:
            status_code = getattr(exc, "code", None)

            if status_code not in (429, 500, 502, 503, 504):
                logger.exception("Non-retryable Gemini API error.")
                raise

            if attempt == MAX_GEMINI_ATTEMPTS:
                logger.exception("Gemini retries exhausted.")
                raise

            delay = 2 ** (attempt + 1)

            logger.warning(
                "Gemini returned HTTP %s. Retrying in %d seconds.",
                status_code,
                delay,
            )
            time.sleep(delay)

    raise RuntimeError("Gemini did not return an answer.")


# --------------------------------------------------
# Question answering with source citations
# --------------------------------------------------

def answer_question(question: str) -> dict:
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # Step 1: Retrieve context
    sources = hybrid_search(question.strip())

    if not sources:
        return {
            "answer": (
                "I couldn't find relevant information in the uploaded documents."
            ),
            "sources": [],
        }

    # Step 2: Build context and source labels
    context_parts = []

    for index, source in enumerate(sources, start=1):
        page = source["page_number"]
        page_label = f", page {page}" if page else ""

        context_parts.append(
            f"[S{index}] Document: {source['filename']}{page_label}\n"
            f"{source['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a document question-answering assistant.

Instructions:
- Answer using only the document excerpts provided below.
- Do not invent facts or use outside knowledge.
- If the excerpts do not answer the question, say so.
- Cite supporting information using [S1], [S2], etc.
- Only use source labels that appear in the supplied excerpts.
- Keep the answer clear and concise.

DOCUMENT EXCERPTS:
{context}

QUESTION:
{question}

Answer with supporting citations.
"""

    # Step 3: Generate answer
    answer = generate_gemini_answer(prompt)

    # Step 4: Identify valid citations
    citation_numbers = re.findall(r"\[S(\d+)\]", answer)

    valid_indices = sorted({
        int(number)
        for number in citation_numbers
        if 1 <= int(number) <= len(sources)
    })

    cited_sources = [
        {
            "source_id": f"S{index}",
            "filename": sources[index - 1]["filename"],
            "page_number": sources[index - 1]["page_number"],
            "chunk_id": sources[index - 1]["id"],
            "text": sources[index - 1]["text"],
        }
        for index in valid_indices
    ]

    logger.info(
        "Question answered. Valid cited sources: %d",
        len(cited_sources),
    )

    return {
        "answer": answer,
        "sources": cited_sources,
    }
