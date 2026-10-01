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
        
        # Save to SQLite assessment_history
        try:
            import json, uuid
            from services.auth_service import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            attempt_id = "att_" + str(uuid.uuid4())[:8]
            tracks_json = json.dumps(response.profile_summary.recommended_tracks if hasattr(response.profile_summary, 'recommended_tracks') else [])
            interests_json = json.dumps(response.profile_summary.interests if hasattr(response.profile_summary, 'interests') else [])
            full_name = response.profile_summary.full_name if hasattr(response.profile_summary, 'full_name') else "Student"

            cursor.execute("""
            INSERT INTO assessment_history (
                student_id, attempt_id, assessment_type, technical_score, 
                starting_quiz, recommended_tracks, dominant_interests, full_name
            ) VALUES (?, ?, 'stellar_assessment', ?, ?, ?, ?, ?)
            """, (
                request.student_id,
                attempt_id,
                response.technical_score,
                response.starting_quiz,
                tracks_json,
                interests_json,
                full_name
            ))
            conn.commit()
            conn.close()
        except Exception as sqle:
            logger.warning(f"SQLite assessment history log notice: {sqle}")

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


@router.get("/history/{student_id}")
def get_assessment_history(student_id: str):
    """
    Returns multi-test assessment attempt history for a student.
    """
    import json
    from services.auth_service import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM assessment_history 
    WHERE student_id = ? OR student_id = 'user_001'
    ORDER BY date_taken DESC
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()

    history = []
    for r in rows:
        try:
            tracks = json.loads(r["recommended_tracks"]) if r["recommended_tracks"] else []
        except Exception:
            tracks = []
        try:
            interests = json.loads(r["dominant_interests"]) if r["dominant_interests"] else []
        except Exception:
            interests = []

        history.append({
            "id": r["id"],
            "attemptId": r["attempt_id"],
            "assessmentType": r["assessment_type"],
            "technicalScore": r["technical_score"],
            "startingQuiz": r["starting_quiz"],
            "recommendedTracks": tracks,
            "dominantInterests": interests,
            "fullName": r["full_name"],
            "dateTaken": r["date_taken"]
        })

    return {
        "success": True,
        "studentId": student_id,
        "totalAttempts": len(history),
        "history": history
    }


