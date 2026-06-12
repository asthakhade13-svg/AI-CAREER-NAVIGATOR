import google.generativeai as genai
from config import settings
import logging

logger = logging.getLogger(__name__)


def mentor_chat(student_id: str, message: str) -> str:
    """
    Uses Gemini API to provide a mentor chatbot response.
    """
    if not settings.GEMINI_API_KEY:
        return "I am an AI Mentor, but my API key is currently not configured."

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are an AI Mentor for a First-Generation B.Tech Computer Science student.
    The student is looking for career guidance, domain explanations, learning roadmaps, or internship advice.
    Be encouraging, use simple language, avoid excessive jargon, and provide highly actionable advice.

    Student's question: {message}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error in mentor chat for {student_id}: {e}")
        return "I am having trouble connecting to my knowledge base right now. Please try again later."
