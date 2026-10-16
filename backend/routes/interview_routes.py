from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from services.interview_service import (
    get_tracks_and_companies_catalog,
    start_interview_session,
    submit_interview_turn,
    get_interview_scorecard,
    get_student_interview_history
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/interview", tags=["AI Mock Interview Simulator"])

class InterviewStartRequest(BaseModel):
    student_id: str
    student_name: Optional[str] = "Candidate"
    track_key: str = "webdev"
    company_tier: str = "faang"

class InterviewSubmitTurnRequest(BaseModel):
    session_id: str
    round_type: str = "behavioral"
    question_index: int = 0
    answer_text: str = ""
    code_snippet: Optional[str] = ""

@router.get("/tracks-and-companies")
def get_tracks_and_companies():
    """
    Returns supported interview roles, company tiers, and round time allocations.
    """
    try:
        return get_tracks_and_companies_catalog()
    except Exception as e:
        logger.error(f"Error fetching interview tracks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
def start_interview(req: InterviewStartRequest):
    """
    Initializes a structured 3-round mock interview session.
    """
    try:
        result = start_interview_session(
            student_id=req.student_id,
            student_name=req.student_name or "Candidate",
            track_key=req.track_key,
            company_tier=req.company_tier
        )
        return result
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-response")
def submit_interview_response(req: InterviewSubmitTurnRequest):
    """
    Submits answer or code for current round, rates response, and advances round.
    """
    try:
        result = submit_interview_turn(
            session_id=req.session_id,
            round_type=req.round_type,
            question_index=req.question_index,
            answer_text=req.answer_text,
            code_snippet=req.code_snippet or ""
        )
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("message", "Session not found"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating interview response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scorecard/{session_id}")
def get_scorecard(session_id: str):
    """
    Returns comprehensive 4-dimension performance rubric & remediation milestone plan.
    """
    try:
        result = get_interview_scorecard(session_id)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("message", "Scorecard not found"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching interview scorecard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{student_id}")
def get_history(student_id: str):
    """
    Retrieves student's previous mock interview sessions.
    """
    try:
        return get_student_interview_history(student_id)
    except Exception as e:
        logger.error(f"Error fetching interview history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
