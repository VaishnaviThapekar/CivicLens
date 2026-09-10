import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes import auth
from app.routes.auth import create_access_token, USERS_DB
from app.db.store import db_store
from app.models.schemas import Complaint, ComplaintStatus, LocationData, ComplaintCategory, PriorityLevel
from app.services.ai_vision import verify_resolution

client = TestClient(app)

def get_citizen_token(email="citizen@civiclens.org", user_id="usr-citizen-001"):
    return create_access_token(email, "Citizen", user_id)

def get_other_citizen_token():
    USERS_DB["other_citizen@civiclens.org"] = {
        "user_id": "usr-citizen-002",
        "email": "other_citizen@civiclens.org",
        "full_name": "Other Citizen",
        "role": "Citizen"
    }
    return create_access_token("other_citizen@civiclens.org", "Citizen", "usr-citizen-002")

def get_officer_token(email="officer@civiclens.org", user_id="usr-officer-001"):
    return create_access_token(email, "Officer", user_id)

def get_other_officer_token():
    USERS_DB["other_officer@civiclens.org"] = {
        "user_id": "usr-officer-002",
        "email": "other_officer@civiclens.org",
        "full_name": "Other Officer",
        "role": "Officer"
    }
    return create_access_token("other_officer@civiclens.org", "Officer", "usr-officer-002")

def setup_test_complaint():
    comp_id = "c-sec-v5-001"
    complaint = Complaint(
        id=comp_id,
        tracking_number="CL-NK-2026-SECV5",
        title="Test Security Vulnerability Issue",
        description="Pothole near street corner",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE,
        department="Road Department",
        priority=PriorityLevel.P3,
        priority_reason="Medium severity road defect",
        status=ComplaintStatus.RESOLVED,
        location=LocationData(lat=19.9975, lng=73.7898, city="Nashik", ward="Ward 63"),
        submitted_by="citizen@civiclens.org",
        submitted_by_user_id="usr-citizen-001",
        submitted_by_email="citizen@civiclens.org",
        officer_assigned="Officer R. K. Patil",
        image_url="https://example.com/before.jpg",
        created_at="2026-09-10T10:00:00",
        updated_at="2026-09-10T10:00:00",
        status_history=[]
    )
    db_store.add_complaint(complaint)
    return comp_id

def test_reopen_non_owner_forbidden():
    comp_id = setup_test_complaint()
    other_token = get_other_citizen_token()
    res = client.post(f"/api/complaints/{comp_id}/reopen", json={"reason": "Still broken"}, headers={"Authorization": f"Bearer {other_token}"})
    assert res.status_code == 403
    assert "Only the complaint author or a Supervisor/Admin" in res.json()["detail"]

def test_citizen_feedback_non_owner_forbidden():
    comp_id = setup_test_complaint()
    other_token = get_other_citizen_token()
    res = client.post("/api/verification/citizen-feedback", json={"complaint_id": comp_id, "feedback": "NO_STILL_EXISTS"}, headers={"Authorization": f"Bearer {other_token}"})
    assert res.status_code == 403
    assert "Only the complaint author or a Supervisor/Admin" in res.json()["detail"]

def test_citizen_confirm_non_owner_forbidden():
    comp_id = setup_test_complaint()
    other_token = get_other_citizen_token()
    res = client.post(f"/api/complaints/{comp_id}/citizen-confirm?action=DISPUTED", headers={"Authorization": f"Bearer {other_token}"})
    assert res.status_code == 403
    assert "Only the complaint author or a Supervisor/Admin" in res.json()["detail"]

def test_officer_status_update_wrong_assignment_forbidden():
    comp_id = setup_test_complaint()
    other_officer_token = get_other_officer_token()
    res = client.put(f"/api/complaints/{comp_id}/status", json={"status": "in_progress", "notes": "Officer updating"}, headers={"Authorization": f"Bearer {other_officer_token}"})
    assert res.status_code == 403
    assert "not authorized to update status for a complaint assigned to" in res.json()["detail"]

def test_public_get_complaints_sanitized():
    setup_test_complaint()
    res = client.get("/api/complaints")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        first = data[0]
        assert "is_public_view" in first
        assert "submitted_by" not in first or first.get("is_public_view") is True

def test_whatsapp_simulate_requires_auth():
    res = client.post("/api/complaints/whatsapp-simulate", json={"sender_phone": "+91 99999 88888", "message_text": "Water pipeline burst"})
    assert res.status_code == 401

def test_ai_verification_missing_before_image_inconclusive():
    res = verify_resolution("c-test-v5", "Officer PWD", "after_repair.jpg", "Repaired patch", gps_lat=19.9975, gps_lng=73.7898, before_image=None)
    assert res.visual_evidence_valid is False
    assert res.ai_verification_score == 0.0
    assert res.confidence == 0.0
    assert "Inconclusive" in res.message
