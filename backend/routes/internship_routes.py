from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel
import re
import json

router = APIRouter()

def parse_stipend_amount(stipend_str: str) -> int:
    """
    Extracts monthly stipend value in INR from strings like:
    '₹1,10,000 / month' -> 110000
    '₹25,000 / month + Research Grant' -> 25000
    '$3,500 / month (₹2,90,000)' -> 290000
    """
    if not stipend_str:
        return 0
    # Match Rupee amount first
    m_inr = re.search(r'₹\s*([0-9,]+)', stipend_str)
    if m_inr:
        try:
            return int(m_inr.group(1).replace(',', ''))
        except Exception:
            pass
    # Match Dollar amount and approximate to INR (1 USD ~ 83 INR)
    m_usd = re.search(r'\$\s*([0-9,]+)', stipend_str)
    if m_usd:
        try:
            return int(m_usd.group(1).replace(',', '')) * 83
        except Exception:
            pass
    # Match any raw numeric sequence
    digits = re.findall(r'\d+', stipend_str.replace(',', ''))
    if digits:
        try:
            return int(digits[0])
        except Exception:
            pass
    return 0

class InternshipItem(BaseModel):
    id: str
    company: str
    logo: str
    logo_bg: str
    logo_color: str
    title: str
    role_type: str
    track: str
    location: str
    stipend: str
    eligibility: str
    deadline: str
    status: str
    description: str
    skills: List[str]
    apply_url: str

