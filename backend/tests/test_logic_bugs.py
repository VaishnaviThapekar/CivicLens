import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.store import db_store
from app.models.schemas import Complaint, LocationData, PriorityLevel, ComplaintStatus, ComplaintCategory

client = TestClient(app)

def setup_fresh_complaint(comp_id="c-logic-001"):
    db_store.clear()
    c = Complaint(
        id=comp_id,
        tracking_number="CL-LOGIC-001",
        title="Test Waterlogging",
        description="Severe flooding near street market",
        category=ComplaintCategory.DRAINAGE_FLOODING,
        priority=PriorityLevel.P1,
        priority_reason="High flooding hazard",
        status=ComplaintStatus.SUBMITTED,
        location=LocationData(
            lat=19.9975,
            lng=73.7898,
            address="Market Street",
            city="Nashik",
            ward="Ward 63"
        )
    )
    db_store.add_complaint(c)
    return c

def test_bug5_cors_headers():
    res = client.options("/api/complaints/", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    assert res.status_code == 200
    assert "access-control-allow-origin" in res.headers

def test_bug6_datastore_persistence():
    setup_fresh_complaint("c-persist-999")
    assert db_store.get_complaint_by_id("c-persist-999") is not None
    # Verify store JSON file exists on disk
    assert db_store.persistence_file.exists()

def test_bug7_invalid_status_rejection():
    from app.routes.auth import create_access_token
    officer_token = create_access_token("officer@civiclens.org", "Officer", "usr-off-1")
    c = setup_fresh_complaint("c-bug7")
    res = client.put(f"/api/complaints/{c.id}/status", json={"status": "invalid_status_xyz"}, headers={"Authorization": f"Bearer {officer_token}"})
    assert res.status_code == 400
    assert "Invalid complaint status" in res.json()["detail"]

def test_bug8_invalid_workflow_transition():
    from app.routes.auth import create_access_token
    officer_token = create_access_token("officer@civiclens.org", "Officer", "usr-off-1")
    c = setup_fresh_complaint("c-bug8")
    # SUBMITTED -> CLOSED is invalid direct transition
    res = client.put(f"/api/complaints/{c.id}/status", json={"status": "closed"}, headers={"Authorization": f"Bearer {officer_token}"})
    assert res.status_code == 400
    assert "Invalid lifecycle transition" in res.json()["detail"]

    # Valid transition SUBMITTED -> ASSIGNED
    res_valid = client.put(f"/api/complaints/{c.id}/status", json={"status": "assigned"}, headers={"Authorization": f"Bearer {officer_token}"})
    assert res_valid.status_code == 200
    assert res_valid.json()["new_status"] == "Assigned to Department"

def test_bug9_clustered_complaint_status():
    db_store.clear()
    payload = {
        "description": "Pothole near college entrance gate",
        "media_type": "text",
        "location": {
            "lat": 19.9975,
            "lng": 73.7898,
            "address": "College Road",
            "city": "Nashik",
            "ward": "Ward 63"
        }
    }
    from app.routes.auth import create_access_token
    token = create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")
    res = client.post("/api/complaints/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Submitted"  # Must remain SUBMITTED, not IN_PROGRESS

def test_bug10_audio_cv_decoupling():
    db_store.clear()
    payload = {
        "description": "Audio voice note report of broken street light",
        "media_type": "voice",
        "voice_transcript": "Streetlight near house number 4 is out",
        "audio_base64": "data:audio/mp3;base64,SUQzBAAAAAAA...",  # Audio payload
        "location": {
            "lat": 19.9975,
            "lng": 73.7898,
            "address": "College Road",
            "city": "Nashik",
            "ward": "Ward 63"
        }
    }
    from app.routes.auth import create_access_token
    token = create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")
    res = client.post("/api/complaints/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["ai_detection"] is None  # Must be None since no image payload was supplied

def test_bug11_orphan_comments_prevention():
    db_store.clear()
    res = client.post("/api/complaints/nonexistent-id-9999/comments", json={"author": "Test", "text": "Orphan comment"})
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()
