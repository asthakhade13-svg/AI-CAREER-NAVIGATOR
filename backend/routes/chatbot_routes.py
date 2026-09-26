from fastapi import APIRouter, HTTPException
from utils.validators import ChatMessage
from services.chatbot_service import mentor_chat
from services.auth_service import get_db_connection

router = APIRouter()


@router.post("/chat")
@router.post("/ask")
async def api_mentor_chat(request: ChatMessage):
    """
    Interact with the Generative AI Mentor Chatbot and persist thread history.
    """
    try:
        response_text = mentor_chat(request.student_id, request.message, custom_api_key=request.api_key)

        # Persist both user and bot message to SQLite
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO chat_messages (student_id, sender, message_text)
            VALUES (?, 'user', ?)
            """, (request.student_id, request.message))
            cursor.execute("""
            INSERT INTO chat_messages (student_id, sender, message_text)
            VALUES (?, 'bot', ?)
            """, (request.student_id, response_text))
            conn.commit()
            conn.close()
        except Exception:
            pass

        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


@router.get("/history/{student_id}")
def get_chat_history(student_id: str):
    """
    Retrieves previous conversation thread messages for the student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM chat_messages WHERE student_id = ? ORDER BY created_at ASC
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()

    messages = [
        {
            "id": r["id"],
            "sender": r["sender"],
            "text": r["message_text"],
            "timestamp": r["created_at"]
        }
        for r in rows
    ]

    return {
        "success": True,
        "studentId": student_id,
        "totalMessages": len(messages),
        "messages": messages
    }


@router.delete("/history/{student_id}")
def clear_chat_history(student_id: str):
    """
    Clears the chat history thread for the student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM chat_messages WHERE student_id = ?
    """, (student_id,))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Chat history cleared"
    }

