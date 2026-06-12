from pydantic import BaseModel, Field
from typing import List, Dict, Optional

try:
    from pydantic import EmailStr
except ImportError:
    # Fallback if email-validator is not installed
    EmailStr = str  # type: ignore


class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    interests: List[str] = []


class QuizSubmission(BaseModel):
    student_id: str
    quiz_id: str
    answers: Dict[str, str]  # question_id -> selected_option


class ChatMessage(BaseModel):
    student_id: str
    message: str
