import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import USERS_DB, TOKENS_DB, OTP_STORE, hash_password, verify_password
from app.services.ai_vision import analyze_image, calculate_image_ssim, verify_resolution
from app.services.spatial_cluster import cluster_complaints, cluster_complaints_spatially
from app.models.schemas import Complaint, ComplaintStatus, PriorityLevel, ComplaintCategory, LocationData

client = TestClient(app)

def test_pbkdf2_password_hashing():
    pwd = "SecurePassword123!"
    h1, s1 = hash_password(pwd)
    assert h1 != pwd
    assert len(s1) == 32
    assert verify_password(pwd, h1, s1) is True
    assert verify_password("WrongPassword", h1, s1) is False

def test_strict_401_authentication_rejection():
    # Attempting to access protected profile endpoint without authorization header
    res_no_auth = client.get("/api/auth/profile")
    assert res_no_auth.status_code == 401
    
    # Attempting with invalid token
    res_invalid = client.get("/api/auth/profile", headers={"Authorization": "Bearer invalid-junk-token"})
    assert res_invalid.status_code == 401

def test_otp_expiry_and_rate_limiting():
    # Dispatch OTP
    res_send = client.post("/api/auth/otp/send", json={"phone": "+91 9998887776"})
    assert res_send.status_code == 200
    data = res_send.json()
    assert "dev_otp" in data
    dev_otp = data["dev_otp"]
    
    # Verify 3 failed attempts trigger rate limit 429
    phone = "+91 9998887776"
    for _ in range(3):
        res_fail = client.post("/api/auth/otp/verify", json={"phone": phone, "otp": "000000"})
        assert res_fail.status_code == 400
        
    res_rate_limit = client.post("/api/auth/otp/verify", json={"phone": phone, "otp": dev_otp})
    assert res_rate_limit.status_code == 429

def test_google_oauth_token_provisioning():
    res_g = client.post("/api/auth/google", json={"email": "testuser@gmail.com", "full_name": "Test User", "id_token": "valid_token_xyz"})
    assert res_g.status_code == 200
    data = res_g.json()
    assert "access_token" in data
    access_token = data["access_token"]
    
    # Use provisioned token to access profile
    res_prof = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {access_token}"})
    assert res_prof.status_code == 200
    assert res_prof.json()["profile"]["email"] == "testuser@gmail.com"

def test_media_upload_endpoint():
    # Valid file upload
    file_content = b"fake image bytes content"
    files = {"file": ("test.jpg", file_content, "image/jpeg")}
    res_upload = client.post("/api/complaints/upload-media", files=files)
    assert res_upload.status_code == 200
    assert "file_url" in res_upload.json()
    
    # Invalid MIME type rejection
    bad_files = {"file": ("test.exe", file_content, "application/x-msdownload")}
    res_bad = client.post("/api/complaints/upload-media", files=bad_files)
    assert res_bad.status_code == 400

def test_pixel_computer_vision_and_ssim():
    res_analysis = analyze_image("pothole_crater.jpg", "Severe asphalt crater on main road")
    assert res_analysis is not None
    assert "Pothole" in res_analysis.object_detected
    assert res_analysis.confidence > 0.8
    assert res_analysis.estimated_area_m2 > 0.0

    ssim_same = calculate_image_ssim("sample1.jpg", "sample1.jpg")
    assert ssim_same == 1.0
    
    ssim_diff = calculate_image_ssim("sample1.jpg", "fake_unrelated_image.jpg")
    assert ssim_diff < 0.5

def test_haversine_and_freshness_verification():
    # Base location at 19.9975, 73.7898
    # 1. GPS mismatch (> 200m away, e.g. 20.05, 73.85)
    res_gps_fail = verify_resolution(
        complaint_id_or_img="c-test-01",
        after_image="after.jpg",
        gps_lat=20.05,
        gps_lng=73.85,
        base_lat=19.9975,
        base_lng=73.7898,
        before_image="before.jpg"
    )
    assert res_gps_fail.fake_resolution_detected is True
    assert res_gps_fail.gps_consistency == "LOW"

    # 2. Genuine verification
    res_ok = verify_resolution(
        complaint_id_or_img="c-test-02",
        after_image="after.jpg",
        gps_lat=19.9976,
        gps_lng=73.7899,
        base_lat=19.9975,
        base_lng=73.7898,
        before_image="before.jpg"
    )
    assert res_ok.fake_resolution_detected is False
    assert res_ok.citizen_confirmation == "PENDING_CITIZEN_REVIEW"

def test_spatial_clustering_multi_factor():
    c1 = Complaint(
        id="c1", tracking_number="CL-1", title="Pothole 1", description="Road pothole",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE, priority=PriorityLevel.P2, priority_reason="Road defect",
        status=ComplaintStatus.SUBMITTED, location=LocationData(lat=19.9975, lng=73.7898, ward="Ward 63"),
        created_at="2026-09-01T10:00:00"
    )
    c2 = Complaint(
        id="c2", tracking_number="CL-2", title="Pothole 2", description="Crater nearby",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE, priority=PriorityLevel.P1, priority_reason="P1 Hazard",
        status=ComplaintStatus.SUBMITTED, location=LocationData(lat=19.9980, lng=73.7900, ward="Ward 63"),
        created_at="2026-08-30T10:00:00"
    )
    clusters = cluster_complaints([c1, c2])
    assert len(clusters) == 1
    assert clusters[0].supporting_reports_count == 2
    # Check dynamic priority (P1 wins over P2)
    assert clusters[0].priority == PriorityLevel.P1
    # Check dynamic created_at (earliest date 2026-08-30)
    assert "2026-08-30" in clusters[0].created_at
