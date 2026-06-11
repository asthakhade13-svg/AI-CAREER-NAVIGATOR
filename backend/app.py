import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import settings
from database import Database

from routes import quiz_routes, recommendation_routes, roadmap_routes, progress_routes, chatbot_routes

app = FastAPI(
    title="First-Generation Career Navigator AI Backend",
    description="AI-powered career guidance platform for B.Tech CS students",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    Database.connect_db()

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("models_saved", exist_ok=True)

@app.on_event("shutdown")
async def shutdown_db_client():
    Database.close_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to First-Generation Career Navigator AI Backend"}

# Include routers
app.include_router(quiz_routes.router, prefix="/api/v1/quiz", tags=["Quiz"])
app.include_router(recommendation_routes.router, prefix="/api/v1/recommendation", tags=["Recommendation"])
app.include_router(roadmap_routes.router, prefix="/api/v1/roadmap", tags=["Roadmap"])
app.include_router(progress_routes.router, prefix="/api/v1/progress", tags=["Progress"])
app.include_router(chatbot_routes.router, prefix="/api/v1/chatbot", tags=["Chatbot"])

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)