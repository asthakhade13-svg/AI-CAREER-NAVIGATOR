from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DomainProgress(BaseModel):
    domain: str
    confidence_score: float
    quizzes_taken: int


class StudentProgress(BaseModel):
    student_id: str
    average_score: float
    learning_streak: int
    domain_progress: List[DomainProgress]
    placement_readiness_score: float
    last_active: datetime
