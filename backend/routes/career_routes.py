from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from services.auth_service import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/careers", tags=["Career Paths & Bookmarks"])

class BookmarkRequest(BaseModel):
    student_id: str
    career_id: str
    career_title: str

@router.post("/bookmark")
def toggle_career_bookmark(payload: BookmarkRequest):
    """
    Toggles bookmark state for a career path.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id FROM saved_careers WHERE student_id = ? AND career_id = ?
    """, (payload.student_id, payload.career_id))
    existing = cursor.fetchone()

    is_bookmarked = False
    if existing:
        cursor.execute("""
        DELETE FROM saved_careers WHERE student_id = ? AND career_id = ?
        """, (payload.student_id, payload.career_id))
        is_bookmarked = False
        message = f"Removed '{payload.career_title}' from saved careers"
    else:
        cursor.execute("""
        INSERT INTO saved_careers (student_id, career_id, career_title)
        VALUES (?, ?, ?)
        """, (payload.student_id, payload.career_id, payload.career_title))
        is_bookmarked = True
        message = f"Saved '{payload.career_title}' to your bookmarks"

    conn.commit()
    conn.close()

    return {
        "success": True,
        "isBookmarked": is_bookmarked,
        "careerId": payload.career_id,
        "message": message
    }


@router.get("/saved/{student_id}")
def get_saved_careers(student_id: str):
    """
    Retrieves all bookmarked career paths for a student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM saved_careers WHERE student_id = ? ORDER BY created_at DESC
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()

    saved_list = [
        {
            "id": r["id"],
            "careerId": r["career_id"],
            "careerTitle": r["career_title"],
            "savedAt": r["created_at"]
        }
        for r in rows
    ]

    return {
        "success": True,
        "studentId": student_id,
        "totalSaved": len(saved_list),
        "savedCareers": saved_list
    }
