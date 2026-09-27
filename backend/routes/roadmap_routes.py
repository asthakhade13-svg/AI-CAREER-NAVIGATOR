from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.roadmap_generator import generate_roadmap

router = APIRouter()


class RoadmapRequest(BaseModel):
    target_domain: str = "Web Development"
    missing_skills: Optional[List[str]] = None
    timeframe: Optional[str] = "6 Months"
    custom_prompt: Optional[str] = None


@router.post("/generate")
async def api_generate_roadmap(request: RoadmapRequest):
    """
    Generate a personalized learning roadmap with milestones, custom prompt, and resources.
    """
    try:
        roadmap = generate_roadmap(
            target_domain=request.target_domain,
            missing_skills=request.missing_skills,
            timeframe=request.timeframe,
            custom_prompt=request.custom_prompt
        )
        return roadmap
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate roadmap.")


@router.get("/export-ics/{track_key}")
def export_roadmap_ics(track_key: str = "aiml"):
    """
    Generates downloadable .ics calendar file containing weekly milestone study schedules.
    """
    from fastapi.responses import Response
    from datetime import datetime, timedelta

    track_names = {
        "aiml": "AI & Machine Learning Engineer",
        "webdev": "Full-Stack Web Development",
        "data": "Data Science & Big Data",
        "cloud": "Cloud Architecture & DevOps",
        "cyber": "Cybersecurity & Ethical Hacking",
        "uiux": "UI/UX Design & Product Strategy"
    }
    track_title = track_names.get(track_key.lower(), "AI Career Track")
    
    start_date = datetime.now() + timedelta(days=1)
    
    milestones = [
        ("Phase 1: Foundations & Core Concepts", 14),
        ("Phase 2: Deep Dive & Framework Implementation", 21),
        ("Phase 3: Real-World Portfolio Project Build", 21),
        ("Phase 4: Capstone Architecture & Deployment", 14),
        ("Phase 5: Technical Mock Interview & Final Verification", 7)
    ]
    
    events = []
    current_dt = start_date

    for title, days in milestones:
        end_dt = current_dt + timedelta(days=days)
        start_str = current_dt.strftime("%Y%m%dT090000Z")
        end_str = end_dt.strftime("%Y%m%dT180000Z")
        now_str = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        
        event = f"""BEGIN:VEVENT
UID:cn-roadmap-{track_key}-{current_dt.strftime("%Y%m%d")}@careernavigator.ai
DTSTAMP:{now_str}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:{track_title} - {title}
DESCRIPTION:Official learning milestone for {track_title}. Focus on scheduled hands-on projects and quizzes on AI Career Navigator.
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT"""
        events.append(event)
        current_dt = end_dt

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI Career Navigator//Student Milestone Scheduler//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:{track_title} Schedule
X-WR-TIMEZONE:UTC
{chr(10).join(events)}
END:VCALENDAR"""

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="CareerNavigator_{track_key}_Schedule.ics"'
        }
    )