ALL_INTERNSHIPS: List[dict] = [
    {
        "id": "google-step-2027",
        "company": "Google",
        "logo": "G",
        "logo_bg": "#EA4335",
        "logo_color": "#FFFFFF",
        "title": "Google STEP Intern (Summer 2027)",
        "role_type": "Software Engineering & UI",
        "track": "webdev",
        "location": "Bangalore / Hyderabad / Remote",
        "stipend": "₹1,10,000 / month",
        "eligibility": "1st & 2nd Year CS/IT Students",
        "deadline": "Rolling (Apply Early)",
        "status": "Open",
        "description": "Student Training in Engineering Program (STEP) is a 12-week development internship focusing on scalable software systems, design algorithms, and 1:1 mentorship from Google engineers.",
        "skills": ["Data Structures", "Python/C++", "System Basics", "Problem Solving"],
        "apply_url": "https://careers.google.com/students/"
    },
    {
        "id": "microsoft-engage-2026",
        "company": "Microsoft",
        "logo": "M",
        "logo_bg": "#00A4EF",
        "logo_color": "#FFFFFF",
        "title": "Microsoft Engage Mentorship & Fellowship",
        "role_type": "Full Stack & Cloud",
        "track": "cloud",
        "location": "Virtual / Hyderabad / Noida",
        "stipend": "₹1,25,000 / month",
        "eligibility": "1st, 2nd & 3rd Year B.Tech Students",
        "deadline": "Open for 2026 Batch",
        "status": "Open",
        "description": "Engage is a direct project-based mentorship program by Microsoft engineers where you build cloud solutions, AI apps, and qualify for fast-track internship interview rounds.",
        "skills": ["React", "Azure / Cloud Basics", "Git & GitHub", "API Design"],
        "apply_url": "https://careers.microsoft.com/students/us/en"
    },
    {
        "id": "figma-ux-fellowship",
        "company": "Figma",
        "logo": "F",
        "logo_bg": "#A259FF",
        "logo_color": "#FFFFFF",
        "title": "Figma UX Design & Product Fellowship",
        "role_type": "Product & UI/UX Design",
        "track": "uiux",
        "location": "Remote / Global",
        "stipend": "$3,500 / month (₹2,90,000)",
        "eligibility": "All college students interested in UI/UX & Design Systems",
        "deadline": "Limited Seats",
        "status": "Featured",
        "description": "Work alongside Figma design advocates and product managers to create community design systems, prototype interactive design challenges, and master auto layout.",
        "skills": ["Figma Mastery", "Design Systems", "User Research", "Interactive Prototyping"],
        "apply_url": "https://www.figma.com/careers/"
    },
    {
        "id": "amazon-sde-intern",
        "company": "Amazon",
        "logo": "A",
        "logo_bg": "#FF9900",
        "logo_color": "#FFFFFF",
        "title": "Amazon SDE / Frontend Intern",
        "role_type": "Backend & Cloud Dev",
        "track": "webdev",
        "location": "Bangalore / Hyderabad / Chennai",
        "stipend": "₹1,15,000 / month",
        "eligibility": "1st to 4th Year B.Tech Students",
        "deadline": "Closing Soon",
        "status": "Closing",
        "description": "Develop high-performance customer-facing services, AWS cloud integrations, and intuitive internal tools used by millions across Amazon operations worldwide.",
        "skills": ["Java / Python / JS", "AWS Services", "Object Oriented Design", "Data Structures"],
        "apply_url": "https://www.amazon.jobs/en/teams/internships-for-students"
    },
    {
        "id": "isro-ai-research",
        "company": "ISRO / DRDO",
        "logo": "I",
        "logo_bg": "#0D9488",
        "logo_color": "#FFFFFF",
        "title": "ISRO AI & Satellite Vision Intern",
        "role_type": "Computer Vision & ML",
        "track": "aiml",
        "location": "Bengaluru / Ahmedabad / Hybrid",
        "stipend": "₹25,000 / month + Research Grant",
        "eligibility": "2nd & 3rd Year B.Tech Students",
        "deadline": "Next Month",
        "status": "Open",
        "description": "Work on satellite imagery processing, deep learning object detection algorithms, and geospatial data analytics alongside senior scientists.",
        "skills": ["PyTorch / TensorFlow", "Computer Vision", "Python", "NumPy & Pandas"],
        "apply_url": "https://www.isro.gov.in/Careers.html"
    },
    {
        "id": "crowdstrike-cyber-intern",
        "company": "CrowdStrike",
        "logo": "C",
        "logo_bg": "#DC2626",
        "logo_color": "#FFFFFF",
        "title": "CrowdStrike Security Analyst Intern",
        "role_type": "Threat Hunting & Security Ops",
        "track": "cyber",
        "location": "Pune / Remote",
        "stipend": "₹80,000 / month",
        "eligibility": "B.Tech Students with Linux & Networking knowledge",
        "deadline": "Active",
        "status": "Open",
        "description": "Analyze real-time endpoint telemetry, triage malware samples, investigate threat intelligence indicators, and build automated security response playbooks.",
        "skills": ["Linux Shell", "Networking (TCP/IP)", "Python Scripting", "SOC Fundamentals"],
        "apply_url": "https://www.crowdstrike.com/careers/"
    }
]

from services.internship_scraper import scrape_live_rss_internships

_LIVE_CACHE: List[dict] = []

@router.get("/list")
@router.get("/listings")
def get_internships(
    track: Optional[str] = Query(None, description="Filter by track: uiux, aiml, cyber, webdev, cloud, data, all"),
    search: Optional[str] = Query(None, description="Keyword search"),
    include_live: bool = Query(True, description="Include live scraped RSS feed openings"),
    remote: Optional[bool] = Query(None, description="Filter remote or virtual openings"),
    min_stipend: Optional[int] = Query(None, description="Filter by minimum monthly stipend in INR"),
    location: Optional[str] = Query(None, description="Filter by location keyword (e.g. Bangalore, Remote, Pune)")
):
    """
    Returns list of curated and live-scraped internship openings with filtering.
    Supports track, search, remote only, minimum monthly stipend (INR), and location keyword.
    """
    global _LIVE_CACHE
    if include_live and not _LIVE_CACHE:
        try:
            _LIVE_CACHE = scrape_live_rss_internships()
        except Exception:
            _LIVE_CACHE = []

    results = list(ALL_INTERNSHIPS) + list(_LIVE_CACHE)

    if track and track != "all":
        results = [i for i in results if i["track"] == track or track in i["role_type"].lower()]

    if search:
        s = search.lower()
        results = [
            i for i in results
            if s in i["title"].lower() or s in i["company"].lower() or any(s in sk.lower() for sk in i.get("skills", [])) or s in i.get("description", "").lower()
        ]

    if remote is True:
        results = [
            i for i in results
            if "remote" in (i.get("location") or "").lower() or "virtual" in (i.get("location") or "").lower()
        ]

    if min_stipend is not None and min_stipend > 0:
        results = [
            i for i in results
            if parse_stipend_amount(i.get("stipend", "")) >= min_stipend
        ]

    if location and location.lower() != "all":
        loc_str = location.lower().strip()
        results = [
            i for i in results
            if loc_str in (i.get("location") or "").lower()
        ]

    return {
        "status": 200,
        "total": len(results),
        "curatedCount": len(ALL_INTERNSHIPS),
        "liveScrapedCount": len(_LIVE_CACHE),
        "internships": results
    }


