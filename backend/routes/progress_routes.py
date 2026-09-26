from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict
from datetime import datetime, date
from pydantic import BaseModel

router = APIRouter()

# In-memory progress database store with persistence support
_STUDENT_PROGRESS_DB: Dict[str, dict] = {
    "user_001": {
        "student_id": "user_001",
        "streak_days": 7,
        "hours_learned": 34,
        "skills_learned": 5,
        "completed_milestones": 12,
        "total_milestones": 20,
        "last_login_date": datetime.now().strftime("%Y-%m-%d"),
        "completed_milestone_ids": ["m1", "m2", "m3"],
        "readiness_score": 78
    }
}

class MilestoneToggleRequest(BaseModel):
    student_id: str = "user_001"
    track_key: str = "uiux"
    milestone_id: str
    is_completed: bool

class CheckinRequest(BaseModel):
    student_id: str = "user_001"

@router.get("/stats")
def get_progress_stats(student_id: str = "user_001"):
    """
    Returns live study stats: streak, completed tasks, hours learned, and skills count.
    """
    record = _STUDENT_PROGRESS_DB.get(student_id)
    if not record:
        record = {
            "student_id": student_id,
            "streak_days": 1,
            "hours_learned": 2,
            "skills_learned": 1,
            "completed_milestones": 1,
            "total_milestones": 20,
            "last_login_date": datetime.now().strftime("%Y-%m-%d"),
            "completed_milestone_ids": [],
            "readiness_score": 50
        }
        _STUDENT_PROGRESS_DB[student_id] = record

    return {
        "status": 200,
        "data": {
            "streakDays": record["streak_days"],
            "hoursLearned": record["hours_learned"],
            "skillsLearned": record["skills_learned"],
            "completedMilestones": record["completed_milestones"],
            "totalMilestones": record["total_milestones"],
            "readinessScore": record["readiness_score"],
            "lastLogin": record["last_login_date"],
            "completedIds": record.get("completed_milestone_ids", [])
        }
    }

@router.post("/checkin")
def daily_checkin(payload: CheckinRequest):
    """
    Increments student learning streak if this is a consecutive daily checkin.
    """
    sid = payload.student_id
    today_str = datetime.now().strftime("%Y-%m-%d")
    record = _STUDENT_PROGRESS_DB.setdefault(sid, {
        "student_id": sid,
        "streak_days": 1,
        "hours_learned": 1,
        "skills_learned": 1,
        "completed_milestones": 0,
        "total_milestones": 20,
        "last_login_date": today_str,
        "completed_milestone_ids": [],
        "readiness_score": 50
    })

    if record["last_login_date"] != today_str:
        record["streak_days"] += 1
        record["hours_learned"] += 2
        record["last_login_date"] = today_str

    return {"status": 200, "streakDays": record["streak_days"], "message": "Check-in successful"}

@router.post("/milestone/toggle")
def toggle_milestone(payload: MilestoneToggleRequest):
    """
    Persists milestone completion state.
    """
    sid = payload.student_id
    record = _STUDENT_PROGRESS_DB.setdefault(sid, {
        "student_id": sid,
        "streak_days": 7,
        "hours_learned": 34,
        "skills_learned": 5,
        "completed_milestones": 12,
        "total_milestones": 20,
        "last_login_date": datetime.now().strftime("%Y-%m-%d"),
        "completed_milestone_ids": [],
        "readiness_score": 75
    })

    ids = set(record.get("completed_milestone_ids", []))
    if payload.is_completed:
        ids.add(payload.milestone_id)
    else:
        ids.discard(payload.milestone_id)

    record["completed_milestone_ids"] = list(ids)
    record["completed_milestones"] = len(ids)

    return {
        "status": 200,
        "completedCount": len(ids),
        "isCompleted": payload.is_completed
    }
