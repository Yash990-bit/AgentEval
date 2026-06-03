from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
import asyncio
import uuid
from typing import List
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.conflict.models import Conflict

router = APIRouter(tags=["conflicts"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        tasks = [connection.send_text(message) for connection in self.active_connections]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


manager = ConnectionManager()

@router.get("/simulations/{simulation_id}/conflicts", response_model=List[dict])
async def get_simulation_conflicts(simulation_id: str, db: Session = Depends(get_db)):
    """Fetch all conflicts detected for a given simulation ID."""
    try:
        sim_uuid = uuid.UUID(simulation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid simulation ID format (must be UUID)")

    conflicts = db.query(Conflict).filter(Conflict.simulation_id == sim_uuid).all()
    return [
        {
            "id": str(c.id),
            "simulation_id": str(c.simulation_id),
            "conflict_type": c.conflict_type.value,
            "detected_at_tick": c.detected_at_tick,
            "agents_involved": c.agents_involved,
            "severity_score": c.severity_score,
            "root_cause": c.root_cause,
            "suggested_resolution": c.suggested_resolution,
            "status": c.status.value,
            "resolved_at_tick": c.resolved_at_tick,
        }
        for c in conflicts
    ]

@router.get("/conflicts/{conflict_id}", response_model=dict)
async def get_conflict(conflict_id: str, db: Session = Depends(get_db)):
    """Fetch details of a specific conflict by ID."""
    try:
        conflict_uuid = uuid.UUID(conflict_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conflict ID format (must be UUID)")

    c = db.query(Conflict).filter(Conflict.id == conflict_uuid).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conflict not found")

    return {
        "id": str(c.id),
        "simulation_id": str(c.simulation_id),
        "conflict_type": c.conflict_type.value,
        "detected_at_tick": c.detected_at_tick,
        "agents_involved": c.agents_involved,
        "severity_score": c.severity_score,
        "root_cause": c.root_cause,
        "suggested_resolution": c.suggested_resolution,
        "status": c.status.value,
        "resolved_at_tick": c.resolved_at_tick,
    }

@router.websocket("/conflicts/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for receiving real-time conflict notification events."""
    await manager.connect(websocket)
    try:
        # Send a welcome message
        await websocket.send_text(
            '{"id":"init","type":"Info","severity":0,"description":"WebSocket connected","timestamp": ""}'
        )
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
