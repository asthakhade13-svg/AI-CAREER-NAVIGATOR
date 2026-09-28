from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import urllib.parse
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


@router.get("/share-payload/{cert_id}")
def get_share_payload(cert_id: str):
    """
    Returns pre-formatted LinkedIn, Twitter/X, and GitHub share links and badge snippets.
    """
    cert = verify_certificate_id(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate ID not found")

    verify_url = f"https://ai-career-navigator.onrender.com/verify.html?certId={cert_id}"
    student_name = cert.get("studentName", "Student")
    track_title = cert.get("trackTitle", "Career Track")

    # LinkedIn Share Link
    linkedin_summary = f"I am proud to share that I have successfully completed the {track_title} career track on AI Career Navigator with a score of {cert.get('scorePercentage', 95)}%!"
    linkedin_url = (
        f"https://www.linkedin.com/profile/add?startTask=CERTIFICATION_NAME"
        f"&name={urllib.parse.quote(track_title + ' Certificate of Completion')}"
        f"&organizationName={urllib.parse.quote('AI Career Navigator')}"
        f"&issueYear=2026&issueMonth=9"
        f"&certUrl={urllib.parse.quote(verify_url)}"
        f"&certId={urllib.parse.quote(cert_id)}"
    )

    # Twitter / X Intent
    tweet_text = f"🎉 Just verified my {track_title} certificate on @AICareerNavigator! Check out my verified credential: {verify_url}"
    twitter_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(tweet_text)}"

    # Markdown Badge
    badge_markdown = f"[![Verified Certificate](https://img.shields.io/badge/Verified_Certificate-{urllib.parse.quote(track_title)}-4f46e5?style=for-the-badge&logo=shield)]({verify_url})"

    return {
        "success": True,
        "certId": cert_id,
        "studentName": student_name,
        "trackTitle": track_title,
        "verifyUrl": verify_url,
        "linkedinUrl": linkedin_url,
        "twitterUrl": twitter_url,
        "badgeMarkdown": badge_markdown
    }


@router.get("/download-pdf/{cert_id}")
def download_certificate_pdf(cert_id: str):
    """
    Generates a high-resolution, print-ready HTML certificate template that automatically opens print-to-PDF dialog.
    """
    cert = verify_certificate_id(cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate ID not found")

    student_name = cert.get("studentName", "Student")
    track_title = cert.get("trackTitle", "Engineering Track")
    issued_at = cert.get("issuedAt", "2026-09-28")
    hash_val = cert.get("verificationHash", "0x000000000000")
    score = cert.get("scorePercentage", 95)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Certificate of Completion - {student_name}</title>
  <style>
    @page {{ size: landscape; margin: 0; }}
    body {{
      font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background: #f8fafc;
      margin: 0;
      padding: 40px;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      box-sizing: border-box;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    .cert-frame {{
      width: 1000px;
      padding: 50px 60px;
      background: #ffffff;
      border: 12px double #6366f1;
      border-radius: 16px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.08);
      text-align: center;
      position: relative;
    }}
    .watermark {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%) rotate(-25deg);
      font-size: 80px;
      color: rgba(99, 102, 241, 0.04);
      font-weight: 900;
      pointer-events: none;
      white-space: nowrap;
    }}
    .header {{ font-size: 15px; letter-spacing: 4px; text-transform: uppercase; color: #6366f1; font-weight: 700; }}
    .title {{ font-size: 38px; font-weight: 800; color: #1e293b; margin: 15px 0 10px; }}
    .subtitle {{ font-size: 16px; color: #64748b; margin-bottom: 25px; }}
    .recipient {{ font-size: 36px; font-weight: 700; color: #4338ca; border-bottom: 2px solid #e2e8f0; display: inline-block; padding: 0 40px 10px; margin-bottom: 20px; }}
    .body-text {{ font-size: 16px; color: #475569; line-height: 1.6; max-width: 750px; margin: 0 auto 30px; }}
    .badge-score {{ display: inline-block; background: #e0e7ff; color: #4338ca; font-weight: 700; padding: 6px 18px; border-radius: 9999px; margin-bottom: 30px; }}
    .footer {{ display: flex; justify-content: space-between; align-items: flex-end; margin-top: 40px; padding-top: 20px; border-top: 1px solid #f1f5f9; }}
    .meta-box {{ text-align: left; font-size: 12px; color: #64748b; }}
    .signature-box {{ text-align: right; }}
    .signature-line {{ font-family: 'Brush Script MT', cursive, sans-serif; font-size: 26px; color: #1e293b; margin-bottom: 4px; }}
    .signature-title {{ font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase; }}
  </style>
</head>
<body onload="window.print()">
  <div class="cert-frame">
    <div class="watermark">AI CAREER NAVIGATOR</div>
    <div class="header">AI Career Navigator &amp; Skill Credentialing</div>
    <h1 class="title">Certificate of Completion</h1>
    <div class="subtitle">This is proudly presented to</div>
    <div class="recipient">{student_name}</div>
    <p class="body-text">
      For successfully mastering the curated curriculum, capstone challenges, and knowledge assessments for the <strong>{track_title}</strong> career track.
    </p>
    <div class="badge-score">Curriculum Mastery Score: {score}%</div>
    <div class="footer">
      <div class="meta-box">
        <div><strong>Certificate ID:</strong> {cert_id}</div>
        <div><strong>Issue Date:</strong> {issued_at}</div>
        <div><strong>Verification Hash:</strong> {hash_val[:20]}...</div>
      </div>
      <div class="signature-box">
        <div class="signature-line">Dr. A. Sharma</div>
        <div class="signature-title">Academic &amp; AI Curriculum Director</div>
      </div>
    </div>
  </div>
</body>
</html>"""

    return HTMLResponse(content=html_content)

