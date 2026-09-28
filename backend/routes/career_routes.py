from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from services.auth_service import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/careers", tags=["Career Paths & Bookmarks"])

class BookmarkRequest(BaseModel):
    student_id: str
    career_id: str
    career_title: str

@router.post("/bookmark")
def toggle_career_bookmark(payload: BookmarkRequest):
    """
    Toggles bookmark state for a career path.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id FROM saved_careers WHERE student_id = ? AND career_id = ?
    """, (payload.student_id, payload.career_id))
    existing = cursor.fetchone()

    is_bookmarked = False
    if existing:
        cursor.execute("""
        DELETE FROM saved_careers WHERE student_id = ? AND career_id = ?
        """, (payload.student_id, payload.career_id))
        is_bookmarked = False
        message = f"Removed '{payload.career_title}' from saved careers"
    else:
        cursor.execute("""
        INSERT INTO saved_careers (student_id, career_id, career_title)
        VALUES (?, ?, ?)
        """, (payload.student_id, payload.career_id, payload.career_title))
        is_bookmarked = True
        message = f"Saved '{payload.career_title}' to your bookmarks"

    conn.commit()
    conn.close()

    return {
        "success": True,
        "isBookmarked": is_bookmarked,
        "careerId": payload.career_id,
        "message": message
    }


@router.get("/saved/{student_id}")
def get_saved_careers(student_id: str):
    """
    Retrieves all bookmarked career paths for a student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM saved_careers WHERE student_id = ? ORDER BY created_at DESC
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()

    saved_list = [
        {
            "id": r["id"],
            "careerId": r["career_id"],
            "careerTitle": r["career_title"],
            "savedAt": r["created_at"]
        }
        for r in rows
    ]

    return {
        "success": True,
        "studentId": student_id,
        "totalSaved": len(saved_list),
        "savedCareers": saved_list
    }


# Career Catalog Repository
CAREER_CATALOG = [
    {
        "id": "aiml",
        "title": "AI & Machine Learning Engineer",
        "domain": "Artificial Intelligence",
        "difficulty": "Intermediate to Advanced",
        "salaryRange": "₹12 - 32 LPA",
        "growthRate": "+38% (High Demand)",
        "description": "Design neural networks, LLM pipelines, and computer vision models using PyTorch, TensorFlow, and Hugging Face.",
        "skills": ["Python", "PyTorch", "TensorFlow", "FastAPI", "NLP", "LLMs", "Docker"],
        "badge": "Hot Track"
    },
    {
        "id": "webdev",
        "title": "Full Stack Web Developer",
        "domain": "Web Development",
        "difficulty": "Beginner to Intermediate",
        "salaryRange": "₹8 - 24 LPA",
        "growthRate": "+24% (Stable)",
        "description": "Build high-performance web applications using React, Next.js, Node.js, and scalable cloud databases.",
        "skills": ["JavaScript", "TypeScript", "React", "Node.js", "PostgreSQL", "Tailwind CSS"],
        "badge": "Popular"
    },
    {
        "id": "cloud",
        "title": "Cloud & DevOps Architect",
        "domain": "Cloud Infrastructure",
        "difficulty": "Intermediate",
        "salaryRange": "₹10 - 28 LPA",
        "growthRate": "+30% (High Demand)",
        "description": "Automate CI/CD pipelines, container orchestration, and serverless architectures with AWS, Kubernetes, and Terraform.",
        "skills": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux"],
        "badge": "In Demand"
    },
    {
        "id": "cyber",
        "title": "Cybersecurity & InfoSec Analyst",
        "domain": "Cybersecurity",
        "difficulty": "Intermediate to Advanced",
        "salaryRange": "₹9 - 26 LPA",
        "growthRate": "+32% (Critical Demand)",
        "description": "Defend networks and infrastructure against threats through ethical hacking, penetration testing, and security auditing.",
        "skills": ["Network Security", "Penetration Testing", "Wireshark", "Cryptography", "Linux"],
        "badge": "High Security"
    },
    {
        "id": "uiux",
        "title": "UI/UX Product Designer",
        "domain": "Design & Product",
        "difficulty": "Beginner to Intermediate",
        "salaryRange": "₹7 - 20 LPA",
        "growthRate": "+20% (Creative)",
        "description": "Create intuitive user journeys, wireframes, high-fidelity prototypes, and design systems with Figma.",
        "skills": ["Figma", "User Research", "Wireframing", "Prototyping", "Design Systems"],
        "badge": "Creative"
    },
    {
        "id": "datascience",
        "title": "Data Scientist & Analytics Lead",
        "domain": "Data & Analytics",
        "difficulty": "Intermediate",
        "salaryRange": "₹10 - 28 LPA",
        "growthRate": "+29% (High Demand)",
        "description": "Derive actionable business intelligence and predictive insights using statistical modeling, Pandas, and PowerBI.",
        "skills": ["Python", "SQL", "Pandas", "Scikit-Learn", "Tableau", "Statistics"],
        "badge": "Data Heavy"
    },
    {
        "id": "web3",
        "title": "Blockchain & Smart Contract Developer",
        "domain": "Web3 & Blockchain",
        "difficulty": "Advanced",
        "salaryRange": "₹14 - 35 LPA",
        "growthRate": "+22% (Emerging)",
        "description": "Develop decentralized applications, ERC protocols, and secure EVM smart contracts using Solidity and Hardhat.",
        "skills": ["Solidity", "EVM", "Hardhat", "Ethers.js", "Web3.js", "Cryptography"],
        "badge": "Emerging"
    }
]


@router.get("/filter")
def filter_careers(
    domain: Optional[str] = Query(None),
    skill: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    Dynamically filters career paths based on domain, required skill, difficulty, or search query.
    """
    results = CAREER_CATALOG

    if domain and domain.lower() != "all":
        results = [c for c in results if domain.lower() in c["domain"].lower() or domain.lower() in c["id"].lower()]

    if skill:
        results = [c for c in results if any(skill.lower() in s.lower() for s in c["skills"])]

    if difficulty and difficulty.lower() != "all":
        results = [c for c in results if difficulty.lower() in c["difficulty"].lower()]

    if search:
        s_term = search.lower()
        results = [
            c for c in results
            if s_term in c["title"].lower()
            or s_term in c["description"].lower()
            or any(s_term in sk.lower() for sk in c["skills"])
        ]

    return {
        "success": True,
        "total": len(results),
        "careers": results
    }

