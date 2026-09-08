from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.db.store import db_store
from app.services.ai_vision import verify_resolution
from app.models.schemas import ResolutionVerificationResult, ComplaintStatus

router = APIRouter(prefix="/api/verification", tags=["Resolution Verification"])

class ResolutionEvidenceSubmission(BaseModel):
    complaint_id: str
    officer_id: str = "Officer PWD-42"
    officer_notes: str = ""
    evidence_image_url: str
    gps_lat: Optional[float] = 19.9975
    gps_lng: Optional[float] = 73.7898
    timestamp: Optional[str] = None

class CitizenFeedbackSubmission(BaseModel):
    complaint_id: str
    feedback: str  # YES_FIXED, NO_STILL_EXISTS, PARTIALLY_FIXED
    citizen_notes: Optional[str] = None

@router.post("/verify-resolution", response_model=ResolutionVerificationResult)
def verify_officer_resolution(payload: ResolutionEvidenceSubmission):
    """
    Submits officer resolution evidence & executes Computer Vision Verification:
    - Compares Before vs After images (SSIM)
    - Checks location GPS consistency & timestamp freshness
    - Detects genuine repairs vs fake/mismatched uploads
    """
    complaint = db_store.get_complaint_by_id(payload.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint ID not found")

    verification_res = verify_resolution(
        complaint_id_or_img=payload.complaint_id,
        officer_id=payload.officer_id,
        after_image=payload.evidence_image_url,
        officer_notes=payload.officer_notes,
        gps_lat=payload.gps_lat,
        gps_lng=payload.gps_lng,
        timestamp=payload.timestamp,
        base_lat=complaint.location.lat if complaint and complaint.location else None,
        base_lng=complaint.location.lng if complaint and complaint.location else None,
        before_image=complaint.image_url if complaint else None
    )

    complaint.resolution_evidence_image_url = payload.evidence_image_url
    complaint.resolution_officer_notes = payload.officer_notes
    complaint.verification_result = verification_res
    now_iso = datetime.now().isoformat()
    complaint.updated_at = now_iso

    # Bug 34 Fix: Enforce lifecycle status workflow consistency (AI_VERIFICATION or REJECTED_FAKE_RESOLUTION)
    if verification_res.fake_resolution_detected:
        complaint.status = ComplaintStatus.REJECTED_FAKE_RESOLUTION
    else:
        complaint.status = ComplaintStatus.AI_VERIFICATION

    complaint.status_history.append({
        "status": complaint.status.value,
        "timestamp": now_iso,
        "actor": "Officer & AI Inspector",
        "notes": verification_res.message
    })

    db_store.update_complaint(complaint)
    return verification_res

# Bug 37 Fix: Backend route alias handler for /verify endpoint (matches frontend api.ts call)
@router.post("/verify", response_model=ResolutionVerificationResult)
def verify_resolution_alias(payload: ResolutionEvidenceSubmission):
    return verify_officer_resolution(payload)

@router.post("/citizen-feedback")
def submit_citizen_feedback(payload: CitizenFeedbackSubmission):
    complaint = db_store.get_complaint_by_id(payload.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint ID not found")

    if payload.feedback == "YES_FIXED":
        complaint.status = ComplaintStatus.CLOSED
        msg = "✓ Incident confirmed resolved and closed."
    elif payload.feedback == "NO_STILL_EXISTS":
        complaint.status = ComplaintStatus.REOPENED
        msg = "⚠️ Citizen marked issue unresolved. Ticket automatically reopened and escalated to supervisor."
    else:
        complaint.status = ComplaintStatus.IN_PROGRESS
        msg = "⚠️ Issue marked partially fixed. Sent back for field contractor inspection."

    now_iso = datetime.now().isoformat()
    complaint.updated_at = now_iso
    complaint.status_history.append({
        "status": complaint.status.value,
        "timestamp": now_iso,
        "actor": "Citizen Feedback",
        "notes": msg
    })

    db_store.update_complaint(complaint)

    return {
        "complaint_id": payload.complaint_id,
        "new_status": complaint.status.value,
        "message": msg
    }

@router.get("/{complaint_id}/timeline")
def get_resolution_timeline(complaint_id: str):
    """
    Bugs 35 & 36 Fixes: Dynamically generates timeline stages based ONLY on actual executed events in complaint.status_history
    with real event timestamps.
    """
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint ID not found")

    timeline = []
    if complaint.status_history:
        for idx, entry in enumerate(complaint.status_history):
            st = entry.get("status", "Updated")
            ts = entry.get("timestamp", complaint.created_at)
            act = entry.get("actor", "System")
            notes = entry.get("notes", f"Status updated to {st}")

            timeline.append({
                "stage": st,
                "date": ts,
                "actor": act,
                "desc": notes
            })
    else:
        timeline.append({
            "stage": ComplaintStatus.SUBMITTED.value,
            "date": complaint.created_at,
            "actor": "Citizen",
            "desc": "Multimodal issue report submitted"
        })

    return {"complaint_id": complaint_id, "timeline": timeline}
