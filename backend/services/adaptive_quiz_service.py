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
            # Filter valid difficulties
            _questions_df["difficulty"] = _questions_df["difficulty"].astype(str).str.strip()
            _questions_df = _questions_df[_questions_df["difficulty"].isin(["Easy", "Medium", "Hard"])].copy()
            # Ensure correct_answer is uppercase
            _questions_df["correct_answer"] = _questions_df["correct_answer"].astype(str).str.strip().str.upper()
            _questions_df["career_field"] = _questions_df["career_field"].astype(str).str.strip()
            _questions_df["question_id"] = _questions_df["question_id"].astype(int)
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
    question_text = str(row["question"])
    career_field = str(row["career_field"])
    difficulty = str(row["difficulty"])

    # Detect if the options are generic placeholders
    placeholders = {
        "Learning core concepts and tools",
        "Using structured development practices",
        "Applying scalable and maintainable engineering practices",
        "Learning core concepts and practical skills",
        "Following structured engineering practices",
        "Using scalable, secure, and maintainable approaches"
    }
    opt_a = str(row["option_a"]).strip()
    is_placeholder = opt_a in placeholders or any(p in opt_a for p in ["Learning core", "Using structured", "Applying scalable", "Following structured"])

    options = {
        "A": str(row["option_a"]),
        "B": str(row["option_b"]),
        "C": str(row["option_c"]),
        "D": str(row["option_d"]),
    }
    correct_answer = str(row["correct_answer"]).strip().upper()

    if is_placeholder:
        try:
            from services.quiz_generator import generate_options_for_question
            enhanced = generate_options_for_question(question_text, career_field, difficulty)
            if enhanced and "options" in enhanced and "correct_answer" in enhanced:
                opt_dict = enhanced["options"]
                if all(k in opt_dict for k in ["A", "B", "C", "D"]):
                    options = {
                        "A": str(opt_dict["A"]),
                        "B": str(opt_dict["B"]),
                        "C": str(opt_dict["C"]),
                        "D": str(opt_dict["D"])
                    }
                    correct_answer = str(enhanced["correct_answer"]).strip().upper()
                    logger.info(f"Dynamically generated options for question ID {row['question_id']}")
        except Exception as e:
            logger.error(f"Failed to dynamically generate options: {e}")

    return {
        "question_id": int(row["question_id"]),
        "career_field": career_field,
        "difficulty": difficulty,
        "question": question_text,
        "options": options,
        "correct_answer": correct_answer,
    }


# ─── Difficulty adjustment ────────────────────────────────────────────────────
DIFFICULTY_UP = {"Easy": "Medium", "Medium": "Hard", "Hard": "Hard"}
DIFFICULTY_DOWN = {"Easy": "Easy", "Medium": "Easy", "Hard": "Medium"}


def _adjust_difficulty(current: str, is_correct: bool) -> str:
    if is_correct:
        return DIFFICULTY_UP[current]
    return DIFFICULTY_DOWN[current]


# ─── Interest → Career Field Mapping ─────────────────────────────────────────
# Maps Q36 questionnaire answer options to canonical career_field values in the CSV.
# Maps the 10 career domains returned by classify_student_profile → question bank career_field values
DOMAIN_TO_FIELD: Dict[str, List[str]] = {
    "AI/ML":               ["Machine Learning", "AI Development", "Data Science", "Artificial Intelligence"],
    "Data Science":        ["Data Science", "Data Analytics", "Machine Learning", "Business Intelligence"],
    "Cyber Security":      ["Cybersecurity", "Network Security", "Ethical Hacking", "Penetration Testing"],
    "Web Development":     ["Web Development", "Full Stack Development", "Frontend Development", "Backend Development"],
    "App Development":     ["Mobile App Development", "Android Development", "iOS Development", "Cross-Platform Development"],
    "UI/UX Design":        ["UI Design", "UX Design", "UI/UX Design", "Motion UI Development"],
    "Cloud Computing":     ["Cloud Computing", "Cloud Architecture", "DevOps Engineering", "Site Reliability Engineering"],
    "DevOps":              ["DevOps Engineering", "DevOps", "Cloud Computing", "Site Reliability Engineering"],
    "Game Development":    ["Game Development", "Game Design", "AR/VR Development", "Interactive Media"],
    "Software Engineering":["Software Engineering", "Full Stack Development", "Backend Development", "Systems Programming"],
}


