from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter()

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
    include_live: bool = Query(True, description="Include live scraped RSS feed openings")
):
    """
    Returns list of curated and live-scraped internship openings with filtering.
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


