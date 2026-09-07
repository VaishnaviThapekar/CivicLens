from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from fastapi.staticfiles import StaticFiles

from app.routes import complaints, verification, officer, intelligence, supervisor, auth
from app.services.pdf_export import generate_audit_report
from app.services.websocket_manager import manager
from app.db.store import db_store

app = FastAPI(
    title="CivicLens — AI-Powered Civic Intelligence API",
    description="Multimodal Civic Grievance Processing, Geospatial Incident Clustering, and AI Resolution Verification Engine.",
    version="1.2.0"
)

# Secure CORS middleware configuration for local & production web clients
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "https://civiclens.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(verification.router)
app.include_router(officer.router)
app.include_router(intelligence.router)
app.include_router(supervisor.router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo ping / heartbeat
            await websocket.send_json({"type": "HEARTBEAT_ACK", "time": datetime.now().isoformat()})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/complaints/{complaint_id}/audit-dossier")
def get_complaint_audit_dossier(complaint_id: str):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return generate_audit_report(complaint)

@app.get("/health")
@app.get("/api/health")
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
