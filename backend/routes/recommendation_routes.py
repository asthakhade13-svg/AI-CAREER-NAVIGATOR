from fastapi import APIRouter, HTTPException
from models.skill_gap_model import SkillAssessmentRequest, SkillGapRequest, SkillGapResponse
from services.career_recommender import recommend_career
from services.skill_gap_analyzer import analyze_skill_gap
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/recommend")
async def api_recommend_career(request: SkillAssessmentRequest):
    """
    Recommend top career domains based on quiz scores and interests.
    """
    try:
        recommendations = recommend_career(request.student_id, request.quiz_results)
        return recommendations
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to recommend career.")


@router.post("/skill_gap", response_model=SkillGapResponse)
async def api_skill_gap(request: SkillGapRequest):
    """
    Analyze skill gap between student's current skills and target domain.
    """
    try:
        gap = analyze_skill_gap(request.student_id, request.target_domain, request.current_skills)
        return gap
    except Exception as e:
        logger.error(f"Skill gap error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze skill gap.")
