import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import USERS_DB, TOKENS_DB, OTP_STORE

client = TestClient(app)

def test_auth_bypass_prevention():
    # 1. Test missing Authorization header -> HTTP 401
    res_no_auth = client.get("/api/auth/profile")
    assert res_no_auth.status_code == 401
    assert "Invalid or missing" in res_no_auth.json()["detail"] or "Missing authorization header" in res_no_auth.json()["detail"]

    # 2. Test invalid Bearer token -> HTTP 401
    res_fake_token = client.get("/api/auth/profile", headers={"Authorization": "Bearer fake_invalid_token_12345"})
    assert res_fake_token.status_code == 401
    assert "Invalid or expired" in res_fake_token.json()["detail"]

    # 3. Test unauthenticated notifications -> HTTP 401
    res_notif_no_auth = client.get("/api/auth/notifications")
    assert res_notif_no_auth.status_code == 401

def test_cryptographic_password_hashing():
    # Login with valid seeded password
    login_res = client.post("/api/auth/login", json={"email": "citizen@civiclens.org", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token in TOKENS_DB

    # Test login with invalid password -> HTTP 401
    login_fail = client.post("/api/auth/login", json={"email": "citizen@civiclens.org", "password": "wrongpassword!"})
    assert login_fail.status_code == 401

    # Test profile access using valid access token
    profile_res = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {token}"})
    assert profile_res.status_code == 200
    assert profile_res.json()["profile"]["email"] == "citizen@civiclens.org"

def test_otp_token_storage_and_rate_limit():
    from app.routes import auth
    auth.DEMO_MODE = True
    phone = "+91 9123456789"
    # Send OTP
    send_res = client.post("/api/auth/otp/send", json={"phone": phone})
    assert send_res.status_code == 200
    dev_otp = send_res.json()["dev_otp"]

    # Test failed verification attempts
    client.post("/api/auth/otp/verify", json={"phone": phone, "otp": "000000"})
    client.post("/api/auth/otp/verify", json={"phone": phone, "otp": "000000"})
    client.post("/api/auth/otp/verify", json={"phone": phone, "otp": "000000"})

    # 4th attempt -> Rate limited HTTP 429
    rate_res = client.post("/api/auth/otp/verify", json={"phone": phone, "otp": dev_otp})
    assert rate_res.status_code == 429

    # Re-send fresh OTP
    send_fresh = client.post("/api/auth/otp/send", json={"phone": phone})
    fresh_otp = send_fresh.json()["dev_otp"]

    # Verify fresh OTP -> HTTP 200 & Token stored in TOKENS_DB
    verify_res = client.post("/api/auth/otp/verify", json={"phone": phone, "otp": fresh_otp})
    assert verify_res.status_code == 200
    otp_token = verify_res.json()["access_token"]
    assert otp_token in TOKENS_DB

    # Verify profile access using OTP token
    profile_res = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {otp_token}"})
    assert profile_res.status_code == 200
