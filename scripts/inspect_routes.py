from backend.app.main import app

for route in app.routes:
    print(
        type(route).__name__,
        "path =", getattr(route, "path", None),
        "name =", getattr(route, "name", None),
        "methods =", getattr(route, "methods", None),
    )
