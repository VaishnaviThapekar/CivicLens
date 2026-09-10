from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
import uuid
import os
from pathlib import Path
from pydantic import BaseModel

from app.models.schemas import (
    Complaint, ComplaintCreate, ComplaintStatus, LocationData
)
from app.db.store import db_store
from app.services.nlp_routing import parse_multilingual_report
from app.services.ai_vision import analyze_complaint_image
from app.services.spatial_cluster import cluster_complaints
from app.services.geo_intelligence import resolve_geolocation
from app.services.websocket_manager import notify_complaint_created, notify_status_changed

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload-media")
async def upload_complaint_media(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif", "video/mp4"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file MIME type '{file.content_type}'. Allowed types: {allowed_types}"
        )

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum limit of 10MB.")

    ext = Path(file.filename).suffix or ".jpg"
    filename = f"media-{uuid.uuid4().hex[:10]}{ext}"
    dest_path = UPLOAD_DIR / filename

    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    return {
        "message": "File uploaded successfully",
        "file_url": f"/uploads/{filename}",
        "filename": filename,
        "content_type": file.content_type,
        "size_bytes": len(file_bytes)
    }

COMMENTS_STORE: Dict[str, List[Dict[str, Any]]] = {}
ATTACHMENTS_STORE: Dict[str, List[Dict[str, Any]]] = {}

# Authoritative Lifecycle State Machine Transition Rules
VALID_TRANSITIONS: Dict[ComplaintStatus, Set[ComplaintStatus]] = {
    ComplaintStatus.SUBMITTED: {ComplaintStatus.AI_ANALYSIS, ComplaintStatus.VERIFIED, ComplaintStatus.ASSIGNED, ComplaintStatus.REJECTED},
    ComplaintStatus.AI_ANALYSIS: {ComplaintStatus.VERIFIED, ComplaintStatus.ASSIGNED, ComplaintStatus.REJECTED},
    ComplaintStatus.VERIFIED: {ComplaintStatus.ASSIGNED, ComplaintStatus.REJECTED},
    ComplaintStatus.ASSIGNED: {ComplaintStatus.IN_PROGRESS, ComplaintStatus.REJECTED},
    ComplaintStatus.IN_PROGRESS: {ComplaintStatus.AI_VERIFICATION, ComplaintStatus.CITIZEN_CONFIRMATION, ComplaintStatus.RESOLVED, ComplaintStatus.REJECTED},
    ComplaintStatus.AI_VERIFICATION: {ComplaintStatus.CITIZEN_CONFIRMATION, ComplaintStatus.RESOLVED, ComplaintStatus.REJECTED},
    ComplaintStatus.CITIZEN_CONFIRMATION: {ComplaintStatus.CLOSED, ComplaintStatus.REOPENED},
    ComplaintStatus.RESOLVED: {ComplaintStatus.CLOSED, ComplaintStatus.REOPENED},
    ComplaintStatus.CLOSED: {ComplaintStatus.REOPENED},
    ComplaintStatus.REOPENED: {ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS, ComplaintStatus.REJECTED},
    ComplaintStatus.REJECTED: {ComplaintStatus.REOPENED}
}

def validate_status_transition(current_status: ComplaintStatus, new_status: ComplaintStatus):
    if current_status == new_status:
        return
    allowed = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid lifecycle transition from '{current_status.value}' to '{new_status.value}'. Allowed transitions: {[s.value for s in allowed]}"
        )

class StatusUpdateRequest(BaseModel):
  status: str
  notes: Optional[str] = "Status updated"

class ReassignRequest(BaseModel):
  department: Optional[str] = None
  ward: Optional[str] = None
  officer_assigned: Optional[str] = None
  team: Optional[str] = None

class CommentRequest(BaseModel):
  author: str
  comment_type: str = "internal"
  text: str

class AttachmentRequest(BaseModel):
  attachment_type: str = "image"
  file_url: str
  description: Optional[str] = "Attached evidence file"

class WhatsAppSimulateRequest(BaseModel):
  sender_phone: Optional[str] = "+91 98765 43210"
  message_text: Optional[str] = "Huge pothole crater near college gate"
  media_url: Optional[str] = "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop"