@router.post("/refresh-live")
def refresh_live_internships():
    """
    Forces a background re-scrape of live tech RSS feeds and updates in-memory cache.
    """
    global _LIVE_CACHE
    _LIVE_CACHE = scrape_live_rss_internships()
    return {
        "status": 200,
        "success": True,
        "message": f"Successfully scraped {len(_LIVE_CACHE)} live tech internship openings",
        "liveCount": len(_LIVE_CACHE),
        "scrapedItems": _LIVE_CACHE
    }


@router.get("/live-feed")
def get_live_feed():
    """
    Returns exclusively the real-time live scraped tech openings.
    """
    global _LIVE_CACHE
    if not _LIVE_CACHE:
        _LIVE_CACHE = scrape_live_rss_internships()
    return {
        "status": 200,
        "success": True,
        "total": len(_LIVE_CACHE),
        "openings": _LIVE_CACHE
    }


@router.get("/{internship_id}")
def get_internship_detail(internship_id: str):
    """
    Returns full details for a single internship (checks both curated and live cache).
    """
    all_combined = list(ALL_INTERNSHIPS) + list(_LIVE_CACHE)
    for item in all_combined:
        if item["id"] == internship_id:
            return {"status": 200, "internship": item}
    return {"status": 404, "message": "Internship not found"}


# ── 3. Internship Bookmarks & Application Pipeline Tracker ──────────────────
from services.auth_service import get_db_connection

class InternshipBookmarkRequest(BaseModel):
    student_id: str = "user_001"
    internship_id: str
    title: str
    company: Optional[str] = ""
    track: Optional[str] = ""
    location: Optional[str] = ""
    stipend: Optional[str] = ""
    apply_url: Optional[str] = ""

class InternshipApplyStatusRequest(BaseModel):
    student_id: str = "user_001"
    internship_id: str
    company: str
    role_title: str
    status: Optional[str] = "Applied"
    notes: Optional[str] = ""


@router.post("/bookmark")
def toggle_internship_bookmark(payload: InternshipBookmarkRequest):
    """
    Toggles bookmark/saved state for an internship opportunity in SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM saved_internships WHERE student_id = ? AND internship_id = ?", (payload.student_id, payload.internship_id))
    existing = cursor.fetchone()

    is_saved = False
    if existing:
        cursor.execute("DELETE FROM saved_internships WHERE student_id = ? AND internship_id = ?", (payload.student_id, payload.internship_id))
        is_saved = False
        message = f"Removed '{payload.title}' from saved internships"
    else:
        cursor.execute("""
        INSERT INTO saved_internships (student_id, internship_id, title, company, track, location, stipend, apply_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (payload.student_id, payload.internship_id, payload.title, payload.company or "", payload.track or "", payload.location or "", payload.stipend or "", payload.apply_url or ""))
        is_saved = True
        message = f"Saved '{payload.title}' to your bookmarks"

    conn.commit()
    conn.close()

    return {
        "success": True,
        "isSaved": is_saved,
        "internshipId": payload.internship_id,
        "message": message
    }


