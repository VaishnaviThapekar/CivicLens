from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from pydantic import BaseModel

from app.models.schemas import (
    Complaint, ComplaintCreate, ComplaintStatus, LocationData
)
from app.db.store import db_store
from app.services.nlp_routing import parse_multilingual_report
from app.services.ai_vision import analyze_complaint_image
from app.services.spatial_cluster import cluster_complaints
from app.services.geo_intelligence import resolve_geolocation
from app.services.whatsapp_bot import process_incoming_whatsapp_message

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

COMMENTS_STORE: Dict[str, List[Dict[str, Any]]] = {}
ATTACHMENTS_STORE: Dict[str, List[Dict[str, Any]]] = {}

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
    seq_num = 1280 + len(db_store.complaints) + 1
    tracking_num = f"CL-NK-2026-00{seq_num}"

    resolved_loc = resolve_geolocation(
        payload.location.lat,
        payload.location.lng,
        payload.location.ward or "Ward 63"
    )

    nlp_result = parse_multilingual_report(
        payload.description,
        payload.voice_transcript or ""
    )

    cv_result = analyze_complaint_image(
        payload.image_url or payload.audio_base64,
        payload.description
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
        updated_at=datetime.now().isoformat()
    )

    all_complaints = list(db_store.complaints.values()) + [new_complaint]
    clusters = cluster_complaints(all_complaints)

    for cl in clusters:
        if new_complaint.id in cl.report_ids:
            new_complaint.cluster_id = cl.cluster_id
            new_complaint.status = ComplaintStatus.IN_PROGRESS
            break

    db_store.add_complaint(new_complaint)
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
        "reopened": ComplaintStatus.REOPENED
    }

    new_st = status_map.get(req.status.lower())
    if new_st:
        complaint.status = new_st
        complaint.updated_at = datetime.now().isoformat()
        db_store.update_complaint(complaint)

    return {"status": "success", "new_status": complaint.status.value, "notes": req.notes}

@router.post("/{complaint_id}/reopen")
def reopen_complaint(complaint_id: str, reason: str = Body(..., embed=True)):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.status = ComplaintStatus.REOPENED
    complaint.updated_at = datetime.now().isoformat()
    db_store.update_complaint(complaint)

    if complaint_id not in COMMENTS_STORE:
        COMMENTS_STORE[complaint_id] = []
    COMMENTS_STORE[complaint_id].append({
        "author": "Citizen / System",
        "type": "citizen",
        "text": f"⚠️ Issue Reopened: {reason}",
        "timestamp": datetime.now().isoformat()
    })

    return {"message": "Issue successfully reopened and escalated to supervisor.", "status": complaint.status.value}

@router.put("/{complaint_id}/assign")
def assign_reassign_complaint(complaint_id: str, req: ReassignRequest):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if req.department: complaint.department = req.department
    if req.officer_assigned: complaint.officer_assigned = req.officer_assigned
    if req.ward: complaint.location.ward = req.ward

    complaint.status = ComplaintStatus.ASSIGNED
    complaint.updated_at = datetime.now().isoformat()
    db_store.update_complaint(complaint)

    return {
        "message": "Complaint reassignment updated",
        "department": complaint.department,
        "officer_assigned": complaint.officer_assigned,
        "ward": complaint.location.ward
    }

@router.post("/{complaint_id}/comments")
def add_comment(complaint_id: str, req: CommentRequest):
    if complaint_id not in COMMENTS_STORE:
        COMMENTS_STORE[complaint_id] = []

    c_entry = {
        "id": f"comment-{uuid.uuid4().hex[:6]}",
        "author": req.author,
        "type": req.comment_type,
        "text": req.text,
        "timestamp": datetime.now().isoformat()
    }
    COMMENTS_STORE[complaint_id].append(c_entry)
    return {"message": "Comment added", "comment": c_entry}

@router.get("/{complaint_id}/comments")
def get_comments(complaint_id: str):
    return {"comments": COMMENTS_STORE.get(complaint_id, [])}

@router.post("/{complaint_id}/attachments")
def add_attachment(complaint_id: str, req: AttachmentRequest):
    if complaint_id not in ATTACHMENTS_STORE:
        ATTACHMENTS_STORE[complaint_id] = []

    a_entry = {
        "id": f"att-{uuid.uuid4().hex[:6]}",
        "type": req.attachment_type,
        "file_url": req.file_url,
        "description": req.description,
        "timestamp": datetime.now().isoformat()
    }
    ATTACHMENTS_STORE[complaint_id].append(a_entry)
    return {"message": "Attachment uploaded", "attachment": a_entry}

@router.get("/{complaint_id}/attachments")
def get_attachments(complaint_id: str):
    return {"attachments": ATTACHMENTS_STORE.get(complaint_id, [])}

@router.post("/{complaint_id}/citizen-confirm")
def confirm_resolution(complaint_id: str, action: str = Query(..., pattern="^(CONFIRMED|DISPUTED)$")):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint or not complaint.verification_result:
        raise HTTPException(status_code=400, detail="No resolution verification record found for this complaint.")

    complaint.verification_result.citizen_confirmation = action
    if action == "CONFIRMED":
        complaint.status = ComplaintStatus.CLOSED
    else:
        complaint.status = ComplaintStatus.REOPENED

    db_store.update_complaint(complaint)
    return {"status": "success", "citizen_confirmation": action, "complaint_status": complaint.status.value}
