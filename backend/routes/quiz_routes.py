from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from models.quiz_evaluation_model import (
    QuizGenerateRequest,
    QuizOutput,
    QuizEvaluationRequest,
    QuizEvaluationResult,
)
from services.quiz_generator import generate_quiz
from services.quiz_evaluator import evaluate_quiz
from services.general_quiz_service import get_general_questions, evaluate_general_quiz
from services.cs_quiz_service import get_cs_questions, evaluate_cs_quiz
from database import db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=QuizOutput)
async def api_generate_quiz(request: QuizGenerateRequest):
    """
    Generate a quiz based on topic and content using Gemini.
    """
    try:
        quiz_data = generate_quiz(request.topic, request.content)

        # Save to DB (no-op if MongoDB is offline)
        try:
            quizzes_col = db.get_collection("quizzes")
            if quizzes_col is not None:
                quizzes_col.insert_one(quiz_data)
        except Exception:
            pass  # Ignore DB errors in local dev

        return quiz_data
    except Exception as e:
        logger.error(f"Generate quiz error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate quiz.")


@router.post("/evaluate", response_model=QuizEvaluationResult)
async def api_evaluate_quiz(request: QuizEvaluationRequest):
    """
    Evaluate student quiz answers.
    """
    try:
        result = evaluate_quiz(request.student_id, request.quiz_id, request.answers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Evaluate quiz error: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate quiz.")


class GeneralQuizEvaluationRequest(BaseModel):
    student_id: str
    answers: dict


@router.get("/general")
async def api_get_general_quiz():
    """
    Get the list of general MCQ questions (excluding correct answers and categories).
    """
    try:
        questions = get_general_questions()
        return questions
    except Exception as e:
        logger.error(f"Error fetching general quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch general quiz.")


@router.post("/general/evaluate")
async def api_evaluate_general_quiz(request: GeneralQuizEvaluationRequest):
    """
    Evaluate general quiz answers, calculate domain scores, and recommend careers.
    """
    try:
        result = evaluate_general_quiz(request.student_id, request.answers)
        return result
    except Exception as e:
        logger.error(f"Error evaluating general quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate general quiz.")


class CSQuizEvaluationRequest(BaseModel):
    student_id: str
    answers: dict


@router.get("/cs")
async def api_get_cs_quiz():
    """
    Get the list of CS MCQ questions (excluding correct answers and categories).
    """
    try:
        questions = get_cs_questions()
        return questions
    except Exception as e:
        logger.error(f"Error fetching CS quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch CS quiz.")


@router.post("/cs/evaluate")
async def api_evaluate_cs_quiz(request: CSQuizEvaluationRequest):
    """
    Evaluate CS quiz answers, calculate domain scores, and recommend careers.
    """
    try:
        result = evaluate_cs_quiz(request.student_id, request.answers)
        return result
    except Exception as e:
        logger.error(f"Error evaluating CS quiz: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate CS quiz.")


# ── 6. Quiz Attempt History Ledger Endpoints ─────────────────────────────────
from services.auth_service import get_db_connection
import json

class LogQuizAttemptRequest(BaseModel):
    student_id: str
    track_key: str
    score: int
    total_questions: Optional[int] = 10
    correct_answers: Optional[int] = 8
    time_taken_sec: Optional[int] = 120
    question_timings: Optional[Dict[str, Any]] = None

@router.post("/log-attempt")
def log_quiz_attempt(req: LogQuizAttemptRequest):
    """
    Records a completed quiz attempt in the persistent SQLite history ledger including per-question timing analytics.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    timings_json = json.dumps(req.question_timings or {})

    cursor.execute("""
    INSERT INTO quiz_attempts (student_id, track_key, score, total_questions, correct_answers, time_taken_sec, question_timings)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (req.student_id, req.track_key, req.score, req.total_questions or 10, req.correct_answers or 8, req.time_taken_sec or 120, timings_json))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Quiz attempt logged successfully",
        "score": req.score,
        "questionTimings": req.question_timings or {}
    }

