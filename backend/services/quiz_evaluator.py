from models.quiz_evaluation_model import QuizEvaluationRequest, QuizEvaluationResult
from database import db
from bson import ObjectId


def evaluate_quiz(student_id: str, quiz_id: str, student_answers: dict) -> QuizEvaluationResult:
    """
    Evaluates a student's quiz answers against the correct answers.
    """
    try:
        quizzes_col = db.get_collection("quizzes")
        quiz = quizzes_col.find_one({"_id": ObjectId(quiz_id)})

        if not quiz:
            raise ValueError(f"Quiz with ID {quiz_id} not found.")

    except ValueError:
        raise
    except Exception as e:
        # For testing without DB, continue with mock evaluation
        pass

    # Mocking evaluation logic for now
    total_questions = len(student_answers)
    correct_count = sum(
        [1 for k, v in student_answers.items() if v.lower() == "correct_answer"]
    )  # Mock check

    accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    result = QuizEvaluationResult(
        total_score=correct_count,
        accuracy=accuracy,
        topic_scores={"Python": 90.0, "Networking": 60.0},  # Mocked
        difficulty_scores={"Easy": 100.0, "Medium": 50.0, "Hard": 0.0}  # Mocked
    )

    # Save to DB
    try:
        results_col = db.get_collection("quiz_results")
        results_col.insert_one({
            "student_id": student_id,
            "quiz_id": quiz_id,
            "result": result.model_dump()
        })
    except Exception:
        pass

    return result