@router.post("", response_model=Complaint)
def create_complaint(payload: ComplaintCreate):
    comp_id = f"c-{uuid.uuid4().hex[:6]}"
    tracking_num = f"CL-NK-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"

    resolved_loc = resolve_geolocation(
        payload.location.lat,
        payload.location.lng,
        payload.location.ward or "Ward 63"
    )

    nlp_result = parse_multilingual_report(
        payload.description,
        payload.voice_transcript or ""
    )

    # Bug 10 Fix: Only pass image_url / image photo base64 to computer vision analysis (never audio base64)
    image_input = payload.image_url if payload.image_url else None

    cv_result = analyze_complaint_image(
        image_input,
        payload.description if image_input else ""
    )

    new_complaint = Complaint(
        id=comp_id,
        tracking_number=tracking_num,
        title=payload.title or nlp_result["title"],
        description=payload.description,
        media_type=payload.media_type,
        category=nlp_result["category"],
        department=nlp_result["department"],
        priority=nlp_result["priority"],
        priority_reason=nlp_result["priority_reason"],
        status=ComplaintStatus.SUBMITTED,
        location=resolved_loc,
        image_url=payload.image_url,
        video_url=payload.video_url,
        voice_transcript=payload.voice_transcript,
        ai_detection=cv_result,
        structured_understanding=nlp_result["structured_understanding"],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        status_history=[{
            "status": ComplaintStatus.SUBMITTED.value,
            "timestamp": datetime.now().isoformat(),
            "actor": "Citizen",
            "notes": "Multimodal issue report submitted"
        }]
    )

    all_complaints = list(db_store.complaints.values()) + [new_complaint]
    clusters = cluster_complaints(all_complaints)

    # Bug 9 Fix: Spatial clustering sets cluster_id without overriding status to IN_PROGRESS prematurely
    for cl in clusters:
        if new_complaint.id in cl.report_ids:
            new_complaint.cluster_id = cl.cluster_id
            break

    db_store.add_complaint(new_complaint)
    notify_complaint_created(new_complaint)
    return new_complaint

@router.post("/whatsapp-simulate")
def simulate_whatsapp_bot_message(req: WhatsAppSimulateRequest):
    return process_incoming_whatsapp_message(
        sender_phone=req.sender_phone,
        message_text=req.message_text,
        media_url=req.media_url
    )