@router.get("/history/{student_id}")
def get_quiz_history(student_id: str):
    """
    Retrieves all past quiz attempts for graphing and progress tracking.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM quiz_attempts WHERE student_id = ? ORDER BY created_at DESC
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()

    attempts = []
    for r in rows:
        raw_timings = r["question_timings"] if "question_timings" in r.keys() and r["question_timings"] else "{}"
        try:
            parsed_timings = json.loads(raw_timings)
        except Exception:
            parsed_timings = {}

        attempts.append({
            "id": r["id"],
            "trackKey": r["track_key"],
            "score": r["score"],
            "totalQuestions": r["total_questions"],
            "correctAnswers": r["correct_answers"],
            "timeTakenSec": r["time_taken_sec"],
            "questionTimings": parsed_timings,
            "createdAt": r["created_at"]
        })

    return {
        "success": True,
        "studentId": student_id,
        "totalAttempts": len(attempts),
        "history": attempts
    }


class QuizResetRequest(BaseModel):
    student_id: str = "user_astha_001"

@router.post("/reset")
def reset_quiz_state(req: QuizResetRequest):
    """
    Clears user quiz attempts and assessment state so the student can retake fresh.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quiz_attempts WHERE student_id = ?", (req.student_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Quiz progress reset successfully for {req.student_id}",
        "studentId": req.student_id,
        "clearedAttempts": deleted_count
    }

