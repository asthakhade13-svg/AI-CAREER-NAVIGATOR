"""
Adaptive Quiz Service — Computer Adaptive Testing (CAT) Engine
==============================================================
- Loads questions from data/adaptive_questions.csv
- Manages in-memory sessions (ACTIVE_SESSIONS)
- Dynamically adjusts difficulty: Easy <-> Medium <-> Hard
- After 30 questions compiles results and recommends career paths
"""

import uuid
import random
import logging
import pandas as pd
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

CSV_PATH = "data/adaptive_questions.csv"

# ─── Global state ────────────────────────────────────────────────────────────
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

# ─── Scoring bracket constants ───────────────────────────────────────────────
QUIZ_LENGTH = 30

LEARNING_PATHS = {
    "beginner": {
        "label": "Beginner Learning Path",
        "description": "Computer Basics + Digital Literacy",
        "resources": [
            {"title": "CS50's Introduction to Computer Science", "url": "https://cs50.harvard.edu/x/", "type": "Course"},
            {"title": "Khan Academy – Computing", "url": "https://www.khanacademy.org/computing", "type": "Course"},
            {"title": "Google Digital Garage – Fundamentals of Digital Marketing", "url": "https://learndigital.withgoogle.com/digitalgarage", "type": "Course"},
            {"title": "Microsoft Digital Literacy", "url": "https://www.microsoft.com/en-us/digital-literacy", "type": "Course"},
            {"title": "Typing.com – Typing Skills", "url": "https://www.typing.com/", "type": "Practice"},
        ]
    },
    "foundation": {
        "label": "Foundation Learning Path",
        "description": "Basic Programming + Office Tools",
        "resources": [
            {"title": "Python for Everybody – Coursera", "url": "https://www.coursera.org/specializations/python", "type": "Course"},
            {"title": "freeCodeCamp – Responsive Web Design", "url": "https://www.freecodecamp.org/learn/responsive-web-design/", "type": "Course"},
            {"title": "Automate the Boring Stuff with Python", "url": "https://automatetheboringstuff.com/", "type": "Book"},
            {"title": "Google Workspace Learning Center", "url": "https://support.google.com/a/users#topic=9296556", "type": "Course"},
            {"title": "W3Schools – HTML, CSS, JS", "url": "https://www.w3schools.com/", "type": "Reference"},
        ]
    },
    "cs_ready": {
        "label": "CS Ready Learning Path",
        "description": "Introductory Computer Science — Programming, Web Dev, AI & more",
        "resources": [
            {"title": "MIT OpenCourseWare – Introduction to CS", "url": "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/", "type": "Course"},
            {"title": "The Odin Project – Full Stack Web Dev", "url": "https://www.theodinproject.com/", "type": "Course"},
            {"title": "fast.ai – Practical Deep Learning", "url": "https://www.fast.ai/", "type": "Course"},
            {"title": "LeetCode – Algorithm Practice", "url": "https://leetcode.com/", "type": "Practice"},
            {"title": "GitHub Learning Lab", "url": "https://lab.github.com/", "type": "Practice"},
        ]
    }
}

CAREER_FIELD_MAP = {
    "Web Development": ["programming_score", "ai_score"],
    "Frontend Development": ["programming_score", "communication_score"],
    "Backend Development": ["programming_score", "logical_score"],
    "Full Stack Development": ["programming_score", "logical_score"],
    "Mobile App Development": ["programming_score", "logical_score"],
    "Android Development": ["programming_score", "logical_score"],
    "iOS Development": ["programming_score", "logical_score"],
    "Desktop Application Development": ["programming_score", "logical_score"],
    "Data Science": ["ai_score", "logical_score"],
    "Machine Learning": ["ai_score", "logical_score"],
    "AI Development": ["ai_score", "programming_score"],
    "Cybersecurity": ["cyber_score", "networking_score"],
    "Networking": ["networking_score", "logical_score"],
    "Cloud Computing": ["networking_score", "programming_score"],
    "DevOps": ["programming_score", "networking_score"],
    "Blockchain": ["programming_score", "logical_score"],
    "IoT": ["programming_score", "logical_score"],
    "Embedded Systems": ["programming_score", "logical_score"],
    "AR/VR Development": ["programming_score", "ai_score"],
    "UI/UX Design": ["communication_score", "logical_score"],
    "Game Development": ["programming_score", "logical_score"],
    "Database Engineering": ["programming_score", "logical_score"],
    "Quantum Computing": ["logical_score", "programming_score"],
    "Bioinformatics": ["ai_score", "logical_score"],
    "FinTech": ["programming_score", "logical_score"],
    "HealthTech": ["programming_score", "ai_score"],
    "Autonomous Vehicle Software": ["ai_score", "programming_score"],
}

