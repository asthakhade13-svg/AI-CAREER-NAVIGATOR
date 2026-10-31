# BUILD: 2026-06-25-v6 — option shuffle + top career paths + FutureWarning fix
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging

logger = logging.getLogger(__name__)

from config import settings
from database import Database
from services.parity_service import sync_directories, resolve_newest_file

# ── Resolve frontend index.html — try multiple candidate paths ─────────────────
# When Railway runs `cd backend && uvicorn app:app`, __file__ may resolve
# differently depending on the Python runtime. We probe all likely locations
# and use the first one that actually exists on disk.
_this_dir  = os.path.dirname(os.path.abspath(__file__))   # always absolute
_repo_root = os.path.dirname(_this_dir)                    # one level up from backend/

_INDEX_CANDIDATES = [
    os.path.join(_this_dir, "..", "frontend", "index.html"),  # standard: ../frontend/
    os.path.join(_repo_root, "frontend", "index.html"),        # repo-root/frontend/
    os.path.join(_repo_root, "index.html"),                    # repo-root/ (legacy fallback)
    os.path.join(_this_dir, "frontend", "index.html"),         # backend/frontend/ (edge case)
]

INDEX_FILE = None
for _candidate in _INDEX_CANDIDATES:
    _candidate = os.path.normpath(_candidate)
    if os.path.exists(_candidate):
        INDEX_FILE = _candidate
        logger.info(f"Frontend index.html resolved to: {INDEX_FILE}")
        break

if INDEX_FILE is None:
    logger.warning("Could not locate frontend index.html — API-only mode")

