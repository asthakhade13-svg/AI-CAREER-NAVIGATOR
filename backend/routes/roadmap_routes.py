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


@router.get("/export-syllabus-pdf/{track_key}")
@router.get("/syllabus/{track_key}")
def export_track_syllabus_pdf(track_key: str = "aiml"):
    """
    Generates a comprehensive, printable multi-page curriculum and syllabus PDF
    covering weekly phases, learning outcomes, capstones, and industry tools.
    """
    from fastapi.responses import HTMLResponse

    track_syllabi = {
        "aiml": {
            "title": "Artificial Intelligence & Machine Learning Specialization",
            "duration": "12 Months (Paced / Intensive)",
            "level": "Undergraduate to Production ML Engineer",
            "overview": "Master foundational mathematics, statistical modeling, supervised/unsupervised machine learning, deep neural networks, computer vision, natural language processing, and scalable LLM/RAG system deployment.",
            "phases": [
                {"week": "Weeks 1–4", "topic": "Python Programming & Computational Foundations", "items": "Object-Oriented Programming, NumPy arrays, vectorized operations, Pandas DataFrame wrangling, Matplotlib & Seaborn visualization."},
                {"week": "Weeks 5–8", "topic": "Mathematics & Statistical Inference for AI", "items": "Multivariate calculus, gradients & Jacobians, linear algebra, matrix decompositions (SVD, PCA), probability distributions, Bayes rule."},
                {"week": "Weeks 9–14", "topic": "Classical Machine Learning Algorithms", "items": "Linear & logistic regression, decision trees, Random Forests, XGBoost/LightGBM, SVMs, k-Means clustering, cross-validation & hyperparameter tuning."},
                {"week": "Weeks 15–22", "topic": "Deep Learning & Neural Architectures", "items": "PyTorch framework, backpropagation, CNNs for computer vision, RNNs/LSTMs, Transformer attention mechanisms, transfer learning."},
                {"week": "Weeks 23–30", "topic": "Generative AI, Large Language Models & RAG", "items": "Hugging Face transformers, LangChain/LlamaIndex, dense vector embeddings (FAISS/ChromaDB), RAG architectures, prompt engineering."},
                {"week": "Weeks 31–36", "topic": "MLOps, Model Serving & Portfolio Capstone", "items": "FastAPI model deployment, Docker containerization, ONNX runtime optimization, Prometheus latency monitoring, end-to-end cloud build."}
            ],
            "capstones": [
                "Autonomous Multi-Document RAG Knowledge Engine with FAISS & LangChain",
                "Real-Time Object Detection & Tracking with PyTorch & YOLOv8",
                "High-Frequency Algorithmic Market Forecasting Model with XGBoost"
            ],
            "tools": ["Python 3.11+", "PyTorch", "Scikit-Learn", "FastAPI", "FAISS", "Docker", "Git/GitHub", "Hugging Face"]
        },
        "webdev": {
            "title": "Full-Stack Web Development & Cloud Architecture",
            "duration": "6 Months (Intensive Bootcamp Pace)",
            "level": "Frontend, Backend & Systems Deployment",
            "overview": "Comprehensive curriculum covering modern semantic HTML5, CSS3/Tailwind, JavaScript ES6+, React 18 component architecture, Node.js/Express REST APIs, PostgreSQL database design, and CI/CD cloud deployment.",
            "phases": [
                {"week": "Weeks 1–3", "topic": "Modern Web Foundations & Responsive UI", "items": "Semantic HTML5, CSS Grid & Flexbox layouts, responsive design, CSS variables, accessibility (a11y), Git & GitHub collaboration."},
                {"week": "Weeks 4–7", "topic": "JavaScript Deep Dive & DOM Engineering", "items": "Closures, prototypes, async/await, Fetch API, DOM manipulation, ES6+ modules, local storage, event loop & memory model."},
                {"week": "Weeks 8–12", "topic": "React.js Framework & State Management", "items": "Component composition, React hooks (useState, useEffect, useMemo), React Router v6, context API, Redux Toolkit, clean UI design."},
                {"week": "Weeks 13–16", "topic": "Backend APIs with Node.js & Express", "items": "RESTful API design, Express middleware, JWT token authentication, bcrypt password hashing, input validation & error handling."},
                {"week": "Weeks 17–20", "topic": "Database Architecture & ORMs", "items": "Relational SQL (PostgreSQL/MySQL), table schemas, complex joins, indexing, Prisma/Mongoose ORM, database migrations."},
                {"week": "Weeks 21–24", "topic": "Production Deployment & Security Hardening", "items": "Docker containers, automated CI/CD GitHub Actions, NGINX reverse proxy, Redis caching, rate limiting, Vercel/Render deployment."}
            ],
            "capstones": [
                "Real-Time Collaborative Project Management Workspace with WebSockets",
                "Scalable E-Commerce API with Stripe Payments & Redis Caching",
                "Developer Social Network with Markdown Blogging & GitHub OAuth"
            ],
            "tools": ["JavaScript / TypeScript", "React.js", "Node.js & Express", "PostgreSQL", "Docker", "Tailwind CSS", "Redis", "Vercel"]
        },
        "uiux": {
            "title": "UI/UX Design & Digital Product Strategy Specialization",
            "duration": "6 Months (Design Thinking to Production Design Systems)",
            "level": "User Research, Interactive Prototyping & Figma Mastery",
            "overview": "Develop industry-standard product design skills including user interviews, empathy mapping, wireframing, high-fidelity auto-layout in Figma, design tokens, usability testing, and cross-functional developer handoff.",
            "phases": [
                {"week": "Weeks 1–3", "topic": "Design Thinking & User Research Methods", "items": "User interviews, persona creation, empathy mapping, qualitative research synthesis, user journey mapping, problem statement formulation."},
                {"week": "Weeks 4–7", "topic": "Information Architecture & Wireframing", "items": "Sitemaps, card sorting, low-fidelity wireframes, user flow diagrams, visual hierarchy, mobile-first information structuring."},
                {"week": "Weeks 8–12", "topic": "Figma Mastery & Advanced Prototyping", "items": "Auto-layout 5.0, components & variants, interactive component states, micro-interactions, smart animate, responsive constraints."},
                {"week": "Weeks 13–16", "topic": "Enterprise Design Systems & UI Kits", "items": "Color theory, WCAG 2.1 contrast compliance, typography scales, spacing grids, design tokens, component library architecture."},
                {"week": "Weeks 17–20", "topic": "Usability Testing & Iterative Validation", "items": "Moderated & unmoderated user tests, heatmaps, task success metrics, A/B variant testing, heuristic evaluation."},
                {"week": "Weeks 21–24", "topic": "Developer Handoff & Portfolio Case Studies", "items": "Design specs, CSS/Tailwind translation, design token export, crafting comprehensive Behance/Dribbble case studies."}
            ],
            "capstones": [
                "Fintech Mobile Banking App with Biometric Auth & Spending Analytics",
                "Healthcare Telemedicine Web Portal with Real-Time Doctor Scheduling",
                "Cross-Platform SaaS Design System with 150+ Accessible Components"
            ],
            "tools": ["Figma", "FigJam", "Miro", "Notion", "Maze Usability Testing", "Adobe Illustrator", "Storybook"]
        },
        "cloud": {
            "title": "Cloud Architecture & DevOps Engineering",
            "duration": "8 Months (Linux, Containers, Kubernetes & AWS)",
            "level": "Cloud Infrastructure & SRE Operations",
            "overview": "Master enterprise infrastructure automation, Linux administration, Docker containerization, Kubernetes cluster orchestration, Terraform Infrastructure as Code (IaC), AWS core services, and automated CI/CD pipelines.",
            "phases": [
                {"week": "Weeks 1–4", "topic": "Linux Systems & Networking Essentials", "items": "Shell scripting, process management, SSH security, DNS, TCP/IP, OSI model, firewall configuration, Git branching strategies."},
                {"week": "Weeks 5–8", "topic": "Docker & Container Architecture", "items": "Dockerfile best practices, multi-stage builds, container networking, volume mounts, Docker Compose multi-service stacks."},
                {"week": "Weeks 9–14", "topic": "Amazon Web Services (AWS) Core Infrastructure", "items": "IAM security policies, EC2 & Auto Scaling, VPC subnets & routing, S3 object storage, RDS database clusters, CloudFront CDN."},
                {"week": "Weeks 15–20", "topic": "Kubernetes Cluster Management & Helm", "items": "Pods, Deployments, StatefulSets, Services, Ingress controllers, ConfigMaps, Secrets, Helm chart packaging, Minikube/EKS."},
                {"week": "Weeks 21–26", "topic": "Infrastructure as Code (Terraform & Ansible)", "items": "Declarative Terraform HCL, state management, reusable modules, automated provisioning, Ansible server configuration."},
                {"week": "Weeks 27–32", "topic": "CI/CD Automation & Observability", "items": "GitHub Actions pipelines, ArgoCD GitOps, Prometheus metrics collection, Grafana dashboards, ELK stack log aggregation."}
            ],
            "capstones": [
                "High-Availability Kubernetes Cluster with Automated Zero-Downtime CI/CD",
                "Terraform AWS Multi-Tier Web Architecture with Auto-Scaling & WAF",
                "Enterprise Monitoring Pipeline with Prometheus, Grafana & PagerDuty"
            ],
            "tools": ["Linux (Ubuntu/RHEL)", "Docker", "Kubernetes", "AWS", "Terraform", "GitHub Actions", "Prometheus", "Grafana"]
        }
    }

    key = track_key.lower().strip()
    curr = track_syllabi.get(key, track_syllabi["aiml"])

    html_phases = "".join([f"""
    <div style="margin-bottom: 20px; page-break-inside: avoid;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 6px; margin-bottom: 8px;">
            <strong style="font-size: 1.05rem; color: #1E293B;">{p['topic']}</strong>
            <span style="font-size: 0.85rem; font-weight: 700; color: #4F46E5; background: #EEF2FF; padding: 2px 10px; border-radius: 12px;">{p['week']}</span>
        </div>
        <p style="font-size: 0.9rem; color: #475569; line-height: 1.6; margin: 0;">{p['items']}</p>
    </div>
    """ for p in curr["phases"]])

    html_capstones = "".join([f"<li style='margin-bottom: 8px; font-size: 0.9rem; color: #334155;'><strong>Project {i+1}:</strong> {c}</li>" for i, c in enumerate(curr["capstones"])])
    html_tools = "".join([f"<span style='display: inline-block; background: #F1F5F9; border: 1px solid #CBD5E1; color: #334155; padding: 4px 12px; border-radius: 16px; font-size: 0.82rem; font-weight: 600; margin: 3px;'>{t}</span>" for t in curr["tools"]])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{curr['title']} - Official Curriculum & Syllabus</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
    <style>
        @page {{ size: A4; margin: 20mm; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1E293B;
            background: #FFFFFF;
            line-height: 1.5;
            padding: 24px;
            max-width: 850px;
            margin: 0 auto;
        }}
        .header-box {{
            border-bottom: 3px solid #4F46E5;
            padding-bottom: 18px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}
        .badge-bar {{
            display: flex;
            gap: 12px;
            margin: 12px 0 18px 0;
        }}
        .badge {{
            font-size: 0.82rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 6px;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
        }}
        .section-title {{
            font-size: 1.15rem;
            font-weight: 800;
            color: #4F46E5;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 28px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="no-print" style="background: #EEF2FF; border: 1px solid #C7D2FE; padding: 14px 20px; border-radius: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <strong style="color: #4338CA; font-size: 0.95rem;">📄 Official Syllabus PDF Ready for Download</strong>
            <p style="margin: 2px 0 0 0; font-size: 0.82rem; color: #475569;">Click the button on the right to save as PDF or print.</p>
        </div>
        <button onclick="window.print()" style="background: #4F46E5; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-print"></i> Save as PDF / Print
        </button>
    </div>

    <div class="header-box">
        <div>
            <div style="font-size: 0.85rem; font-weight: 800; color: #4F46E5; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">
                <i class="fas fa-compass"></i> AI Career Navigator · Official Accreditation Curriculum
            </div>
            <h1 style="font-size: 1.7rem; font-weight: 800; margin: 0; color: #0F172A;">{curr['title']}</h1>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 0.8rem; color: #64748B; display: block;">Academic Year 2026</span>
            <span style="font-size: 0.8rem; font-weight: 700; color: #10B981;">Verified Industry Standard ✓</span>
        </div>
    </div>

    <div class="badge-bar">
        <span class="badge">⏱️ <strong>Duration:</strong> {curr['duration']}</span>
        <span class="badge">🎯 <strong>Target Level:</strong> {curr['level']}</span>
    </div>

    <div class="section-title"><i class="fas fa-bullseye"></i> Executive Curriculum Overview</div>
    <p style="font-size: 0.92rem; color: #334155; line-height: 1.6; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 16px; border-radius: 10px; margin: 0;">
        {curr['overview']}
    </p>

    <div class="section-title"><i class="fas fa-layer-group"></i> Phased Milestone Curriculum</div>
    {html_phases}

    <div class="section-title"><i class="fas fa-laptop-code"></i> Capstone Portfolio Deliverables</div>
    <ul style="padding-left: 20px; margin-top: 6px;">
        {html_capstones}
    </ul>

    <div class="section-title"><i class="fas fa-tools"></i> Production Tools & Frameworks Mastered</div>
    <div style="margin-top: 8px;">
        {html_tools}
    </div>

    <div style="margin-top: 36px; padding-top: 16px; border-top: 1.5px dashed #CBD5E1; display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #64748B;">
        <span>Generated by First-Gen AI Career Navigator</span>
        <span>Accreditation Verification ID: <strong>CN-2026-SYLLABUS-{key.upper()}</strong></span>
    </div>
</body>
</html>"""

    return HTMLResponse(content=html_content)



# ── Granular Roadmap Sub-Milestone Checklist Sync ───────────────────────────
class SubtaskToggleRequest(BaseModel):
    student_id: str = "user_001"
    track_key: str
    subtask_id: str
    subtask_text: Optional[str] = ""
    is_completed: bool = True


@router.post("/subtask/toggle")
def toggle_roadmap_subtask(payload: SubtaskToggleRequest):
    """
    Persists granular subtask / checklist item completion to SQLite roadmap_subtasks.
    """
    from services.auth_service import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    is_comp = 1 if payload.is_completed else 0
    cursor.execute("""
    INSERT INTO roadmap_subtasks (student_id, track_key, subtask_id, subtask_text, is_completed, completed_at)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(student_id, track_key, subtask_id) DO UPDATE SET
        is_completed = excluded.is_completed,
        subtask_text = excluded.subtask_text,
        completed_at = CURRENT_TIMESTAMP
    """, (payload.student_id, payload.track_key, payload.subtask_id, payload.subtask_text, is_comp))

    if payload.is_completed and payload.subtask_text:
        try:
            cursor.execute("""
            INSERT INTO activity_logs (student_id, action_type, title, description, icon, color)
            VALUES (?, 'roadmap_subtask', ?, ?, 'fa-check-circle', 'teal')
            """, (
                payload.student_id, 
                f"Roadmap Item: {payload.subtask_text[:40]}", 
                f"Completed study item in {payload.track_key.upper()} roadmap."
            ))
        except Exception:
            pass

    conn.commit()

    cursor.execute("""
    SELECT subtask_id FROM roadmap_subtasks 
    WHERE student_id = ? AND track_key = ? AND is_completed = 1
    """, (payload.student_id, payload.track_key))
    completed_rows = cursor.fetchall()
    completed_ids = [r["subtask_id"] for r in completed_rows]
    conn.close()

    return {
        "status": 200,
        "success": True,
        "subtaskId": payload.subtask_id,
        "isCompleted": payload.is_completed,
        "completedCount": len(completed_ids),
        "completedIds": completed_ids
    }


class CustomTaskRequest(BaseModel):
    student_id: str = "user_001"
    track_key: str
    subtask_text: str
    milestone_index: Optional[int] = 0
    subtask_id: Optional[str] = None


@router.post("/custom-task")
def add_custom_roadmap_task(payload: CustomTaskRequest):
    """
    Appends a custom personal study goal / subtask to the active career track.
    """
    import time
    from services.auth_service import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    subtask_id = payload.subtask_id or f"custom_{payload.track_key}_{int(time.time() * 1000)}"
    milestone_idx = payload.milestone_index if payload.milestone_index is not None else 0

    cursor.execute("""
    INSERT INTO roadmap_subtasks (student_id, track_key, subtask_id, subtask_text, is_completed, is_custom, milestone_index, completed_at)
    VALUES (?, ?, ?, ?, 0, 1, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(student_id, track_key, subtask_id) DO UPDATE SET
        subtask_text = excluded.subtask_text,
        is_custom = 1,
        milestone_index = excluded.milestone_index
    """, (payload.student_id, payload.track_key, subtask_id, payload.subtask_text, milestone_idx))

    try:
        cursor.execute("""
        INSERT INTO activity_logs (student_id, action_type, title, description, icon, color)
        VALUES (?, 'roadmap_custom_task', ?, ?, 'fa-plus-circle', 'purple')
        """, (
            payload.student_id,
            f"Added Custom Goal: {payload.subtask_text[:35]}",
            f"Added personal study goal in {payload.track_key.upper()} roadmap."
        ))
    except Exception:
        pass

    conn.commit()
    conn.close()

    return {
        "status": 200,
        "success": True,
        "taskId": subtask_id,
        "subtaskId": subtask_id,
        "taskText": payload.subtask_text,
        "milestoneIndex": milestone_idx,
        "trackKey": payload.track_key,
        "message": "Custom task added successfully."
    }


@router.delete("/custom-task/{task_id}")
def delete_custom_roadmap_task(task_id: str, student_id: Optional[str] = None):
    """
    Deletes a custom personal roadmap subtask from SQLite.
    """
    from services.auth_service import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    if student_id:
        cursor.execute("DELETE FROM roadmap_subtasks WHERE subtask_id = ? AND student_id = ?", (task_id, student_id))
    else:
        cursor.execute("DELETE FROM roadmap_subtasks WHERE subtask_id = ?", (task_id,))

    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()

    return {
        "status": 200,
        "success": True,
        "deletedId": task_id,
        "deletedCount": deleted_count,
        "message": "Custom task deleted successfully."
    }


@router.get("/subtasks/{student_id}")
def get_roadmap_subtasks(student_id: str, track_key: Optional[str] = None):
    """
    Retrieves all persisted subtask completion states and custom tasks for a student.
    """
    from services.auth_service import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    if track_key:
        cursor.execute("""
        SELECT subtask_id, is_completed, subtask_text, is_custom, milestone_index, completed_at FROM roadmap_subtasks 
        WHERE student_id = ? AND track_key = ?
        """, (student_id, track_key))
    else:
        cursor.execute("""
        SELECT subtask_id, is_completed, subtask_text, is_custom, milestone_index, completed_at FROM roadmap_subtasks 
        WHERE student_id = ?
        """, (student_id,))

    rows = cursor.fetchall()
    conn.close()

    completed_ids = [r["subtask_id"] for r in rows if r["is_completed"]]
    states = {r["subtask_id"]: bool(r["is_completed"]) for r in rows}
    custom_tasks = [
        {
            "id": r["subtask_id"],
            "subtaskId": r["subtask_id"],
            "text": r["subtask_text"],
            "isCompleted": bool(r["is_completed"]),
            "milestoneIndex": r["milestone_index"] if "milestone_index" in r.keys() and r["milestone_index"] is not None else 0,
            "completedAt": r["completed_at"]
        }
        for r in rows if ("is_custom" in r.keys() and r["is_custom"] == 1)
    ]

    return {
        "status": 200,
        "success": True,
        "studentId": student_id,
        "trackKey": track_key,
        "completedIds": completed_ids,
        "states": states,
        "customTasks": custom_tasks,
        "totalCompleted": len(completed_ids)
    }



