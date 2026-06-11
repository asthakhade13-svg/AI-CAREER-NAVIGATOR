from fastapi import APIRouter, HTTPException
from models.quiz_evaluation_model import (
    QuizGenerateRequest,
    QuizOutput,
    QuizEvaluationRequest,
    QuizEvaluationResult,
)
from services.quiz_generator import generate_quiz
from services.quiz_evaluator import evaluate_quiz
from database import db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=QuizOutput)
async def api_generate_quiz(request: QuizGenerateRequest):
    """
    Generate a quiz based on topic and content using Gemini.
    """
    try:
        quiz_data = generate_quiz(request.topic, request.content)

        # Save to DB
        try:
            quizzes_col = db.get_collection("quizzes")
            quizzes_col.insert_one(quiz_data)
        except Exception:
            pass  # Ignore DB error for local dev if not connected

        return quiz_data
    except Exception as e:
        logger.error(f"Generate quiz error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate quiz.")


@router.post("/evaluate", response_model=QuizEvaluationResult)
async def api_evaluate_quiz(request: QuizEvaluationRequest):
    """
    Evaluate student quiz answers.
    """
    try:
        result = evaluate_quiz(request.student_id, request.quiz_id, request.answers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Evaluate quiz error: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate quiz.")
