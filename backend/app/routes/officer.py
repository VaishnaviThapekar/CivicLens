from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.store import db_store
from app.models.schemas import Complaint, ComplaintStatus, PriorityLevel
from app.routes.complaints import validate_status_transition

router = APIRouter(prefix="/api/officer", tags=["Officer Operations"])

class StatusUpdatePayload(BaseModel):
    complaint_id: str
    status: ComplaintStatus
    officer_name: Optional[str] = "Officer R. K. Patil"
    notes: Optional[str] = None

@router.get("/queue", response_model=List[Complaint])
def get_officer_queue():
    """
    Returns AI-prioritized queue for municipal officers.
    Sorted by P1 (Critical) -> P2 (High) -> P3 (Medium) -> P4 (Low).
    """
    complaints = db_store.get_all_complaints()
    
    def get_p_weight(p):
        p_str = p.value if hasattr(p, "value") else str(p)
        if "P1" in p_str or "Critical" in p_str: return 1
        if "P2" in p_str or "High" in p_str: return 2
        if "P3" in p_str or "Medium" in p_str: return 3
        return 4
    
    sorted_queue = sorted(
        complaints,
        key=lambda c: (get_p_weight(c.priority), c.created_at),
        reverse=False
    )
    return sorted_queue

@router.post("/update-status", response_model=Complaint)
def update_complaint_status(payload: StatusUpdatePayload):
    complaint = db_store.get_complaint_by_id(payload.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Bug 8 Fix: Enforce lifecycle state transition rules in officer portal
    validate_status_transition(complaint.status, payload.status)
    
    complaint.status = payload.status
    if payload.officer_name:
        complaint.officer_assigned = payload.officer_name
    complaint.updated_at = datetime.now().isoformat()
    
    db_store.update_complaint(complaint)
    return complaint
