from fastapi.testclient import TestClient
from app.main import app
from app.services.geo_intelligence import resolve_geolocation

client = TestClient(app)

def test_login_auth():
    payload = {"email": "citizen@civiclens.org", "password": "password123"}
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "Citizen"

def test_google_oauth():
    res = client.post("/api/auth/oauth/google")
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_otp_flow():
    from app.routes import auth
    auth.DEMO_MODE = True
    res_send = client.post("/api/auth/otp/send", json={"phone": "+91 98765 43210"})
    assert res_send.status_code == 200
    res_verify = client.post("/api/auth/otp/verify", json={"phone": "+91 98765 43210", "otp": "123456"})
    assert res_verify.status_code == 200

def test_geolocation_intelligence():
    loc = resolve_geolocation(19.9975, 73.7898, "Ward 63")
    assert loc.city == "Nashik"
    assert loc.ward == "Ward 63"
    assert "ST_SetSRID" in loc.postgis_geometry
