from fastapi import APIRouter, HTTPException
from utils.validators import ChatMessage
from services.chatbot_service import mentor_chat

router = APIRouter()


@router.post("/chat")
async def api_mentor_chat(request: ChatMessage):
    """
    Interact with the AI Mentor Chatbot.
    """
    try:
        response_text = mentor_chat(request.student_id, request.message)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Chatbot service unavailable.")
