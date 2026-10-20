from fastapi import FastAPI, File, UploadFile
from fastapi.testclient import TestClient

app = FastAPI()

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}

client = TestClient(app)
response = client.post(
    "/test-upload",
    files={"file": ("test.txt", b"hello upload", "text/plain")},
)
print("Status:", response.status_code)
print("Response:", response.text)