def _map_domain_to_field(domain: str, all_fields: List[str]) -> str:
    """
    Maps a classify_student_profile domain name to the best matching career_field
    that actually exists in the adaptive questions CSV.
    """
    if not domain:
        return random.choice(all_fields)

    # Try DOMAIN_TO_FIELD first
    candidates = DOMAIN_TO_FIELD.get(domain, [])
    for c in candidates:
        if c in all_fields:
            return c

    # Fall back to partial/keyword match
    lower = domain.lower()
    for field in all_fields:
        if lower in field.lower() or field.lower() in lower:
            return field
    for keyword in lower.split():
        if len(keyword) >= 3:
            for field in all_fields:
                if keyword in field.lower():
                    return field

    logger.warning(f"Could not map domain '{domain}' to any question bank field; picking random.")
    return random.choice(all_fields)


INTEREST_TO_FIELD: Dict[str, List[str]] = {
    # Q36 choices (exact strings the frontend sends)
    "Software Development":   ["Full Stack Development", "Backend Development", "Frontend Development", "Web Development"],
    "AI/ML":                  ["Machine Learning", "AI Development", "Data Science", "Artificial Intelligence"],
    "Data Science":           ["Data Science", "Data Analytics", "Machine Learning"],
    "Cybersecurity":          ["Cybersecurity", "Network Security", "Ethical Hacking"],
    "Cloud Computing":        ["Cloud Computing", "DevOps Engineering", "Cloud Architecture"],
    "DevOps":                 ["DevOps Engineering", "Cloud Computing", "Site Reliability Engineering"],
    "UI/UX Design":           ["UI Design", "UX Design", "UI/UX Design", "Motion UI Development"],
    "Product Management":     ["Product Management", "Agile Project Management", "IT Consulting"],
    "Entrepreneurship":       ["FinTech Engineering", "EdTech Engineering", "Web Development"],
    "Research":               ["Artificial Intelligence", "Quantum Computing", "Computational Linguistics"],
    # Activity interests from Q35 (Coding, Designing, etc.) as fallbacks
    "Coding":                 ["Web Development", "Backend Development", "Full Stack Development"],
    "Designing":              ["UI Design", "Motion UI Development", "UX Design"],
    "Teaching":               ["EdTech Engineering", "E-Learning Development"],
    "Writing":                ["Technical Writing", "Content Management Systems"],
    "Management":             ["IT Consulting", "Agile Project Management", "Product Management"],
    "Business":               ["FinTech Engineering", "CRM Development", "ERP Development"],
}


def _map_interest_to_field(interest_field: Optional[str], all_fields: List[str]) -> str:
    """
    Given the raw interest string from the questionnaire, return the best
    matching career_field that actually exists in the question bank.
    Tries INTEREST_TO_FIELD mapping first, then partial-string matching,
    then falls back to a random field.
    """
    if not interest_field:
        return random.choice(all_fields)

    # 1. Exact match
    if interest_field in all_fields:
        return interest_field

    # 2. Mapping lookup
    candidates = INTEREST_TO_FIELD.get(interest_field, [])
    for candidate in candidates:
        if candidate in all_fields:
            return candidate

    # 3. Partial / case-insensitive substring match
    lower = interest_field.lower()
    for field in all_fields:
        if lower in field.lower() or field.lower() in lower:
            return field

    # 4. Keyword match (split on spaces)
    for keyword in lower.split():
        if len(keyword) >= 3:  # skip tiny words
            for field in all_fields:
                if keyword in field.lower():
                    return field

    # 5. Random fallback
    logger.warning(f"Could not map interest '{interest_field}' to any known field; picking random.")
    return random.choice(all_fields)


