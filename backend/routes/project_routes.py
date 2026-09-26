from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
import logging
from services.project_service import get_recommended_projects

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/projects", tags=["AI Project & Capstone Blueprints"])

@router.get("/recommend")
def recommend_projects(track: str = Query("aiml")):
    """
    Returns personalized portfolio project blueprints tailored to the student's career track.
    """
    try:
        projects = get_recommended_projects(track)
        return {
            "success": True,
            "track": track,
            "totalProjects": len(projects),
            "projects": projects
        }
    except Exception as e:
        logger.error(f"Error fetching recommended projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))
