import pandas as pd
import logging
from typing import List, Dict, Any, Union
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
            "Personality & Aptitude",
            "Career Goals & Preferences",
            "Existing Technical Exposure",
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
    Evaluates a student's profile based on the 3-layer assessment architecture.
    Calculates final suitability scores for 10 career domains and recommends the Top 3.
    """
    def get_ans(q_num: int, default=None):
        val = answers.get(f"q{q_num}")
        if val is None:
            val = answers.get(str(q_num))
        return default if val is None else val

    # Helper to map Likert scale and rating answers to numerical scale (1.0 to 5.0)
    def to_val(q_num: int) -> float:
        ans_val = get_ans(q_num)
        if ans_val is None:
            return 3.0 # neutral default
        
        ans_str = str(ans_val).strip().lower()
        if "strongly disagree" in ans_str:
            return 1.0
        elif "disagree" in ans_str:
            return 2.0
        elif "neutral" in ans_str:
            return 3.0
        elif "strongly agree" in ans_str:
            return 5.0
        elif "agree" in ans_str:
            return 4.0
        
        # Rating categories for placement importance
        if "not important" in ans_str:
            return 1.0
        elif "somewhat important" in ans_str:
            return 2.0
        elif "important" in ans_str and "very" not in ans_str:
            return 4.0
        elif "very important" in ans_str:
            return 5.0

        try:
            return float(ans_val)
        except (ValueError, TypeError):
            return 3.0

    # Helper to convert a 1-5 rating/Likert value to a 0-100 percentage
    def scale_1_5_to_100(val: float) -> float:
        return ((val - 1.0) / 4.0) * 100.0

    # ── Layer 1: Personality & Aptitude Traits (50% weight) ──
    analytical_thinking = scale_1_5_to_100((to_val(1) + to_val(2)) / 2.0)
    creativity          = scale_1_5_to_100((to_val(3) + to_val(4)) / 2.0)
    curiosity           = scale_1_5_to_100((to_val(5) + to_val(6)) / 2.0)
    attention_to_detail = scale_1_5_to_100((to_val(7) + to_val(8)) / 2.0)
    communication       = scale_1_5_to_100((to_val(9) + to_val(10)) / 2.0)
    leadership          = scale_1_5_to_100((to_val(11) + to_val(12)) / 2.0)
    building_mindset    = scale_1_5_to_100((to_val(13) + to_val(14)) / 2.0)
    research_mindset    = scale_1_5_to_100((to_val(15) + to_val(16)) / 2.0)
    user_empathy        = scale_1_5_to_100((to_val(17) + to_val(18)) / 2.0)

    # ── Layer 2: Career Goals & Preferences (30% weight) ──
    placement_focus     = scale_1_5_to_100((to_val(19) + to_val(20)) / 2.0)
    technical_expertise = scale_1_5_to_100((to_val(21) + to_val(22)) / 2.0)
    research_orient     = scale_1_5_to_100((to_val(23) + to_val(24)) / 2.0)
    entrepreneurship    = scale_1_5_to_100((to_val(25) + to_val(26)) / 2.0)
    leadership_mgmt     = scale_1_5_to_100((to_val(27) + to_val(28)) / 2.0)

    # ── Layer 3: Existing Skills (20% weight) ──
    # Q29: Programming rating (1-5)
    prog_rating = scale_1_5_to_100(to_val(29))
    
    # Q30: Languages list
    lang_ans = get_ans(30)
    lang_count = 0
    if lang_ans:
        if isinstance(lang_ans, list):
            lang_count = len(lang_ans)
        elif isinstance(lang_ans, str):
            lang_count = len([l.strip() for l in lang_ans.split("|") if l.strip()])
    langs_score = min(lang_count / 3.0, 1.0) * 100.0 # 3+ languages gives 100%

    # Q31: Projects Built (Yes/No)
    proj_built = str(get_ans(31, "")).strip().lower()
    proj_built_score = 100.0 if "yes" in proj_built else 0.0

    # Q32: Number of projects completed ("0"|"1-2"|"3-5"|"5+")
    proj_count_ans = str(get_ans(32, "")).strip()
    if proj_count_ans == "0":
        proj_count_score = 0.0
    elif proj_count_ans == "1-2":
        proj_count_score = 50.0
    elif proj_count_ans == "3-5":
        proj_count_score = 85.0
    elif proj_count_ans == "5+":
        proj_count_score = 100.0
    else:
        proj_count_score = 0.0

    # Q33: Git/GitHub experience
    git_exp = str(get_ans(33, "")).strip().lower()
    if "never" in git_exp:
        git_score = 0.0
    elif "beginner" in git_exp:
        git_score = 33.0
    elif "intermediate" in git_exp:
        git_score = 66.0
    elif "advanced" in git_exp:
        git_score = 100.0
    else:
        git_score = 0.0

    # Overall Existing Technical Exposure Score (0-100%)
    existing_skills_score = (prog_rating + langs_score + proj_built_score + proj_count_score + git_score) / 5.0

    # ── Derived Traits for Domain Mapping ──
    # Problem Solving is a mix of Analytical Thinking and raw Programming/DSA experience
    problem_solving = 0.6 * analytical_thinking + 0.4 * prog_rating
    # Technical Depth is a mix of Technical Expertise goals and Programming experience
    technical_depth = 0.6 * technical_expertise + 0.4 * prog_rating

    # ── Calculate suitability scores for all 10 domains ──
    domain_configs = {
        "AI/ML": {
            "traits": {"Analytical Thinking": 0.35, "Curiosity": 0.25, "Research Mindset": 0.25, "Technical Depth": 0.15},
            "goals": {"Research Orientation": 0.60, "Technical Expertise": 0.40}
        },
        "Data Science": {
            "traits": {"Analytical Thinking": 0.40, "Research Mindset": 0.30, "Attention to Detail": 0.20, "Curiosity": 0.10},
            "goals": {"Research Orientation": 0.40, "Technical Expertise": 0.60}
        },
        "Cyber Security": {
            "traits": {"Attention to Detail": 0.35, "Problem Solving": 0.30, "Curiosity": 0.20, "Technical Depth": 0.15},
            "goals": {"Technical Expertise": 0.70, "Placement Focus": 0.30}
        },
        "Web Development": {
            "traits": {"Building Mindset": 0.35, "Problem Solving": 0.25, "Creativity": 0.20, "User Empathy": 0.20},
            "goals": {"Placement Focus": 0.60, "Technical Expertise": 0.40}
        },
        "App Development": {
            "traits": {"Building Mindset": 0.40, "Problem Solving": 0.35, "Creativity": 0.15, "User Empathy": 0.10},
            "goals": {"Placement Focus": 0.50, "Technical Expertise": 0.30, "Entrepreneurship": 0.20}
        },
        "UI/UX Design": {
            "traits": {"Creativity": 0.40, "User Empathy": 0.40, "Communication": 0.20},
            "goals": {"Placement Focus": 0.50, "Leadership": 0.50}
        },
        "Cloud Computing": {
            "traits": {"Problem Solving": 0.40, "Technical Depth": 0.30, "Analytical Thinking": 0.20, "Attention to Detail": 0.10},
            "goals": {"Technical Expertise": 0.60, "Placement Focus": 0.40}
        },
        "DevOps": {
            "traits": {"Problem Solving": 0.35, "Technical Depth": 0.30, "Attention to Detail": 0.20, "Building Mindset": 0.15},
            "goals": {"Technical Expertise": 0.60, "Placement Focus": 0.40}
        },
        "Game Development": {
            "traits": {"Creativity": 0.35, "Building Mindset": 0.35, "Problem Solving": 0.20, "Curiosity": 0.10},
            "goals": {"Technical Expertise": 0.50, "Entrepreneurship": 0.30, "Placement Focus": 0.20}
        },
        "Software Engineering": {
            "traits": {"Problem Solving": 0.35, "Analytical Thinking": 0.30, "Building Mindset": 0.20, "Technical Depth": 0.15},
            "goals": {"Placement Focus": 0.50, "Technical Expertise": 0.30, "Leadership": 0.20}
        }
    }

    trait_scores_calculated = {
        "Analytical Thinking": analytical_thinking,
        "Creativity": creativity,
        "Curiosity": curiosity,
        "Attention to Detail": attention_to_detail,
        "Communication": communication,
        "Leadership": leadership,
        "Building Mindset": building_mindset,
        "Research Mindset": research_mindset,
        "User Empathy": user_empathy,
        "Problem Solving": problem_solving,
        "Technical Depth": technical_depth
    }

    goal_scores_calculated = {
        "Placement Focus": placement_focus,
        "Technical Expertise": technical_expertise,
        "Research Orientation": research_orient,
        "Entrepreneurship": entrepreneurship,
        "Leadership": leadership_mgmt
    }

    career_scores = []
    for domain, weights in domain_configs.items():
        t_score = sum(trait_scores_calculated[t] * w for t, w in weights["traits"].items())
        g_score = sum(goal_scores_calculated[g] * w for g, w in weights["goals"].items())
        final_score = 0.50 * t_score + 0.30 * g_score + 0.20 * existing_skills_score
        career_scores.append((domain, final_score))

    career_scores.sort(key=lambda x: x[1], reverse=True)
    top_3 = career_scores[:3]

    sorted_traits = sorted(trait_scores_calculated.items(), key=lambda x: x[1], reverse=True)
    dominant_traits = [t[0] for t in sorted_traits[:4]]

    recommended_careers = []
    for rank, (domain, score) in enumerate(top_3):
        required = set(domain_configs[domain]["traits"].keys())
        intersection = [dt for dt in dominant_traits if dt in required]
        if not intersection:
            intersection = list(required)[:2]
        
        bullets = [f"Aligned with your {it}" for it in intersection[:3]]
        if domain in ["AI/ML", "Data Science"] and research_orient > 60:
            bullets.append("Matches your research and innovation orientation")
        elif placement_focus > 60:
            bullets.append("Strongly fits your campus placement focus")

        recommended_careers.append({
            "domain": domain,
            "score": round(score, 1),
            "reason": " • ".join(bullets)
        })

    if existing_skills_score >= 35.0:
        starting_quiz = "cs"
        route_reason = "baseline technical skills indicate experienced exposure."
    else:
        starting_quiz = "general"
        route_reason = "establishing fundamental computing competencies."

    reason_text = (
        f"The recommendation engine evaluated your profile and identified your top career paths. "
        f"You are routed to the '{starting_quiz}' quiz starting tier, as your technical exposure score is "
        f"{round(existing_skills_score, 1)}% ({route_reason})."
    )

    # ── Full trait score export for adaptive quiz seeding ──
    all_trait_scores = {
        # Personality & Aptitude (Layer 1)
        "analytical_thinking": round(analytical_thinking, 1),
        "creativity": round(creativity, 1),
        "curiosity": round(curiosity, 1),
        "attention_to_detail": round(attention_to_detail, 1),
        "communication": round(communication, 1),
        "leadership": round(leadership, 1),
        "building_mindset": round(building_mindset, 1),
        "research_mindset": round(research_mindset, 1),
        "user_empathy": round(user_empathy, 1),
        # Career Goals (Layer 2)
        "placement_focus": round(placement_focus, 1),
        "technical_expertise": round(technical_expertise, 1),
        "research_orientation": round(research_orient, 1),
        "entrepreneurship": round(entrepreneurship, 1),
        "leadership_management": round(leadership_mgmt, 1),
        # Existing Skills (Layer 3)
        "existing_skills": round(existing_skills_score, 1),
    }

    profile_summary = ProfileSummary(
        full_name="Student",
        email="",
        current_year="1st Year",
        interests=dominant_traits,
        favorite_subject="Core CSE",
        primary_motivation="Career Navigation"
    )

    return QuestionnaireResponse(
        student_id=student_id,
        technical_score=float(existing_skills_score),
        starting_quiz=starting_quiz,
        reason=reason_text,
        profile_summary=profile_summary,
        recommended_careers=recommended_careers,
        trait_scores=all_trait_scores
    )
