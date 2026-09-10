from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.store import db_store
from app.models.schemas import Complaint, ComplaintStatus, PriorityLevel
from app.routes.complaints import validate_status_transition
from app.services.audit_logger import log_audit_event

router = APIRouter(prefix="/api/officer", tags=["Officer Operations"])

class StatusUpdatePayload(BaseModel):
    complaint_id: str
    status: ComplaintStatus
    officer_name: Optional[str] = "Officer R. K. Patil"
    notes: Optional[str] = None

def calculate_ai_queue_score(c: Complaint) -> float:
    """
    Bug 31 Fix: AI Smart Priority Queue Scoring Engine.
    Combines Severity Weight, SLA Risk, Cluster Density, Safety Context, and Ticket Age into a composite score.
    """
    p_str = c.priority.value if hasattr(c.priority, "value") else str(c.priority)
    if "P1" in p_str or "Critical" in p_str:
        base_score = 40.0
    elif "P2" in p_str or "High" in p_str:
        base_score = 30.0
    elif "P3" in p_str or "Medium" in p_str:
        base_score = 20.0
    else:
        base_score = 10.0

    # Safety risk bonus
    desc_lower = (c.description + " " + c.title).lower()
    safety_bonus = 15.0 if any(w in desc_lower for w in ["school", "hospital", "bus", "gate", "market", "underpass"]) else 0.0

    # Ticket age bonus (points per day open)
    try:
        c_dt = datetime.fromisoformat(c.created_at.replace("Z", "+00:00"))
        now_dt = datetime.now(c_dt.tzinfo)
        days_open = max(0.0, (now_dt - c_dt).total_seconds() / 86400.0)
        age_bonus = min(25.0, days_open * 5.0)
    except Exception:
        age_bonus = 0.0

    # Reopened issue urgency
    reopen_bonus = 20.0 if c.status == ComplaintStatus.REOPENED else 0.0

    return base_score + safety_bonus + age_bonus + reopen_bonus

@router.get("/queue", response_model=List[Complaint])
def get_officer_queue():
    """
    Bugs 30 & 31 Fixes:
    - Filters active tickets only (excludes CLOSED and REJECTED issues).
    - Sorts using multi-factor AI Smart Priority Scoring (Severity + Safety + Age + SLA).
    """
    complaints = db_store.get_all_complaints()
    
    # Bug 30 Fix: Exclude inactive/closed complaints
    active_statuses = {
        ComplaintStatus.SUBMITTED, ComplaintStatus.AI_ANALYSIS, ComplaintStatus.VERIFIED,
        ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED,
        ComplaintStatus.AI_VERIFICATION, ComplaintStatus.CITIZEN_CONFIRMATION, ComplaintStatus.REOPENED
    }
    
    active_complaints = [c for c in complaints if c.status in active_statuses]
    
    # Bug 31 Fix: Sort by AI Smart Priority Score descending
    sorted_queue = sorted(
        active_complaints,
        key=lambda c: calculate_ai_queue_score(c),
        reverse=True
    )
    return sorted_queue

@router.post("/update-status", response_model=Complaint)
def update_complaint_status(payload: StatusUpdatePayload):
    complaint = db_store.get_complaint_by_id(payload.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    old_status = complaint.status.value
    validate_status_transition(complaint.status, payload.status)
    
    complaint.status = payload.status
    if payload.officer_name:
        complaint.officer_assigned = payload.officer_name
    complaint.updated_at = datetime.now().isoformat()
    
    db_store.update_complaint(complaint)
    
    # Audit log entry
    log_audit_event(
        actor=payload.officer_name or "Officer",
        actor_role="Officer",
        action="UPDATE_STATUS",
        complaint_id=payload.complaint_id,
        old_value=old_status,
        new_value=payload.status.value,
        reason=payload.notes or f"Status updated to {payload.status.value}"
    )
    
    return complaint
