
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.app.services.document_processor import extract_document
from backend.app.services.storage_service import UPLOAD_DIR
from backend.app.services.rag_service import load_chunks, save_chunks, collection

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/")
def list_documents():
    chunks = load_chunks()
    documents = {}

    for chunk in chunks:
        doc_id = chunk["document_id"]
        documents.setdefault(doc_id, {
            "document_id": doc_id,
            "filename": chunk["filename"],
            "chunks": 0,
        })
        documents[doc_id]["chunks"] += 1

    return {"documents": list(documents.values())}


@router.get("/{document_id}/text")
def get_document_text(document_id: UUID):
    matches = list(UPLOAD_DIR.glob(f"{document_id}.*"))

    if not matches:
        raise HTTPException(status_code=404, detail="Document not found.")

    return extract_document(matches[0])


@router.delete("/{document_id}")
def delete_document(document_id: UUID):
    doc_id = str(document_id)
    chunks = load_chunks()
    remaining = [
        chunk for chunk in chunks
        if chunk["document_id"] != doc_id
    ]

    if len(remaining) == len(chunks):
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove indexed vectors and metadata from ChromaDB.
    collection.delete(where={"document_id": doc_id})

    # Remove the document from our BM25 chunk registry.
    save_chunks(remaining)

    # Remove the original uploaded file.
    for path in UPLOAD_DIR.glob(f"{doc_id}.*"):
        path.unlink(missing_ok=True)

    return {"message": "Document deleted successfully", "document_id": doc_id}
