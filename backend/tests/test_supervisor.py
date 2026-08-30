from fastapi.testclient import TestClient
from app.main import app
from app.db.store import db_store
from app.models.schemas import Complaint, LocationData, PriorityLevel, ComplaintStatus, ComplaintCategory

client = TestClient(app)

def test_get_contractor_rankings():
    db_store.clear()
    res = client.get("/api/supervisor/contractors")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert "contractor_id" in data[0]

def test_get_audit_log():
    db_store.clear()
    res = client.get("/api/supervisor/audit-log")
    assert res.status_code == 200
    data = res.json()
    assert "fake_resolution_audits" in data
    assert "citizen_appeals" in data

def test_citizen_appeal():
    db_store.clear()
    c = Complaint(
        id="c-appeal-1",
        tracking_number="CL-999",
        title="Test Issue Appeal",
        description="Road not repaired properly",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE,
        priority=PriorityLevel.P2,
        priority_reason="Citizen dispute",
        status=ComplaintStatus.RESOLVED,
        location=LocationData(
            lat=19.9975,
            lng=73.7898,
            address="College Road",
            city="Nashik",
            ward="Ward 63"
        )
    )
    db_store.add_complaint(c)

    payload = {
        "complaint_id": "c-appeal-1",
        "citizen_name": "Vaishnavi",
        "reason": "Pothole was only partially filled with loose gravel."
    }
    res = client.post("/api/supervisor/appeal-resolution", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    updated = db_store.get_complaint_by_id("c-appeal-1")
    assert updated.status == ComplaintStatus.REOPENED
