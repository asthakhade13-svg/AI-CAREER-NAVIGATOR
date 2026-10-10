import sqlite3
import os
import json
import logging
import hmac
import hashlib
import base64
import time
import secrets
import struct
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "career_nav.db")
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "career_nav_secure_jwt_secret_2026_first_gen")

_DB_INITIALIZED = False

def get_db_connection():
    global _DB_INITIALIZED
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if not _DB_INITIALIZED:
        _DB_INITIALIZED = True
        init_sqlite_db()
    return conn

def init_sqlite_db():
    """Initializes SQLite tables for users, goals, certificates, and progress."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            college TEXT DEFAULT 'Oriental Institute of Science & Technology (OIST)',
            year TEXT DEFAULT '1st Year',
            branch TEXT DEFAULT 'Computer Science & Engineering',
            career_track TEXT DEFAULT 'aiml',
            bio TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            is_2fa_enabled INTEGER DEFAULT 0,
            totp_secret TEXT DEFAULT '',
            token_version INTEGER DEFAULT 1,
            session_revoked_at TIMESTAMP DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT DEFAULT ''")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_2fa_enabled INTEGER DEFAULT 0")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN totp_secret TEXT DEFAULT ''")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN token_version INTEGER DEFAULT 1")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN session_revoked_at TIMESTAMP DEFAULT NULL")
        except Exception:
            pass
        
        # 2. Weekly Goals Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_goals (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            target_hours REAL DEFAULT 10.0,
            target_milestones INTEGER DEFAULT 3,
            focus_topic TEXT DEFAULT 'Data Structures & Algorithms',
            achieved_hours REAL DEFAULT 0.0,
            achieved_milestones INTEGER DEFAULT 0,
            week_start_date TEXT NOT NULL,
            status TEXT DEFAULT 'in_progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 3. Certificates Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            certificate_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            track_key TEXT NOT NULL,
            track_title TEXT NOT NULL,
            score_percentage INTEGER DEFAULT 95,
            skills_acquired TEXT DEFAULT '',
            verification_hash TEXT NOT NULL,
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 4. Progress Checkins Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            activity_type TEXT DEFAULT 'checkin',
            track_key TEXT DEFAULT '',
            milestone_id TEXT DEFAULT '',
            hours_spent REAL DEFAULT 0.5,
            log_date DATE DEFAULT (DATE('now')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 5. Saved / Bookmarked Careers Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_careers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            career_id TEXT NOT NULL,
            career_title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, career_id)
        )
        """)

        # 6. Notifications Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 7. Goal Items Table (Individual Goal Checklists)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS goal_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            goal_text TEXT NOT NULL,
            is_completed INTEGER DEFAULT 0,
            week_id TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, goal_text)
        )
        """)

        # 8. Password Resets Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            reset_token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            is_used INTEGER DEFAULT 0
        )
        """)

        # 9. Quiz Attempt History Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            track_key TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER DEFAULT 10,
            correct_answers INTEGER DEFAULT 8,
            time_taken_sec INTEGER DEFAULT 120,
            question_timings TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        try:
            cursor.execute("ALTER TABLE quiz_attempts ADD COLUMN question_timings TEXT DEFAULT '{}'")
        except Exception:
            pass

        # 10. Milestones Progress Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS milestones_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            track_key TEXT NOT NULL,
            milestone_id TEXT NOT NULL,
            is_completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, track_key, milestone_id)
        )
        """)

        # 11. Student Badges Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            badge_id TEXT NOT NULL,
            badge_name TEXT NOT NULL,
            icon TEXT DEFAULT '🏆',
            description TEXT DEFAULT '',
            is_unlocked INTEGER DEFAULT 1,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, badge_id)
        )
        """)

        # 12. Activity Logs Stream Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT DEFAULT 'fa-check',
            color TEXT DEFAULT 'green',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 13. Study Logs Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            day_name TEXT NOT NULL,
            hours_spent REAL DEFAULT 2.0,
            category TEXT DEFAULT 'Coding Practice',
            session_notes TEXT DEFAULT '',
            log_date DATE DEFAULT (DATE('now')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        try:
            cursor.execute("ALTER TABLE study_logs ADD COLUMN category TEXT DEFAULT 'Coding Practice'")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE study_logs ADD COLUMN session_notes TEXT DEFAULT ''")
        except Exception:
            pass

        # 14. Chat Messages History Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 15. Capstone Project Milestones Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            step_id TEXT NOT NULL,
            is_completed INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, project_id, step_id)
        )
        """)

        # 16. User Preferences & Settings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            student_id TEXT PRIMARY KEY,
            email_digest INTEGER DEFAULT 1,
            streak_reminders INTEGER DEFAULT 1,
            dark_mode INTEGER DEFAULT 0,
            custom_api_key TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 17. Capstone Project Submissions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            github_url TEXT NOT NULL,
            demo_url TEXT DEFAULT '',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, project_id)
        )
        """)

        # 18. Resource Completions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resource_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            resource_id TEXT NOT NULL,
            resource_title TEXT DEFAULT '',
            track_key TEXT DEFAULT '',
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, resource_id)
        )
        """)

        # 19. Roadmap Granular Subtasks Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmap_subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            track_key TEXT NOT NULL,
            subtask_id TEXT NOT NULL,
            subtask_text TEXT DEFAULT '',
            is_completed INTEGER DEFAULT 1,
            is_custom INTEGER DEFAULT 0,
            milestone_index INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, track_key, subtask_id)
        )
        """)
        try:
            cursor.execute("ALTER TABLE roadmap_subtasks ADD COLUMN is_custom INTEGER DEFAULT 0")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE roadmap_subtasks ADD COLUMN milestone_index INTEGER DEFAULT 0")
        except Exception:
            pass

        # 20. Assessment Multi-Attempt History Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            attempt_id TEXT NOT NULL,
            assessment_type TEXT DEFAULT 'stellar_assessment',
            technical_score REAL DEFAULT 0,
            starting_quiz TEXT DEFAULT 'intermediate',
            recommended_tracks TEXT DEFAULT '[]',
            dominant_interests TEXT DEFAULT '[]',
            full_name TEXT DEFAULT '',
            date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 21. Resume Scans & ATS Reports Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            track_key TEXT NOT NULL,
            ats_score INTEGER DEFAULT 75,
            matched_skills TEXT DEFAULT '[]',
            missing_skills TEXT DEFAULT '[]',
            suggested_improvements TEXT DEFAULT '[]',
            file_name TEXT DEFAULT '',
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 22. Analytics Events Table (Shares & Referrals)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            target_id TEXT DEFAULT '',
            platform TEXT DEFAULT 'generic',
            referral_code TEXT DEFAULT '',
            metadata TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 23. Saved Internships Bookmarks Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            internship_id TEXT NOT NULL,
            title TEXT NOT NULL,
            company TEXT DEFAULT '',
            track TEXT DEFAULT '',
            location TEXT DEFAULT '',
            stipend TEXT DEFAULT '',
            apply_url TEXT DEFAULT '',
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, internship_id)
        )
        """)

        # 24. Internship Application Pipeline Tracker Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS internship_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            internship_id TEXT NOT NULL,
            company TEXT NOT NULL,
            role_title TEXT NOT NULL,
            status TEXT DEFAULT 'Applied',
            notes TEXT DEFAULT '',
            applied_date DATE DEFAULT (DATE('now')),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, internship_id)
        )
        """)

        # 25. Capstone Project Mentor & Peer Reviews Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            reviewer_name TEXT NOT NULL,
            reviewer_role TEXT DEFAULT 'AI Mentor / Senior Engineer',
            code_quality_grade TEXT DEFAULT 'A - Production Ready',
            feedback_notes TEXT NOT NULL,
            suggestions TEXT DEFAULT '',
            review_date TEXT DEFAULT (DATE('now')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Insert a default demo user if not present
        cursor.execute("SELECT id FROM users WHERE email = 'astha@example.com' OR email = 'astha.khade@oist.edu'")
        demo_user = cursor.fetchone()
        if not demo_user:
            demo_salt = secrets.token_hex(16)
            demo_pwd_hash = hash_password_with_salt("password123", demo_salt)
            cursor.execute("""
            INSERT OR IGNORE INTO users (id, full_name, email, password_hash, college, year, branch, career_track, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "user_astha_001",
                "Astha Khade",
                "astha.khade@oist.edu",
                f"{demo_salt}${demo_pwd_hash}",
                "Oriental Institute of Science & Technology (OIST)",
                "1st Year",
                "Computer Science & Engineering",
                "aiml",
                "Passionate 1st year CSE student exploring AI/ML, Full Stack, and Cloud Engineering."
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"SQLite database successfully initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}")


# ── Password Hashing ──────────────────────────────────────────────────────────
def hash_password_with_salt(password: str, salt: str) -> str:
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return key.hex()

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hash_password_with_salt(password, salt)
    return f"{salt}${hashed}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        if "$" not in stored_hash:
            return False
        salt, expected_hash = stored_hash.split("$", 1)
        computed_hash = hash_password_with_salt(password, salt)
        return hmac.compare_digest(computed_hash, expected_hash)
    except Exception:
        return False


# ── URL-Safe Base64 JWT Token Implementation ──────────────────────────────────
def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4)) if (len(data) % 4) != 0 else ''
    return base64.urlsafe_b64decode(data + padding)

def create_jwt_token(payload: Dict[str, Any], expires_in_seconds: int = 259200) -> str:
    """Generates an RFC 7519 HMAC-SHA256 JWT token (valid for 3 days by default)."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload_copy = dict(payload)
    payload_copy["exp"] = int(time.time()) + expires_in_seconds
    payload_copy["iat"] = int(time.time())

    encoded_header = base64url_encode(json.dumps(header).encode('utf-8'))
    encoded_payload = base64url_encode(json.dumps(payload_copy).encode('utf-8'))

    signature_input = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signature_input, hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies HMAC signature and expiration of JWT token."""
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return None
        encoded_header, encoded_payload, encoded_signature = parts
        
        signature_input = f"{encoded_header}.{encoded_payload}".encode('utf-8')
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), signature_input, hashlib.sha256).digest()
        actual_sig = base64url_decode(encoded_signature)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload = json.loads(base64url_decode(encoded_payload).decode('utf-8'))
        if "exp" in payload and payload["exp"] < int(time.time()):
            return None  # Token expired

        return payload
    except Exception as e:
        logger.warning(f"JWT Verification failed: {e}")
        return None


# ── RFC 6238 TOTP 2FA Implementation ──────────────────────────────────────────
def generate_totp_secret() -> str:
    """Generates a secure 32-character base32 secret for Authenticator apps."""
    raw = secrets.token_bytes(20)
    return base64.b32encode(raw).decode('utf-8').replace('=', '')

def get_totp_token(secret: str, intervals_no: int) -> int:
    """Calculates a 6-digit TOTP code for a given 30-second interval."""
    key = base64.b32decode(secret + '=' * (-len(secret) % 8), casefold=True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return h

def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
    """Verifies user-submitted 6-digit TOTP code within a 30-second ±window."""
    if not secret or not code:
        return False
    try:
        int_code = int(str(code).strip())
    except ValueError:
        return False
    
    current_interval = int(time.time() // 30)
    for i in range(-window, window + 1):
        if get_totp_token(secret, current_interval + i) == int_code:
            return True
    return False

