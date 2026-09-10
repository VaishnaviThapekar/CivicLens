"""
Unit test suite for CivicLens Backend Bugs 32 to 40.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.db.store import db_store
from app.models.schemas import Complaint, LocationData, ComplaintCategory, ComplaintStatus, PriorityLevel

client = TestClient(app)

def create_sample_complaint(comp_id: str, ward: str = "Ward 63", status: ComplaintStatus = ComplaintStatus.SUBMITTED, created_at: str = None, updated_at: str = None):
    now = datetime.now().isoformat()
    c_time = created_at or now
    u_time = updated_at or now

    complaint = Complaint(
        id=comp_id,
        tracking_number=f"CL-NK-{datetime.now().year}-{comp_id.upper()}",
        title=f"Test issue {comp_id}",
        description="Sample test complaint for bugs 32-40",
        media_type="image",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE,
        department="Municipal Road & Bridges Division",
        priority=PriorityLevel.P2,
        priority_reason="Test priority",
        status=status,
        location=LocationData(lat=19.9975, lng=73.7898, ward=ward),
        created_at=c_time,
        updated_at=u_time,
        status_history=[{
            "status": status.value,
            "timestamp": c_time,
            "actor": "Citizen",
            "notes": "Multimodal issue report submitted"
        }]
    )
    db_store.add_complaint(complaint)
    return complaint

def test_bug_32_ward_average_resolution_days_calculated():
    """Bug 32: Verify ward average resolution days is calculated dynamically for resolved complaints."""
    db_store.complaints.clear()

    c_time = (datetime.now() - timedelta(days=2)).isoformat()
    u_time = datetime.now().isoformat()

    create_sample_complaint("c-res-1", ward="Ward 63", status=ComplaintStatus.CLOSED, created_at=c_time, updated_at=u_time)

    res = client.get("/api/intelligence/wards")
    assert res.status_code == 200
    wards = res.json()

    w63 = next(w for w in wards if w["ward_id"] == "Ward 63")
    assert w63["resolved_count"] == 1
    # Average resolution days should be approximately 2.0 days (not 0.0)
    assert w63["avg_resolution_days"] >= 1.9

def test_bug_33_sla_config_authorization_check():
    """Bug 33: Verify SLA configuration update requires authorization header (HTTP 401/403 when unauthenticated)."""
    from app.routes.auth import create_access_token
    # Without Auth header -> HTTP 401/403 Forbidden
    res_unauth = client.put("/api/intelligence/sla/config", json={"Critical": 3})
    assert res_unauth.status_code in [401, 403]

    # With Supervisor Auth header -> HTTP 200 OK
    sup_token = create_access_token("supervisor@civiclens.org", "Supervisor", "usr-sup-1")
    res_auth = client.put("/api/intelligence/sla/config", json={"Critical": 3}, headers={"Authorization": f"Bearer {sup_token}"})
    assert res_auth.status_code == 200
    assert res_auth.json()["sla_matrix"]["Critical"] == 3

def test_bug_34_verification_status_workflow_consistency():
    """Bug 34: Verify AI verification transition status is AI_VERIFICATION (pending citizen confirmation review)."""
    from app.routes.auth import create_access_token
    comp = create_sample_complaint("c-verify-34")

    officer_token = create_access_token("officer@civiclens.org", "Officer", "usr-off-1")
    res = client.post("/api/verification/verify-resolution", json={
        "complaint_id": comp.id,
        "officer_id": "Officer Desk",
        "evidence_image_url": "https://example.com/repaired.jpg",
        "gps_lat": 19.9975,
        "gps_lng": 73.7898
    }, headers={"Authorization": f"Bearer {officer_token}"})

    assert res.status_code == 200
    updated_comp = db_store.get_complaint_by_id(comp.id)
    assert updated_comp.status == ComplaintStatus.AI_VERIFICATION

def test_bugs_35_36_dynamic_timeline_and_real_timestamps():
    """Bugs 35 & 36: Verify timeline displays only executed stages with real event timestamps."""
    from app.routes.auth import create_access_token
    comp = create_sample_complaint("c-timeline-35")

    officer_token = create_access_token("officer@civiclens.org", "Officer", "usr-off-1")
    # Perform status update
    client.put(f"/api/complaints/{comp.id}/status", json={"status": "assigned", "notes": "Assigned to PWD team"}, headers={"Authorization": f"Bearer {officer_token}"})

    res = client.get(f"/api/verification/{comp.id}/timeline")
    assert res.status_code == 200
    timeline = res.json()["timeline"]

    # Should only contain 2 executed stages: SUBMITTED and ASSIGNED
    assert len(timeline) == 2
    assert timeline[0]["stage"] in ["Submitted", "submitted"]
    assert timeline[1]["stage"] in ["Assigned to Department", "assigned"]
    assert "date" in timeline[0]
    assert "date" in timeline[1]

def test_bug_37_verification_verify_alias_endpoint():
    """Bug 37: Verify /api/verification/verify endpoint alias resolves without HTTP 404."""
    from app.routes.auth import create_access_token
    comp = create_sample_complaint("c-verify-37")

    officer_token = create_access_token("officer@civiclens.org", "Officer", "usr-off-1")
    res = client.post("/api/verification/verify", json={
        "complaint_id": comp.id,
        "officer_id": "Officer PWD-42",
        "evidence_image_url": "https://example.com/repaired.jpg",
        "gps_lat": 19.9975,
        "gps_lng": 73.7898
    }, headers={"Authorization": f"Bearer {officer_token}"})

    assert res.status_code == 200
    assert res.json()["visual_evidence_valid"] is True
