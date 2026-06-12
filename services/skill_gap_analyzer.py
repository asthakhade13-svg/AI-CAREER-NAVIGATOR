from typing import List
from utils.helpers import load_json
from models.skill_gap_model import SkillGapResponse


def analyze_skill_gap(student_id: str, target_domain: str, current_skills: List[str]) -> SkillGapResponse:
    """
    Compares student's current skills against industry requirements for a target domain.
    """
    try:
        industry_skills = load_json("data/industry_skills.json")
    except FileNotFoundError:
        industry_skills = {}

    required_skills = industry_skills.get(target_domain, [])

    missing_skills = [
        skill for skill in required_skills
        if skill.lower() not in [s.lower() for s in current_skills]
    ]

    # Simple priority order based on order in JSON
    priority_order = missing_skills

    suggested_resources = [
        f"Search for '{skill} course for beginners'" for skill in missing_skills
    ]

    return SkillGapResponse(
        target_domain=target_domain,
        missing_skills=missing_skills,
        priority_order=priority_order,
        suggested_resources=suggested_resources
    )
