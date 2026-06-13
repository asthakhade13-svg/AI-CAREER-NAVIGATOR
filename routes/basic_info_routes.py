from fastapi import APIRouter, HTTPException
from models.basic_info_model import QuestionnaireSubmit, QuestionnaireResponse
from services.basic_info_service import get_basic_info_questions, classify_student_profile
from services.adaptive_quiz_service import _get_available_fields
from database import db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/questions")
async def api_get_questions():
    """
    Retrieve all grouped interest questionnaire questions.
    """
    try:
        questions = get_basic_info_questions()
        return questions
    except Exception as e:
        logger.error(f"Error fetching questionnaire questions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch questionnaire.")

@router.get("/career_fields")
async def api_get_career_fields():
    """
    Return a sorted list of all unique career fields available in the adaptive question bank.
    The frontend uses this to populate the career interest picker in the questionnaire.
    """
    try:
        fields = sorted(_get_available_fields())
        return {"career_fields": fields}
    except Exception as e:
        logger.error(f"Error fetching career fields: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch career fields.")

@router.post("/evaluate", response_model=QuestionnaireResponse)
async def api_evaluate_profile(request: QuestionnaireSubmit):
    """
    Submit questionnaire responses and get automatic starting quiz classification.
    """
    try:
        response = classify_student_profile(request.student_id, request.answers)
        
        # Optionally save the student profile submission in MongoDB (no-op if DB is offline)
        try:
            profiles_col = db.get_collection("student_profiles")
            if profiles_col is not None:
                profiles_col.update_one(
                    {"student_id": request.student_id},
                    {
                        "$set": {
                            "student_id": request.student_id,
                            "answers": request.answers,
                            "technical_score": response.technical_score,
                            "starting_quiz": response.starting_quiz,
                            "reason": response.reason,
                            "profile_summary": response.profile_summary.model_dump()
                        }
                    },
                    upsert=True
                )
        except Exception as e:
            logger.warning(f"Failed to save student profile to MongoDB: {e}")
            
        return response
    except Exception as e:
        logger.error(f"Error evaluating profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate profile.")

