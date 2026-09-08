from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.db.store import db_store
from app.models.schemas import Complaint, ComplaintStatus
from app.services.cpgrams_sync import format_cpgrams_dossier

router = APIRouter(prefix="/api/supervisor", tags=["Supervisor & Contractor Audit"])

class CitizenAppealSubmission(BaseModel):
    complaint_id: str
    citizen_name: str = "Anonymous Citizen"
    reason: str
    supporting_photo_url: Optional[str] = None

class EmergencyBroadcastPayload(BaseModel):
    zone: str = "Zone 4"
    title: str
    message: str
    severity: str = "HIGH"

@router.get("/contractors")
def get_contractor_rankings():
    """
    Bug 48 Fix: Derive contractor analytics metrics dynamically from actual complaints in db_store.
    """
    complaints = db_store.get_all_complaints()
    contractor_defs = [
        {"id": "CON-101", "name": "Apex Roadways & PWD Infra Ltd", "dept_keyword": "road"},
        {"id": "CON-102", "name": "Metro Sanitation & Waste Logistics", "dept_keyword": "sanitation"},
        {"id": "CON-103", "name": "Lumina Electrical Grid Corp", "dept_keyword": "electrical"},
        {"id": "CON-104", "name": "AquaFlow Water Systems Ltd", "dept_keyword": "water"}
    ]

    rankings = []
    for c_def in contractor_defs:
        key = c_def["dept_keyword"]
        dept_c = [c for c in complaints if key in (c.department or "").lower() or key in (c.category.value if hasattr(c.category, 'value') else str(c.category)).lower()]
        
        assigned = len(dept_c)
        fakes = sum(1 for c in dept_c if c.status == ComplaintStatus.REJECTED_FAKE_RESOLUTION)
        verified = sum(1 for c in dept_c if c.verification_result and c.verification_result.visual_evidence_valid)
        
        pass_rate = round((verified / max(1, verified + fakes)) * 100.0, 1) if (verified + fakes) > 0 else 100.0
        penalty_deduction = fakes * 25000

        # Calculate avg repair days for resolved complaints in department
        resolved_c = [c for c in dept_c if c.status in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED, ComplaintStatus.AI_VERIFICATION]]
        if resolved_c:
            days_list = []
            for c in resolved_c:
                try:
                    c_dt = datetime.fromisoformat(c.created_at.replace("Z", "+00:00"))
                    u_dt = datetime.fromisoformat(c.updated_at.replace("Z", "+00:00"))
                    days_list.append(max(0.1, (u_dt - c_dt).total_seconds() / 86400.0))
                except Exception:
                    days_list.append(1.5)
            avg_days = round(sum(days_list) / len(days_list), 1)
        else:
            avg_days = 0.0

        rankings.append({
            "contractor_id": c_def["id"],
            "name": c_def["name"],
            "department": f"Municipal {key.capitalize()} Cell",
            "total_assigned": assigned,
            "ai_verification_pass_rate": pass_rate,
            "fake_flag_count": fakes,
            "sla_breach_penalties_inr": f"₹{penalty_deduction:,}",
            "avg_repair_days": avg_days,
            "quality_rating": "A+ (Excellent)" if fakes == 0 else "Under Penalty Audit"
        })

    return rankings

@router.post("/cpgrams/sync/{complaint_id}")
def sync_with_cpgrams(complaint_id: str):
    """
    Bug 49 Fix: Clarify CPGRAMS dossier export formatting response wording.
    """
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    dossier = format_cpgrams_dossier(complaint)
    return {
        "message": "CPGRAMS-compliant grievance dossier generated successfully. Ready for National CPGRAMS Portal submission.",
        "cpgrams_dossier": dossier
    }

@router.get("/audit-log")
def get_supervisor_audit_log():
    complaints = db_store.get_all_complaints()
    fake_flags = [c for c in complaints if c.status == ComplaintStatus.REJECTED_FAKE_RESOLUTION]
    reopened = [c for c in complaints if c.status == ComplaintStatus.REOPENED]

    return {
        "fake_resolution_audits": [
            {
                "complaint_id": c.id,
                "tracking_number": c.tracking_number,
                "officer_assigned": c.officer_assigned or "Assigned Officer",
                "ai_score": c.verification_result.ai_verification_score if c.verification_result else 0.0,
                "reason": c.verification_result.message if c.verification_result else "Mismatched evidence",
                "flagged_at": c.updated_at
            }
            for c in fake_flags
        ],
        "citizen_appeals": [
            {
                "complaint_id": c.id,
                "tracking_number": c.tracking_number,
                "title": c.title,
                "ward": c.location.ward,
                "status": c.status.value
            }
            for c in reopened
        ]
    }

@router.post("/appeal-resolution")
def submit_citizen_appeal(payload: CitizenAppealSubmission):
    complaint = db_store.get_complaint_by_id(payload.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.status = ComplaintStatus.REOPENED
    if complaint.verification_result:
        complaint.verification_result.citizen_confirmation = "DISPUTED"
        complaint.verification_result.message = f"🔴 CITIZEN APPEAL LODGED: '{payload.reason}'"

    db_store.update_complaint(complaint)
    return {
        "status": "success",
        "message": "Appeal lodged successfully. Issue escalated to Municipal Supervisor Audit Queue.",
        "complaint_status": complaint.status.value
    }
