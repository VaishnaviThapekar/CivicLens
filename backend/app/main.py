import os
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
from fastapi.staticfiles import StaticFiles

from app.routes import complaints, verification, officer, intelligence, supervisor, auth
from app.routes.auth import require_role, get_current_user_email
from app.services.pdf_export import generate_audit_report
from app.services.websocket_manager import manager
from app.db.store import db_store

app = FastAPI(
    title="CivicLens — AI-Powered Civic Intelligence API",
    description="Multimodal Civic Grievance Processing, Geospatial Incident Clustering, and AI Resolution Verification Engine.",
    version="1.3.0"
)

# Bug 25 Fix: Secure CORS middleware configuration for production & local clients
custom_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
ALLOWED_ORIGINS = list(set([
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "https://civiclens.vercel.app"
] + [o.strip() for o in custom_origins if o.strip()]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include standard API Routers (/api)
app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(verification.router)
app.include_router(officer.router)
app.include_router(intelligence.router)
app.include_router(supervisor.router)

# Bug 44 Fix: API v1 Versioning Prefix Alias (/api/v1)
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth.router)
v1_router.include_router(complaints.router)
v1_router.include_router(verification.router)
v1_router.include_router(officer.router)
v1_router.include_router(intelligence.router)
v1_router.include_router(supervisor.router)
app.include_router(v1_router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    # Enforce WebSocket JWT token authentication
    effective_token = token
    if not effective_token:
        auth_hdr = websocket.headers.get("authorization") or websocket.headers.get("sec-websocket-protocol")
        if auth_hdr:
            effective_token = auth_hdr.replace("Bearer ", "").strip()

    if not effective_token:
        await websocket.close(code=4001, reason="Unauthorized connection: Authentication token required")
        return

    try:
        user_email = get_current_user_email(f"Bearer {effective_token}")
    except Exception:
        await websocket.close(code=4001, reason="Unauthorized connection: Invalid or expired token")
        return

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo ping / heartbeat
            await websocket.send_json({"type": "HEARTBEAT_ACK", "time": datetime.now().isoformat(), "user": user_email})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/complaints/{complaint_id}/audit-dossier")
@app.get("/api/v1/complaints/{complaint_id}/audit-dossier")
def get_complaint_audit_dossier(
    complaint_id: str,
    user: dict = Depends(require_role("Supervisor", "Administrator"))
):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return generate_audit_report(complaint)

@app.get("/health")
@app.get("/api/health")
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CivicLens AI Platform Engine",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
def root_status():
    return {
        "status": "online",
        "system": "CivicLens AI Engine",
        "api_versions": ["/api", "/api/v1"],
        "features": [
            "Multimodal NLP Intent Extraction",
            "Computer Vision Infrastructure Defect Detection",
            "Geospatial Incident Clustering (DBSCAN / Haversine)",
            "AI Resolution Verification & Anti-Fraud Evidence Matching",
            "Predictive Civic Risk Forecasting",
            "WebSocket Real-Time Live Status Broadcaster",
            "Supervisor Audit & Contractor SLA Escalation",
            "CPGRAMS Dossier Export Engine"
        ]
    }
