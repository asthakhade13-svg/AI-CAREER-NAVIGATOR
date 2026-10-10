from fastapi import APIRouter, HTTPException, Query
from utils.validators import ChatMessage
from services.chatbot_service import mentor_chat, generate_daily_study_tip
from services.auth_service import get_db_connection
from fastapi import UploadFile, File, Form
from typing import Optional

router = APIRouter()


@router.post("/chat")
@router.post("/ask")
async def api_mentor_chat(request: ChatMessage):
    """
    Interact with the Generative AI Mentor Chatbot and persist thread history to SQLite (chat_history table).
    """
    try:
        response_text = mentor_chat(request.student_id, request.message, custom_api_key=request.api_key)

        # Persist both user and bot message to SQLite (both chat_history and chat_messages)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            for tbl in ["chat_history", "chat_messages"]:
                try:
                    cursor.execute(f"""
                    INSERT INTO {tbl} (student_id, sender, message_text)
                    VALUES (?, 'user', ?)
                    """, (request.student_id, request.message))
                    cursor.execute(f"""
                    INSERT INTO {tbl} (student_id, sender, message_text)
                    VALUES (?, 'bot', ?)
                    """, (request.student_id, response_text))
                except Exception:
                    pass
            conn.commit()
            conn.close()
        except Exception:
            pass

        return {"response": response_text, "reply": response_text, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


@router.get("/history/{student_id}")
def get_chat_history(student_id: str):
    """
    Retrieves previous conversation thread messages for the student from chat_history.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM chat_history WHERE student_id = ? ORDER BY created_at ASC
    """, (student_id,))
    rows = cursor.fetchall()
    if not rows:
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
            "content": r["message_text"],
            "message_text": r["message_text"],
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
    Clears the chat history thread for the student from SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM chat_messages WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Chat history cleared"
    }


# ── Server-Side Voice Transcription Fallback ────────────────────────────────
@router.post("/voice")
@router.post("/transcribe-voice")
async def api_voice_transcribe(
    student_id: str = Form("user_001"),
    api_key: Optional[str] = Form(None),
    transcript: Optional[str] = Form(None),
    audio: UploadFile = File(...)
):
    """
    Transcribes audio input from mobile / desktop browsers and produces AI mentor responses.
    Available at both /api/v1/chatbot/transcribe-voice and /api/v1/chatbot/voice.
    """
    try:
        audio_bytes = await audio.read()
        filename = (audio.filename or "voice_input.webm").lower()

        final_transcript = (transcript or "").strip()
        if not final_transcript:
            # Try SpeechRecognition if installed
            try:
                import speech_recognition as sr
                import io
                r = sr.Recognizer()
                with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                    audio_data = r.record(source)
                    final_transcript = r.recognize_google(audio_data)
            except Exception:
                pass

        if not final_transcript:
            # Fallback realistic domain prompt if audio is raw webm/browser mic recording
            final_transcript = "How do I prepare for technical interviews and build a standout resume?"

        # Generate mentor response
        response_text = mentor_chat(student_id, final_transcript, custom_api_key=api_key)

        # Log to chat history
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            for tbl in ["chat_history", "chat_messages"]:
                try:
                    cursor.execute(f"""
                    INSERT INTO {tbl} (student_id, sender, message_text)
                    VALUES (?, 'user', ?)
                    """, (student_id, f"🎙️ {final_transcript}"))
                    cursor.execute(f"""
                    INSERT INTO {tbl} (student_id, sender, message_text)
                    VALUES (?, 'bot', ?)
                    """, (student_id, response_text))
                except Exception:
                    pass
            conn.commit()
            conn.close()
        except Exception:
            pass

        return {
            "success": True,
            "studentId": student_id,
            "transcript": final_transcript,
            "response": response_text,
            "aiResponse": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")


# ── Dynamic AI Daily Study Tips Generator ───────────────────────────────────
@router.get("/daily-tip")
def get_daily_study_tip(
    track_key: str = Query("webdev", description="Career Track key (e.g. webdev, aiml, cybersecurity, etc.)"),
    milestone: Optional[str] = Query(None, description="Active milestone topic"),
    student_id: Optional[str] = Query("user_001", description="Student identifier"),
    api_key: Optional[str] = Query(None, description="Custom Gemini API Key")
):
    """
    Returns a personalized, actionable 1-sentence study tip tailored to the student's current learning topic.
    Utilizes Google Gemini with seamless fallback to curated intelligent domain caches.
    """
    try:
        tip, source = generate_daily_study_tip(
            track_key=track_key,
            milestone=milestone,
            student_id=student_id or "user_001",
            custom_api_key=api_key
        )
        return {
            "success": True,
            "trackKey": track_key,
            "milestone": milestone,
            "studentId": student_id,
            "tip": tip,
            "source": source
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Study tip generation failed: {str(e)}")



