from pydantic import BaseModel
from typing import List


class SkillAssessmentRequest(BaseModel):
    student_id: str
    quiz_results: dict  # Can include domain scores


class SkillGapRequest(BaseModel):
    student_id: str
    target_domain: str
    current_skills: List[str]


class SkillGapResponse(BaseModel):
    target_domain: str
    missing_skills: List[str]
    priority_order: List[str]
    suggested_resources: List[str]
