
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.services.storage_service import save_document, UPLOAD_DIR
from backend.app.services.rag_service import index_document

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    result = await save_document(file)

    try:
        indexed = index_document(
            file_path=UPLOAD_DIR / result["stored_name"],
            document_id=result["document_id"],
            original_filename=result["filename"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Upload succeeded, but document indexing failed: {exc}",
        ) from exc

    return {
        "message": "Document uploaded and indexed successfully",
        **result,
        **indexed,
    }
