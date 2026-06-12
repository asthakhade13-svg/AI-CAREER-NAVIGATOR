import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import settings
from database import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan event handler — replaces deprecated on_event."""
    # ── Startup ──────────────────────────────────────────────────────────────
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

from routes import quiz_routes, recommendation_routes, roadmap_routes, progress_routes, chatbot_routes

@app.get("/")
def read_root():
    return {"message": "Welcome to First-Generation Career Navigator AI Backend"}

# Include routers
app.include_router(quiz_routes.router,           prefix="/api/v1/quiz",           tags=["Quiz"])
app.include_router(recommendation_routes.router, prefix="/api/v1/recommendation", tags=["Recommendation"])
app.include_router(roadmap_routes.router,        prefix="/api/v1/roadmap",        tags=["Roadmap"])
app.include_router(progress_routes.router,       prefix="/api/v1/progress",       tags=["Progress"])
app.include_router(chatbot_routes.router,        prefix="/api/v1/chatbot",        tags=["Chatbot"])

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)