@router.get("", response_model=List[Complaint])
def get_complaints(
    ward: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    complaints = db_store.get_all_complaints()
    if ward:
        complaints = [c for c in complaints if c.location.ward.lower() == ward.lower()]
    if status:
        complaints = [c for c in complaints if c.status.value.lower() == status.lower()]
    if category:
        complaints = [c for c in complaints if c.category.value.lower() == category.lower()]
    return complaints

@router.get("/{complaint_id}", response_model=Complaint)
def get_complaint_detail(complaint_id: str):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@router.put("/{complaint_id}/status")
def update_complaint_status(complaint_id: str, req: StatusUpdateRequest):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    status_map = {
        "submitted": ComplaintStatus.SUBMITTED,
        "ai_analysis": ComplaintStatus.AI_ANALYSIS,
        "verified": ComplaintStatus.VERIFIED,
        "assigned": ComplaintStatus.ASSIGNED,
        "in_progress": ComplaintStatus.IN_PROGRESS,
        "resolved": ComplaintStatus.RESOLVED,
        "ai_verification": ComplaintStatus.AI_VERIFICATION,
        "citizen_confirmation": ComplaintStatus.CITIZEN_CONFIRMATION,
        "closed": ComplaintStatus.CLOSED,
        "reopened": ComplaintStatus.REOPENED,
        "rejected": ComplaintStatus.REJECTED
    }

    st_key = req.status.lower()
    if st_key not in status_map:
        # Bug 7 Fix: Reject invalid status instead of returning dummy success
        raise HTTPException(
            status_code=400,
            detail=f"Invalid complaint status '{req.status}'. Valid statuses: {list(status_map.keys())}"
        )

    new_st = status_map[st_key]
    
    # Bug 8 Fix: Validate workflow transition
    validate_status_transition(complaint.status, new_st)

    complaint.status = new_st
    now_iso = datetime.now().isoformat()
    complaint.updated_at = now_iso
    complaint.status_history.append({
        "status": complaint.status.value,
        "timestamp": now_iso,
        "actor": "System / Officer",
        "notes": req.notes or f"Status updated to {complaint.status.value}"
    })
    db_store.update_complaint(complaint)
    notify_status_changed(complaint_id, complaint.status.value, complaint.tracking_number)

    return {"status": "success", "new_status": complaint.status.value, "notes": req.notes}

@router.post("/{complaint_id}/reopen")
def reopen_complaint(complaint_id: str, reason: str = Body(..., embed=True)):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    validate_status_transition(complaint.status, ComplaintStatus.REOPENED)

    complaint.status = ComplaintStatus.REOPENED
    now_iso = datetime.now().isoformat()
    complaint.updated_at = now_iso
    complaint.status_history.append({
        "status": complaint.status.value,
        "timestamp": now_iso,
        "actor": "Citizen",
        "notes": f"⚠️ Issue Reopened: {reason}"
    })
    db_store.update_complaint(complaint)

    if complaint_id not in COMMENTS_STORE:
        COMMENTS_STORE[complaint_id] = []
    COMMENTS_STORE[complaint_id].append({
        "author": "Citizen / System",
        "type": "citizen",
        "text": f"⚠️ Issue Reopened: {reason}",
        "timestamp": now_iso
    })

    return {"message": "Issue successfully reopened and escalated to supervisor.", "status": complaint.status.value}

@router.put("/{complaint_id}/assign")
def assign_reassign_complaint(complaint_id: str, req: ReassignRequest):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    validate_status_transition(complaint.status, ComplaintStatus.ASSIGNED)

    if req.department: complaint.department = req.department
    if req.officer_assigned: complaint.officer_assigned = req.officer_assigned
    if req.ward: complaint.location.ward = req.ward
    if req.team: complaint.team_assigned = req.team

    complaint.status = ComplaintStatus.ASSIGNED
    now_iso = datetime.now().isoformat()
    complaint.updated_at = now_iso
    complaint.status_history.append({
        "status": complaint.status.value,
        "timestamp": now_iso,
        "actor": "Supervisor",
        "notes": f"Assigned to {complaint.department} ({complaint.officer_assigned or 'Officer'})"
    })
    db_store.update_complaint(complaint)

    return {
        "message": "Complaint reassignment updated",
        "department": complaint.department,
        "officer_assigned": complaint.officer_assigned,
        "ward": complaint.location.ward,
        "team": complaint.team_assigned
    }

@router.post("/{complaint_id}/comments")
def add_comment(complaint_id: str, req: CommentRequest):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint with ID '{complaint_id}' not found")

    c_entry = {
        "id": f"comment-{uuid.uuid4().hex[:6]}",
        "author": req.author,
        "type": req.comment_type,
        "text": req.text,
        "timestamp": datetime.now().isoformat()
    }
    db_store.add_comment(complaint_id, c_entry)
    return {"message": "Comment added", "comment": c_entry}

@router.get("/{complaint_id}/comments")
def get_comments(complaint_id: str):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint with ID '{complaint_id}' not found")
    return {"comments": db_store.get_comments(complaint_id)}

@router.post("/{complaint_id}/attachments")
def add_attachment(complaint_id: str, req: AttachmentRequest):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint with ID '{complaint_id}' not found")

    a_entry = {
        "id": f"att-{uuid.uuid4().hex[:6]}",
        "type": req.attachment_type,
        "file_url": req.file_url,
        "description": req.description,
        "timestamp": datetime.now().isoformat()
    }
    db_store.add_attachment(complaint_id, a_entry)
    return {"message": "Attachment uploaded", "attachment": a_entry}

@router.get("/{complaint_id}/attachments")
def get_attachments(complaint_id: str):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint with ID '{complaint_id}' not found")
    return {"attachments": db_store.get_attachments(complaint_id)}

@router.post("/{complaint_id}/citizen-confirm")
def confirm_resolution(complaint_id: str, action: str = Query(..., pattern="^(CONFIRMED|DISPUTED)$")):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint or not complaint.verification_result:
        raise HTTPException(status_code=400, detail="No resolution verification record found for this complaint.")

    complaint.verification_result.citizen_confirmation = action
    if action == "CONFIRMED":
        validate_status_transition(complaint.status, ComplaintStatus.CLOSED)
        complaint.status = ComplaintStatus.CLOSED
    else:
        validate_status_transition(complaint.status, ComplaintStatus.REOPENED)
        complaint.status = ComplaintStatus.REOPENED

    db_store.update_complaint(complaint)
    return {"status": "success", "citizen_confirmation": action, "complaint_status": complaint.status.value}
