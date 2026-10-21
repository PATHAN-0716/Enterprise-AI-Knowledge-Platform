from fastapi import FastAPI, File, UploadFile
from fastapi.testclient import TestClient

app = FastAPI()


@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "content": content.decode("utf-8")}


client = TestClient(app)


def test_upload():
    response = client.post(
        "/test-upload",
        files={"file": ("test.txt", b"Hello, world!", "text/plain")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "test.txt",
        "content": "Hello, world!",
    }
