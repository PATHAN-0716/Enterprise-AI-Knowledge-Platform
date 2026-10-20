# Enterprise AI Knowledge Platform

A document-based AI question-answering platform that allows users to upload documents, retrieve relevant information using hybrid search, and receive AI-generated answers with source citations.

The application combines **Retrieval-Augmented Generation (RAG)**, semantic embeddings, keyword search, reranking, and Google's Gemini model in a containerized full-stack application.

## Key Features

- **Multi-format document upload:** Supports PDF, DOCX, and TXT files.
- **Document processing:** Extracts text, splits documents into chunks, and prepares them for retrieval.
- **Semantic search:** Uses Sentence Transformers embeddings to retrieve contextually relevant content.
- **Keyword search:** Uses BM25 to find relevant matches based on document terms.
- **Hybrid retrieval:** Combines semantic and keyword search to improve candidate retrieval.
- **Cross-encoder reranking:** Reorders retrieved candidates to prioritize relevance.
- **AI-powered answers:** Uses Google Gemini to generate answers grounded in retrieved document content.
- **Source citations:** Supports source attribution for answers when valid source references are available.
- **Persistent vector storage:** Uses ChromaDB to store document embeddings for retrieval.
- **Interactive web interface:** Provides a React-based interface for uploading documents and asking questions.
- **Containerized deployment:** Uses Docker Compose to run the frontend and backend together.

## Architecture

```text
                  User
                   |
                   v
          React + Vite Frontend
              localhost:3000
                   |
                   v
             FastAPI Backend
              localhost:8000
                   |
          +--------+---------+
          |                  |
          v                  v
    Document Upload       User Question
          |                  |
          v                  v
   PDF / DOCX / TXT     Hybrid Retrieval
          |             /            \
          v            v              v
     Text Extraction  Vector Search  BM25 Search
          |            \              /
          v             \            /
     Text Chunking       Candidate Fusion
          |                      |
          v                      v
  Sentence Transformers    Cross-Encoder Reranking
          |                      |
          v                      v
       ChromaDB              Relevant Chunks
                                   |
                                   v
                             Gemini Model
                                   |
                                   v
                         Answer + Source References
```

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI, Uvicorn |
| Embeddings | Sentence Transformers |
| Keyword retrieval | BM25 (`rank-bm25`) |
| Vector database | ChromaDB |
| Reranking | Cross-encoder model |
| Generative AI | Google Gemini API |
| Document processing | PyPDF, python-docx |
| Containerization | Docker, Docker Compose |
| API documentation | FastAPI Swagger UI |

## Project Structure

```text
Enterprise-AI-Knowledge-Platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── upload.py
│   │   │   ├── documents.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── storage_service.py
│   │   │   ├── rag_service.py
│   │   │   └── chunks.json
│   │   ├── .env                  # Local secrets; not committed
│   │   └── main.py
│   ├── uploads/                  # Uploaded documents; local data
│   ├── chroma_db/                # Vector database; local data
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   └── App.jsx
│   ├── nginx.conf
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

*The tree highlights the main components. Retain any additional files already present in your actual project; filenames and directories can vary with implementation.*

## How It Works

### 1. Document ingestion

Users upload a PDF, DOCX, or TXT document through the frontend. The FastAPI backend validates the file type and size, saves the document, and passes it to the document-processing pipeline.

### 2. Text extraction and chunking

The application extracts the document's text and divides it into smaller chunks. Chunking allows retrieval to focus on relevant passages instead of sending an entire document to the language model.

### 3. Embedding and indexing

Sentence Transformers generates vector embeddings for document chunks. ChromaDB stores the vectors for semantic retrieval, while BM25 provides keyword-based retrieval.

### 4. Hybrid retrieval and reranking

When a user asks a question, the application searches for relevant chunks using semantic and keyword retrieval. The candidates are combined and reranked with a cross-encoder to prioritize relevant context.

### 5. Answer generation

The retrieved context is supplied to the Gemini model to generate a response. The application supports source attribution so users can trace answers to relevant document content.

## Prerequisites

- Docker Desktop installed and running
- Git installed
- A Google Gemini API key
- VS Code (recommended)

Docker Compose is used to run the application without manually installing backend and frontend dependencies on the host machine.

## Configuration

The backend uses environment variables for configuration. Create a local environment file at:

`backend/app/.env`

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Use the exact environment variable names expected by your backend code. Never commit the real `.env` file or expose API keys in source code, screenshots, logs, or GitHub.

## Run with Docker Compose

Clone the repository and enter its directory:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Enterprise-AI-Knowledge-Platform
```

Create `backend/app/.env` and configure your API key, then build and start the services:

```bash
docker compose up --build -d
```

Check the running containers:

```bash
docker compose ps
```

View backend logs:

```bash
docker compose logs -f backend
```

View frontend logs:

```bash
docker compose logs -f frontend
```

Stop the application:

```bash
docker compose down
```

The application uses local Docker volumes/bind mounts for uploaded files and vector database data. Keep those directories safe when cleaning up or resetting the project.

## Access the Application

| Resource | URL |
|---|---|
| Web application | http://localhost:3000 |
| Backend health check | http://localhost:8000/health |
| FastAPI Swagger UI | http://localhost:8000/docs |
| OpenAPI schema | http://localhost:8000/openapi.json |

## Supported Documents and Limits

The current storage service accepts `.pdf`, `.docx`, and `.txt` files and enforces a maximum upload size of **10 MB per file**.

Retrieval quality depends on document text extraction, chunking, embedding quality, candidate retrieval, and reranking. Answers may not always contain a valid citation, so verify important information against the original document.

## Security and Data Handling

- Keep API keys and local `.env` files out of version control.
- Do not commit private documents, uploaded files, ChromaDB data, or local chunk caches.
- Review `.gitignore` before pushing the repository.
- Treat the current application as a development/portfolio project. Add appropriate authentication, authorization, rate limiting, and production security controls before exposing it publicly.

## Troubleshooting

**Backend is unavailable**

```bash
docker compose ps
docker compose logs --tail 100 backend
```

**Frontend is unavailable**

```bash
docker compose logs --tail 100 frontend
```

**Upload fails**

- Verify the file is PDF, DOCX, or TXT.
- Check that the file is within the 10 MB limit.
- Inspect backend logs for the actual error.
- Confirm the required Python dependencies are listed in `backend/requirements.txt`.

**Gemini requests fail**

- Verify `backend/app/.env` exists.
- Confirm the API key is valid and the configured model is available.
- Inspect backend logs for the provider's error response.

**Rebuild after dependency changes**

```bash
docker compose up --build -d
```

## Future Improvements

- User authentication and document-level access control
- Improved citation display and source passage previews
- Automated evaluation of retrieval relevance and answer groundedness
- Background processing for larger document collections
- Production deployment with monitoring and usage controls

## Author

**Pathan Adilsha Khan**

Enterprise AI Knowledge Platform — a full-stack RAG application demonstrating document ingestion, hybrid retrieval, reranking, and AI-powered question answering.
#   E n t e r p r i s e - A I - K n o w l e d g e - P l a t f o r m  
 