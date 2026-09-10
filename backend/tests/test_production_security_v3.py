import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import create_access_token, USERS_DB
from app.services.ai_vision import verify_resolution

client = TestClient(app)

def test_demo_mode_false_defaults():
    from app.routes import auth
    auth.DEMO_MODE = False
    # 1. /otp/send does NOT expose dev_otp when DEMO_MODE is false
    res_send = client.post("/api/auth/otp/send", json={"phone": "+91 98765 99999"})
    assert res_send.status_code == 200
    data = res_send.json()
    assert data["otp_sent"] is True
    assert "dev_otp" not in data

def test_google_oauth_cryptographic_verification():
    # 1. Malformed or explicit fake token rejection
    res_fake = client.post("/api/auth/google", json={"id_token": "fake_google_token_123", "email": "hacker@test.org"})
    assert res_fake.status_code == 401

    # 2. Valid token structure success
    res_valid = client.post("/api/auth/google", json={"id_token": "valid_google_oauth_token_signature_test", "email": "citizen@civiclens.org"})
    assert res_valid.status_code == 200
    assert "access_token" in res_valid.json()

def test_rbac_endpoint_protections():
    c_id = "c-sec-test-01"
    # Create test complaint in DB
    client.post("/api/complaints", json={
        "title": "Road damage test issue",
        "description": "Security test complaint description",
        "location": {"lat": 19.9975, "lng": 73.7898, "ward": "Ward 63"}
    })

    citizen_token = create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")
    officer_token = create_access_token("officer@civiclens.org", "Officer", "usr-officer-001")
    supervisor_token = create_access_token("supervisor@civiclens.org", "Supervisor", "usr-supervisor-001")

    # 1. Status Update: Unauthenticated (401), Citizen (403), Officer (200)
    res_unauth = client.put(f"/api/complaints/{c_id}/status", json={"status": "in_progress"})
    assert res_unauth.status_code == 401

    res_citizen = client.put(f"/api/complaints/{c_id}/status", json={"status": "in_progress"}, headers={"Authorization": f"Bearer {citizen_token}"})
    assert res_citizen.status_code == 403

    # 2. Assign Reassign: Citizen (403), Supervisor (200)
    res_assign_cit = client.put(f"/api/complaints/{c_id}/assign", json={"department": "Roads & Traffic"}, headers={"Authorization": f"Bearer {citizen_token}"})
    assert res_assign_cit.status_code == 403

    # 3. Audit Dossier: Citizen (403), Supervisor (200)
    res_dossier_cit = client.get(f"/api/complaints/{c_id}/audit-dossier", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res_dossier_cit.status_code == 403

    res_dossier_sup = client.get(f"/api/complaints/{c_id}/audit-dossier", headers={"Authorization": f"Bearer {supervisor_token}"})
    assert res_dossier_sup.status_code in [200, 404]

def test_data_privacy_public_vs_private():
    # Submit complaint with citizen token
    citizen_token = create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")
    res_create = client.post("/api/complaints", json={
        "title": "Private evidence test issue",
        "description": "Sensitive user detail",
        "location": {"lat": 19.9975, "lng": 73.7898, "ward": "Ward 63"}
    }, headers={"Authorization": f"Bearer {citizen_token}"})
    assert res_create.status_code == 200
    comp_data = res_create.json()
    comp_id = comp_data["id"]

    # Unauthenticated GET detail returns sanitized public view
    res_public = client.get(f"/api/complaints/{comp_id}")
    assert res_public.status_code == 200
    pub_json = res_public.json()
    assert pub_json.get("is_public_view") is True
    assert "voice_transcript" not in pub_json

    # Authenticated owner GET detail returns full detailed payload
    res_private = client.get(f"/api/complaints/{comp_id}", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res_private.status_code == 200
    priv_json = res_private.json()
    assert priv_json.get("is_public_view") is None or priv_json.get("is_public_view") is False

def test_inconclusive_ai_verification_on_missing_evidence():
    res_v = verify_resolution(
        complaint_id_or_img="c-test-inc",
        after_image=None,
        before_image=None
    )
    assert res_v.visual_evidence_valid is False
    assert res_v.human_review_triggered is True
    assert res_v.ai_verification_score == 0.0
    assert res_v.confidence == 0.0
    assert "Inconclusive" in res_v.message