@router.delete("/reset/{student_id}")
def delete_quiz_state(student_id: str):
    """
    RESTful endpoint to delete past quiz attempts for a student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quiz_attempts WHERE student_id = ?", (student_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Quiz progress reset successfully for {student_id}",
        "studentId": student_id,
        "clearedAttempts": deleted_count
    }


# ── 7. Standard 10-Question Assessment & Review Mistakes Endpoints ───────────

QUIZ_QUESTIONS_DATABASE = [
    {
        "id": 1,
        "topic": "web_development",
        "topicName": "Web Development",
        "questionText": "Which HTTP status code signifies that a requested resource was successfully created on the server?",
        "options": [
            {"id": 1, "optionText": "200 OK"},
            {"id": 2, "optionText": "201 Created"},
            {"id": 3, "optionText": "204 No Content"},
            {"id": 4, "optionText": "304 Not Modified"}
        ],
        "correctOptionId": 2,
        "explanation": "HTTP status code 201 Created confirms that the request succeeded and resulted in a new resource being created on the server (RFC 7231).",
        "roadmapLink": "roadmap.html?track=webdev"
    },
    {
        "id": 2,
        "topic": "web_development",
        "topicName": "Web Development",
        "questionText": "In modern frontend development, what is the primary architectural purpose of the Virtual DOM in React?",
        "options": [
            {"id": 1, "optionText": "To directly mutate browser HTML nodes synchronously"},
            {"id": 2, "optionText": "To bypass the browser's JavaScript execution engine"},
            {"id": 3, "optionText": "To compute minimal DOM diffs in memory before batching updates to the real DOM"},
            {"id": 4, "optionText": "To replace CSS cascade computations"}
        ],
        "correctOptionId": 3,
        "explanation": "The Virtual DOM maintains a lightweight tree in memory. On state updates, it reconciles diffs and batches real DOM updates to prevent costly browser reflows.",
        "roadmapLink": "roadmap.html?track=webdev"
    },
    {
        "id": 3,
        "topic": "ai_ml",
        "topicName": "AI / ML",
        "questionText": "What occurs when a machine learning model memorizes noise in training data instead of learning generalized patterns?",
        "options": [
            {"id": 1, "optionText": "Underfitting"},
            {"id": 2, "optionText": "Overfitting"},
            {"id": 3, "optionText": "Gradient Descent"},
            {"id": 4, "optionText": "Data Imputation"}
        ],
        "correctOptionId": 2,
        "explanation": "Overfitting happens when model complexity causes it to memorize noise in training samples, yielding high training accuracy but poor validation performance.",
        "roadmapLink": "roadmap.html?track=aiml"
    },
    {
        "id": 4,
        "topic": "ai_ml",
        "topicName": "AI / ML",
        "questionText": "Which activation function is most widely adopted in deep neural networks to prevent vanishing gradients?",
        "options": [
            {"id": 1, "optionText": "Sigmoid"},
            {"id": 2, "optionText": "Tanh"},
            {"id": 3, "optionText": "ReLU (Rectified Linear Unit)"},
            {"id": 4, "optionText": "Softmax"}
        ],
        "correctOptionId": 3,
        "explanation": "ReLU f(x)=max(0, x) provides a constant derivative of 1 for positive inputs, avoiding gradient saturation and vanishing gradient problems in deep architectures.",
        "roadmapLink": "roadmap.html?track=aiml"
    },
    {
        "id": 5,
        "topic": "data_structures",
        "topicName": "Data Structures",
        "questionText": "What is the worst-case time complexity of searching an element in a balanced Binary Search Tree (AVL or Red-Black Tree)?",
        "options": [
            {"id": 1, "optionText": "O(1)"},
            {"id": 2, "optionText": "O(log N)"},
            {"id": 3, "optionText": "O(N)"},
            {"id": 4, "optionText": "O(N log N)"}
        ],
        "correctOptionId": 2,
        "explanation": "Self-balancing binary search trees bound their height to O(log N) through tree rotations, guaranteeing logarithmic complexity for search, insertion, and deletion.",
        "roadmapLink": "roadmap.html?track=dsa"
    },
    {
        "id": 6,
        "topic": "data_structures",
        "topicName": "Data Structures",
        "questionText": "Which abstract data type operates on a FIFO basis and is canonical for Breadth-First Search (BFS) graph traversal?",
        "options": [
            {"id": 1, "optionText": "Stack"},
            {"id": 2, "optionText": "Priority Queue"},
            {"id": 3, "optionText": "Queue"},
            {"id": 4, "optionText": "Binary Heap"}
        ],
        "correctOptionId": 3,
        "explanation": "A Queue follows First-In First-Out (FIFO) ordering, ensuring BFS visits graph vertices in strictly increasing order of path distance from root.",
        "roadmapLink": "roadmap.html?track=dsa"
    },
    {
        "id": 7,
        "topic": "cybersecurity",
        "topicName": "Cybersecurity",
        "questionText": "Which cryptographic primitive guarantees sender non-repudiation and tamper detection for messages?",
        "options": [
            {"id": 1, "optionText": "Symmetric stream cipher encryption"},
            {"id": 2, "optionText": "Digital Signatures via Asymmetric Cryptography"},
            {"id": 3, "optionText": "Base64 encoding with URL safety"},
            {"id": 4, "optionText": "Unsalted MD5 hashing"}
        ],
        "correctOptionId": 2,
        "explanation": "Digital signatures use private keys for signing and public keys for verification, providing data integrity, authenticity, and non-repudiation.",
        "roadmapLink": "roadmap.html?track=cyber"
    },
    {
        "id": 8,
        "topic": "cybersecurity",
        "topicName": "Cybersecurity",
        "questionText": "What is the primary remediation to prevent SQL Injection (SQLi) vulnerabilities in database querying code?",
        "options": [
            {"id": 1, "optionText": "Client-side HTML input length limits"},
            {"id": 2, "optionText": "Parameterized queries / Prepared statements"},
            {"id": 3, "optionText": "Base64 encoding all URL parameters"},
            {"id": 4, "optionText": "Disabling TLS/SSL encryption"}
        ],
        "correctOptionId": 2,
        "explanation": "Parameterized queries decouple query logic from user parameters, forcing the database engine to parse inputs strictly as literals rather than SQL commands.",
        "roadmapLink": "roadmap.html?track=cyber"
    },
    {
        "id": 9,
        "topic": "cloud_computing",
        "topicName": "Cloud Computing",
        "questionText": "Which cloud computing model abstracts infrastructure provisioning completely and bills only per event execution?",
        "options": [
            {"id": 1, "optionText": "Infrastructure as a Service (IaaS)"},
            {"id": 2, "optionText": "Serverless / Function-as-a-Service (FaaS)"},
            {"id": 3, "optionText": "Bare Metal as a Service (BMaaS)"},
            {"id": 4, "optionText": "Colocation"}
        ],
        "correctOptionId": 2,
        "explanation": "Serverless (FaaS) runs ephemeral containers triggered by events, automatically scaling and charging solely for compute milliseconds executed.",
        "roadmapLink": "roadmap.html?track=cloud"
    },
    {
        "id": 10,
        "topic": "cloud_computing",
        "topicName": "Cloud Computing",
        "questionText": "Which architectural strategy guarantees high availability and disaster resilience within a single cloud provider region?",
        "options": [
            {"id": 1, "optionText": "Multi-Availability Zone (Multi-AZ) redundant deployment"},
            {"id": 2, "optionText": "Single monolithic EC2 instance deployment"},
            {"id": 3, "optionText": "Disabling auto-scaling and health checks"},
            {"id": 4, "optionText": "Storing backups solely on instance ephemeral storage"}
        ],
        "correctOptionId": 1,
        "explanation": "Multi-AZ architectures distribute instances across geographically separated data centers with isolated power and transit, ensuring continuous availability.",
        "roadmapLink": "roadmap.html?track=cloud"
    }
]


@router.get("/questions")
def get_standard_quiz_questions():
    """
    Returns the standard 10 multi-domain assessment questions for quiz.html.
    Excludes the correct answer key so students cannot inspect it during the live assessment.
    """
    return [
        {
            "id": q["id"],
            "topic": q["topic"],
            "topicName": q["topicName"],
            "questionText": q["questionText"],
            "options": q["options"]
        }
        for q in QUIZ_QUESTIONS_DATABASE
    ]


class QuizSubmissionPayload(BaseModel):
    student_id: Optional[str] = "user_001"
    answers: List[Dict[str, Any]]


@router.post("/submit")
def submit_standard_quiz(payload: QuizSubmissionPayload):
    """
    Evaluates quiz submissions, calculates multi-domain scores, recommends top career match,
    and returns comprehensive question-by-question review items with concept explanations and roadmap links.
    """
    submitted_map = {}
    for item in payload.answers:
        q_id = item.get("questionId") or item.get("id")
        opt_id = item.get("selectedOptionId") or item.get("optionId")
        if q_id is not None:
            submitted_map[int(q_id)] = int(opt_id) if opt_id is not None else None

    total_questions = len(QUIZ_QUESTIONS_DATABASE)
    correct_count = 0
    domain_totals = {
        "web_development": {"correct": 0, "total": 0},
        "ai_ml": {"correct": 0, "total": 0},
        "data_structures": {"correct": 0, "total": 0},
        "cybersecurity": {"correct": 0, "total": 0},
        "cloud_computing": {"correct": 0, "total": 0}
    }

    review_list = []

    for q in QUIZ_QUESTIONS_DATABASE:
        q_id = q["id"]
        topic = q["topic"]
        domain_totals[topic]["total"] += 1

        selected_opt_id = submitted_map.get(q_id)
        correct_opt_id = q["correctOptionId"]
        is_correct = (selected_opt_id == correct_opt_id)

        if is_correct:
            correct_count += 1
            domain_totals[topic]["correct"] += 1

        # Resolve selected text and correct text
        selected_text = "Not Answered"
        correct_text = ""
        for opt in q["options"]:
            if opt["id"] == selected_opt_id:
                selected_text = opt["optionText"]
            if opt["id"] == correct_opt_id:
                correct_text = opt["optionText"]

        review_list.append({
            "questionId": q_id,
            "questionText": q["questionText"],
            "topic": topic,
            "topicName": q["topicName"],
            "selectedOptionId": selected_opt_id,
            "correctOptionId": correct_opt_id,
            "isCorrect": is_correct,
            "selectedText": selected_text,
            "correctText": correct_text,
            "explanation": q["explanation"],
            "roadmapLink": q["roadmapLink"],
            "options": q["options"]
        })

    def calc_pct(c, t):
        return round((c / t) * 100) if t > 0 else 0

    web_score = calc_pct(domain_totals["web_development"]["correct"], domain_totals["web_development"]["total"])
    aiml_score = calc_pct(domain_totals["ai_ml"]["correct"], domain_totals["ai_ml"]["total"])
    dsa_score = calc_pct(domain_totals["data_structures"]["correct"], domain_totals["data_structures"]["total"])
    cyber_score = calc_pct(domain_totals["cybersecurity"]["correct"], domain_totals["cybersecurity"]["total"])
    cloud_score = calc_pct(domain_totals["cloud_computing"]["correct"], domain_totals["cloud_computing"]["total"])
    total_score = round((correct_count / total_questions) * 100)

    # Determine top career match
    domain_scores = [
        ("Web Development", web_score),
        ("Artificial Intelligence & Machine Learning", aiml_score),
        ("Data Structures & Algorithms Engineering", dsa_score),
        ("Cybersecurity Engineering", cyber_score),
        ("Cloud Solutions Architecture", cloud_score)
    ]
    domain_scores.sort(key=lambda x: x[1], reverse=True)
    top_career = domain_scores[0][0]

    return {
        "success": True,
        "totalScore": total_score,
        "correctAnswers": correct_count,
        "totalQuestions": total_questions,
        "webDevScore": web_score,
        "aiMlScore": aiml_score,
        "dsaScore": dsa_score,
        "cyberScore": cyber_score,
        "cloudScore": cloud_score,
        "topCareerMatch": top_career,
        "review": review_list
    }





