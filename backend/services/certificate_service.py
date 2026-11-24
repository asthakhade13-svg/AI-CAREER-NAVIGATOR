import hashlib
import uuid
import datetime
import logging
from typing import Dict, Any, List, Optional
from services.auth_service import get_db_connection

logger = logging.getLogger(__name__)

# ── Ensure document_hash column exists (safe migration) ───────────────────────
def _ensure_document_hash_column():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(certificates)")
        cols = [row["name"] for row in cursor.fetchall()]
        if "document_hash" not in cols:
            cursor.execute("ALTER TABLE certificates ADD COLUMN document_hash TEXT DEFAULT NULL")
            conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"document_hash migration: {e}")

_ensure_document_hash_column()

TRACK_SKILLS_MAP = {
    "aiml": [
        "Python for Data Science", "Supervised & Unsupervised ML",
        "Deep Learning Architectures", "PyTorch & Scikit-Learn",
        "Model Deployment & Evaluation", "Prompt Engineering"
    ],
    "uiux": [
        "User Research & Empathy Mapping", "Wireframing & Prototyping",
        "Figma Design Systems", "Information Architecture",
        "Usability Testing & WCAG Accessibility", "Design-to-Code Handoff"
    ],
    "cyber": [
        "Network Security Protocols", "Vulnerability Assessment",
        "OWASP Top 10 Defense", "Penetration Testing Basics",
        "Cryptography & Access Control", "Incident Response"
    ],
    "webdev": [
        "Modern Responsive Frontend", "RESTful API Design",
        "Backend Architecture", "State Management",
        "Database Design & SQL", "Cloud CI/CD & Deployment"
    ],
    "cloud": [
        "Cloud Architecture (AWS/GCP)", "Docker & Containerization",
        "Kubernetes Orchestration", "Infrastructure as Code",
        "CI/CD Pipelines", "Serverless Computing"
    ],
    "datascience": [
        "Exploratory Data Analysis (EDA)", "Statistical Inference",
        "SQL Data Wrangling", "Interactive Dashboards",
        "Predictive Modeling", "Big Data Processing"
    ]
}

TRACK_NAME_MAP = {
    "aiml": "AI & Machine Learning Engineer Specialization",
    "uiux": "UI/UX & Product Design Specialization",
    "cyber": "Cybersecurity & Defense Analyst Specialization",
    "webdev": "Full-Stack Web Engineering Specialization",
    "cloud": "Cloud Architecture & DevOps Specialization",
    "datascience": "Data Science & Analytics Specialization"
}


def generate_certificate_record(
    student_id: str,
    student_name: str,
    track_key: str,
    score_percentage: int = 95
) -> Dict[str, Any]:
    track_key = track_key.lower().strip()
    track_title = TRACK_NAME_MAP.get(track_key, f"{track_key.upper()} Professional Specialization")
    skills = TRACK_SKILLS_MAP.get(track_key, ["Core Engineering Foundations", "Applied Problem Solving", "Industry Project Readiness"])

    # Generate unique Certificate ID: CN-2026-{TRACK}-{HEX}
    unique_suffix = uuid.uuid4().hex[:6].upper()
    cert_id = f"CN-2026-{track_key[:4].upper()}-{unique_suffix}"
    
    # Generate cryptographic tamper verification hash
    raw_payload = f"{cert_id}|{student_id}|{student_name}|{track_key}|{score_percentage}|2026"
    verification_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()[:24].upper()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO certificates (
        certificate_id, student_id, student_name, track_key, track_title,
        score_percentage, skills_acquired, verification_hash
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cert_id,
        student_id,
        student_name,
        track_key,
        track_title,
        score_percentage,
        ", ".join(skills),
        verification_hash
    ))
    conn.commit()

    cursor.execute("SELECT * FROM certificates WHERE certificate_id = ?", (cert_id,))
    row = cursor.fetchone()
    conn.close()

    return {
        "certificateId": row["certificate_id"],
        "studentId": row["student_id"],
        "studentName": row["student_name"],
        "trackKey": row["track_key"],
        "trackTitle": row["track_title"],
        "scorePercentage": row["score_percentage"],
        "skillsAcquired": skills,
        "verificationHash": row["verification_hash"],
        "issuedAt": row["issued_at"],
        "issuer": "First-Gen AI Career Navigator Accreditation Board",
        "verificationUrl": f"https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/verify.html?certId={cert_id}"
    }


