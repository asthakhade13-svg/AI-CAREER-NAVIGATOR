from models.quiz_evaluation_model import QuizEvaluationResult
from database import db
import logging

logger = logging.getLogger(__name__)


def evaluate_quiz(student_id: str, quiz_id: str, student_answers: dict) -> QuizEvaluationResult:
    """
    Evaluates a student's quiz answers against the correct answers.
    Falls back to mock evaluation if MongoDB is not connected.
    """
    quiz = None
    try:
        quizzes_col = db.get_collection("quizzes")
        if quizzes_col is not None:
            from bson import ObjectId
            quiz = quizzes_col.find_one({"_id": ObjectId(quiz_id)})
    except Exception as e:
        logger.warning(f"Could not fetch quiz from DB: {e}")

    # Evaluate against DB quiz if found, else use mock evaluation
    total_questions = len(student_answers)

    if quiz:
        correct_count = sum(
            1 for q_id, ans in student_answers.items()
            if quiz.get(q_id, {}).get("correct_answer", "").lower() == ans.lower()
        )
    else:
        # Mock check for dev without DB
        correct_count = sum(
            1 for v in student_answers.values() if v.lower() == "a"
        )

    accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    result = QuizEvaluationResult(
        total_score=correct_count,
        accuracy=accuracy,
        topic_scores={"Python": 90.0, "Networking": 60.0},
        difficulty_scores={"Easy": 100.0, "Medium": 50.0, "Hard": 0.0}
    )

    # Save to DB (no-op if MongoDB is offline)
    try:
        results_col = db.get_collection("quiz_results")
        if results_col is not None:
            results_col.insert_one({
                "student_id": student_id,
                "quiz_id": quiz_id,
                "result": result.model_dump()
            })
    except Exception:
        pass

    return result
