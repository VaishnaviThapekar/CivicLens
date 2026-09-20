import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routes.auth import create_access_token, USERS_DB
from app.services.exif_phash import check_perceptual_similarity, compute_dhash
from app.services.sla_engine import calculate_sla_deadline
from app.services.cpgrams_sync import execute_cpgrams_sync_all, format_cpgrams_dossier
from app.services.contractor_scorecard import calculate_dynamic_contractor_scorecard

client = TestClient(app)

def get_supervisor_token():
    USERS_DB["supervisor@civiclens.org"] = {
        "user_id": "usr-sup-001",
        "email": "supervisor@civiclens.org",
        "role": "Supervisor",
        "full_name": "Supervisor Rajesh"
    }
    return create_access_token("supervisor@civiclens.org", "Supervisor", "usr-sup-001")

def test_perceptual_dhash_similarity():
    # Test identical empty/None handling
    is_dup, sim, dist = check_perceptual_similarity(None, None)
    assert is_dup is False
    assert sim == 0.0

def test_sla_near_breach_detection():
    # 80% elapsed time calculation test
    now_iso = "2026-09-20T10:00:00"
    res = calculate_sla_deadline(now_iso, "P1 — Critical")
    assert "is_near_breach" in res
    assert "elapsed_percentage" in res
    assert "escalation_stage" in res

def test_dynamic_contractor_scorecard():
    scorecard = calculate_dynamic_contractor_scorecard()
    assert isinstance(scorecard, list)
    assert len(scorecard) >= 3
    for c in scorecard:
        assert "ai_vision_pass_rate" in c
        assert "durability_score" in c
        assert "status" in c

def test_cpgrams_sync_execution():
    res = execute_cpgrams_sync_all()
    assert res["status"] == "SUCCESS"
    assert "synced_records_count" in res
    assert "synced_dossiers" in res

def test_contractors_scorecard_endpoint():
    token = get_supervisor_token()
    res = client.get("/api/intelligence/contractors/scorecard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_cpgrams_sync_endpoint():
    token = get_supervisor_token()
    res = client.get("/api/intelligence/cpgrams/sync", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
