from fastapi.testclient import TestClient
from backend.app.main import app

with TestClient(app) as client:
    response = client.post(
        "/upload",
        files={"file": ("test.exe", b"hello", "text/plain")},
    )
    print("Status:", response.status_code)
    print("Response:", response.text)
