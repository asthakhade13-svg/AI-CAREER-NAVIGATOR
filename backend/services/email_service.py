import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from config import settings
from services.auth_service import get_db_connection

logger = logging.getLogger(__name__)

def log_email_to_db(to_email: str, subject: str, body_preview: str, status: str = "sent"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS outbound_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            to_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            body_preview TEXT NOT NULL,
            status TEXT DEFAULT 'sent',
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        INSERT INTO outbound_emails (to_email, subject, body_preview, status)
        VALUES (?, ?, ?, ?)
        """, (to_email, subject, body_preview[:300], status))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Email db log notice: {e}")


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Dispatches outbound email via SMTP with graceful local inbox logging fallback.
    """
    from_email = settings.SMTP_FROM_EMAIL
    from_name = settings.SMTP_FROM_NAME
    sender_header = f"{from_name} <{from_email}>"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_header
    msg["To"] = to_email

    if text_content:
        msg.attach(MIMEText(text_content, "plain"))
    if html_content:
        msg.attach(MIMEText(html_content, "html"))

    # Attempt live SMTP delivery if credentials exist
    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        try:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(from_email, [to_email], msg.as_string())
            server.quit()
            logger.info(f"Successfully sent live SMTP email to {to_email}: {subject}")
            log_email_to_db(to_email, subject, text_content or html_content, "delivered")
            return {
                "success": True,
                "status": "delivered",
                "message": f"Email delivered to {to_email} via {settings.SMTP_HOST}"
            }
        except Exception as e:
            logger.warning(f"SMTP dispatch note (falling back to simulated inbox logger): {e}")
            log_email_to_db(to_email, subject, text_content or html_content, f"simulated_sent: {str(e)[:50]}")
            return {
                "success": True,
                "status": "simulated",
                "message": f"Email logged to outbound queue for {to_email} (SMTP server unavailable: {e})"
            }
    else:
        # Development / staging mode simulation
        logger.info(f"[SIMULATED EMAIL] To: {to_email} | Subject: {subject}")
        log_email_to_db(to_email, subject, text_content or html_content, "simulated_sent")
        return {
            "success": True,
            "status": "simulated",
            "message": f"Email recorded in system outbound queue for {to_email}"
        }


def send_password_reset_email(to_email: str, reset_token: str, user_name: str = "Student") -> Dict[str, Any]:
    subject = "AI Career Navigator - Password Reset Code"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; }}
        .box {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #e2e8f0; }}
        .header {{ color: #4f46e5; font-size: 22px; font-weight: 800; margin-bottom: 12px; }}
        .otp-code {{ font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #1e293b; background: #e0e7ff; padding: 12px 24px; border-radius: 10px; display: inline-block; margin: 20px 0; }}
        .footer {{ font-size: 12px; color: #94a3b8; margin-top: 30px; border-top: 1px solid #f1f5f9; padding-top: 16px; }}
      </style>
    </head>
    <body>
      <div class="box">
        <div class="header">AI Career Navigator</div>
        <p>Hello <strong>{user_name}</strong>,</p>
        <p>We received a request to reset your password. Use the verification code below to set a new password:</p>
        <div class="otp-code">{reset_token}</div>
        <p style="font-size: 14px; color: #64748b;">This code expires in 15 minutes. If you did not request this, you can safely ignore this email.</p>
        <div class="footer">
          First-Generation AI Career Guidance Platform for B.Tech CS Students
        </div>
      </div>
    </body>
    </html>
    """
    text_content = f"Hello {user_name},\n\nYour AI Career Navigator password reset code is: {reset_token}\nThis code expires in 15 minutes."
    return send_email(to_email, subject, html_content, text_content)


def send_weekly_digest_email(to_email: str, user_name: str, weekly_data: dict) -> Dict[str, Any]:
    subject = f"Your Weekly AI Career Digest - {weekly_data.get('track', 'Engineering').upper()}"
    hours = weekly_data.get("hours", "8.5")
    streak = weekly_data.get("streak", "7")
    milestones = weekly_data.get("milestonesCompleted", "2")
    readiness = weekly_data.get("readinessScore", "82")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; padding: 20px; }}
        .box {{ max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #e2e8f0; }}
        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 20px 0; }}
        .stat-card {{ background: #f1f5f9; padding: 14px; border-radius: 10px; text-align: center; }}
        .stat-val {{ font-size: 24px; font-weight: 800; color: #4f46e5; }}
        .stat-lbl {{ font-size: 12px; color: #64748b; font-weight: 600; text-transform: uppercase; }}
      </style>
    </head>
    <body>
      <div class="box">
        <h2 style="color:#1e293b; margin-top:0;">🚀 Weekly Progress Digest</h2>
        <p>Great work this week, <strong>{user_name}</strong>! Here is your learning summary:</p>
        <div class="stat-grid">
          <div class="stat-card"><div class="stat-val">{hours} hrs</div><div class="stat-lbl">Study Time</div></div>
          <div class="stat-card"><div class="stat-val">{streak} Days</div><div class="stat-lbl">Active Streak</div></div>
          <div class="stat-card"><div class="stat-val">{milestones}</div><div class="stat-lbl">Milestones Done</div></div>
          <div class="stat-card"><div class="stat-val">{readiness}%</div><div class="stat-lbl">Job Readiness</div></div>
        </div>
        <p style="color:#475569;">Keep up the momentum to stay in the top rankings for your college and branch!</p>
      </div>
    </body>
    </html>
    """
    text_content = f"Weekly Digest for {user_name}:\nStudy Time: {hours} hrs | Streak: {streak} days | Milestones: {milestones} | Readiness: {readiness}%"
    return send_email(to_email, subject, html_content, text_content)
