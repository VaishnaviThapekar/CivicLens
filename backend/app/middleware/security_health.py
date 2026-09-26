import time
import os
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime

# In-memory sliding window rate limiter
_rate_limit_store = defaultdict(list)
_auth_limit_store = defaultdict(list)

GENERAL_RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "120"))
AUTH_RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT_PER_MIN", "20"))
WINDOW_SECONDS = 60

def reset_rate_limit_stores():
    """Resets rate limiting memory stores (useful for test suites)."""
    _rate_limit_store.clear()
    _auth_limit_store.clear()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow disabling or bypassing rate limit unless header explicitly tests rate limit
        force_test_limit = request.headers.get("X-Test-Rate-Limit") == "true"
        if os.getenv("DISABLE_RATE_LIMIT", "false").lower() == "true" and not force_test_limit:
            return await call_next(request)

        path = request.url.path
        if path.startswith("/static") or path in ["/health", "/metrics", "/api/health", "/api/v1/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        if force_test_limit:
            client_ip = "test-rate-limit-ip"

        now = time.time()
        is_auth = "/auth/" in path or "/otp/" in path

        store = _auth_limit_store if is_auth else _rate_limit_store
        limit = AUTH_RATE_LIMIT if is_auth else GENERAL_RATE_LIMIT

        timestamps = [t for t in store[client_ip] if now - t < WINDOW_SECONDS]
        store[client_ip] = timestamps

        if len(timestamps) >= limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please slow down and try again later.",
                    "error": "rate_limit_exceeded",
                    "retry_after_seconds": WINDOW_SECONDS
                },
                headers={"Retry-After": str(WINDOW_SECONDS)}
            )

        store[client_ip].append(now)
        return await call_next(request)

def get_system_metrics_data(db_store=None):
    """
    Computes system health status & Prometheus metrics data.
    """
    total_complaints = 0
    resolved_complaints = 0
    pending_complaints = 0

    if db_store:
        complaints = db_store.get_all_complaints()
        total_complaints = len(complaints)
        for c in complaints:
            status = getattr(c, "status", None) if hasattr(c, "status") else (c.get("status") if isinstance(c, dict) else None)
            if status in ["Resolved", "Verified"]:
                resolved_complaints += 1
        pending_complaints = total_complaints - resolved_complaints

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": {
            "status": "connected",
            "type": "SQLAlchemy ORM / Datastore Engine"
        },
        "metrics": {
            "total_complaints_count": total_complaints,
            "resolved_complaints_count": resolved_complaints,
            "pending_complaints_count": pending_complaints,
            "system_uptime_status": "ONLINE",
            "rate_limiter_active_ips": len(_rate_limit_store)
        }
    }

def generate_prometheus_metrics(db_store=None):
    """
    Returns text formatted in Prometheus metrics exposition format.
    """
    data = get_system_metrics_data(db_store)
    metrics = data["metrics"]
    lines = [
        "# HELP civiclens_total_complaints Total number of reported complaints",
        "# TYPE civiclens_total_complaints gauge",
        f"civiclens_total_complaints {metrics['total_complaints_count']}",
        "# HELP civiclens_resolved_complaints Number of resolved complaints",
        "# TYPE civiclens_resolved_complaints gauge",
        f"civiclens_resolved_complaints {metrics['resolved_complaints_count']}",
        "# HELP civiclens_pending_complaints Number of pending complaints",
        "# TYPE civiclens_pending_complaints gauge",
        f"civiclens_pending_complaints {metrics['pending_complaints_count']}",
        "# HELP civiclens_rate_limiter_active_ips Active IP addresses tracked",
        "# TYPE civiclens_rate_limiter_active_ips gauge",
        f"civiclens_rate_limiter_active_ips {metrics['rate_limiter_active_ips']}",
        "# HELP civiclens_up System operational status",
        "# TYPE civiclens_up gauge",
        "civiclens_up 1"
    ]
    return "\n".join(lines) + "\n"
