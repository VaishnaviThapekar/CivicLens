from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.store import db_store
from app.models.schemas import Complaint, ComplaintStatus, PriorityLevel

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
    
    # Priority sorting weights
    p_weight = {
        PriorityLevel.P1: 1,
        PriorityLevel.P2: 2,
        PriorityLevel.P3: 3,
        PriorityLevel.P4: 4
    }
    
    sorted_queue = sorted(
        complaints,
        key=lambda c: (p_weight.get(c.priority, 5), c.created_at),
        reverse=False
    )
    return sorted_queue

@router.post("/update-status", response_model=Complaint)
def update_complaint_status(payload: StatusUpdatePayload):
    complaint = db_store.get_complaint_by_id(payload.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = payload.status
    if payload.officer_name:
        complaint.officer_assigned = payload.officer_name
    complaint.updated_at = datetime.now().isoformat()
    
    db_store.update_complaint(complaint)
    return complaint
