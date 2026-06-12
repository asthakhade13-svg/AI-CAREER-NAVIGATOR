from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class QuizGenerateRequest(BaseModel):
    topic: str
    content: str


class MCQ(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    difficulty: str
    topic_tag: str


class TrueFalse(BaseModel):
    question: str
    correct_answer: str  # "True" or "False"
    difficulty: str
    topic_tag: str


class FillInBlank(BaseModel):
    question: str
    correct_answer: str
    difficulty: str
    topic_tag: str


class QuizOutput(BaseModel):
    topic: str
    mcqs: List[MCQ]
    true_false: List[TrueFalse]
    fill_in_blanks: List[FillInBlank]


class QuizEvaluationRequest(BaseModel):
    student_id: str
    quiz_id: str
    answers: Dict[str, str]


class QuizEvaluationResult(BaseModel):
    total_score: int
    accuracy: float
    topic_scores: Dict[str, float]
    difficulty_scores: Dict[str, float]
