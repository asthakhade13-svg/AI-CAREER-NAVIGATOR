from typing import List


def generate_roadmap(target_domain: str, missing_skills: List[str]) -> dict:
    """
    Generates a personalized learning roadmap.
    Currently uses static templates, but can be extended to use Gemini.
    """
    roadmap = []

    roadmap.append(f"Step 1: Understand the basics of {target_domain}.")

    for i, skill in enumerate(missing_skills, start=2):
        roadmap.append(f"Step {i}: Learn {skill}. Focus on foundational concepts and practical exercises.")

    roadmap.append(f"Step {len(missing_skills) + 2}: Build 2-3 projects incorporating all these skills.")
    roadmap.append(f"Step {len(missing_skills) + 3}: Create a GitHub portfolio and update your resume.")
    roadmap.append(f"Step {len(missing_skills) + 4}: Apply for beginner internships in {target_domain}.")

    return {
        "domain": target_domain,
        "roadmap": roadmap
    }