# ─── Data Loader ─────────────────────────────────────────────────────────────
_questions_df: Optional[pd.DataFrame] = None


def _load_questions() -> pd.DataFrame:
    """Load and cache questions from CSV."""
    global _questions_df
    if _questions_df is None:
        try:
            _questions_df = pd.read_csv(CSV_PATH)
            # Normalize column names
            _questions_df.columns = [c.strip().lower().replace(" ", "_") for c in _questions_df.columns]
            # Ensure correct_answer is uppercase
            _questions_df["correct_answer"] = _questions_df["correct_answer"].str.strip().str.upper()
            _questions_df["difficulty"] = _questions_df["difficulty"].str.strip()
            _questions_df["career_field"] = _questions_df["career_field"].str.strip()
            logger.info(f"Adaptive questions loaded: {len(_questions_df)} rows")
        except Exception as e:
            logger.error(f"Failed to load adaptive_questions.csv: {e}")
            _questions_df = pd.DataFrame()
    return _questions_df


def _get_available_fields() -> List[str]:
    """Return list of unique career fields in the question bank."""
    df = _load_questions()
    if df.empty:
        return list(CAREER_FIELD_MAP.keys())
    return df["career_field"].unique().tolist()


def _pick_question(session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Pick the next question for the session.
    Rotates career fields every ~5 questions and avoids repeating questions.
    """
    df = _load_questions()
    if df.empty:
        return None

    difficulty = session["current_difficulty"]
    used_ids = set(session["used_question_ids"])
    fields = session["field_rotation"]

    # Rotate through fields every 5 questions
    rotation_idx = session["questions_answered"] // 5
    rotation_idx = min(rotation_idx, len(fields) - 1)
    current_field = fields[rotation_idx]

    # Filter available questions
    mask = (
        (df["difficulty"] == difficulty) &
        (df["career_field"] == current_field) &
        (~df["question_id"].isin(used_ids))
    )
    candidates = df[mask]

    # If no candidates for current field+difficulty, fall back to any field
    if candidates.empty:
        mask = (df["difficulty"] == difficulty) & (~df["question_id"].isin(used_ids))
        candidates = df[mask]

    # If still empty, broaden to any unused question
    if candidates.empty:
        candidates = df[~df["question_id"].isin(used_ids)]

    if candidates.empty:
        return None

    row = candidates.sample(1).iloc[0]
    return {
        "question_id": int(row["question_id"]),
        "career_field": str(row["career_field"]),
        "difficulty": str(row["difficulty"]),
        "question": str(row["question"]),
        "options": {
            "A": str(row["option_a"]),
            "B": str(row["option_b"]),
            "C": str(row["option_c"]),
            "D": str(row["option_d"]),
        },
        "correct_answer": str(row["correct_answer"]),
    }


# ─── Difficulty adjustment ────────────────────────────────────────────────────
DIFFICULTY_UP = {"Easy": "Medium", "Medium": "Hard", "Hard": "Hard"}
DIFFICULTY_DOWN = {"Easy": "Easy", "Medium": "Easy", "Hard": "Medium"}


def _adjust_difficulty(current: str, is_correct: bool) -> str:
    if is_correct:
        return DIFFICULTY_UP[current]
    return DIFFICULTY_DOWN[current]


# ─── Session Management ───────────────────────────────────────────────────────
def start_adaptive_session(
    student_id: str,
    technical_score: float,
    interest_field: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initialise a new adaptive quiz session.

    Args:
        student_id: The student's identifier.
        technical_score: Score from the Basic Info Questionnaire (determines start difficulty).
        interest_field: The student's primary interest from questionnaire (determines first field).

    Returns:
        A dict with session_id and the first question.
    """
    session_id = str(uuid.uuid4())

    # Determine starting difficulty
    starting_difficulty = "Medium" if technical_score >= 15 else "Easy"

    # Build a rotation of career fields — start with student's interest, then rotate others
    all_fields = _get_available_fields()
    if interest_field and interest_field in all_fields:
        primary = [interest_field]
    else:
        primary = ["Web Development"]  # sensible default

    other_fields = [f for f in all_fields if f not in primary]
    random.shuffle(other_fields)
    field_rotation = (primary + other_fields)[:6]  # cover up to 6 fields in 30 Qs

    session: Dict[str, Any] = {
        "session_id": session_id,
        "student_id": student_id,
        "technical_score": technical_score,
        "current_difficulty": starting_difficulty,
        "field_rotation": field_rotation,
        "questions_answered": 0,
        "correct_answers": 0,
        "used_question_ids": [],
        "answers_history": [],  # list of {question_id, given_answer, correct_answer, is_correct, field, difficulty}
        "domain_correct": {},   # {field: correct_count}
        "domain_total": {},     # {field: total_count}
        "completed": False,
    }

    # Get first question
    first_q = _pick_question(session)
    if first_q is None:
        logger.error("No questions available to start session!")
        return {"error": "No questions available."}

    session["current_question"] = first_q
    session["used_question_ids"].append(first_q["question_id"])
    ACTIVE_SESSIONS[session_id] = session

    logger.info(f"Started adaptive session {session_id} for student {student_id} | difficulty={starting_difficulty}")

    return {
        "session_id": session_id,
        "question_number": 1,
        "total_questions": QUIZ_LENGTH,
        "current_difficulty": starting_difficulty,
        "question": {
            "question_id": first_q["question_id"],
            "career_field": first_q["career_field"],
            "question": first_q["question"],
            "options": first_q["options"],
        }
    }


def submit_adaptive_answer(
    session_id: str,
    question_id: int,
    given_answer: str
) -> Dict[str, Any]:
    """
    Submit an answer and advance the session.

    Returns either the next question payload or the final results if 30 Qs are done.
    """
    session = ACTIVE_SESSIONS.get(session_id)
    if not session:
        return {"error": "Session not found. Please start a new session."}

    if session["completed"]:
        return {"error": "Quiz already completed."}

    current_q = session.get("current_question")
    if current_q is None or current_q["question_id"] != question_id:
        return {"error": "Question ID mismatch."}

    # Grade the answer
    is_correct = given_answer.strip().upper() == current_q["correct_answer"]
    field = current_q["career_field"]

    # Update stats
    session["questions_answered"] += 1
    if is_correct:
        session["correct_answers"] += 1

    session["domain_correct"][field] = session["domain_correct"].get(field, 0) + (1 if is_correct else 0)
    session["domain_total"][field] = session["domain_total"].get(field, 0) + 1

    session["answers_history"].append({
        "question_id": question_id,
        "question": current_q["question"],
        "given_answer": given_answer.upper(),
        "correct_answer": current_q["correct_answer"],
        "is_correct": is_correct,
        "field": field,
        "difficulty": current_q["difficulty"],
    })

    # Adjust difficulty
    session["current_difficulty"] = _adjust_difficulty(current_q["difficulty"], is_correct)

    # Check if quiz is complete
    if session["questions_answered"] >= QUIZ_LENGTH:
        session["completed"] = True
        return _compile_results(session)

    # Get next question
    next_q = _pick_question(session)
    if next_q is None:
        # Edge case: exhausted questions — just end early
        session["completed"] = True
        return _compile_results(session)

    session["current_question"] = next_q
    session["used_question_ids"].append(next_q["question_id"])

    return {
        "completed": False,
        "question_number": session["questions_answered"] + 1,
        "total_questions": QUIZ_LENGTH,
        "current_difficulty": session["current_difficulty"],
        "is_correct": is_correct,
        "question": {
            "question_id": next_q["question_id"],
            "career_field": next_q["career_field"],
            "question": next_q["question"],
            "options": next_q["options"],
        }
    }


# ─── Results Compilation ──────────────────────────────────────────────────────
def _compile_results(session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compile final quiz results, determine learning path bracket, and run
    the Random Forest career recommender.
    """
    total_correct = session["correct_answers"]
    total_answered = session["questions_answered"]

    # Determine scoring bracket
    if total_correct <= 10:
        bracket = "beginner"
    elif total_correct <= 20:
        bracket = "foundation"
    else:
        bracket = "cs_ready"

    learning_path = LEARNING_PATHS[bracket]

    # Build per-domain percentage scores for the recommender
    domain_pct = {}
    for field, total in session["domain_total"].items():
        correct = session["domain_correct"].get(field, 0)
        domain_pct[field] = round((correct / total) * 100, 1) if total > 0 else 0.0

    # Map field scores → model feature vector
    programming_score = _avg_domain_scores(domain_pct, [
        "Web Development", "Frontend Development", "Backend Development",
        "Full Stack Development", "Mobile App Development",
        "Android Development", "iOS Development", "Desktop Application Development"
    ])
    logical_score = _avg_domain_scores(domain_pct, [
        "Database Engineering", "Quantum Computing", "Blockchain", "Game Development"
    ])
    networking_score = _avg_domain_scores(domain_pct, [
        "Networking", "Cloud Computing", "DevOps", "IoT"
    ])
    ai_score = _avg_domain_scores(domain_pct, [
        "Data Science", "Machine Learning", "AI Development",
        "AR/VR Development", "Bioinformatics", "Autonomous Vehicle Software"
    ])
    cyber_score = _avg_domain_scores(domain_pct, ["Cybersecurity"])
    communication_score = _avg_domain_scores(domain_pct, [
        "UI/UX Design", "FinTech", "HealthTech"
    ])

    feature_scores = {
        "programming_score": programming_score,
        "logical_score": logical_score,
        "networking_score": networking_score,
        "ai_score": ai_score,
        "cyber_score": cyber_score,
        "communication_score": communication_score,
    }

    # Run ML recommender
    career_recommendations = _run_recommender(session["student_id"], feature_scores)

    # Domain breakdown list for UI
    domain_breakdown = [
        {"field": field, "correct": session["domain_correct"].get(field, 0),
         "total": total, "percentage": domain_pct.get(field, 0)}
        for field, total in sorted(session["domain_total"].items(), key=lambda x: -x[1])
    ]

    return {
        "completed": True,
        "session_id": session["session_id"],
        "student_id": session["student_id"],
        "total_questions": total_answered,
        "total_correct": total_correct,
        "accuracy_pct": round((total_correct / total_answered) * 100, 1) if total_answered > 0 else 0,
        "bracket": bracket,
        "learning_path": learning_path,
        "domain_breakdown": domain_breakdown,
        "feature_scores": feature_scores,
        "career_recommendations": career_recommendations,
    }


def _avg_domain_scores(domain_pct: Dict[str, float], fields: List[str]) -> float:
    """Average domain percentage for a set of fields."""
    scores = [domain_pct[f] for f in fields if f in domain_pct]
    if not scores:
        return 50.0  # default mid-range if no data
    return round(sum(scores) / len(scores), 1)


def _run_recommender(student_id: str, feature_scores: Dict[str, float]) -> List[Dict[str, Any]]:
    """Call the trained Random Forest model; fall back gracefully on failure."""
    try:
        from services.career_recommender import recommend_career
        result = recommend_career(student_id, feature_scores)
        return result.get("recommendations", [])
    except Exception as e:
        logger.warning(f"Recommender failed for {student_id}: {e}")
        # Rule-based fallback
        sorted_scores = sorted(feature_scores.items(), key=lambda x: -x[1])
        fallback_map = {
            "programming_score": "Web Development",
            "ai_score": "AI/ML",
            "networking_score": "Cloud Computing",
            "cyber_score": "Cybersecurity",
            "logical_score": "Data Science",
            "communication_score": "UI/UX",
        }
        fallback = []
        for feat, score in sorted_scores[:3]:
            fallback.append({
                "domain": fallback_map.get(feat, feat),
                "score": round(score, 1)
            })
        return fallback


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an active session by ID."""
    return ACTIVE_SESSIONS.get(session_id)
