from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from services.certificate_service import (
    generate_certificate_record,
    verify_certificate_id,
    get_student_certificates
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/certificates", tags=["Verifiable Certificates"])

class CertificateGenerateRequest(BaseModel):
    student_id: str
    student_name: str
    track_key: str
    score_percentage: Optional[int] = 95


@router.post("/generate")
def create_certificate(req: CertificateGenerateRequest):
    try:
        cert_data = generate_certificate_record(
            student_id=req.student_id,
            student_name=req.student_name,
            track_key=req.track_key,
            score_percentage=req.score_percentage or 95
        )
        return {
            "success": True,
            "message": "Certificate issued and cryptographically signed successfully",
            "certificate": cert_data
        }
    except Exception as e:
        logger.error(f"Error generating certificate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify/{cert_id}")
def verify_certificate(cert_id: str):
    cert = verify_certificate_id(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate ID not found or invalid")
    return {
        "success": True,
        "verification": cert
    }


@router.get("/user/{student_id}")
def get_user_certs(student_id: str):
    certs = get_student_certificates(student_id)
    return {
        "success": True,
        "studentId": student_id,
        "totalCertificates": len(certs),
        "certificates": certs
    }
