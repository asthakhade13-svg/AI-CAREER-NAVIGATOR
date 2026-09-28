from fastapi import APIRouter, HTTPException
from models.skill_gap_model import SkillAssessmentRequest, SkillGapRequest, SkillGapResponse
from services.career_recommender import recommend_career
from services.skill_gap_analyzer import analyze_skill_gap
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/recommend")
async def api_recommend_career(request: SkillAssessmentRequest):
    """
    Recommend top career domains based on quiz scores and interests.
    """
    try:
        recommendations = recommend_career(request.student_id, request.quiz_results)
        return recommendations
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to recommend career.")


@router.post("/skill_gap", response_model=SkillGapResponse)
async def api_skill_gap(request: SkillGapRequest):
    """
    Analyze skill gap between student's current skills and target domain.
    """
    try:
        gap = analyze_skill_gap(request.student_id, request.target_domain, request.current_skills)
        return gap
    except Exception as e:
        logger.error(f"Skill gap error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze skill gap.")


@router.get("/skill-gap/{student_id}")
def get_student_skill_gap(student_id: str, track: str = "aiml"):
    """
    Personalized Skill Gap Remediation Engine: Evaluates student's current learning status
    and returns high-priority gap areas with targeted study paths.
    """
    track_gaps = {
        "aiml": {
            "targetDomain": "AI & Machine Learning Engineer",
            "currentReadiness": 72,
            "acquiredSkills": ["Python Core", "NumPy", "Pandas", "Linear Algebra Basics"],
            "missingSkills": [
                {"skill": "PyTorch & Deep Learning", "priority": "High", "timeToLearn": "2 Weeks", "estimatedHours": 18},
                {"skill": "FastAPI Model Serving", "priority": "Medium", "timeToLearn": "1 Week", "estimatedHours": 10},
                {"skill": "Vector DBs & RAG (Chroma/LangChain)", "priority": "High", "timeToLearn": "2 Weeks", "estimatedHours": 15}
            ],
            "actionPlan": [
                "Build and fine-tune an image or text classifier in PyTorch",
                "Deploy the inference pipeline as a REST API using FastAPI",
                "Implement a local RAG agent with ChromaDB and an open-source LLM"
            ]
        },
        "webdev": {
            "targetDomain": "Full Stack Web Developer",
            "currentReadiness": 78,
            "acquiredSkills": ["HTML5", "CSS3", "JavaScript", "Tailwind CSS"],
            "missingSkills": [
                {"skill": "React & Next.js App Router", "priority": "High", "timeToLearn": "2 Weeks", "estimatedHours": 20},
                {"skill": "PostgreSQL & Prisma ORM", "priority": "High", "timeToLearn": "1.5 Weeks", "estimatedHours": 12},
                {"skill": "Dockerized CI/CD Deployment", "priority": "Medium", "timeToLearn": "1 Week", "estimatedHours": 8}
            ],
            "actionPlan": [
                "Convert static multi-page site into dynamic Next.js components",
                "Connect database persistence with Prisma and PostgreSQL",
                "Deploy on Render or Vercel with automatic GitHub Actions deployment"
            ]
        },
        "cloud": {
            "targetDomain": "Cloud & DevOps Architect",
            "currentReadiness": 65,
            "acquiredSkills": ["Linux CLI", "Git", "Basic Networking"],
            "missingSkills": [
                {"skill": "Docker & Multi-stage Containers", "priority": "High", "timeToLearn": "1.5 Weeks", "estimatedHours": 14},
                {"skill": "Kubernetes Clusters (K8s)", "priority": "High", "timeToLearn": "3 Weeks", "estimatedHours": 24},
                {"skill": "Terraform (IaC)", "priority": "Medium", "timeToLearn": "2 Weeks", "estimatedHours": 15}
            ],
            "actionPlan": [
                "Containerize a multi-tier microservice with Docker Compose",
                "Write Kubernetes manifests (Deployments, Services, Ingress)",
                "Provision cloud infrastructure on AWS using Terraform scripts"
            ]
        }
    }

    selected = track_gaps.get(track.lower(), track_gaps["aiml"])
    return {
        "success": True,
        "studentId": student_id,
        "track": track,
        "analysis": selected
    }

