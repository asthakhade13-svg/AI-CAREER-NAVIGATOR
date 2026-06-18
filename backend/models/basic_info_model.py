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
    full_name: Optional[str] = "Student"
    email: Optional[str] = ""
    current_year: Optional[str] = "1st Year"
    interests: Optional[List[str]] = Field(default_factory=list)
    favorite_subject: Optional[str] = ""
    primary_motivation: Optional[str] = ""

class QuestionnaireResponse(BaseModel):
    student_id: str
    technical_score: float
    starting_quiz: str = Field(..., description="Either 'general' or 'cs'")
    reason: str
    profile_summary: ProfileSummary
    recommended_careers: Optional[List[Dict[str, Union[str, float, str]]]] = None
    trait_scores: Optional[Dict[str, float]] = Field(
        default=None,
        description="Computed trait scores (0-100) for all 9 personality/aptitude traits and 5 career goal dimensions"
    )
