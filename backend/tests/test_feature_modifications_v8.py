import pytest
from app.services.nlp_routing import parse_multilingual_report
from app.services.spatial_cluster import derive_cluster_priority, derive_cluster_root_cause
from app.services.gamification import calculate_karma_award
from app.services.notification_engine import format_multichannel_templates
from app.models.schemas import PriorityLevel

def test_nlp_sentiment_urgency_and_landmarks():
    res = parse_multilingual_report("Huge danger pothole near school and hospital gate", voice_transcript="")
    assert "sentiment_urgency_score" in res
    assert res["sentiment_urgency_score"] >= 0.5
    assert "detected_landmarks" in res
    assert "School Zone" in res["detected_landmarks"]
    assert "Hospital Zone" in res["detected_landmarks"]

def test_cluster_auto_escalation_to_p1_critical():
    reports_3 = [
        {"id": "c-1", "category": "Road Infrastructure", "priority": "P3 — Medium"},
        {"id": "c-2", "category": "Road Infrastructure", "priority": "P3 — Medium"},
        {"id": "c-3", "category": "Road Infrastructure", "priority": "P2 — High"}
    ]
    priority = derive_cluster_priority(reports_3)
    assert priority == PriorityLevel.P1

def test_cluster_evidence_root_cause_hypothesis():
    reports_water = [
        {"id": "c-w1", "category": "Water Supply & Leakage"},
        {"id": "c-w2", "category": "Drainage & Waterlogging"}
    ]
    cause = derive_cluster_root_cause(reports_water)
    assert "AI hypothesis" in cause["detected_root_cause"]
    assert "Subsurface Water Leakage" in cause["detected_root_cause"]

def test_karma_point_award_multipliers():
    res_base = calculate_karma_award("SUBMIT_REPORT", has_exif_telemetry=False, is_ground_verified=False)
    assert res_base["total_karma_awarded"] == 50

    res_bonus = calculate_karma_award("SUBMIT_REPORT", has_exif_telemetry=True, is_ground_verified=True)
    assert res_bonus["total_karma_awarded"] == 105
    assert len(res_bonus["bonus_reasons"]) == 2

def test_multichannel_notification_formatting():
    channels = format_multichannel_templates("STATUS_CHANGED", "CL-NK-2026-00101", "Work in Progress")
    assert "sms" in channels
    assert "whatsapp" in channels
    assert "push" in channels
    assert "email_subject" in channels
    assert "CL-NK-2026-00101" in channels["sms"]
