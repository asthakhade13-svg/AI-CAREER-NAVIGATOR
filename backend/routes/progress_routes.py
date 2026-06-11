from fastapi import APIRouter, HTTPException
from database import db
from datetime import datetime
from models.progress_model import StudentProgress

router = APIRouter()


@router.get("/{student_id}", response_model=StudentProgress)
async def get_student_progress(student_id: str):
    """
    Retrieve student's learning progress.
    """
    try:
        progress_col = db.get_collection("progress_logs")
        progress = progress_col.find_one({"student_id": student_id})

        if not progress:
            # Return mock data if not found (for demonstration)
            return StudentProgress(
                student_id=student_id,
                average_score=75.5,
                learning_streak=5,
                domain_progress=[],
                placement_readiness_score=60.0,
                last_active=datetime.now()
            )

        return progress
    except Exception as e:
        # Fallback for dev without DB
        return StudentProgress(
            student_id=student_id,
            average_score=80.0,
            learning_streak=3,
            domain_progress=[],
            placement_readiness_score=70.0,
            last_active=datetime.now()
        )
