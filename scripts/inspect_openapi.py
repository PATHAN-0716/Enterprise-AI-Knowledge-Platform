from backend.app.main import app

schema = app.openapi()
print("Upload path present:", "/upload" in schema.get("paths", {}))
print("Upload path schema:", schema.get("paths", {}).get("/upload"))
