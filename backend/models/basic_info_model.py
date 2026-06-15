from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union

class QuestionModel(BaseModel):
    question_id: int
    section: str
    question: str
    question_type: str
    options: List[str] = []

class QuestionnaireSubmit(BaseModel):
    student_id: str
    answers: Dict[str, Union[str, int, float, List[str]]]

class ProfileSummary(BaseModel):
    full_name: str
    email: str
    current_year: str
    interests: List[str]
    favorite_subject: str
    primary_motivation: str

class QuestionnaireResponse(BaseModel):
    student_id: str
    technical_score: float
    starting_quiz: str = Field(..., description="Either 'general' or 'cs'")
    reason: str
    profile_summary: ProfileSummary
