from fastapi.testclient import TestClient
from app.main import app
from app.db.store import db_store
from app.models.schemas import Complaint, LocationData, PriorityLevel, ComplaintStatus, ComplaintCategory

client = TestClient(app)

def setup_test_complaint():
    db_store.clear()
    c = Complaint(
        id="c-test-101",
        tracking_number="CL-101",
        title="Test Pothole Issue",
        description="Pothole near main gate",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE,
        priority=PriorityLevel.P1,
        priority_reason="High accident risk",
        status=ComplaintStatus.SUBMITTED,
        location=LocationData(
            lat=19.9975,
            lng=73.7898,
            address="College Road",
            city="Nashik",
            ward="Ward 63"
        )
    )
    db_store.add_complaint(c)
    return c

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_get_complaints():
    setup_test_complaint()
    res = client.get("/api/complaints/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1

def test_submit_complaint():
    db_store.clear()
    payload = {
        "description": "Large road defect near college gate",
        "media_type": "text",
        "location": {
            "lat": 19.9975,
            "lng": 73.7898,
            "address": "College Road",
            "city": "Nashik",
            "ward": "Ward 63"
        }
    }
    res = client.post("/api/complaints/", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "tracking_number" in data

def test_get_intelligence_stats():
    setup_test_complaint()
    res = client.get("/api/intelligence/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_reports" in data
    assert data["total_reports"] >= 1
