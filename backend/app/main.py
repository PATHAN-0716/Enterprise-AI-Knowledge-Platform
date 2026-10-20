
import os
import logging
from fastapi import Request
from starlette.responses import JSONResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from backend.app.api.upload import router as upload_router
from backend.app.api.documents import router as documents_router
from backend.app.api.chat import router as chat_router

app = FastAPI(title="Enterprise AI Knowledge Platform")
logger = logging.getLogger("uvicorn.error")

@app.middleware("http")
async def log_upload_errors(request: Request, call_next):
    if request.url.path == "/upload" and request.method == "POST":
        print("UPLOAD CONTENT-TYPE:", request.headers.get("content-type"))
        print("UPLOAD CONTENT-LENGTH:", request.headers.get("content-length"))

    response = await call_next(request)
    return response

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error; check backend logs"},
    )
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Enterprise AI Knowledge Platform!"
    }


@app.get("/health")
def health():
    return {"status": "ok"}
