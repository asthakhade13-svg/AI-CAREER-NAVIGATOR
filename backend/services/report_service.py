import datetime
import logging
from typing import Dict, Any, List, Optional
from services.auth_service import get_db_connection

logger = logging.getLogger(__name__)

TRACK_FOCUS_MAP = {
    "aiml": {
        "focus": "Neural Network Architectures & PyTorch Tensors",
        "next_goals": [
            "Implement a multi-layer perceptron from scratch in NumPy",
            "Fine-tune a lightweight HuggingFace transformer model",
            "Publish your trained model inference demo on HuggingFace Spaces"
        ],
        "key_skill": "Deep Learning & Applied Computer Vision/NLP"
    },
    "uiux": {
        "focus": "High-Fidelity Interactive Prototyping & Design Tokens",
        "next_goals": [
            "Build a full 10-screen mobile design system in Figma",
            "Conduct 3 peer user-testing sessions and map affinity diagrams",
            "Prepare a case study highlighting problem statements & UI iterations"
        ],
        "key_skill": "User Experience Research & Design Systems"
    },
    "cyber": {
        "focus": "Network Defense, Wireshark & OWASP Vulnerability Patching",
        "next_goals": [
            "Complete 3 TryHackMe or HackTheBox defensive challenges",
            "Audit a sample web application for SQLi and XSS vulnerabilities",
            "Write an incident report with recommended firewall configurations"
        ],
        "key_skill": "Threat Modeling & Penetration Testing Basics"
    },
    "webdev": {
        "focus": "Asynchronous Backend Architecture & State Management",
        "next_goals": [
            "Build a responsive Full-Stack application with JWT Authentication",
            "Implement database indexing and query optimization on PostgreSQL/SQLite",
            "Deploy the project to Vercel/Render with automated CI/CD GitHub Actions"
        ],
        "key_skill": "Full-Stack Web Development & Cloud Deployment"
    },
    "cloud": {
        "focus": "Container Orchestration & Terraform Infrastructure as Code",
        "next_goals": [
            "Containerize a multi-service application with Docker Compose",
            "Deploy a microservice cluster using Kubernetes manifests",
            "Set up automated monitoring and alerting with Prometheus/Grafana"
        ],
        "key_skill": "Cloud Architecture & DevOps CI/CD Pipelines"
    },
    "datascience": {
        "focus": "Exploratory Data Analysis & Statistical Hypothesis Testing",
        "next_goals": [
            "Clean and process a messy 100k+ row Kaggle dataset using Pandas",
            "Build an interactive Streamlit dashboard for real-time exploratory charts",
            "Train an ensemble model with hyperparameter tuning using Optuna"
        ],
        "key_skill": "Data Wrangling & Predictive Analytics"
    }
}