@router.get("/saved/{student_id}")
def get_saved_internships(student_id: str):
    """
    Retrieves all bookmarked internships for a student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_internships WHERE student_id = ? ORDER BY saved_at DESC", (student_id,))
    rows = cursor.fetchall()
    conn.close()

    saved_list = [
        {
            "id": r["id"],
            "internshipId": r["internship_id"],
            "title": r["title"],
            "company": r["company"],
            "track": r["track"],
            "location": r["location"],
            "stipend": r["stipend"],
            "applyUrl": r["apply_url"],
            "savedAt": r["saved_at"]
        }
        for r in rows
    ]

    return {
        "success": True,
        "studentId": student_id,
        "total": len(saved_list),
        "savedInternships": saved_list
    }


@router.post("/apply-status")
def update_internship_apply_status(payload: InternshipApplyStatusRequest):
    """
    Updates or inserts student internship application pipeline tracking status (Applied, Interviewing, Offered, Rejected).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO internship_applications (student_id, internship_id, company, role_title, status, notes, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(student_id, internship_id) DO UPDATE SET
        company = excluded.company,
        role_title = excluded.role_title,
        status = excluded.status,
        notes = excluded.notes,
        updated_at = CURRENT_TIMESTAMP
    """, (payload.student_id, payload.internship_id, payload.company, payload.role_title, payload.status or "Applied", payload.notes or ""))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "studentId": payload.student_id,
        "internshipId": payload.internship_id,
        "status": payload.status,
        "message": f"Application status updated to '{payload.status}' for {payload.company}"
    }


@router.get("/my-applications/{student_id}")
@router.get("/applications/{student_id}")
def get_student_applications(student_id: str):
    """
    Retrieves all tracked internship applications for a student.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM internship_applications WHERE student_id = ? ORDER BY updated_at DESC", (student_id,))
    rows = cursor.fetchall()
    conn.close()

    apps = [
        {
            "id": r["id"],
            "internshipId": r["internship_id"],
            "company": r["company"],
            "roleTitle": r["role_title"],
            "status": r["status"],
            "notes": r["notes"],
            "appliedDate": r["applied_date"],
            "updatedAt": r["updated_at"]
        }
        for r in rows
    ]

    return {
        "success": True,
        "studentId": student_id,
        "total": len(apps),
        "applications": apps
    }


# ── 4. 1-Click Application Modal & AI Cover Letter Generator ────────────────
class CoverLetterRequest(BaseModel):
    student_id: str = "user_001"
    internship_id: str
    company: str
    role_title: str
    skills: Optional[List[str]] = []
    resume_summary: Optional[str] = ""
    student_name: Optional[str] = ""
    tone: Optional[str] = "Professional"

class OneClickApplyRequest(BaseModel):
    student_id: str = "user_001"
    internship_id: str
    company: str
    role_title: str
    status: Optional[str] = "Applied"
    resume_file: Optional[str] = ""
    cover_letter: Optional[str] = ""
    notes: Optional[str] = ""


@router.get("/resumes/{student_id}")
def get_student_resumes(student_id: str):
    """
    Retrieves the student's ATS-scanned resumes from SQLite for 1-click application selection.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, file_name, track_key, ats_score, matched_skills, scanned_at
    FROM resume_scans
    WHERE student_id = ? OR student_id = 'user_001'
    ORDER BY scanned_at DESC LIMIT 5
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()

    resumes = []
    for r in rows:
        matched = []
        try:
            if r["matched_skills"]:
                matched = json.loads(r["matched_skills"])
        except Exception:
            pass

        resumes.append({
            "id": r["id"],
            "fileName": r["file_name"] or "Tech_Resume.pdf",
            "trackKey": r["track_key"],
            "atsScore": r["ats_score"],
            "matchedSkills": matched,
            "scannedAt": r["scanned_at"]
        })

    # Default fallback resume if student has not yet run ATS scanner
    if not resumes:
        clean_name = student_id.split("@")[0].replace(".", "_").capitalize()
        resumes.append({
            "id": 1,
            "fileName": f"{clean_name}_Tech_Resume_2026.pdf",
            "trackKey": "webdev",
            "atsScore": 84,
            "matchedSkills": ["Python", "JavaScript", "React", "Data Structures"],
            "scannedAt": "Recently Verified"
        })

    return {
        "success": True,
        "studentId": student_id,
        "resumes": resumes
    }


@router.post("/generate-cover-letter")
def generate_cover_letter(payload: CoverLetterRequest):
    """
    Auto-generates a tailored 1-paragraph AI cover letter matching the role's keywords,
    company background, and the student's ATS-scanned resume strengths.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    student_name = payload.student_name
    if not student_name:
        cursor.execute("SELECT full_name FROM users WHERE id = ? OR LOWER(email) = LOWER(?)", (payload.student_id, payload.student_id))
        user_row = cursor.fetchone()
        student_name = user_row["full_name"] if user_row else "Astha Khade"

    cursor.execute("""
    SELECT file_name, ats_score, matched_skills
    FROM resume_scans
    WHERE student_id = ? OR student_id = 'user_001'
    ORDER BY scanned_at DESC LIMIT 1
    """, (payload.student_id,))
    scan_row = cursor.fetchone()
    conn.close()

    ats_score = scan_row["ats_score"] if scan_row else 85
    resume_file = scan_row["file_name"] if scan_row else f"{student_name.split()[0]}_Resume.pdf"

    role_skills = payload.skills or ["Software Engineering", "System Design", "Problem Solving"]
    skills_highlight = ", ".join(role_skills[:3]) if role_skills else "Software Engineering"
    primary_skill = role_skills[0] if role_skills else "software engineering"

    cover_letter = (
        f"Dear Hiring Team at {payload.company},\n\n"
        f"I am writing to express my strong enthusiasm for the {payload.role_title} position. "
        f"As an aspiring software engineer with hands-on technical proficiency in {skills_highlight} "
        f"and an ATS-optimized academic portfolio (ATS Score: {ats_score}/100 on {resume_file}), I have developed robust problem-solving "
        f"foundations through production-grade projects and algorithmic challenges. I have closely followed {payload.company}'s "
        f"impact in tech and am eager to apply my practical skills in {primary_skill} to build scalable, high-quality features "
        f"while actively learning from your world-class engineering team. Thank you for your consideration—I welcome the opportunity "
        f"to bring my dedication, fast learning agility, and collaborative drive to {payload.company} this term."
    )

    return {
        "success": True,
        "studentId": payload.student_id,
        "studentName": student_name,
        "company": payload.company,
        "roleTitle": payload.role_title,
        "atsScore": ats_score,
        "resumeFile": resume_file,
        "matchedKeywords": role_skills,
        "coverLetter": cover_letter
    }


@router.post("/apply-one-click")
def apply_one_click(payload: OneClickApplyRequest):
    """
    Submits a 1-click application, bundling the ATS resume and AI cover letter,
    and recording the pipeline status (Applied, Under Review, or Interview Scheduled) in SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    valid_statuses = ["Applied", "Under Review", "Interview Scheduled", "Interviewing", "Offered", "Rejected"]
    status_to_record = payload.status if payload.status in valid_statuses else "Applied"

    full_notes = payload.notes or ""
    if payload.resume_file:
        full_notes = f"[Resume Attached: {payload.resume_file}]\n{full_notes}".strip()
    if payload.cover_letter:
        full_notes = f"{full_notes}\n[AI Cover Letter]:\n{payload.cover_letter}".strip()

    cursor.execute("""
    INSERT INTO internship_applications (student_id, internship_id, company, role_title, status, notes, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(student_id, internship_id) DO UPDATE SET
        company = excluded.company,
        role_title = excluded.role_title,
        status = excluded.status,
        notes = excluded.notes,
        updated_at = CURRENT_TIMESTAMP
    """, (
        payload.student_id,
        payload.internship_id,
        payload.company,
        payload.role_title,
        status_to_record,
        full_notes
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "studentId": payload.student_id,
        "internshipId": payload.internship_id,
        "company": payload.company,
        "roleTitle": payload.role_title,
        "status": status_to_record,
        "resumeFile": payload.resume_file,
        "message": f"1-Click Application recorded with status '{status_to_record}' for {payload.company}."
    }



