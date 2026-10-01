from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.roadmap_generator import generate_roadmap

router = APIRouter()


class RoadmapRequest(BaseModel):
    target_domain: str = "Web Development"
    missing_skills: Optional[List[str]] = None
    timeframe: Optional[str] = "6 Months"
    custom_prompt: Optional[str] = None


@router.post("/generate")
async def api_generate_roadmap(request: RoadmapRequest):
    """
    Generate a personalized learning roadmap with milestones, custom prompt, and resources.
    """
    try:
        roadmap = generate_roadmap(
            target_domain=request.target_domain,
            missing_skills=request.missing_skills,
            timeframe=request.timeframe,
            custom_prompt=request.custom_prompt
        )
        return roadmap
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate roadmap.")


@router.get("/export-ics/{track_key}")
def export_roadmap_ics(track_key: str = "aiml"):
    """
    Generates downloadable .ics calendar file containing weekly milestone study schedules.
    """
    from fastapi.responses import Response
    from datetime import datetime, timedelta

    track_names = {
        "aiml": "AI & Machine Learning Engineer",
        "webdev": "Full-Stack Web Development",
        "data": "Data Science & Big Data",
        "cloud": "Cloud Architecture & DevOps",
        "cyber": "Cybersecurity & Ethical Hacking",
        "uiux": "UI/UX Design & Product Strategy"
    }
    track_title = track_names.get(track_key.lower(), "AI Career Track")
    
    start_date = datetime.now() + timedelta(days=1)
    
    milestones = [
        ("Phase 1: Foundations & Core Concepts", 14),
        ("Phase 2: Deep Dive & Framework Implementation", 21),
        ("Phase 3: Real-World Portfolio Project Build", 21),
        ("Phase 4: Capstone Architecture & Deployment", 14),
        ("Phase 5: Technical Mock Interview & Final Verification", 7)
    ]
    
    events = []
    current_dt = start_date

    for title, days in milestones:
        end_dt = current_dt + timedelta(days=days)
        start_str = current_dt.strftime("%Y%m%dT090000Z")
        end_str = end_dt.strftime("%Y%m%dT180000Z")
        now_str = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        
        event = f"""BEGIN:VEVENT
UID:cn-roadmap-{track_key}-{current_dt.strftime("%Y%m%d")}@careernavigator.ai
DTSTAMP:{now_str}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:{track_title} - {title}
DESCRIPTION:Official learning milestone for {track_title}. Focus on scheduled hands-on projects and quizzes on AI Career Navigator.
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT"""
        events.append(event)
        current_dt = end_dt

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI Career Navigator//Student Milestone Scheduler//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:{track_title} Schedule
X-WR-TIMEZONE:UTC
{chr(10).join(events)}
END:VCALENDAR"""

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="CareerNavigator_{track_key}_Schedule.ics"'
        }
    )


# ── Granular Roadmap Sub-Milestone Checklist Sync ───────────────────────────
class SubtaskToggleRequest(BaseModel):
    student_id: str = "user_001"
    track_key: str
    subtask_id: str
    subtask_text: Optional[str] = ""
    is_completed: bool = True


@router.post("/subtask/toggle")
def toggle_roadmap_subtask(payload: SubtaskToggleRequest):
    """
    Persists granular subtask / checklist item completion to SQLite roadmap_subtasks.
    """
    from services.auth_service import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    is_comp = 1 if payload.is_completed else 0
    cursor.execute("""
    INSERT INTO roadmap_subtasks (student_id, track_key, subtask_id, subtask_text, is_completed, completed_at)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(student_id, track_key, subtask_id) DO UPDATE SET
        is_completed = excluded.is_completed,
        subtask_text = excluded.subtask_text,
        completed_at = CURRENT_TIMESTAMP
    """, (payload.student_id, payload.track_key, payload.subtask_id, payload.subtask_text, is_comp))

    if payload.is_completed and payload.subtask_text:
        try:
            cursor.execute("""
            INSERT INTO activity_logs (student_id, action_type, title, description, icon, color)
            VALUES (?, 'roadmap_subtask', ?, ?, 'fa-check-circle', 'teal')
            """, (
                payload.student_id, 
                f"Roadmap Item: {payload.subtask_text[:40]}", 
                f"Completed study item in {payload.track_key.upper()} roadmap."
            ))
        except Exception:
            pass

    conn.commit()

    cursor.execute("""
    SELECT subtask_id FROM roadmap_subtasks 
    WHERE student_id = ? AND track_key = ? AND is_completed = 1
    """, (payload.student_id, payload.track_key))
    completed_rows = cursor.fetchall()
    completed_ids = [r["subtask_id"] for r in completed_rows]
    conn.close()

    return {
        "status": 200,
        "success": True,
        "subtaskId": payload.subtask_id,
        "isCompleted": payload.is_completed,
        "completedCount": len(completed_ids),
        "completedIds": completed_ids
    }


@router.get("/subtasks/{student_id}")
def get_roadmap_subtasks(student_id: str, track_key: Optional[str] = None):
    """
    Retrieves all persisted subtask completion states for a student.
    """
    from services.auth_service import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    if track_key:
        cursor.execute("""
        SELECT subtask_id, is_completed, subtask_text, completed_at FROM roadmap_subtasks 
        WHERE student_id = ? AND track_key = ?
        """, (student_id, track_key))
    else:
        cursor.execute("""
        SELECT subtask_id, is_completed, subtask_text, completed_at FROM roadmap_subtasks 
        WHERE student_id = ?
        """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    completed_ids = [r["subtask_id"] for r in rows if r["is_completed"]]
    states = {r["subtask_id"]: bool(r["is_completed"]) for r in rows}

    return {
        "status": 200,
        "success": True,
        "studentId": student_id,
        "trackKey": track_key,
        "completedIds": completed_ids,
        "states": states,
        "totalCompleted": len(completed_ids)
    }


