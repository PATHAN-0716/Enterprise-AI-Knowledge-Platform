import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from backend.app.services import storage_service


def run_async(coroutine):
    return asyncio.run(coroutine)


def test_save_valid_txt(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "UPLOAD_DIR", tmp_path)

    content = b"FastAPI and retrieval augmented generation"
    upload = UploadFile(
        filename="guide.txt",
        file=BytesIO(content),
    )

    result = run_async(storage_service.save_document(upload))
    saved_path = tmp_path / result["stored_name"]

    assert result["filename"] == "guide.txt"
    assert result["size_bytes"] == len(content)
    assert saved_path.exists()
    assert saved_path.read_bytes() == content


def test_reject_unsupported_extension(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "UPLOAD_DIR", tmp_path)

    upload = UploadFile(
        filename="program.exe",
        file=BytesIO(b"not allowed"),
    )

    with pytest.raises(HTTPException) as error:
        run_async(storage_service.save_document(upload))

    assert error.value.status_code == 400


def test_reject_oversized_file(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_service, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(storage_service, "MAX_FILE_SIZE", 10)

    upload = UploadFile(
        filename="large.txt",
        file=BytesIO(b"x" * 11),
    )

    with pytest.raises(HTTPException) as error:
        run_async(storage_service.save_document(upload))

    assert error.value.status_code == 413
    assert list(tmp_path.iterdir()) == []
