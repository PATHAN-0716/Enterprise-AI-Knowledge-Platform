# Enterprise AI Knowledge Platform

An AI-powered knowledge platform that enables users to upload documents, search enterprise knowledge, and receive context-aware answers using Retrieval-Augmented Generation (RAG).

## Overview

The Enterprise AI Knowledge Platform transforms unstructured documents into searchable knowledge. Users can upload documents, retrieve relevant information using hybrid search, and ask natural-language questions through an AI-powered chat interface.

The application combines semantic search, keyword retrieval, reranking, and a large language model to provide relevant answers grounded in document content.

## Key Features

- **Document Upload:** Upload supported PDF, DOCX, and TXT documents.
- **Document Processing:** Extract text, split content into chunks, and prepare documents for retrieval.
- **Semantic Search:** Retrieve relevant information using embedding-based similarity.
- **Hybrid Retrieval:** Combine semantic search with BM25 keyword-based retrieval.
- **Reranking:** Improve the relevance of retrieved document chunks using a cross-encoder reranker.
- **AI-Powered Chat:** Generate context-aware answers using Google's Gemini API.
- **Source-Grounded Responses:** Use retrieved document context to support answers and citations where available.
- **REST API:** Expose backend functionality through FastAPI.
- **Containerized Deployment:** Run the frontend and backend using Docker Compose.

## Architecture

```text
                  User
                   |
                   v
          React + Vite Frontend
                   |
                   v
              FastAPI Backend
                   |
          +--------+---------+
          |                  |
          v                  v
    Document Upload      Chat / Query
          |                  |
          v                  v
    Text Extraction     Hybrid Retrieval
          |             /            \
          v        Semantic Search   BM25
    Text Chunking           \          /
          |                  v
          v               Reranking
    Embeddings                 |
          |                    v
          v               Relevant Chunks
     ChromaDB                   |
                               v
                         Gemini API
                               |
                               v
                         AI Response
```

## Technology Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- Uvicorn
- Sentence Transformers
- ChromaDB
- BM25 (`rank-bm25`)
- LangChain text splitters

### AI and Retrieval
- Google Gemini API
- Sentence embeddings
- Vector similarity search
- BM25 keyword retrieval
- Cross-encoder reranking
- Retrieval-Augmented Generation (RAG)

### Document Processing
- PyPDF
- python-docx
- Python multipart file handling

### DevOps and Testing
- Docker
- Docker Compose
- Nginx
- Pytest
- Git and GitHub
- GitHub Actions

## Project Structure

```text
Enterprise-AI-Knowledge-Platform/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .vscode/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   └── upload.py
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── chunks.json
│   │   │   ├── document_processor.py
│   │   │   ├── rag_service.py
│   │   │   └── storage_service.py
│   │   ├── utils/
│   │   ├── main.py
│   │   └── .env
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
├── sample_documents/
├── scripts/
├── tests/
├── .dockerignore
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Prerequisites

- Docker Desktop with Docker Compose
- Git
- A Google Gemini API key

For local development without Docker:
- Python 3.12 or a compatible Python version
- Node.js and npm

## Configuration

Create or update `backend/app/.env` with your Gemini API key.

```env
GEMINI_API_KEY=your_gemini_api_key
```

Use the existing `.env.example` as a reference for the required configuration variables.

**Security:** Never commit your actual `.env` file, API keys, or other secrets to GitHub.

## Run with Docker Compose

Clone the repository:

```bash
git clone https://github.com/PATHAN-0716/Enterprise-AI-Knowledge-Platform.git
cd Enterprise-AI-Knowledge-Platform
```

Configure the backend environment file at:

```text
backend/app/.env
```

Add the required environment variables before starting the application.

Build and start the application:

```bash
docker compose up --build -d
```

Check running containers:

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

## Access the Application

| Component | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Health Check | http://localhost:8000/health |
| API Documentation | http://localhost:8000/docs |

The API documentation is available through FastAPI's Swagger UI when the backend is running.

## Local Development

### Backend

Create and activate a virtual environment from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r backend/requirements.txt
```

Configure the environment file, then start the backend:

```powershell
uvicorn backend.app.main:app --reload
```

### Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Use the local development URL printed by Vite. Ensure the frontend API URL is configured correctly for the backend.

## Testing

Run the backend tests from the project root:

```powershell
python -m pytest tests -v
```

The test suite includes document processing, storage, and upload-related tests.

## Data and Persistence

The Docker Compose configuration mounts local directories and files for persistent application data, including:

- Uploaded documents
- ChromaDB storage
- Document chunk data

These locations help retain relevant data across container restarts. Keep local data out of version control when it contains private documents, generated indexes, or other sensitive information.

## Future Improvements

- Authentication and role-based access control
- Multi-user document collections
- Improved source attribution and citation validation
- Background document ingestion for large files
- Retrieval and response evaluation
- Observability, performance monitoring, and deployment automation

## Author

**Pathan Adilsha Khan**

GitHub: [PATHAN-0716](https://github.com/PATHAN-0716)

## License

A license has not yet been specified. Add a `LICENSE` file before distributing the project under an open-source license.
