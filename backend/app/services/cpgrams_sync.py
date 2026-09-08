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
    loc = getattr(complaint, "location", None)
    lat = getattr(loc, "lat", getattr(loc, "latitude", 19.9975)) if loc else 19.9975
    lng = getattr(loc, "lng", getattr(loc, "longitude", 73.7898)) if loc else 73.7898
    address = getattr(loc, "address", "Central District") if loc else "Central District"
    ward = getattr(loc, "ward", "Ward 63") if loc else "Ward 63"

    tn = getattr(complaint, "tracking_number", "CL-NK-2026-00101")
    cat = getattr(complaint, "category", "Road Infrastructure")
    cat_val = cat.value if hasattr(cat, 'value') else str(cat)

    pri = getattr(complaint, "priority", "P2 — High")
    pri_val = pri.value if hasattr(pri, 'value') else str(pri)

    return {
        "cpgrams_registration_id": f"GOV-IN-2026-CPG-{tn.replace('CL-NK-', '')}",
        "ministry_department": "Ministry of Urban Affairs & Housing / Public Works Department",
        "state": "Maharashtra",
        "district": "Central District",
        "complainant_category": "Citizen Grievance",
        "grievance_details": {
            "local_tracking_number": tn,
            "category": cat_val,
            "title": getattr(complaint, "title", "Civic Grievance"),
            "description": getattr(complaint, "description", ""),
            "location": f"{address}, {ward}",
            "coordinates": f"{lat}, {lng}",
            "priority": pri_val
        },
        "sync_status": "CPGRAMS_EXPORT_DOSSIER_GENERATED",
        "timestamp": datetime.now().isoformat()
    }
