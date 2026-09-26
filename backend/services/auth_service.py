import sqlite3
import os
import json
import logging
import hmac
import hashlib
import base64
import time
import secrets
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
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
