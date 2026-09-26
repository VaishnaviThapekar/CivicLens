import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, init_db
from app.db.models import UserModel, ComplaintModel
from app.middleware.security_health import reset_rate_limit_stores

client = TestClient(app)

def setup_function():
    reset_rate_limit_stores()

def teardown_function():
    reset_rate_limit_stores()

def test_security_headers_middleware():
    """Verifies OWASP security headers present on API responses."""
    reset_rate_limit_stores()
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Strict-Transport-Security" in response.headers

def test_health_check_endpoint():
    """Verifies detailed health check endpoint returning system & datastore metrics."""
    reset_rate_limit_stores()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "metrics" in data
    assert data["metrics"]["system_uptime_status"] == "ONLINE"

def test_prometheus_metrics_endpoint():
    """Verifies Prometheus metrics exposition endpoint returns text/plain format."""
    reset_rate_limit_stores()
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    assert "civiclens_total_complaints" in text
    assert "civiclens_resolved_complaints" in text
    assert "civiclens_pending_complaints" in text
    assert "civiclens_up 1" in text

def test_rate_limiting_middleware():
    """Verifies rate limiting returns HTTP 429 when threshold exceeded."""
    reset_rate_limit_stores()
    blocked = False
    headers = {"X-Test-Rate-Limit": "true"}
    for _ in range(30):
        res = client.post("/api/auth/otp/send", json={"phone": "+919876543210"}, headers=headers)
        if res.status_code == 429:
            blocked = True
            assert res.json()["error"] == "rate_limit_exceeded"
            break
    assert blocked is True
    reset_rate_limit_stores()

def test_sqlalchemy_orm_models_and_db():
    """Verifies SQLAlchemy schema initialization and model queries."""
    init_db()
    db = SessionLocal()
    try:
        user_count = db.query(UserModel).count()
        complaint_count = db.query(ComplaintModel).count()
        assert isinstance(user_count, int)
        assert isinstance(complaint_count, int)
    finally:
        db.close()

def test_docs_export_openapi_and_postman():
    """Verifies OpenAPI specification and Postman collection exporter endpoints."""
    reset_rate_limit_stores()
    res_openapi = client.get("/api/docs/openapi.json")
    assert res_openapi.status_code == 200
    spec = res_openapi.json()
    assert spec["info"]["title"].startswith("CivicLens")

    res_postman = client.get("/api/docs/postman-collection.json")
    assert res_postman.status_code == 200
    postman = res_postman.json()
    assert postman["info"]["schema"] == "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    assert len(postman["item"]) > 0
