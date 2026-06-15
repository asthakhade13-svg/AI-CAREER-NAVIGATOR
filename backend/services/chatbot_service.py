import google.generativeai as genai
import requests
from config import settings
import logging

logger = logging.getLogger(__name__)


def mentor_chat(student_id: str, message: str) -> str:
    """
    Uses Grok or Gemini API to provide a mentor chatbot response.
    """
    prompt = f"""
    You are an AI Mentor for a First-Generation B.Tech Computer Science student.
    The student is looking for career guidance, domain explanations, learning roadmaps, or internship advice.
    Be encouraging, use simple language, avoid excessive jargon, and provide highly actionable advice.

    Student's question: {message}
    """

    # 1. Try Grok or Groq first if key is present
    if settings.GROK_API_KEY:
        try:
            # Check if it is a Groq key (starts with gsk_) or Grok key
            if settings.GROK_API_KEY.startswith("gsk_"):
                api_url = "https://api.groq.com/openai/v1/chat/completions"
                model_name = "llama-3.3-70b-versatile"
                logger.info("Using Groq API for mentor chat")
            else:
                api_url = "https://api.x.ai/v1/chat/completions"
                model_name = "grok-2-1212"
                logger.info("Using Grok API for mentor chat")

            headers = {
                "Authorization": f"Bearer {settings.GROK_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            res = requests.post(api_url, headers=headers, json=payload, timeout=10)
            if res.ok:
                return res.json()["choices"][0]["message"]["content"]
            else:
                logger.error(f"External API error ({model_name}): {res.status_code} - {res.text}")
        except Exception as e:
            logger.error(f"Error in external mentor chat: {e}")

    # 2. Fallback to Gemini
    if settings.GEMINI_API_KEY:
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error in Gemini mentor chat for {student_id}: {e}")

    return "I am an AI Mentor, but my API key is currently not configured."
