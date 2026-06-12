"""
Adaptive Quiz Routes
====================
POST /api/v1/quiz/adaptive/start   — Start a new adaptive quiz session
POST /api/v1/quiz/adaptive/answer  — Submit an answer and get next question or results
GET  /api/v1/quiz/adaptive/status  — Get session status (for reconnect)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import logging

from services.adaptive_quiz_service import (
    start_adaptive_session,
    submit_adaptive_answer,
    get_session,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Request / Response Schemas ───────────────────────────────────────────────
class StartSessionRequest(BaseModel):
    student_id: str = Field(..., description="Unique student identifier")
    technical_score: float = Field(0.0, description="Technical familiarity score from questionnaire")
    interest_field: Optional[str] = Field(None, description="Primary interest/career field from questionnaire")


class SubmitAnswerRequest(BaseModel):
    session_id: str = Field(..., description="Session ID returned from /start")
    question_id: int = Field(..., description="ID of the question being answered")
    given_answer: str = Field(..., description="Answer choice: A, B, C, or D")


# ─── Endpoints ────────────────────────────────────────────────────────────────
@router.post("/start")
async def api_start_adaptive_quiz(request: StartSessionRequest):
    """
    Start a new Computer Adaptive Test (CAT) session.

    Returns the session_id and first question.
    """
    try:
        result = start_adaptive_session(
            student_id=request.student_id,
            technical_score=request.technical_score,
            interest_field=request.interest_field,
        )
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting adaptive quiz session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start adaptive quiz session.")


@router.post("/answer")
async def api_submit_adaptive_answer(request: SubmitAnswerRequest):
    """
    Submit an answer to the current question.

    Returns:
    - If quiz is still in progress: next question + metadata.
    - If quiz is complete: final results with learning path + career recommendations.
    """
    try:
        result = submit_adaptive_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            given_answer=request.given_answer,
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting adaptive answer: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit answer.")


@router.get("/status/{session_id}")
async def api_get_session_status(session_id: str):
    """
    Get the current status of an adaptive quiz session.
    Useful for reconnection/resume after page refresh.
    """
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {
        "session_id": session_id,
        "student_id": session["student_id"],
        "questions_answered": session["questions_answered"],
        "correct_answers": session["correct_answers"],
        "total_questions": 30,
        "completed": session["completed"],
        "current_difficulty": session.get("current_difficulty"),
    }
