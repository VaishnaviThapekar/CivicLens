"""
CivicLens Real-Time WebSocket Event Broadcaster
Manages live WebSocket connections to stream status updates, new incidents, and city pulse tickers to citizens and authority dashboards without page refreshes.
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
      self.active_connections.remove(websocket)

  async def send_personal_message(self, message: dict, websocket: WebSocket):
    await websocket.send_json(message)

  async def broadcast(self, message: dict):
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
    "new_status": new_status,
    "timestamp": asyncio.get_event_loop().time()
  }
  await manager.broadcast(payload)

async def broadcast_new_incident(incident_data: dict):
  payload = {
    "type": "NEW_INCIDENT",
    "incident": incident_data
  }
  await manager.broadcast(payload)
