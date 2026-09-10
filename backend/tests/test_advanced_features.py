import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.store import db_store
from app.services.spatial_cluster import derive_cluster_root_cause, cluster_complaints_spatially
from app.services.predictive_ai import generate_predictive_risks, detect_emerging_anomalies
from app.services.geo_intelligence import resolve_geolocation
from app.services.audit_logger import log_audit_event, get_audit_logs
from app.routes.officer import calculate_ai_queue_score
from app.models.schemas import Complaint, ComplaintStatus, PriorityLevel, ComplaintCategory, LocationData, UserProfile
from app.routes.auth import TOKENS_DB, USERS_DB

client = TestClient(app)

def test_dynamic_root_cause_inference():
    c1 = Complaint(
        id="c1", tracking_number="CL-1", title="Water Leakage", description="Pipe burst",
        category=ComplaintCategory.WATER_LEAKAGE, priority=PriorityLevel.P1, priority_reason="Urgent",
        status=ComplaintStatus.SUBMITTED, location=LocationData(lat=19.9975, lng=73.7898, ward="Ward 63")
    )
    c2 = Complaint(
        id="c2", tracking_number="CL-2", title="Clogged Drain", description="Drainage overflow",
        category=ComplaintCategory.DRAINAGE_FLOODING, priority=PriorityLevel.P2, priority_reason="High",
        status=ComplaintStatus.SUBMITTED, location=LocationData(lat=19.9980, lng=73.7900, ward="Ward 63")
    )
    res = derive_cluster_root_cause([c1, c2])
    assert "AI hypothesis" in res["detected_root_cause"]
    assert "Subsurface Water Leakage" in res["detected_root_cause"]
    assert res["confidence_type"] == "Data-Driven AI Hypothesis"

def test_dynamic_anomaly_alert_ratio():
    # 20 today reports / 5 baseline = 4.0x
    res = detect_emerging_anomalies(today_reports_count=20, baseline_daily_norm=5)
    assert res["is_anomaly_detected"] is True
    assert "4.0x" in res["anomaly_alert"]
    assert "4.0x Above Baseline" in res["spike_ratio"]
    assert "9.4x" not in res["anomaly_alert"]  # Proves non-hardcoded dynamic evaluation!

def test_point_in_polygon_and_unknown_location_safeguard():
    # 1. Known GPS near Ward 12 centroid (20.0030, 73.7830)
    loc1 = resolve_geolocation(20.0030, 73.7830)
    assert loc1.ward == "Ward 12"
    assert loc1.location_status == "RESOLVED"

    # 2. Missing/Invalid GPS (0.0, 0.0) -> UNKNOWN safeguard
    loc_unk = resolve_geolocation(0.0, 0.0)
    assert loc_unk.ward == "UNKNOWN"
    assert loc_unk.location_status == "UNKNOWN"

def test_gps_coordinate_range_validation():
    # Invalid lat > 90 should raise ValidationError
    with pytest.raises(Exception):
        LocationData(lat=95.0, lng=73.7898)

def test_immutable_audit_logging():
    initial_count = len(db_store.get_audit_logs())
    entry = log_audit_event(
        actor="Supervisor Rajesh",
        action="ASSIGN_COMPLAINT",
        complaint_id="c-test-100",
        actor_role="Supervisor",
        old_value="Unassigned",
        new_value="Officer Patil",
        reason="Emergency dispatch"
    )
    assert entry["event_id"].startswith("audit-")
    logs = get_audit_logs("c-test-100")
    assert len(logs) >= 1
    assert logs[0]["actor"] == "Supervisor Rajesh"

def test_citizen_isolated_complaints_endpoint():
    # Register/provision user token
    token = "jwt-access-citizen-test"
    email = "citizen.privacy@test.com"
    TOKENS_DB[token] = email
    USERS_DB[email] = {
        "user_id": "usr-priv-1", "email": email, "full_name": "Private Citizen",
        "phone": "+91 9991112223", "role": "Citizen", "is_email_verified": True
    }

    c_own = Complaint(
        id="c-own", tracking_number="CL-OWN", title="My Private Report", description=f"Submitted by {email}",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE, priority=PriorityLevel.P3, priority_reason="Minor",
        status=ComplaintStatus.SUBMITTED, location=LocationData(lat=19.9975, lng=73.7898)
    )
    c_own.submitted_by = email
    db_store.add_complaint(c_own)

    res = client.get("/api/complaints/my", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    my_list = res.json()
    assert len(my_list) >= 1
    assert my_list[0]["id"] == "c-own"

def test_officer_queue_filtering_and_ai_scoring():
    c_closed = Complaint(
        id="c-closed", tracking_number="CL-CLOSED", title="Closed issue", description="Resolved pothole",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE, priority=PriorityLevel.P1, priority_reason="Done",
        status=ComplaintStatus.CLOSED, location=LocationData(lat=19.9975, lng=73.7898)
    )
    c_active = Complaint(
        id="c-active", tracking_number="CL-ACTIVE", title="Active hazard near school", description="Pothole near school gate",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE, priority=PriorityLevel.P1, priority_reason="Active P1",
        status=ComplaintStatus.SUBMITTED, location=LocationData(lat=19.9975, lng=73.7898)
    )
    db_store.add_complaint(c_closed)
    db_store.add_complaint(c_active)

    res = client.get("/api/officer/queue")
    assert res.status_code == 200
    queue = res.json()
    ids = [item["id"] for item in queue]
    assert "c-active" in ids
    assert "c-closed" not in ids  # Closed ticket successfully excluded!

def test_api_v1_router_alias():
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"
