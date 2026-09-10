import pytest
from fastapi.testclient import TestClient
import jwt
from app.main import app
from app.routes.auth import USERS_DB, TOKENS_DB, OTP_STORE, JWT_SECRET, JWT_ALGORITHM, create_access_token, create_refresh_token
from app.services.ai_vision import verify_resolution
from app.models.schemas import Complaint, ComplaintStatus, PriorityLevel, ComplaintCategory, LocationData

client = TestClient(app)

def test_public_registration_forces_citizen_role():
    # Attacker tries submitting role="Administrator" on public register
    res = client.post("/api/auth/register", json={
        "email": "attacker@civiclens.org",
        "password": "Password123!",
        "full_name": "Attacker User",
        "role": "Administrator"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "Citizen"
    # Verify in DB
    assert USERS_DB["attacker@civiclens.org"]["role"] == "Citizen"

def test_admin_create_user_endpoint_rbac():
    # Non-admin user attempts access
    citizen_token = create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")
    res_forbidden = client.post(
        "/api/auth/admin/create-user",
        json={"email": "officer.new@civiclens.org", "password": "Password123!", "full_name": "Officer New", "role": "Officer"},
        headers={"Authorization": f"Bearer {citizen_token}"}
    )
    assert res_forbidden.status_code == 403

    # Admin user provisions new Officer
    admin_email = "admin@civiclens.org"
    USERS_DB[admin_email] = {"user_id": "usr-admin-1", "email": admin_email, "full_name": "Admin", "role": "Administrator"}
    admin_token = create_access_token(admin_email, "Administrator", "usr-admin-1")

    res_ok = client.post(
        "/api/auth/admin/create-user",
        json={"email": "officer.new@civiclens.org", "password": "Password123!", "full_name": "Officer New", "role": "Officer"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_ok.status_code == 200
    assert res_ok.json()["role"] == "Officer"

def test_pyjwt_token_decoding_and_refresh_rotation():
    email = "citizen@civiclens.org"
    access_t = create_access_token(email, "Citizen", "usr-citizen-001")
    refresh_t = create_refresh_token(email)
    TOKENS_DB[refresh_t] = email

    # Profile call using PyJWT
    res_prof = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {access_t}"})
    assert res_prof.status_code == 200

    # Refresh rotation
    res_ref = client.post("/api/auth/refresh", json={"refresh_token": refresh_t})
    assert res_ref.status_code == 200
    data = res_ref.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_t

def test_google_oauth_invalid_token_rejection():
    res_bad = client.post("/api/auth/google", json={"email": "hacker@gmail.com", "full_name": "Hacker", "id_token": "invalid_fake_token"})
    assert res_bad.status_code == 401

def test_magic_byte_file_upload_validation():
    token = create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")
    
    # Fake text file pretending to be image/jpeg
    fake_img_bytes = b"NOT_A_REAL_IMAGE_HEADER_CONTENT"
    files = {"file": ("fake.jpg", fake_img_bytes, "image/jpeg")}
    
    res_upload = client.post("/api/complaints/upload-media", files=files, headers={"Authorization": f"Bearer {token}"})
    assert res_upload.status_code == 400
    assert "Corrupted image" in res_upload.json()["detail"]

def test_missing_evidence_inconclusive_resolution():
    res_inconclusive = verify_resolution(
        complaint_id_or_img="c-missing-ev",
        after_image=None,
        before_image=None
    )
    assert res_inconclusive.visual_evidence_valid is False
    assert res_inconclusive.human_review_triggered is True
    assert res_inconclusive.confidence == 0.0
    assert "Inconclusive" in res_inconclusive.message

def test_rbac_protected_intelligence_endpoints():
    citizen_token = create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")
    
    # Unauthenticated / Citizen access to agentic dispatch should fail with 403
    res_dispatch = client.post(
        "/api/intelligence/agentic-dispatch",
        json={"report_text": "Pothole crater", "area_sqm": 12.0},
        headers={"Authorization": f"Bearer {citizen_token}"}
    )
    assert res_dispatch.status_code == 403

    # Authorized Supervisor access to agentic dispatch should succeed
    sup_email = "supervisor@civiclens.org"
    USERS_DB[sup_email] = {"user_id": "usr-sup-1", "email": sup_email, "full_name": "Supervisor", "role": "Supervisor"}
    sup_token = create_access_token(sup_email, "Supervisor", "usr-sup-1")

    res_sup = client.post(
        "/api/intelligence/agentic-dispatch",
        json={"report_text": "Pothole crater", "area_sqm": 12.0},
        headers={"Authorization": f"Bearer {sup_token}"}
    )
    assert res_sup.status_code == 200
    assert res_sup.json()["dispatched_by"] == sup_email
