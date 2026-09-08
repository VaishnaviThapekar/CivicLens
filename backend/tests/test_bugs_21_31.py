"""
Unit test suite for CivicLens Backend & AI Engine Bugs 21 to 31.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.db.store import db_store
from app.models.schemas import Complaint, LocationData, ComplaintCategory, ComplaintStatus, PriorityLevel
from app.services.spatial_cluster import cluster_complaints_spatially
from app.services.nlp_routing import parse_multilingual_report, detect_language
from app.services.predictive_ai import generate_predictive_risks, detect_emerging_anomalies

client = TestClient(app)

def create_test_complaint(comp_id: str, ward: str = "Ward 63", category: str = "Road Infrastructure", priority: PriorityLevel = PriorityLevel.P3, created_at: str = None):
    cat_enum = ComplaintCategory.ROAD_INFRASTRUCTURE
    for c in ComplaintCategory:
        if c.value == category:
            cat_enum = c
            break

    complaint = Complaint(
        id=comp_id,
        tracking_number=f"CL-NK-{datetime.now().year}-{comp_id.upper()}",
        title=f"Test issue {comp_id}",
        description="Sample test complaint description",
        media_type="image",
        category=cat_enum,
        department="Municipal Department",
        priority=priority,
        priority_reason="Test priority reason",
        status=ComplaintStatus.SUBMITTED,
        location=LocationData(lat=19.9975, lng=73.7898, ward=ward),
        created_at=created_at or datetime.now().isoformat()
    )
    db_store.add_complaint(complaint)
    return complaint

def test_bug_21_22_dynamic_cluster_priority_and_creation_date():
    """Bugs 21 & 22: Verify dynamic cluster priority resolution and earliest created_at timestamp."""
    old_time = (datetime.now() - timedelta(days=2)).isoformat()
    new_time = datetime.now().isoformat()

    c1 = create_test_complaint("c-p3-old", priority=PriorityLevel.P3, created_at=old_time)
    c2 = create_test_complaint("c-p1-new", priority=PriorityLevel.P1, created_at=new_time)

    res = cluster_complaints_spatially([c1, c2])
    assert len(res["clusters"]) == 1
    cluster = res["clusters"][0]

    # Bug 21: Cluster priority should elevate to highest member priority (P1)
    assert cluster.priority == PriorityLevel.P1
    # Bug 22: Creation date should match earliest report timestamp
    assert cluster.created_at == old_time

def test_bug_23_devanagari_marathi_hindi_nlp():
    """Bug 23: Verify Devanagari script detection and vocabulary parsing for Marathi and Hindi."""
    marathi_text = "इथे रस्त्यावर खूप मोठा खड्डा आहे"
    hindi_text = "यहाँ सड़क पर बहुत कचरा पड़ा है"

    assert detect_language(marathi_text) == "Marathi"
    assert detect_language(hindi_text) == "Hindi"

    parsed_m = parse_multilingual_report(marathi_text)
    assert parsed_m["category"] == ComplaintCategory.ROAD_INFRASTRUCTURE

    parsed_h = parse_multilingual_report(hindi_text)
    assert parsed_h["category"] == ComplaintCategory.GARBAGE_SANITATION

def test_bug_24_traffic_category_classification():
    """Bug 24: Verify TRAFFIC_SAFETY category parsing and routing."""
    report_en = "Heavy traffic jam and signal failure near market gate"
    report_mr = "वाहतूक कोंडी आणि ट्रॅफिक सिग्नल बंद आहे"

    parsed_en = parse_multilingual_report(report_en)
    assert parsed_en["category"] == ComplaintCategory.TRAFFIC_SAFETY
    assert parsed_en["department"] == "Traffic Infrastructure Control Cell"

    parsed_mr = parse_multilingual_report(report_mr)
    assert parsed_mr["category"] == ComplaintCategory.TRAFFIC_SAFETY

def test_bug_25_unmatched_complaint_routing():
    """Bug 25: Verify unmatched general complaints are routed cleanly without hardcoding road pothole defaults."""
    report = "General query regarding municipal counter operating hours"
    parsed = parse_multilingual_report(report)

    assert parsed["title"] == "General Municipal Civic Grievance"
    assert parsed["priority"] in [PriorityLevel.P3, PriorityLevel.P4]

def test_bug_26_dynamic_multi_factor_priority():
    """Bug 26: Verify multi-factor priority scoring based on text, duration, and safety indicators."""
    critical_report = "Huge pothole crater near school entrance cause severe accident hazard yesterday"
    parsed = parse_multilingual_report(critical_report)

    assert parsed["priority"] in [PriorityLevel.P1, PriorityLevel.P2]
    assert "Dynamic Multi-Factor Score" in parsed["priority_reason"]

def test_bug_27_28_db_driven_predictive_risks():
    """Bugs 27 & 28: Verify predictive risks respond dynamically to database state."""
    db_store.complaints.clear()

    # With 0 complaints
    risks_empty = generate_predictive_risks()
    assert risks_empty[0].probability == 0.15
    assert "0 active drainage" in risks_empty[0].trigger_factors[1]

    # Add 3 drainage complaints in Ward 63
    create_test_complaint("c-drain-1", ward="Ward 63", category="Drainage & Waterlogging")
    create_test_complaint("c-drain-2", ward="Ward 63", category="Drainage & Waterlogging")

    risks_active = generate_predictive_risks()
    assert risks_active[0].probability > 0.15
    assert "2 active drainage" in risks_active[0].trigger_factors[1]

def test_bug_29_accurate_zero_anomaly_detection():
    """Bug 29: Verify anomaly detection reports 0.0x baseline when 0 complaints exist (no 47 fallback)."""
    res = detect_emerging_anomalies(today_reports_count=0, baseline_daily_norm=5)

    assert res["is_anomaly_detected"] is False
    assert res["today_reports_count"] == 0
    assert "0.0x Above Baseline" in res["spike_ratio"]
    assert "Normal Report Volume" in res["anomaly_alert"]

def test_bug_30_31_enum_priority_stats_and_sla_overdue():
    """Bugs 30 & 31: Verify enum priority stats comparison and real time-based SLA overdue calculations."""
    db_store.complaints.clear()

    # Newly created P1 complaint (created now) should NOT be overdue immediately!
    new_comp = create_test_complaint("c-new-p1", priority=PriorityLevel.P1, created_at=datetime.now().isoformat())

    # Old P1 complaint created 10 hours ago (> 4h SLA limit) SHOULD be overdue!
    old_time = (datetime.now() - timedelta(hours=10)).isoformat()
    old_comp = create_test_complaint("c-old-p1", priority=PriorityLevel.P1, created_at=old_time)

    res = client.get("/api/intelligence/stats")
    assert res.status_code == 200
    data = res.json()

    assert data["critical_issues"] == 2
    # Only old_comp should be overdue, NOT new_comp!
    assert data["overdue_issues"] == 1