def verify_certificate_id(cert_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM certificates WHERE certificate_id = ?", (cert_id.strip(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    skills = [s.strip() for s in row["skills_acquired"].split(",") if s.strip()]
    return {
        "isValid": True,
        "certificateId": row["certificate_id"],
        "studentName": row["student_name"],
        "trackTitle": row["track_title"],
        "scorePercentage": row["score_percentage"],
        "skillsAcquired": skills,
        "verificationHash": row["verification_hash"],
        "issuedAt": row["issued_at"],
        "issuer": "First-Gen AI Career Navigator Accreditation Board"
    }


def get_student_certificates(student_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM certificates WHERE student_id = ? ORDER BY issued_at DESC", (student_id,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        skills = [s.strip() for s in r["skills_acquired"].split(",") if s.strip()]
        results.append({
            "certificateId": r["certificate_id"],
            "studentName": r["student_name"],
            "trackKey": r["track_key"],
            "trackTitle": r["track_title"],
            "scorePercentage": r["score_percentage"],
            "skillsAcquired": skills,
            "verificationHash": r["verification_hash"],
            "issuedAt": r["issued_at"],
            "verificationUrl": f"https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/verify.html?certId={r['certificate_id']}"
        })
    return results


# ── Document-level SHA-256 tamper detection ───────────────────────────────────

def register_document_hash(cert_id: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Computes SHA-256 of the uploaded certificate file and stores it
    as the official document fingerprint for future tamper detection.
    Called when the student first downloads/exports their certificate.
    """
    doc_hash = hashlib.sha256(file_bytes).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT certificate_id, document_hash FROM certificates WHERE certificate_id = ?",
        (cert_id.strip(),)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "error": "Certificate ID not found"}

    if row["document_hash"]:
        # Already registered — return existing fingerprint (don't overwrite)
        conn.close()
        return {
            "success": True,
            "certId": cert_id,
            "documentHash": row["document_hash"],
            "alreadyRegistered": True,
            "message": "Document fingerprint already registered for this certificate."
        }

    cursor.execute(
        "UPDATE certificates SET document_hash = ? WHERE certificate_id = ?",
        (doc_hash, cert_id.strip())
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "certId": cert_id,
        "documentHash": doc_hash,
        "alreadyRegistered": False,
        "message": "Document fingerprint registered successfully."
    }


def verify_document_hash(cert_id: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Computes SHA-256 of an uploaded file and compares it against
    the stored document fingerprint to detect tampering.
    Returns is_authentic=True only when hashes match exactly.
    """
    uploaded_hash = hashlib.sha256(file_bytes).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT certificate_id, student_name, track_title, verification_hash, document_hash FROM certificates WHERE certificate_id = ?",
        (cert_id.strip(),)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "success": False,
            "certId": cert_id,
            "error": "Certificate ID not found in ledger."
        }

    stored_doc_hash = row["document_hash"]

    if not stored_doc_hash:
        return {
            "success": False,
            "certId": cert_id,
            "uploadedHash": uploaded_hash,
            "error": "No document fingerprint registered for this certificate yet. "
                     "The original file must be registered first via the export flow."
        }

    is_authentic = (uploaded_hash == stored_doc_hash)

    return {
        "success": True,
        "certId": cert_id,
        "studentName": row["student_name"],
        "trackTitle": row["track_title"],
        "isAuthentic": is_authentic,
        "uploadedHash": uploaded_hash,
        "storedHash": stored_doc_hash,
        "metadataHash": row["verification_hash"],
        "tamperStatus": "AUTHENTIC" if is_authentic else "TAMPERED",
        "message": (
            "✅ Document integrity verified. File matches the original registered certificate."
            if is_authentic else
            "❌ Document mismatch detected. This file has been modified or is not the original certificate."
        )
    }

