from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from services.project_service import get_recommended_projects
from services.auth_service import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/projects", tags=["AI Project & Capstone Blueprints"])

@router.get("/recommend")
def recommend_projects(track: str = Query("aiml")):
    """
    Returns personalized portfolio project blueprints tailored to the student's career track.
    """
    try:
        projects = get_recommended_projects(track)
        return {
            "success": True,
            "track": track,
            "totalProjects": len(projects),
            "projects": projects
        }
    except Exception as e:
        logger.error(f"Error fetching recommended projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ProjectMilestoneToggleRequest(BaseModel):
    student_id: str
    project_id: str
    step_id: str
    is_completed: bool


@router.post("/milestone/toggle")
def toggle_project_milestone(payload: ProjectMilestoneToggleRequest):
    """
    Toggles completion status of a capstone project milestone step.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO project_milestones (student_id, project_id, step_id, is_completed, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id, project_id, step_id) 
        DO UPDATE SET is_completed = ?, updated_at = CURRENT_TIMESTAMP
        """, (payload.student_id, payload.project_id, payload.step_id, 1 if payload.is_completed else 0, 1 if payload.is_completed else 0))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "studentId": payload.student_id,
            "projectId": payload.project_id,
            "stepId": payload.step_id,
            "isCompleted": payload.is_completed,
            "message": f"Step '{payload.step_id}' marked as {'completed' if payload.is_completed else 'incomplete'}"
        }
    except Exception as e:
        logger.error(f"Error toggling project milestone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/milestones/{student_id}/{project_id}")
def get_project_milestones(student_id: str, project_id: str):
    """
    Retrieves completed step IDs for a specific project.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT step_id, is_completed, updated_at FROM project_milestones
        WHERE student_id = ? AND project_id = ?
        """, (student_id, project_id))
        rows = cursor.fetchall()
        conn.close()

        completed_steps = [r["step_id"] for r in rows if r["is_completed"] == 1]

        return {
            "success": True,
            "studentId": student_id,
            "projectId": project_id,
            "completedStepIds": completed_steps,
            "count": len(completed_steps)
        }
    except Exception as e:
        logger.error(f"Error fetching project milestones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ProjectSubmitRequest(BaseModel):
    student_id: str
    project_id: str
    github_url: str
    demo_url: Optional[str] = ""


@router.post("/submit")
def submit_capstone_project(payload: ProjectSubmitRequest):
    """
    Submits a capstone project repository, stores in SQLite, logs activity,
    and unlocks the 'Intern Ready' badge.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO project_submissions (student_id, project_id, github_url, demo_url, submitted_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id, project_id)
        DO UPDATE SET github_url = excluded.github_url, demo_url = excluded.demo_url, submitted_at = CURRENT_TIMESTAMP
        """, (payload.student_id, payload.project_id, payload.github_url.strip(), payload.demo_url.strip() if payload.demo_url else ""))

        # Log Activity Stream
        cursor.execute("""
        INSERT INTO activity_logs (student_id, action_type, title, description, icon, color)
        VALUES (?, 'capstone_submission', 'Submitted Capstone Project Repository', ?, 'fa-laptop-code', 'emerald')
        """, (payload.student_id, f"Project {payload.project_id} submitted: {payload.github_url.strip()}"))

        # Unlock Badge if exists
        cursor.execute("""
        INSERT OR IGNORE INTO student_badges (student_id, badge_id, badge_name, icon, description, is_unlocked)
        VALUES (?, 'b12', 'Intern Ready', '💼', 'Finish portfolio capstone project', 1)
        """, (payload.student_id,))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": "Capstone project submitted successfully and badge unlocked!",
            "submission": {
                "studentId": payload.student_id,
                "projectId": payload.project_id,
                "githubUrl": payload.github_url.strip(),
                "demoUrl": payload.demo_url.strip() if payload.demo_url else ""
            }
        }
    except Exception as e:
        logger.error(f"Error submitting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions/{student_id}")
def get_user_project_submissions(student_id: str):
    """
    Retrieves all submitted capstone repositories for a student.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM project_submissions WHERE student_id = ? ORDER BY submitted_at DESC", (student_id,))
        rows = cursor.fetchall()
        conn.close()

        submissions = [
            {
                "id": r["id"],
                "projectId": r["project_id"],
                "githubUrl": r["github_url"],
                "demoUrl": r["demo_url"],
                "submittedAt": r["submitted_at"]
            }
            for r in rows
        ]

        return {
            "success": True,
            "studentId": student_id,
            "totalSubmissions": len(submissions),
            "submissions": submissions
        }
    except Exception as e:
        logger.error(f"Error fetching project submissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


