from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import uuid
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
            "bio": updated_user["bio"]
        }
    }
