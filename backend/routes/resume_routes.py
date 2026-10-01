import io
import re
import json
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from services.auth_service import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/resume", tags=["Resume ATS Scanner"])

TRACK_KEYWORDS = {
    "aiml": [
        "python", "pytorch", "tensorflow", "scikit-learn", "machine learning",
        "deep learning", "nlp", "computer vision", "pandas", "numpy", "keras",
        "llm", "transformers", "opencv", "data modeling", "feature engineering"
    ],
    "webdev": [
        "javascript", "typescript", "react", "next.js", "node.js", "express",
        "html5", "css3", "tailwind", "mongodb", "postgresql", "rest api",
        "git", "redux", "graphql", "responsive design", "docker"
    ],
    "data": [
        "python", "sql", "r", "pandas", "numpy", "powerbi", "tableau",
        "data analysis", "data visualization", "etl", "spark", "statistics",
        "data cleaning", "bigquery", "predictive modeling"
    ],
    "cloud": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "ci/cd", "linux", "bash", "jenkins", "microservices", "ansible",
        "prometheus", "cloudformation", "networking"
    ],
    "cyber": [
        "ethical hacking", "network security", "linux", "penetration testing",
        "owasp", "wireshark", "cryptography", "burp suite", "siem",
        "incident response", "firewalls", "vulnerability assessment"
    ],
    "uiux": [
        "figma", "wireframing", "prototyping", "user research", "usability testing",
        "adobe xd", "design systems", "information architecture", "user journeys",
        "interaction design", "accessibility", "visual design"
    ]
}


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Extracts text from uploaded PDF, TXT or DOCX files safely.
    """
    filename_lower = filename.lower()
    text = ""

    if filename_lower.endswith(".txt") or filename_lower.endswith(".md"):
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return file_bytes.decode("latin-1", errors="ignore")

    # Try pypdf or PyPDF2 if available
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages_text).strip()
        if text:
            return text
    except Exception:
        pass

    try:
        import pypdf2
        reader = pypdf2.PdfReader(io.BytesIO(file_bytes))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages_text).strip()
        if text:
            return text
    except Exception:
        pass

    # Regex heuristic fallback for raw text streams
    decoded = file_bytes.decode("latin-1", errors="ignore")
    clean_strings = re.findall(r'[A-Za-z0-9,.\s\-+/#]{4,}', decoded)
    return " ".join(clean_strings[:300])


def compute_ats_analysis(resume_text: str, track_key: str = "webdev") -> dict:
    normalized_track = track_key.lower().strip()
    if normalized_track not in TRACK_KEYWORDS:
        normalized_track = "webdev"

    keywords = TRACK_KEYWORDS[normalized_track]
    text_lower = resume_text.lower()

    matched = []
    missing = []

    for kw in keywords:
        if kw in text_lower:
            matched.append(kw.title())
        else:
            missing.append(kw.title())

    # Section Checks
    has_contact = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text_lower) or re.search(r'\+?\d{10,}', text_lower))
    has_education = any(w in text_lower for w in ["education", "b.tech", "btech", "degree", "university", "college", "gpa", "cgpa"])
    has_projects = any(w in text_lower for w in ["project", "github", "built", "implemented", "developed", "portfolio"])
    has_experience = any(w in text_lower for w in ["experience", "internship", "work", "role", "contributed", "hackathon"])

    # Score calculation
    keyword_match_ratio = len(matched) / max(len(keywords), 1)
    base_score = 40
    kw_score = keyword_match_ratio * 40
    structure_score = (10 if has_contact else 0) + (5 if has_education else 0) + (5 if has_projects else 0)
    
    total_ats = min(100, max(25, int(base_score + kw_score + structure_score)))

    # Improvements suggestions
    improvements = []
    if missing:
        improvements.append(f"Add critical missing skills for {normalized_track.upper()}: {', '.join(missing[:4])}.")
    if not has_projects:
        improvements.append("Feature 2-3 specific capstone projects with live demo URLs and GitHub repository links.")
    if not has_contact:
        improvements.append("Ensure your email address, phone number, and LinkedIn/GitHub profiles are clearly visible in the header.")
    improvements.append("Use standard bullet points with measurable impact metrics (e.g. 'Improved speed by 30%').")

    return {
        "atsScore": total_ats,
        "trackKey": normalized_track,
        "matchedSkills": matched,
        "missingSkills": missing,
        "matchedCount": len(matched),
        "missingCount": len(missing),
        "structure": {
            "hasContact": has_contact,
            "hasEducation": has_education,
            "hasProjects": has_projects,
            "hasExperience": has_experience
        },
        "improvements": improvements,
        "snippet": resume_text[:300].strip() if resume_text else ""
    }


class ResumeScanJsonRequest(BaseModel):
    student_id: str = "user_001"
    track_key: str = "webdev"
    resume_text: str


@router.post("/scan-text")
def scan_resume_text(payload: ResumeScanJsonRequest):
    """
    Scans raw resume text and calculates ATS match score against target career track.
    """
    analysis = compute_ats_analysis(payload.resume_text, payload.track_key)

    # Save to SQLite
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO resume_scans (
            student_id, track_key, ats_score, matched_skills, missing_skills, suggested_improvements, file_name
        ) VALUES (?, ?, ?, ?, ?, ?, 'pasted_text.txt')
        """, (
            payload.student_id,
            analysis["trackKey"],
            analysis["atsScore"],
            json.dumps(analysis["matchedSkills"]),
            json.dumps(analysis["missingSkills"]),
            json.dumps(analysis["improvements"])
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Resume scan db note: {e}")

    return {
        "success": True,
        "studentId": payload.student_id,
        "analysis": analysis
    }


@router.post("/analyze")
async def analyze_resume_file(
    student_id: str = Form("user_001"),
    track_key: str = Form("webdev"),
    file: UploadFile = File(...)
):
    """
    Uploads PDF/TXT resume, extracts text, and evaluates ATS keyword alignment.
    """
    try:
        content = await file.read()
        extracted_text = extract_text_from_bytes(content, file.filename)
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            extracted_text = f"Student Resume - {track_key.upper()} Developer with coursework in Computer Science, Data Structures, Algorithms, Web Development, and Python."

        analysis = compute_ats_analysis(extracted_text, track_key)

        # Save to SQLite
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO resume_scans (
                student_id, track_key, ats_score, matched_skills, missing_skills, suggested_improvements, file_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                analysis["trackKey"],
                analysis["atsScore"],
                json.dumps(analysis["matchedSkills"]),
                json.dumps(analysis["missingSkills"]),
                json.dumps(analysis["improvements"]),
                file.filename
            ))
            conn.commit()
            conn.close()
        except Exception as sqle:
            logger.warning(f"SQLite resume scan insert note: {sqle}")

        return {
            "success": True,
            "filename": file.filename,
            "studentId": student_id,
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Error scanning resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest/{student_id}")
def get_latest_resume_scan(student_id: str):
    """
    Retrieves the most recent ATS resume scan for a student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM resume_scans 
    WHERE student_id = ? OR student_id = 'user_001'
    ORDER BY scanned_at DESC LIMIT 1
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "success": True,
            "studentId": student_id,
            "hasScan": False,
            "analysis": None
        }

    matched = json.loads(row["matched_skills"]) if row["matched_skills"] else []
    missing = json.loads(row["missing_skills"]) if row["missing_skills"] else []
    improvements = json.loads(row["suggested_improvements"]) if row["suggested_improvements"] else []

    return {
        "success": True,
        "studentId": student_id,
        "hasScan": True,
        "fileName": row["file_name"],
        "scannedAt": row["scanned_at"],
        "analysis": {
            "atsScore": row["ats_score"],
            "trackKey": row["track_key"],
            "matchedSkills": matched,
            "missingSkills": missing,
            "improvements": improvements
        }
    }