# ─── Profile-Seeded First Question Generator ─────────────────────────────────
def _build_trait_narrative(trait_scores: Dict[str, float]) -> str:
    """
    Convert raw trait scores into a human-readable profile narrative
    for the LLM prompt.
    """
    # Sort traits by score descending
    traits_layer1 = [
        ("Analytical Thinking", trait_scores.get("analytical_thinking", 50)),
        ("Creativity",          trait_scores.get("creativity", 50)),
        ("Curiosity",           trait_scores.get("curiosity", 50)),
        ("Attention to Detail", trait_scores.get("attention_to_detail", 50)),
        ("Communication",       trait_scores.get("communication", 50)),
        ("Leadership",          trait_scores.get("leadership", 50)),
        ("Building Mindset",    trait_scores.get("building_mindset", 50)),
        ("Research Mindset",    trait_scores.get("research_mindset", 50)),
        ("User Empathy",        trait_scores.get("user_empathy", 50)),
    ]
    goals_layer2 = [
        ("Placement Focus",       trait_scores.get("placement_focus", 50)),
        ("Technical Expertise",   trait_scores.get("technical_expertise", 50)),
        ("Research Orientation",  trait_scores.get("research_orientation", 50)),
        ("Entrepreneurship",      trait_scores.get("entrepreneurship", 50)),
        ("Leadership & Management", trait_scores.get("leadership_management", 50)),
    ]

    top3_traits = sorted(traits_layer1, key=lambda x: x[1], reverse=True)[:3]
    top2_goals  = sorted(goals_layer2,  key=lambda x: x[1], reverse=True)[:2]

    trait_text = ", ".join([f"{n} ({v:.0f}%)" for n, v in top3_traits])
    goal_text  = ", ".join([f"{n} ({v:.0f}%)" for n, v in top2_goals])
    tech_score = trait_scores.get("existing_skills", 0)
    tech_level = "Advanced" if tech_score >= 70 else ("Intermediate" if tech_score >= 35 else "Beginner")

    return (
        f"Top personality traits: {trait_text}. "
        f"Top career goals: {goal_text}. "
        f"Technical exposure level: {tech_level} ({tech_score:.0f}% score)."
    )


def generate_profile_seeded_first_question(
    trait_scores: Dict[str, float],
    top_domain: str,
    starting_difficulty: str,
) -> Optional[Dict[str, Any]]:
    """
    Calls Groq (or Gemini fallback) to generate a fully personalised first
    adaptive test question derived directly from the student's trait analysis.

    The prompt tells the LLM:
      - The student's dominant personality traits (from Layer 1)
      - The student's top career goals (from Layer 2)
      - The recommended career domain (from the recommendation engine)
      - The target difficulty level

    Returns a question dict compatible with the session format, or None on failure.
    """
    from config import settings
    import requests as _req

    narrative = _build_trait_narrative(trait_scores)
    tech_level = "Beginner" if trait_scores.get("existing_skills", 0) < 35 else \
                 ("Intermediate" if trait_scores.get("existing_skills", 0) < 70 else "Advanced")

    prompt = f"""You are an expert Computer Science career assessment engine.

A B.Tech CSE student has just completed a 3-layer personality and career assessment.
Here is their profile:
- {narrative}
- Recommended career domain: {top_domain}
- Technical background: {tech_level}

Based on this profile, generate the FIRST question of their personalised adaptive technical test.
The question must:
1. Be directly relevant to the domain: "{top_domain}"
2. Match difficulty: {starting_difficulty}
3. Test a real technical concept or foundational idea in {top_domain}
4. Be a 4-option MCQ with exactly one correct answer
5. Feel natural as an opening question for someone with the traits described above

Return ONLY valid JSON matching this structure exactly:
{{
  "question": "<the full question text>",
  "options": {{
    "A": "<option A>",
    "B": "<option B>",
    "C": "<option C>",
    "D": "<option D>"
  }},
  "correct_answer": "<A|B|C|D>",
  "career_field": "{top_domain}",
  "difficulty": "{starting_difficulty}",
  "rationale": "<one sentence why this question fits this student's profile>"
}}"""

    def _call_llm(api_url: str, model: str, key: str) -> Optional[Dict[str, Any]]:
        try:
            res = _req.post(
                api_url,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}],
                      "response_format": {"type": "json_object"}},
                timeout=12,
            )
            if res.ok:
                import json as _json
                raw = res.json()["choices"][0]["message"]["content"].strip()
                raw = raw.lstrip("```json").lstrip("```").rstrip("```").strip()
                return _json.loads(raw)
        except Exception as e:
            logger.error(f"LLM call failed ({model}): {e}")
        return None

    result = None

    # 1. Try Groq (gsk_...) or Grok
    if settings.GROK_API_KEY:
        if settings.GROK_API_KEY.startswith("gsk_"):
            result = _call_llm("https://api.groq.com/openai/v1/chat/completions",
                               "llama-3.3-70b-versatile", settings.GROK_API_KEY)
        else:
            result = _call_llm("https://api.x.ai/v1/chat/completions",
                               "grok-2-1212", settings.GROK_API_KEY)

    # 2. Fallback to Gemini
    if result is None and settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            import json as _json
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model_obj = genai.GenerativeModel("gemini-1.5-flash")
            resp = model_obj.generate_content(prompt)
            raw = resp.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            result = _json.loads(raw)
        except Exception as e:
            logger.error(f"Gemini first-question generation failed: {e}")

    if result is None:
        logger.warning("LLM unavailable for first question generation; will use question bank fallback.")
        return None

    # Validate minimal structure
    if not all(k in result for k in ["question", "options", "correct_answer"]):
        logger.error(f"LLM returned incomplete question structure: {result}")
        return None

    # Assign a synthetic question_id outside the bank's range
    return {
        "question_id": 99999,   # sentinel: marks AI-generated question
        "career_field": result.get("career_field", top_domain),
        "difficulty": result.get("difficulty", starting_difficulty),
        "question": result["question"],
        "options": result["options"],
        "correct_answer": str(result["correct_answer"]).strip().upper(),
        "ai_generated": True,
        "rationale": result.get("rationale", ""),
    }


