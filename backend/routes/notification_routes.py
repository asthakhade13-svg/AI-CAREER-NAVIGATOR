from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from services.auth_service import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["Notification Center"])

class MarkReadRequest(BaseModel):
    student_id: str
    notification_id: Optional[int] = None

class CreateNotificationRequest(BaseModel):
    student_id: str
    title: str
    message: str
    type: Optional[str] = "info"


@router.get("/{student_id}")
def get_notifications(student_id: str):
    """
    Returns notifications for the student, automatically seeding default welcome alerts if new.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM notifications WHERE student_id = ? ORDER BY created_at DESC
    """, (student_id,))
    rows = cursor.fetchall()

    if not rows:
        # Seed default notifications for a rich student experience
        default_notifs = [
            ("🔥 7-Day Streak Active!", "You're on fire! Keep up daily check-ins to unlock the Consistency Badge.", "streak"),
            ("📊 Weekly AI Digest Ready", "Your weekly performance digest and recommended study goals have been calculated.", "report"),
            ("🎓 Verified Certificate Available", "You qualify to claim your Verifiable Specialization Certificate.", "cert"),
            ("💼 Spring 2026 Internships Preview", "Tech internship roles are opening soon. Check out requirements in the dashboard.", "internship")
        ]
        for title, msg, n_type in default_notifs:
            cursor.execute("""
            INSERT INTO notifications (student_id, title, message, type, is_read)
            VALUES (?, ?, ?, ?, 0)
            """, (student_id, title, msg, n_type))
        conn.commit()

        cursor.execute("""
        SELECT * FROM notifications WHERE student_id = ? ORDER BY created_at DESC
        """, (student_id,))
        rows = cursor.fetchall()

    conn.close()

    notif_list = [
        {
            "id": r["id"],
            "studentId": r["student_id"],
            "title": r["title"],
            "message": r["message"],
            "type": r["type"],
            "isRead": bool(r["is_read"]),
            "createdAt": r["created_at"]
        }
        for r in rows
    ]

    unread_count = sum(1 for n in notif_list if not n["isRead"])

    return {
        "success": True,
        "studentId": student_id,
        "unreadCount": unread_count,
        "total": len(notif_list),
        "notifications": notif_list
    }


@router.post("/mark-read")
def mark_notifications_read(payload: MarkReadRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    if payload.notification_id:
        cursor.execute("""
        UPDATE notifications SET is_read = 1 WHERE id = ? AND student_id = ?
        """, (payload.notification_id, payload.student_id))
    else:
        cursor.execute("""
        UPDATE notifications SET is_read = 1 WHERE student_id = ?
        """, (payload.student_id,))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Notifications marked as read"
    }


@router.post("/send")
def create_notification(payload: CreateNotificationRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO notifications (student_id, title, message, type, is_read)
    VALUES (?, ?, ?, ?, 0)
    """, (payload.student_id, payload.title, payload.message, payload.type or "info"))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Notification dispatched successfully"
    }
