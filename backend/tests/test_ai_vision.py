import pytest
from app.services.ai_vision import analyze_complaint_image, verify_resolution, calculate_image_ssim
from PIL import Image

def test_analyze_complaint_image_pothole():
    details = analyze_complaint_image(None, "Huge pothole on road")
    assert details.object_detected == "Road Surface Pothole"
    assert details.confidence >= 0.85
    assert details.risk_level == "HIGH"

def test_verify_resolution_valid_repair():
    res = verify_resolution(
        "c-test-1", "Officer PWD", "repaired_after.jpg", "Repaired asphalt patch",
        gps_lat=19.9975, gps_lng=73.7898, base_lat=19.9975, base_lng=73.7898, before_image="before.jpg"
    )
    assert res.visual_evidence_valid is True
    assert res.fake_resolution_detected is False
    assert res.ai_verification_score >= 80.0

def test_verify_resolution_fake_detection():
    res = verify_resolution(
        "c-test-2", "Officer PWD", "data:image/png;base64,dummy", "test_fake unrelated evidence",
        gps_lat=19.9975, gps_lng=73.7898, base_lat=19.9975, base_lng=73.7898, before_image="before.jpg"
    )
    assert res.visual_evidence_valid is False
    assert res.fake_resolution_detected is True
    assert "Verification Failed" in res.message
