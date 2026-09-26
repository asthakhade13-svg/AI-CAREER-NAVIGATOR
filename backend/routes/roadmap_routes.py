from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.roadmap_generator import generate_roadmap

router = APIRouter()


class RoadmapRequest(BaseModel):
    target_domain: str = "Web Development"
    missing_skills: Optional[List[str]] = None
    timeframe: Optional[str] = "6 Months"
    custom_prompt: Optional[str] = None


@router.post("/generate")
async def api_generate_roadmap(request: RoadmapRequest):
    """
    Generate a personalized learning roadmap with milestones, custom prompt, and resources.
    """
    try:
        roadmap = generate_roadmap(
            target_domain=request.target_domain,
            missing_skills=request.missing_skills,
            timeframe=request.timeframe,
            custom_prompt=request.custom_prompt
        )
        return roadmap
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate roadmap.")