FRONTEND_DIR = os.path.dirname(INDEX_FILE) if INDEX_FILE else None



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan event handler — replaces deprecated on_event."""
    # ── Startup ──────────────────────────────────────────────────────────────
    try:
        from services.auth_service import init_sqlite_db
        init_sqlite_db()
    except Exception as e:
        logger.warning(f"SQLite init note: {e}")

    try:
        sync_res = sync_directories()
        if sync_res.get("totalSynced", 0) > 0:
            logger.info(f"Frontend dual-directory parity sync: updated {sync_res['totalSynced']} files.")
    except Exception as e:
        logger.warning(f"Parity sync note: {e}")

    Database.connect_db()           # graceful — won't crash if Mongo is offline
    os.makedirs("output", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("models_saved", exist_ok=True)
    yield
    # ── Shutdown ─────────────────────────────────────────────────────────────
    Database.close_db()


app = FastAPI(
    title="First-Generation Career Navigator AI Backend",
    description="AI-powered career guidance platform for B.Tech CS students",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes import (
    quiz_routes,
    recommendation_routes,
    roadmap_routes,
    progress_routes,
    chatbot_routes,
    basic_info_routes,
    adaptive_quiz_routes,
    internship_routes,
    auth_routes,
    certificate_routes,
    project_routes,
    career_routes,
    notification_routes,
    dashboard_routes,
    resume_routes,
    websocket_routes,
    portfolio_routes,
    interview_routes
)

# ── Health check (used by frontend ping) ─────────────────────────────────────
@app.get("/health")
def health_check():
    return JSONResponse({"status": "ok", "version": "1.0.0"})

# ── Serve frontend index.html at root ─────────────────────────────────────────
_NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}

def _serve_index():
    candidates = [
        os.path.join(_this_dir, "..", "frontend", "index.html"),
        os.path.join(_repo_root, "frontend", "index.html"),
        os.path.join(_repo_root, "index.html"),
        os.path.join(_this_dir, "frontend", "index.html"),
    ]
    resolved = resolve_newest_file("index.html", candidates)
    if resolved and os.path.exists(resolved):
        return FileResponse(resolved, headers=_NO_CACHE_HEADERS)
    if INDEX_FILE and os.path.exists(INDEX_FILE):
        return FileResponse(INDEX_FILE, headers=_NO_CACHE_HEADERS)
    return JSONResponse({"message": "Welcome to First-Generation Career Navigator AI Backend"})

@app.get("/")
def serve_frontend():
    return _serve_index()

@app.get("/index.html")
def serve_index_html():
    """Explicit route so /index.html also gets no-cache headers."""
    return _serve_index()

def _serve_page(filename: str):
    candidates = [
        os.path.join(_this_dir, "..", "frontend", filename),
        os.path.join(_repo_root, "frontend", filename),
        os.path.join(_repo_root, filename),
        os.path.join(_this_dir, "frontend", filename),
    ]
    resolved = resolve_newest_file(filename, candidates)
    if resolved and os.path.exists(resolved):
        return FileResponse(resolved, headers=_NO_CACHE_HEADERS)
    return JSONResponse({"message": f"{filename} not found"}, status_code=404)

def _serve_portfolio():
    return _serve_page("portfolio.html")

@app.get("/portfolio/{student_id}")
def serve_portfolio_for_student(student_id: str):
    """Serves the public student showcase & recruiter portfolio page."""
    return _serve_portfolio()

@app.get("/{page_name}.html")
def serve_html_page(page_name: str):
    """Serves frontend html pages with no-cache headers."""
    return _serve_page(f"{page_name}.html")

@app.get("/{asset_name}.css")
def serve_css_file(asset_name: str):
    """Serves frontend css stylesheets."""
    return _serve_page(f"{asset_name}.css")

@app.get("/api.js")
def serve_api_js():
    """Serves frontend api.js SDK."""
    return _serve_page("api.js")

@app.get("/manifest.json")
def serve_manifest():
    """Serves PWA Web App Manifest with correct application/manifest+json MIME."""
    res = _serve_page("manifest.json")
    if isinstance(res, FileResponse):
        res.headers["Content-Type"] = "application/manifest+json"
    return res

@app.get("/sw.js")
def serve_service_worker():
    """Serves Service Worker with Service-Worker-Allowed header scoped to root."""
    res = _serve_page("sw.js")
    if isinstance(res, FileResponse):
        res.headers["Content-Type"] = "application/javascript"
        res.headers["Service-Worker-Allowed"] = "/"
    return res

@app.get("/icons/{icon_name}")
def serve_icon_file(icon_name: str):
    """Serves PWA icons."""
    return _serve_page(os.path.join("icons", icon_name))

# Include API routers
app.include_router(dashboard_routes.router)
app.include_router(auth_routes.router)
app.include_router(certificate_routes.router)
app.include_router(project_routes.router)
app.include_router(career_routes.router)
app.include_router(notification_routes.router)
app.include_router(resume_routes.router)
app.include_router(websocket_routes.router)
app.include_router(portfolio_routes.router)
app.include_router(interview_routes.router)
app.include_router(basic_info_routes.router,        prefix="/api/v1/basic_info",         tags=["Basic Info"])
app.include_router(adaptive_quiz_routes.router,     prefix="/api/v1/quiz/adaptive",      tags=["Adaptive Quiz"])
app.include_router(quiz_routes.router,              prefix="/api/v1/quiz",               tags=["Quiz"])
app.include_router(recommendation_routes.router,    prefix="/api/v1/recommendation",     tags=["Recommendation"])
app.include_router(roadmap_routes.router,           prefix="/api/v1/roadmap",            tags=["Roadmap"])
app.include_router(progress_routes.router,          prefix="/api/v1/progress",           tags=["Progress"])
app.include_router(chatbot_routes.router,           prefix="/api/v1/chatbot",            tags=["Chatbot"])
app.include_router(internship_routes.router,        prefix="/api/v1/internships",        tags=["Internships"])

# Mount static assets (images, etc.) from the frontend directory.
# html=False so this NEVER intercepts / or /index.html — those are handled above.
if FRONTEND_DIR and os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend-assets")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)