# ─── Session Management ───────────────────────────────────────────────────────
def start_adaptive_session(
    student_id: str,
    technical_score: float,
    interest_field: Optional[str] = None,
    recommended_careers: Optional[List[str]] = None,
    trait_scores: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Initialise a new adaptive quiz session seeded from the 3-layer profile.

    Args:
        student_id          : The student's identifier.
        technical_score     : Existing-skills score from Layer 3 (determines start difficulty).
        interest_field      : Top recommended career domain (from classify_student_profile).
        recommended_careers : Full ordered list of recommended domains (Top 3).
        trait_scores        : All computed personality + goal scores from the basic info assessment.

    First Question Strategy:
      - If LLM is available: generate a bespoke question from the student's trait profile
      - Otherwise: pick from the question bank matching the top recommended domain

    Field rotation strategy (questions 2-30):
      - Q2–Q5   → top recommended domain
      - Q6–Q10  → 2nd recommended domain (if present)
      - Q11–Q15 → 3rd recommended domain (if present)
      - Q16–Q30 → shuffle of other available fields
    """
    session_id = str(uuid.uuid4())

    # ── Determine starting difficulty ──────────────────────────────────────────
    # Layer 3 score: 0-100.  ≥35 = experienced → Medium; else → Easy
    starting_difficulty = "Medium" if technical_score >= 35 else "Easy"

    all_fields = _get_available_fields()

    # ── Build profile-aligned field rotation ──────────────────────────────────
    if recommended_careers and len(recommended_careers) > 0:
        ordered_pref = []
        for domain in recommended_careers:
            field = _map_domain_to_field(domain, all_fields)
            if field not in ordered_pref:
                ordered_pref.append(field)
        logger.info(f"Recommended domains {recommended_careers} → fields {ordered_pref}")
    else:
        primary = _map_interest_to_field(interest_field, all_fields)
        ordered_pref = [primary]
        logger.info(f"Interest '{interest_field}' → mapped to field '{primary}'")

    other_fields = [f for f in all_fields if f not in ordered_pref]
    random.shuffle(other_fields)
    field_rotation = (ordered_pref + other_fields)[:6]

    session: Dict[str, Any] = {
        "session_id": session_id,
        "student_id": student_id,
        "technical_score": technical_score,
        "current_difficulty": starting_difficulty,
        "field_rotation": field_rotation,
        "questions_answered": 0,
        "correct_answers": 0,
        "used_question_ids": [],
        "answers_history": [],
        "domain_correct": {},
        "domain_total": {},
        "completed": False,
    }

    # ── Get first question — AI-generated if trait_scores available ────────────
    top_domain = interest_field or (recommended_careers[0] if recommended_careers else None)
    first_q = None
    ai_generated = False

    if trait_scores and top_domain:
        logger.info(f"Attempting AI-generated first question for domain='{top_domain}' difficulty={starting_difficulty}")
        first_q = generate_profile_seeded_first_question(
            trait_scores=trait_scores,
            top_domain=top_domain,
            starting_difficulty=starting_difficulty,
        )
        if first_q:
            ai_generated = True
            logger.info(f"AI-generated first question ready: {first_q['question'][:80]}...")

    # Fallback to question bank
    if first_q is None:
        first_q = _pick_question(session)

    if first_q is None:
        logger.error("No questions available to start session!")
        return {"error": "No questions available."}

    session["current_question"] = first_q
    # Only add to used_ids if from the bank (AI question has sentinel ID 99999)
    if not ai_generated:
        session["used_question_ids"].append(first_q["question_id"])
    ACTIVE_SESSIONS[session_id] = session

    logger.info(f"Started adaptive session {session_id} | difficulty={starting_difficulty} | q1_source={'AI' if ai_generated else 'bank'}")

    return {
        "session_id": session_id,
        "question_number": 1,
        "total_questions": QUIZ_LENGTH,
        "current_difficulty": starting_difficulty,
        "ai_seeded": ai_generated,
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
