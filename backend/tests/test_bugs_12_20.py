"""
Unit test suite for CivicLens Backend & AI Engine Bugs 12 to 20.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.db.store import db_store
from app.routes.auth import create_access_token
from app.models.schemas import Complaint, LocationData, ComplaintCategory, ComplaintStatus, PriorityLevel
from app.services.ai_vision import analyze_image, calculate_image_ssim, verify_resolution
from app.services.spatial_cluster import cluster_complaints_spatially

client = TestClient(app)

def create_sample_complaint(comp_id: str, lat: float = 19.9975, lng: float = 73.7898, category: str = "Road Infrastructure"):
    cat_enum = ComplaintCategory.ROAD_INFRASTRUCTURE
    for c in ComplaintCategory:
        if c.value == category:
            cat_enum = c
            break

    complaint = Complaint(
        id=comp_id,
        tracking_number=f"CL-NK-{datetime.now().year}-TEST01",
        title=f"Sample issue {comp_id}",
        description="Pothole crater on road near college gate",
        media_type="image",
        category=cat_enum,
        department="Municipal Road & Bridges Division",
        priority=PriorityLevel.P2,
        priority_reason="Test priority",
        status=ComplaintStatus.SUBMITTED,
        location=LocationData(lat=lat, lng=lng, ward="Ward 63"),
        image_url="https://example.com/pothole.jpg"
    )
    db_store.add_complaint(complaint)
    return complaint

def test_bug_12_orphan_attachments_prevented():
    """Bug 12: Verify HTTP 404 is returned when adding or fetching attachments for nonexistent complaints."""
    res_post = client.post("/api/complaints/c-nonexistent-99999/attachments", json={
        "attachment_type": "image",
        "file_url": "https://example.com/evidence.jpg",
        "description": "Orphan attachment test"
    })
    assert res_post.status_code == 404
    assert "not found" in res_post.json()["detail"].lower()

    res_get = client.get("/api/complaints/c-nonexistent-99999/attachments")
    assert res_get.status_code == 404

def test_bug_13_team_assignment_field_persisted():
    """Bug 13: Verify team assignment is persisted in Complaint schema and returned in response."""
    comp = create_sample_complaint("c-test-team-13")

    reassign_payload = {
        "department": "Municipal PWD",
        "officer_assigned": "Officer Rajesh",
        "team": "Alpha Rapid Action Squad 4"
    }

    supervisor_token = create_access_token("supervisor@civiclens.org", "Supervisor", "usr-supervisor-001")
    res = client.put(f"/api/complaints/{comp.id}/assign", json=reassign_payload, headers={"Authorization": f"Bearer {supervisor_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["team"] == "Alpha Rapid Action Squad 4"

    fetched = db_store.get_complaint_by_id(comp.id)
    assert fetched.team_assigned == "Alpha Rapid Action Squad 4"

def test_bug_14_dynamic_unique_tracking_number():
    """Bug 14: Verify dynamic tracking number generation with current year and unique hash."""
    payload = {
        "description": "Huge crater on main road",
        "media_type": "image",
        "image_url": "https://example.com/pothole.jpg",
        "location": {"lat": 19.9975, "lng": 73.7898, "ward": "Ward 63"}
    }

    token = create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")
    res1 = client.post("/api/complaints", json=payload, headers={"Authorization": f"Bearer {token}"})
    res2 = client.post("/api/complaints", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert res1.status_code == 200
    assert res2.status_code == 200

    tn1 = res1.json()["tracking_number"]
    tn2 = res2.json()["tracking_number"]

    current_year = str(datetime.now().year)
    assert current_year in tn1
    assert current_year in tn2
    assert tn1 != tn2
    assert tn1.startswith("CL-NK-")

def test_bug_15_ai_vision_hybrid_feature_extraction():
    """Bug 15: Verify analyze_image returns None when inputs missing, and returns analysis_type metadata."""
    assert analyze_image(None, "") is None

    result = analyze_image("https://example.com/pothole.jpg", "Pothole crater")
    assert result is not None
    assert result.analysis_type == "Hybrid Computer Vision & Image Feature Classifier"
    assert "Feature Hash:" in result.visual_summary

def test_bug_16_calculate_image_ssim_perceptual_hash():
    """Bug 16: Verify calculate_image_ssim metrics and fake image detection."""
    assert calculate_image_ssim("img_same.jpg", "img_same.jpg") == 1.0
    assert calculate_image_ssim("img_a.jpg", "fake_recycled_img.jpg") == 0.32

    sim = calculate_image_ssim("https://example.com/before.jpg", "https://example.com/after.jpg")
    assert 0.0 <= sim <= 1.0

def test_bug_17_resolution_verification_gps_and_timestamp():
    """Bug 17: Verify Haversine GPS mismatch > 200m flags fake resolution and EXPIRED timestamp."""
    # GPS Mismatch > 200m (e.g. 19.9975, 73.7898 vs 20.0500, 73.8500 ~ 9km apart)
    res_gps = verify_resolution(
        complaint_id_or_img="c-test-gps",
        after_image="https://example.com/repaired.jpg",
        gps_lat=20.0500,
        gps_lng=73.8500,
        base_lat=19.9975,
        base_lng=73.7898
    )
    assert res_gps.gps_consistency == "LOW"
    assert res_gps.fake_resolution_detected is True
    assert res_gps.human_review_triggered is True

    # Timestamp Stale > 48h
    old_ts = (datetime.now() - timedelta(hours=72)).isoformat()
    res_ts = verify_resolution(
        complaint_id_or_img="c-test-ts",
        timestamp=old_ts
    )
    assert res_ts.timestamp_freshness == "EXPIRED"

def test_bug_18_ai_verification_pending_citizen_confirmation():
    """Bug 18: Verify genuine AI verification sets citizen_confirmation to PENDING_CITIZEN_REVIEW."""
    comp = create_sample_complaint("c-test-bug-18")
    comp.status = ComplaintStatus.IN_PROGRESS
    db_store.update_complaint(comp)

    officer_token = create_access_token("officer@civiclens.org", "Officer", "usr-officer-001")
    res = client.post("/api/verification/verify-resolution", json={
        "complaint_id": comp.id,
        "officer_id": "Officer Desk 1",
        "officer_notes": "Road re-asphalted cleanly",
        "evidence_image_url": "https://example.com/genuine_fix.jpg",
        "gps_lat": 19.9975,
        "gps_lng": 73.7898
    }, headers={"Authorization": f"Bearer {officer_token}"})

    assert res.status_code == 200
    v_data = res.json()
    assert v_data["citizen_confirmation"] == "PENDING_CITIZEN_REVIEW"
    assert v_data["fake_resolution_detected"] is False

    updated_comp = db_store.get_complaint_by_id(comp.id)
    assert updated_comp.status == ComplaintStatus.AI_VERIFICATION

def test_bug_19_order_independent_spatial_clustering():
    """Bug 19: Verify spatial clustering is order-independent across input permutation."""
    c1 = create_sample_complaint("c-order-1", lat=19.9975, lng=73.7898)
    c2 = create_sample_complaint("c-order-2", lat=19.9980, lng=73.7903)
    c3 = create_sample_complaint("c-order-3", lat=19.9985, lng=73.7908)

    order1_res = cluster_complaints_spatially([c1, c2, c3])
    order2_res = cluster_complaints_spatially([c3, c1, c2])

    assert len(order1_res["clusters"]) == len(order2_res["clusters"])
    ids1 = set(order1_res["clusters"][0].report_ids)
    ids2 = set(order2_res["clusters"][0].report_ids)
    assert ids1 == ids2 == {"c-order-1", "c-order-2", "c-order-3"}

def test_bug_20_unique_incidents_count_and_reduction_ratio():
    """Bug 20: Verify unique_incidents_count includes clusters + unclustered single reports."""
    # 3 close reports (1 cluster) + 1 far report (unclustered)
    c1 = create_sample_complaint("c-ratio-1", lat=19.9975, lng=73.7898)
    c2 = create_sample_complaint("c-ratio-2", lat=19.9976, lng=73.7899)
    c3 = create_sample_complaint("c-ratio-3", lat=19.9977, lng=73.7900)
    c_far = create_sample_complaint("c-ratio-far", lat=20.0500, lng=73.8500)

    res = cluster_complaints_spatially([c1, c2, c3, c_far])

    assert res["total_raw_reports"] == 4
    assert len(res["clusters"]) == 1
    # 1 cluster + 1 unclustered single = 2 unique incidents
    assert res["unique_incidents_count"] == 2
    # Reduction = (4 - 2) / 4 * 100 = 50.0%
    assert res["reduction_ratio_percent"] == 50.0
