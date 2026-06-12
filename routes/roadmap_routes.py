from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.roadmap_generator import generate_roadmap

router = APIRouter()


class RoadmapRequest(BaseModel):
    target_domain: str
    missing_skills: List[str]


@router.post("/generate")
async def api_generate_roadmap(request: RoadmapRequest):
    """
    Generate a personalized learning roadmap.
    """
    try:
        roadmap = generate_roadmap(request.target_domain, request.missing_skills)
        return roadmap
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate roadmap.")
