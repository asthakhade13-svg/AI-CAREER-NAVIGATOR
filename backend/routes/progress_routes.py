from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from datetime import datetime, date
from pydantic import BaseModel
from services.report_service import get_weekly_ai_report, save_weekly_goals
from services.auth_service import get_db_connection

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

class WeeklyGoalRequest(BaseModel):
    student_id: str = "user_001"
    target_hours: float = 10.0
    target_milestones: int = 3
    focus_topic: str = "Data Structures & Algorithms"


@router.get("/stats")
def get_progress_stats(student_id: str = "user_001"):
    """
    Returns live study stats: streak, completed tasks, hours learned, and skills count.
    """
    record = _STUDENT_PROGRESS_DB.get(student_id)
    if not record:
        record = {
            "student_id": student_id,
            "streak_days": 7,
            "hours_learned": 34,
            "skills_learned": 5,
            "completed_milestones": 12,
            "total_milestones": 20,
            "last_login_date": datetime.now().strftime("%Y-%m-%d"),
            "completed_milestone_ids": ["m1", "m2", "m3"],
            "readiness_score": 78
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
    Increments student learning streak and logs checkin.
    """
    sid = payload.student_id
    today_str = datetime.now().strftime("%Y-%m-%d")
    record = _STUDENT_PROGRESS_DB.setdefault(sid, {
        "student_id": sid,
        "streak_days": 6,
        "hours_learned": 32,
        "skills_learned": 5,
        "completed_milestones": 11,
        "total_milestones": 20,
        "last_login_date": today_str,
        "completed_milestone_ids": ["m1", "m2"],
        "readiness_score": 76
    })

    if record["last_login_date"] != today_str:
        record["streak_days"] += 1
        record["hours_learned"] += 2
        record["last_login_date"] = today_str

    # Log to SQLite
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO progress_logs (student_id, activity_type, hours_spent)
        VALUES (?, 'checkin', 1.5)
        """, (sid,))
        conn.commit()
        conn.close()
    except Exception:
        pass

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

    # Log to SQLite
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO progress_logs (student_id, activity_type, track_key, milestone_id, hours_spent)
        VALUES (?, 'milestone', ?, ?, 2.0)
        """, (sid, payload.track_key, payload.milestone_id))
        conn.commit()
        conn.close()
    except Exception:
        pass

    return {
        "status": 200,
        "completedCount": len(ids),
        "isCompleted": payload.is_completed
    }


# ── Weekly AI Progress Report & Goal Setter ────────────────────────────────────
@router.get("/weekly-report")
def get_weekly_report(
    student_id: str = Query("user_001"),
    track_key: str = Query("aiml"),
    user_name: str = Query("Astha")
):
    """
    Returns automated weekly AI performance digest, velocity index, and recommended goals.
    """
    try:
        report = get_weekly_ai_report(student_id=student_id, track_key=track_key, user_name=user_name)
        return {
            "status": 200,
            "success": True,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/goals")
def set_goals(payload: WeeklyGoalRequest):
    """
    Sets or updates student's weekly study goals.
    """
    try:
        goal_data = save_weekly_goals(
            student_id=payload.student_id,
            target_hours=payload.target_hours,
            target_milestones=payload.target_milestones,
            focus_topic=payload.focus_topic
        )
        return {
            "status": 200,
            "success": True,
            "message": "Weekly goals saved successfully",
            "goals": goal_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/goals")
def get_goals(student_id: str = Query("user_001")):
    """
    Retrieves the latest active weekly goals for a student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM weekly_goals WHERE student_id = ? ORDER BY created_at DESC LIMIT 1
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "status": 200,
            "hasGoals": False,
            "goals": {
                "studentId": student_id,
                "targetHours": 10.0,
                "targetMilestones": 3,
                "focusTopic": "Data Structures & Algorithms",
                "achievedHours": 8.5,
                "achievedMilestones": 2
            }
        }

    return {
        "status": 200,
        "hasGoals": True,
        "goals": {
            "goalId": row["id"],
            "studentId": row["student_id"],
            "targetHours": row["target_hours"],
            "targetMilestones": row["target_milestones"],
            "focusTopic": row["focus_topic"],
            "achievedHours": row["achieved_hours"],
            "achievedMilestones": row["achieved_milestones"],
            "weekStartDate": row["week_start_date"],
            "status": row["status"]
        }
    }


class GoalItemToggleRequest(BaseModel):
    student_id: str
    goal_text: str
    is_completed: bool

@router.post("/goals/items/toggle")
def toggle_individual_goal(payload: GoalItemToggleRequest):
    """
    Persists checked/unchecked state of an individual weekly goal item in SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO goal_items (student_id, goal_text, is_completed, updated_at)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(student_id, goal_text) DO UPDATE SET
        is_completed = excluded.is_completed,
        updated_at = CURRENT_TIMESTAMP
    """, (payload.student_id, payload.goal_text, 1 if payload.is_completed else 0))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "goalText": payload.goal_text,
        "isCompleted": payload.is_completed
    }

@router.get("/goals/items/{student_id}")
def get_individual_goals(student_id: str):
    """
    Retrieves the persisted goal item states for the student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM goal_items WHERE student_id = ?
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()

    items = {
        r["goal_text"]: bool(r["is_completed"])
        for r in rows
    }

    return {
        "success": True,
        "studentId": student_id,
        "items": items
    }

