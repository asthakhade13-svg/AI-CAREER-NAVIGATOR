from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import uuid
import datetime
import logging
from services.auth_service import (
    get_db_connection,
    hash_password,
    verify_password,
    create_jwt_token,
    verify_jwt_token
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication & Profile"])

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    college: Optional[str] = "Oriental Institute of Science & Technology (OIST)"
    year: Optional[str] = "1st Year"
    branch: Optional[str] = "Computer Science & Engineering"
    career_track: Optional[str] = "aiml"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    college: Optional[str] = None
    year: Optional[str] = None
    branch: Optional[str] = None
    career_track: Optional[str] = None
    bio: Optional[str] = None

def get_current_user_payload(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "").strip()
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired JWT token")
    return payload


@router.post("/register")
def register_user(req: RegisterRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check existing user
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (req.email,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user_id = f"usr_{uuid.uuid4().hex[:10]}"
    password_hash = hash_password(req.password)

    cursor.execute("""
    INSERT INTO users (id, full_name, email, password_hash, college, year, branch, career_track)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        req.full_name.strip(),
        req.email.lower().strip(),
        password_hash,
        req.college or "Oriental Institute of Science & Technology (OIST)",
        req.year or "1st Year",
        req.branch or "Computer Science & Engineering",
        req.career_track or "aiml"
    ))
    conn.commit()
    conn.close()

    token = create_jwt_token({
        "sub": user_id,
        "email": req.email.lower().strip(),
        "name": req.full_name.strip()
    })

    return {
        "success": True,
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user_id,
            "fullName": req.full_name.strip(),
            "email": req.email.lower().strip(),
            "college": req.college,
            "year": req.year,
            "branch": req.branch,
            "careerTrack": req.career_track
        }
    }


@router.post("/login")
def login_user(req: LoginRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (req.email.strip(),))
    user_row = cursor.fetchone()
    conn.close()

    if not user_row:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(req.password, user_row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_jwt_token({
        "sub": user_row["id"],
        "email": user_row["email"],
        "name": user_row["full_name"]
    })

    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user_row["id"],
            "fullName": user_row["full_name"],
            "email": user_row["email"],
            "college": user_row["college"],
            "year": user_row["year"],
            "branch": user_row["branch"],
            "careerTrack": user_row["career_track"],
            "bio": user_row["bio"]
        }
    }


@router.get("/me")
def get_current_user_profile(user_payload: Dict[str, Any] = Depends(get_current_user_payload)):
    user_id = user_payload.get("sub")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    conn.close()

    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "success": True,
        "user": {
            "id": user_row["id"],
            "fullName": user_row["full_name"],
            "email": user_row["email"],
            "college": user_row["college"],
            "year": user_row["year"],
            "branch": user_row["branch"],
            "careerTrack": user_row["career_track"],
            "bio": user_row["bio"],
            "createdAt": user_row["created_at"]
        }
    }


@router.put("/profile")
def update_profile(req: ProfileUpdateRequest, user_payload: Dict[str, Any] = Depends(get_current_user_payload)):
    user_id = user_payload.get("sub")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    updates = []
    params = []

    if req.full_name:
        updates.append("full_name = ?")
        params.append(req.full_name.strip())
    if req.college:
        updates.append("college = ?")
        params.append(req.college.strip())
    if req.year:
        updates.append("year = ?")
        params.append(req.year.strip())
    if req.branch:
        updates.append("branch = ?")
        params.append(req.branch.strip())
    if req.career_track:
        updates.append("career_track = ?")
        params.append(req.career_track.strip())
    if req.bio is not None:
        updates.append("bio = ?")
        params.append(req.bio.strip())

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    updated_user = cursor.fetchone()
    conn.close()

    return {
        "success": True,
        "message": "Profile updated successfully",
        "user": {
            "id": updated_user["id"],
            "fullName": updated_user["full_name"],
            "email": updated_user["email"],
            "college": updated_user["college"],
            "year": updated_user["year"],
            "branch": updated_user["branch"],
            "careerTrack": updated_user["career_track"],
            "bio": updated_user["bio"],
            "avatarUrl": updated_user["avatar_url"]
        }
    }


# ── 4. Forgot Password & Reset Endpoints ─────────────────────────────────────
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (req.email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        # Return success true for security reason (prevent email enumeration)
        return {
            "success": True,
            "message": "If an account exists with this email, a 6-digit recovery code has been generated.",
            "devOtp": "123456"
        }

    # Generate 6-digit OTP
    otp = f"{uuid.uuid4().int % 900000 + 100000}"
    expires_at = (datetime.datetime.now() + datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO password_resets (email, reset_token, expires_at, is_used)
    VALUES (?, ?, ?, 0)
    """, (req.email.lower().strip(), otp, expires_at))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "A 6-digit password reset OTP has been sent to your email.",
        "otp": otp # Provided for smooth in-app demo & verification
    }

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest):
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM password_resets
    WHERE LOWER(email) = LOWER(?) AND reset_token = ? AND is_used = 0
    ORDER BY id DESC LIMIT 1
    """, (req.email.lower().strip(), req.otp.strip()))
    reset_record = cursor.fetchone()

    # Allow demo OTP 123456 as well
    if not reset_record and req.otp != "123456":
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid or expired reset OTP")

    new_hash = hash_password(req.new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE LOWER(email) = LOWER(?)", (new_hash, req.email.lower().strip()))
    if reset_record:
        cursor.execute("UPDATE password_resets SET is_used = 1 WHERE id = ?", (reset_record["id"],))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Password successfully reset. You can now login with your new password."
    }


# ── 5. Google OAuth Social Login Endpoints ────────────────────────────────────
class GoogleLoginRequest(BaseModel):
    id_token: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None

@router.get("/google/url")
def get_google_auth_url():
    client_id = "ai-career-navigator-google-client.apps.googleusercontent.com"
    redirect_uri = "https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/login.html"
    scope = "openid email profile"
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=token&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
    return {
        "success": True,
        "authUrl": auth_url
    }

@router.post("/google/callback")
def google_auth_callback(req: GoogleLoginRequest):
    email = (req.email or "student.google@gmail.com").lower().strip()
    name = req.name or "Google Student"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    user_row = cursor.fetchone()

    if not user_row:
        user_id = f"usr_{uuid.uuid4().hex[:10]}"
        pwd_hash = hash_password(uuid.uuid4().hex)
        cursor.execute("""
        INSERT INTO users (id, full_name, email, password_hash, college, year, branch, career_track)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            name,
            email,
            pwd_hash,
            "Oriental Institute of Science & Technology (OIST)",
            "1st Year",
            "Computer Science & Engineering",
            "aiml"
        ))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()

    conn.close()

    token = create_jwt_token({
        "sub": user_row["id"],
        "email": user_row["email"],
        "name": user_row["full_name"]
    })

    u_dict = dict(user_row)
    return {
        "success": True,
        "message": "Google authentication successful",
        "token": token,
        "user": {
            "id": u_dict.get("id"),
            "fullName": u_dict.get("full_name"),
            "email": u_dict.get("email"),
            "college": u_dict.get("college"),
            "year": u_dict.get("year"),
            "branch": u_dict.get("branch"),
            "careerTrack": u_dict.get("career_track"),
            "avatarUrl": u_dict.get("avatar_url", "")
        }
    }


# ── 7. Profile Avatar Photo Upload Endpoint ──────────────────────────────────
class AvatarUploadRequest(BaseModel):
    student_id: str
    avatar_base64: str

@router.post("/avatar")
def upload_avatar(req: AvatarUploadRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET avatar_url = ? WHERE id = ? OR email = ?", (req.avatar_base64, req.student_id, req.student_id))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Profile avatar updated successfully",
        "avatarUrl": req.avatar_base64
    }

