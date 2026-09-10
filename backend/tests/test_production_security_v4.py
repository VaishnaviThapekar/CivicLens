import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.routes import auth
from app.routes.auth import create_access_token, USERS_DB
from app.db.store import db_store
from app.models.schemas import ComplaintStatus

client = TestClient(app)

def test_oidc_claims_extraction():
    # Verify Google OIDC token claims derive user identity directly
    res = client.post("/api/auth/google", json={
        "id_token": "valid_google_oauth_token_signature_v4",
        "email": "forged_email@hacker.org",  # Should be overridden by verified claims
        "full_name": "Forged Name"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "citizen@civiclens.org"

def test_production_demo_mode_false_and_reset_token_expiry():
    auth.DEMO_MODE = False

    # 1. /otp/send hides dev_otp when DEMO_MODE is False
    res_otp = client.post("/api/auth/otp/send", json={"phone": "+91 98765 11111"})
    assert res_otp.status_code == 200
    assert "dev_otp" not in res_otp.json()

    # 2. Password reset token expiry test
    res_forgot = client.post("/api/auth/forgot-password", json={"email": "citizen@civiclens.org"})
    assert res_forgot.status_code == 200
    reset_tok = res_forgot.json()["reset_token"]

    # Artificially expire the reset token
    auth.RESET_TOKENS[reset_tok]["expires_at"] = datetime.now(timezone.utc) - timedelta(minutes=1)

    res_reset = client.post("/api/auth/reset-password", json={"reset_token": reset_tok, "new_password": "NewSecurePassword123!"})
    assert res_reset.status_code == 400
    assert "expired" in res_reset.json()["detail"].lower()

def test_authenticated_complaint_creation_and_ownership():
    user1_token = create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")
    user2_token = create_access_token("officer@civiclens.org", "Officer", "usr-officer-001")

    # 1. Unauthenticated submission fails (401)
    res_unauth = client.post("/api/complaints", json={
        "description": "Unauthenticated test submission",
        "location": {"lat": 19.9975, "lng": 73.7898, "ward": "Ward 63"}
    })
    assert res_unauth.status_code == 401

    # 2. Authenticated submission binds submitted_by_user_id & email
    res_create = client.post("/api/complaints", json={
        "title": "Road pothole submission v4",
        "description": "Pothole near central gate",
        "location": {"lat": 19.9975, "lng": 73.7898, "ward": "Ward 63"}
    }, headers={"Authorization": f"Bearer {user1_token}"})
    assert res_create.status_code == 200
    c_data = res_create.json()
    comp_id = c_data["id"]
    assert c_data["submitted_by_email"] == "citizen@civiclens.org"
    assert c_data["submitted_by_user_id"] == "usr-citizen-001"

    # 3. /my endpoint strictly isolates user complaints
    res_my1 = client.get("/api/complaints/my", headers={"Authorization": f"Bearer {user1_token}"})
    assert res_my1.status_code == 200
    my_ids1 = [c["id"] for c in res_my1.json()]
    assert comp_id in my_ids1

    res_my2 = client.get("/api/complaints/my", headers={"Authorization": f"Bearer {user2_token}"})
    assert res_my2.status_code == 200
    my_ids2 = [c["id"] for c in res_my2.json()]
    assert comp_id not in my_ids2

def test_officer_ticket_assignment_guardrail():
    # Setup complaint assigned to officer1
    comp = db_store.get_all_complaints()[0]
    comp.officer_assigned = "officer1@civiclens.org"
    comp.status = ComplaintStatus.IN_PROGRESS
    db_store.update_complaint(comp)

    USERS_DB["officer1@civiclens.org"] = {"user_id": "usr-off-1", "email": "officer1@civiclens.org", "role": "Officer", "full_name": "Officer 1"}
    USERS_DB["officer2@civiclens.org"] = {"user_id": "usr-off-2", "email": "officer2@civiclens.org", "role": "Officer", "full_name": "Officer 2"}
    USERS_DB["supervisor@civiclens.org"] = {"user_id": "usr-sup-1", "email": "supervisor@civiclens.org", "role": "Supervisor", "full_name": "Supervisor R"}

    officer1_token = create_access_token("officer1@civiclens.org", "Officer", "usr-off-1")
    officer2_token = create_access_token("officer2@civiclens.org", "Officer", "usr-off-2")
    supervisor_token = create_access_token("supervisor@civiclens.org", "Supervisor", "usr-sup-1")

    # 1. Officer 2 trying to verify Officer 1's ticket returns 403 Forbidden
    res_off2 = client.post("/api/verification/verify-resolution", json={
        "complaint_id": comp.id,
        "evidence_image_url": "https://example.com/repaired.jpg",
        "gps_lat": 19.9975,
        "gps_lng": 73.7898
    }, headers={"Authorization": f"Bearer {officer2_token}"})
    assert res_off2.status_code == 403
    assert "not authorized" in res_off2.json()["detail"].lower()

    # 2. Officer 1 verifying assigned ticket returns 200 OK
    res_off1 = client.post("/api/verification/verify-resolution", json={
        "complaint_id": comp.id,
        "evidence_image_url": "https://example.com/repaired.jpg",
        "gps_lat": 19.9975,
        "gps_lng": 73.7898
    }, headers={"Authorization": f"Bearer {officer1_token}"})
    assert res_off1.status_code == 200

    # 3. Supervisor bypassing assignment check returns 200 OK
    res_sup = client.post("/api/verification/verify-resolution", json={
        "complaint_id": comp.id,
        "evidence_image_url": "https://example.com/repaired.jpg",
        "gps_lat": 19.9975,
        "gps_lng": 73.7898
    }, headers={"Authorization": f"Bearer {supervisor_token}"})
    assert res_sup.status_code == 200

def test_websocket_mandatory_authentication():
    # 1. Connection without token fails (close code 4001)
    with pytest.raises(Exception):
        with client.websocket_connect("/ws"):
            pass

    # 2. Connection with valid token succeeds
    token = create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")
    with client.websocket_connect(f"/ws?token={token}") as ws:
        ws.send_text("PING")
        data = ws.receive_json()
        assert data["type"] == "HEARTBEAT_ACK"
        assert data["user"] == "citizen@civiclens.org"
