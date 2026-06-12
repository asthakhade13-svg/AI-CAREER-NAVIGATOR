import pandas as pd
import logging
from typing import List, Dict, Any
from models.basic_info_model import QuestionModel, QuestionnaireResponse, ProfileSummary

logger = logging.getLogger(__name__)

CSV_PATH = "data/basic_info_questions.csv"

def get_basic_info_questions() -> List[Dict[str, Any]]:
    """
    Loads basic information questions from the CSV file and returns them
    grouped by section for clean rendering in the frontend.
    """
    try:
        df = pd.read_csv(CSV_PATH)
        sections_dict = {}
        
        for index, row in df.iterrows():
            q_id = int(row["question_id"])
            section = str(row["section"])
            question_text = str(row["question"])
            q_type = str(row["question_type"])
            
            raw_options = row["options"]
            options = []
            if pd.notna(raw_options) and str(raw_options).strip() != "":
                options = [opt.strip() for opt in str(raw_options).split("|")]
                
            q_data = {
                "question_id": q_id,
                "section": section,
                "question": question_text,
                "question_type": q_type,
                "options": options
            }
            
            if section not in sections_dict:
                sections_dict[section] = []
            sections_dict[section].append(q_data)
            
        # Format as list of sections to preserve ordering
        ordered_sections = [
            "Basic Information",
            "Academic Background",
            "Technical Knowledge Assessment",
            "Skills Assessment",
            "Interests",
            "Personality & Work Style",
            "Career Awareness",
            "Learning & Growth",
            "Aptitude & Reasoning",
            "Goals"
        ]
        
        result = []
        for sec in ordered_sections:
            if sec in sections_dict:
                result.append({
                    "section": sec,
                    "questions": sections_dict[sec]
                })
        return result
    except Exception as e:
        logger.error(f"Error reading basic info CSV: {e}")
        return []

def classify_student_profile(student_id: str, answers: Dict[str, Any]) -> QuestionnaireResponse:
    """
    Classifies a student's technical level based on interest questionnaire.
    Returns whether they should take 'general' or 'cs' quiz.
    """
    # Normalize keys: answers could be key 'q13' or '13'
    def get_ans(q_num: int, default=None):
        val = answers.get(f"q{q_num}")
        if val is None:
            val = answers.get(str(q_num))
        return default if val is None else val

    # 1. Rating sum (Q13, Q17-23)
    rating_questions = [13, 17, 18, 19, 20, 21, 22, 23]
    rating_sum = 0
    for rq in rating_questions:
        ans_val = get_ans(rq)
        try:
            rating_sum += int(ans_val) if ans_val is not None else 1
        except (ValueError, TypeError):
            rating_sum += 1

    # 2. Languages points (Q14)
    lang_ans = get_ans(14)
    lang_count = 0
    if lang_ans:
        if isinstance(lang_ans, list):
            lang_count = len(lang_ans)
        elif isinstance(lang_ans, str):
            lang_count = len([l.strip() for l in lang_ans.split("|") if l.strip()])
    lang_points = min(lang_count, 5) # limit to 5 points max

    # 3. Project points (Q15, Q16)
    proj_built = str(get_ans(15, "")).strip().lower()
    proj_points = 0
    if proj_built == "yes":
        proj_points += 2
        proj_count_ans = str(get_ans(16, "")).strip()
        if proj_count_ans in ["1-2"]:
            proj_points += 1
        elif proj_count_ans in ["3-5"]:
            proj_points += 2
        elif proj_count_ans in ["6-10"]:
            proj_points += 3
        elif proj_count_ans in ["10+"]:
            proj_points += 4

    # 4. Git experience (Q24)
    git_exp = str(get_ans(24, "")).strip().lower()
    git_points = 0
    if "beginner" in git_exp:
        git_points += 1
    elif "intermediate" in git_exp:
        git_points += 2
    elif "advanced" in git_exp:
        git_points += 3

    # Calculate final technical familiarity score
    technical_score = rating_sum + lang_points + proj_points + git_points

    # Route decision: Threshold is 15 points
    if technical_score >= 15:
        starting_quiz = "cs"
        reason = f"Based on your profile, you scored {technical_score} on Technical Familiarity (ratings: {rating_sum}/40, languages: {lang_count}, projects: {proj_points}, git: {git_points}). This indicates experienced baseline knowledge in core CS subjects."
    else:
        starting_quiz = "general"
        reason = f"Based on your profile, you scored {technical_score} on Technical Familiarity (ratings: {rating_sum}/40, languages: {lang_count}, projects: {proj_points}, git: {git_points}). This suggests starting with the General Quiz to establish fundamental computing competencies."

    # Extract details for profile summary
    full_name = str(get_ans(1, "Anonymous")).strip()
    email = str(get_ans(2, "")).strip()
    current_year = str(get_ans(5, "1st Year")).strip()
    
    interests_ans = get_ans(35)
    interests = []
    if interests_ans:
        if isinstance(interests_ans, list):
            interests = interests_ans
        elif isinstance(interests_ans, str):
            interests = [i.strip() for i in interests_ans.split("|") if i.strip()]
            
    fav_subject = str(get_ans(9, "Computer Science")).strip()
    motivation = str(get_ans(37, "Innovation")).strip()

    profile_summary = ProfileSummary(
        full_name=full_name,
        email=email,
        current_year=current_year,
        interests=interests,
        favorite_subject=fav_subject,
        primary_motivation=motivation
    )

    return QuestionnaireResponse(
        student_id=student_id,
        technical_score=float(technical_score),
        starting_quiz=starting_quiz,
        reason=reason,
        profile_summary=profile_summary
    )
