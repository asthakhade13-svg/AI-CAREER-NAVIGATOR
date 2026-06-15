from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.quiz_evaluation_model import (
    QuizGenerateRequest,
    QuizOutput,
    QuizEvaluationRequest,
    QuizEvaluationResult,
)
from services.quiz_generator import generate_quiz
from services.quiz_evaluator import evaluate_quiz
from services.general_quiz_service import get_general_questions, evaluate_general_quiz
from services.cs_quiz_service import get_cs_questions, evaluate_cs_quiz
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

        # Save to DB (no-op if MongoDB is offline)
        try:
            quizzes_col = db.get_collection("quizzes")
            if quizzes_col is not None:
                quizzes_col.insert_one(quiz_data)
        except Exception:
            pass  # Ignore DB errors in local dev

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


class GeneralQuizEvaluationRequest(BaseModel):
    student_id: str
    answers: dict


@router.get("/general")
async def api_get_general_quiz():
    """
    Get the list of general MCQ questions (excluding correct answers and categories).
    """
    try:
        questions = get_general_questions()
        return questions
    except Exception as e:
        logger.error(f"Error fetching general quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch general quiz.")


@router.post("/general/evaluate")
async def api_evaluate_general_quiz(request: GeneralQuizEvaluationRequest):
    """
    Evaluate general quiz answers, calculate domain scores, and recommend careers.
    """
    try:
        result = evaluate_general_quiz(request.student_id, request.answers)
        return result
    except Exception as e:
        logger.error(f"Error evaluating general quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate general quiz.")


class CSQuizEvaluationRequest(BaseModel):
    student_id: str
    answers: dict


@router.get("/cs")
async def api_get_cs_quiz():
    """
    Get the list of CS MCQ questions (excluding correct answers and categories).
    """
    try:
        questions = get_cs_questions()
        return questions
    except Exception as e:
        logger.error(f"Error fetching CS quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch CS quiz.")


@router.post("/cs/evaluate")
async def api_evaluate_cs_quiz(request: CSQuizEvaluationRequest):
    """
    Evaluate CS quiz answers, calculate domain scores, and recommend careers.
    """
    try:
        result = evaluate_cs_quiz(request.student_id, request.answers)
        return result
    except Exception as e:
        logger.error(f"Error evaluating CS quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate CS quiz.")