def get_weekly_ai_report(student_id: str, track_key: str = "aiml", user_name: str = "Astha") -> Dict[str, Any]:
    track_key = track_key.lower().strip() if track_key else "aiml"
    config = TRACK_FOCUS_MAP.get(track_key, TRACK_FOCUS_MAP["aiml"])
    
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Retrieve weekly goals if any
    cursor.execute("""
    SELECT * FROM weekly_goals WHERE student_id = ? ORDER BY created_at DESC LIMIT 1
    """, (student_id,))
    goal_row = cursor.fetchone()
    
    # Count checkin and study logs in the last 7 days
    seven_days_ago = today - datetime.timedelta(days=7)
    cursor.execute("""
    SELECT COUNT(*) as days_active, SUM(hours_spent) as total_hours
    FROM progress_logs
    WHERE student_id = ? AND log_date >= ?
    """, (student_id, seven_days_ago.isoformat()))
    log_stats = cursor.fetchone()

    cursor.execute("""
    SELECT SUM(hours_spent) as total_study_hours
    FROM study_logs
    WHERE student_id = ? AND log_date >= ?
    """, (student_id, seven_days_ago.isoformat()))
    study_stats = cursor.fetchone()

    cursor.execute("""
    SELECT COUNT(*) as completed_milestones
    FROM milestones_progress
    WHERE student_id = ? AND is_completed = 1
    """, (student_id,))
    milestone_stats = cursor.fetchone()
    conn.close()

    active_days = (log_stats["days_active"] if log_stats and log_stats["days_active"] else 0)
    prog_hours = float(log_stats["total_hours"] or 0) if log_stats else 0.0
    study_hours = float(study_stats["total_study_hours"] or 0) if study_stats else 0.0
    logged_hours = round(prog_hours + study_hours, 1)
    milestones_done = int(milestone_stats["completed_milestones"]) if milestone_stats and milestone_stats["completed_milestones"] is not None else 0

    target_hours = goal_row["target_hours"] if goal_row else 10.0
    target_milestones = goal_row["target_milestones"] if goal_row else 3
    pace_percentage = min(100, int((logged_hours / max(1.0, target_hours)) * 100))

    if logged_hours > 0 or milestones_done > 0:
        digest_text = (
            f"Great work this week, {user_name}! You completed {logged_hours} hours of focused "
            f"learning in the {track_key.upper()} track ({milestones_done} milestones completed). "
            f"Keep up daily practice to maintain steady momentum toward placement readiness."
        )
        strengths_list = [
            f"Active learning sessions ({active_days} out of 7 days active)",
            f"Building core {config['key_skill']} competencies",
            "Progressing on structured learning track"
        ]
    else:
        digest_text = (
            f"Welcome to your learning journey, {user_name}! Your personalized {track_key.upper()} curriculum is ready. "
            f"Begin by exploring your milestone topics, logging study sessions, and completing practice challenges."
        )
        strengths_list = [
            "Account setup complete and career track active",
            "Structured curriculum roadmap available",
            "Personalized daily tips and AI mentor ready"
        ]

    return {
        "studentId": student_id,
        "studentName": user_name,
        "trackKey": track_key,
        "reportPeriod": f"{week_start.strftime('%b %d')} - {today.strftime('%b %d, %Y')}",
        "paceIndex": f"{pace_percentage}%",
        "streakDays": active_days,
        "hoursLearnedThisWeek": logged_hours,
        "targetHours": target_hours,
        "milestonesAchieved": milestones_done,
        "targetMilestones": target_milestones,
        "velocityGrade": "A+ Elite Pace" if pace_percentage >= 80 else ("B+ Steady Momentum" if pace_percentage >= 40 else "Getting Started 🌱"),
        "currentFocus": config["focus"],
        "aiDigest": digest_text,
        "strengths": strengths_list,
        "growthAreas": [
            "Deepen hands-on project documentation and Git commit hygiene",
            "Practice explaining your architectural trade-offs in technical mock sessions"
        ],
        "recommendedGoals": config["next_goals"]
    }


def save_weekly_goals(
    student_id: str,
    target_hours: float,
    target_milestones: int,
    focus_topic: str
) -> Dict[str, Any]:
    today = datetime.date.today()
    week_start = (today - datetime.timedelta(days=today.weekday())).isoformat()
    goal_id = f"goal_{student_id}_{week_start}"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO weekly_goals (
        id, student_id, target_hours, target_milestones, focus_topic, week_start_date
    ) VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        target_hours = excluded.target_hours,
        target_milestones = excluded.target_milestones,
        focus_topic = excluded.focus_topic
    """, (
        goal_id,
        student_id,
        target_hours,
        target_milestones,
        focus_topic,
        week_start
    ))
    conn.commit()

    cursor.execute("SELECT * FROM weekly_goals WHERE id = ?", (goal_id,))
    row = cursor.fetchone()
    conn.close()

    return {
        "goalId": row["id"],
        "studentId": row["student_id"],
        "targetHours": row["target_hours"],
        "targetMilestones": row["target_milestones"],
        "focusTopic": row["focus_topic"],
        "weekStartDate": row["week_start_date"],
        "status": row["status"]
    }
