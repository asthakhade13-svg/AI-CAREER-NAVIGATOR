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

