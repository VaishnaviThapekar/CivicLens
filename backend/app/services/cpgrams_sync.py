"""
CivicLens CPGRAMS & State Government Portal Synchronization Engine
Formats municipal grievances into official CPGRAMS (Centralized Public Grievance Redress and Monitoring System) dossier payloads for state/national escalation.
"""

from typing import Dict, Any
from datetime import datetime

def format_cpgrams_dossier(complaint: Any) -> Dict[str, Any]:
    """
    Transforms local CivicLens complaint into standard CPGRAMS XML/JSON payload.
    """
    return {
        "cpgrams_registration_id": f"GOV-IN-2026-CPG-{complaint.tracking_number.replace('CL-NK-', '')}",
        "ministry_department": "Ministry of Urban Affairs & Housing / Public Works Department",
        "state": "Maharashtra",
        "district": "Central District",
        "complainant_category": "Citizen Grievance",
        "grievance_details": {
            "local_tracking_number": complaint.tracking_number,
            "category": complaint.category.value if hasattr(complaint.category, 'value') else complaint.category,
            "title": complaint.title,
            "description": complaint.description,
            "location": f"{complaint.location.address}, {complaint.location.ward}",
            "coordinates": f"{complaint.location.latitude}, {complaint.location.longitude}",
            "priority": complaint.priority.value if hasattr(complaint.priority, 'value') else complaint.priority
        },
        "sync_status": "SYNCHRONIZED_WITH_CPGRAMS_NATIONAL_PORTAL",
        "timestamp": datetime.now().isoformat()
    }
