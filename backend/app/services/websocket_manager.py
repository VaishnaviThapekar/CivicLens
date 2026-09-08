"""
CivicLens Real-Time WebSocket Event Broadcaster
Manages live WebSocket connections to stream status updates, new incidents, and city pulse tickers to citizens and authority dashboards without page refreshes.
Features: Exception-safe connection cleanup and complaint lifecycle event broadcasting.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            try:
                self.active_connections.remove(websocket)
            except Exception:
                pass

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """Bugs 44 & 45 Fix: Broadcasts real-time events and cleans up stale/failed connections automatically."""
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

async def broadcast_status_update(complaint_id: str, new_status: str, tracking_number: str):
    payload = {
        "type": "STATUS_UPDATE",
        "complaint_id": complaint_id,
        "tracking_number": tracking_number,
        "new_status": new_status
    }
    await manager.broadcast(payload)

async def broadcast_new_incident(incident_data: dict):
    payload = {
        "type": "NEW_INCIDENT",
        "incident": incident_data
    }
    await manager.broadcast(payload)

def notify_complaint_created(complaint: Any):
    try:
        c_dict = complaint.model_dump(mode="json") if hasattr(complaint, "model_dump") else str(complaint)
        payload = {"type": "NEW_INCIDENT", "incident": c_dict}
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast(payload))
    except Exception:
        pass

def notify_status_changed(complaint_id: str, new_status: str, tracking_number: str = ""):
    try:
        payload = {
            "type": "STATUS_UPDATE",
            "complaint_id": complaint_id,
            "tracking_number": tracking_number,
            "new_status": new_status
        }
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast(payload))
    except Exception:
        pass
