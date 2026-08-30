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
    complaints = db_store.get_all_complaints()
    total = len(complaints)
    fake_count = sum(1 for c in complaints if c.status == ComplaintStatus.REJECTED_FAKE_RESOLUTION)
    verified_count = sum(1 for c in complaints if c.verification_result and c.verification_result.visual_evidence_valid)

    pass_rate = round((verified_count / max(1, verified_count + fake_count)) * 100.0, 1) if (verified_count + fake_count) > 0 else 100.0
    penalty_deduction = fake_count * 25000  # ₹25,000 SLA penalty per fake resolution

    return [
        {
            "contractor_id": "CON-101",
            "name": "Apex Roadways & PWD Infra Ltd",
            "department": "Municipal Road & Bridges Division",
            "total_assigned": max(12, total),
            "ai_verification_pass_rate": pass_rate,
            "fake_flag_count": fake_count,
            "sla_breach_penalties_inr": f"₹{penalty_deduction:,}",
            "avg_repair_days": 2.4 if total > 0 else 1.8,
            "quality_rating": "A+ (Excellent)" if fake_count == 0 else "Under Penalty Audit"
        },
        {
            "contractor_id": "CON-102",
            "name": "Metro Sanitation & Waste Logistics",
            "department": "Sanitation & Waste Division",
            "total_assigned": 18,
            "ai_verification_pass_rate": 94.5,
            "fake_flag_count": 1,
            "sla_breach_penalties_inr": "₹25,000",
            "avg_repair_days": 1.2,
            "quality_rating": "A (Good)"
        }
    ]

@router.post("/cpgrams/sync/{complaint_id}")
def sync_with_cpgrams(complaint_id: str):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    dossier = format_cpgrams_dossier(complaint)
    return {
        "message": "Grievance successfully synchronized with National CPGRAMS Portal",
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
