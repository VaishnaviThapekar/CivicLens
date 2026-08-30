from typing import Dict, Any
from app.models.schemas import Complaint
from datetime import datetime

def generate_audit_report(complaint: Complaint) -> Dict[str, Any]:
    """
    Generates an official CPGRAMS-compatible Municipal Grievance Audit Dossier.
    """
    return {
        "document_type": "OFFICIAL MUNICIPAL CIVIC GRIEVANCE AUDIT DOSSIER",
        "cpgrams_compatible_id": f"CPG-2026-{complaint.tracking_number.replace('CL-', '')}",
        "civiclens_tracking_number": complaint.tracking_number,
        "date_generated": datetime.now().isoformat(),
        "incident_details": {
            "title": complaint.title,
            "category": complaint.category.value,
            "assigned_department": complaint.department,
            "priority": complaint.priority.value,
            "status": complaint.status.value,
            "location": {
                "address": complaint.location.address,
                "ward": complaint.location.ward,
                "coordinates": f"{complaint.location.lat}° N, {complaint.location.lng}° E"
            }
        },
        "multimodal_evidence": {
            "image_attached": bool(complaint.image_url),
            "voice_transcript_attached": bool(complaint.voice_transcript),
            "voice_transcript": complaint.voice_transcript or "N/A"
        },
        "ai_vision_inspection": {
            "object_detected": complaint.ai_detection.object_detected,
            "confidence_score": f"{int(complaint.ai_detection.confidence * 100)}%",
            "risk_level": complaint.ai_detection.risk_level,
            "road_obstruction": complaint.ai_detection.road_obstruction
        },
        "resolution_verification_audit": {
            "claimed_resolution": complaint.verification_result.claimed_resolution if complaint.verification_result else False,
            "ai_verification_score": f"{complaint.verification_result.ai_verification_score}%" if complaint.verification_result else "N/A",
            "fake_resolution_flagged": complaint.verification_result.fake_resolution_detected if complaint.verification_result else False,
            "citizen_confirmation": complaint.verification_result.citizen_confirmation if complaint.verification_result else "PENDING",
            "audit_message": complaint.verification_result.message if complaint.verification_result else "No verification run yet"
        }
    }
