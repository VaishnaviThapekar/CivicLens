import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import create_access_token, USERS_DB
from app.services.material_quantifier import estimate_repair_materials
from app.services.iot_sensor import get_drone_inspection_audits
from app.services.pdf_export import generate_ward_audit_report_html

client = TestClient(app)

def get_citizen_token():
    USERS_DB["citizen@civiclens.org"] = {
        "user_id": "usr-citizen-001",
        "email": "citizen@civiclens.org",
        "role": "Citizen",
        "full_name": "Alex Morgan"
    }
    return create_access_token("citizen@civiclens.org", "Citizen", "usr-citizen-001")

def test_material_quantifier_calculation():
    res_road = estimate_repair_materials(category="Road Infrastructure", area_sqm=5.0, severity="P1 — Critical")
    assert "estimated_total_cost_inr" in res_road
    assert res_road["estimated_total_cost_inr"] > 0
    assert "formatted_cost_inr" in res_road
    assert "material_breakdown" in res_road
    assert len(res_road["material_breakdown"]) >= 3

def test_material_quantifier_drainage():
    res_drain = estimate_repair_materials(category="Drainage & Waterlogging", area_sqm=3.5, severity="P2 — High")
    assert "estimated_total_cost_inr" in res_drain
    assert res_drain["estimated_total_cost_inr"] > 0
    assert "material_breakdown" in res_drain

def test_drone_audits_service():
    audits = get_drone_inspection_audits()
    assert isinstance(audits, list)
    assert len(audits) >= 1

def test_pdf_export_service():
    html_out = generate_ward_audit_report_html("Ward 63")
    assert isinstance(html_out, str)
    assert "Ward 63" in html_out
    assert "Municipal Ward Quality & Audit Dossier" in html_out or "CivicLens" in html_out

def test_material_estimate_endpoint():
    token = get_citizen_token()
    # Create sample complaint first
    res_create = client.post("/api/complaints", json={
        "title": "Road crater near main gate",
        "description": "Deep pothole defect",
        "media_type": "image",
        "location": {"lat": 19.9975, "lng": 73.7898, "city": "Nashik", "ward": "Ward 63"}
    }, headers={"Authorization": f"Bearer {token}"})
    assert res_create.status_code == 200
    comp_id = res_create.json()["id"]

    res_est = client.get(f"/api/intelligence/material-estimate/{comp_id}", headers={"Authorization": f"Bearer {token}"})
    assert res_est.status_code == 200
    data = res_est.json()
    assert "estimated_total_cost_inr" in data
    assert "material_breakdown" in data

def test_drone_audits_endpoint():
    token = get_citizen_token()
    res = client.get("/api/intelligence/drone-audits", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_export_pdf_endpoint():
    res = client.get("/api/intelligence/export-audit-pdf?ward_name=Ward%2063")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
