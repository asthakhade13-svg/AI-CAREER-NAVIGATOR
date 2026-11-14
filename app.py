# AI Career Navigator — Root Application Bridge
# This file bridges root execution (e.g. Render / Railway default root directory)
# directly into the full backend application in backend/app.py.
import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.join(_this_dir, "backend")

if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Switch working directory to backend so relative paths (data/, config, etc.) resolve
os.chdir(_backend_dir)

from app import app, serve_frontend, health_check

if __name__ == "__main__":
    import uvicorn
    from config import settings
    uvicorn.run("app:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
