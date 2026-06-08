from fastapi import APIRouter, Depends, HTTPException, Path, WebSocket, WebSocketDisconnect
from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from app.schemas.analytics import SimulationAnalyticsRead, AgentPerformanceMetricsRead
from app.services.analytics_service import compute_simulation_analytics, get_agent_performance_metrics
from app.dependencies import get_db
from app.models.simulation_analytics import SimulationAnalytics
from . import simulation

router = APIRouter(prefix="/simulations", tags=["analytics"])

class AnalyticsConnectionManager:
    def __init__(self):
        # Maps simulation_id (UUID) -> List of WebSocket connections
        self.active_connections: dict[UUID, List[WebSocket]] = {}

    async def connect(self, simulation_id: UUID, websocket: WebSocket):
        await websocket.accept()
        if simulation_id not in self.active_connections:
            self.active_connections[simulation_id] = []
        self.active_connections[simulation_id].append(websocket)

    def disconnect(self, simulation_id: UUID, websocket: WebSocket):
        if simulation_id in self.active_connections:
            if websocket in self.active_connections[simulation_id]:
                self.active_connections[simulation_id].remove(websocket)
            if not self.active_connections[simulation_id]:
                del self.active_connections[simulation_id]

    async def broadcast(self, simulation_id: UUID, message: dict):
        if simulation_id in self.active_connections:
            for connection in self.active_connections[simulation_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = AnalyticsConnectionManager()

@router.get("/{simulation_id}/analytics", response_model=SimulationAnalyticsRead)
def get_simulation_analytics(simulation_id: UUID = Path(...), db: Session = Depends(get_db)):
    analytics = db.query(SimulationAnalytics).filter_by(simulation_id=simulation_id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found for this simulation")
    return analytics

@router.post("/{simulation_id}/analytics/compute", response_model=SimulationAnalyticsRead)
def compute_analytics(simulation_id: UUID = Path(...), db: Session = Depends(get_db)):
    if simulation.engine is None:
        raise HTTPException(status_code=400, detail="No active simulation engine running")
    # Compute and persist analytics
    analytics = compute_simulation_analytics(db, simulation_id, simulation.engine, getattr(simulation.engine, 'tick_counter', 0))
    return analytics

@router.get("/{simulation_id}/agents/metrics", response_model=List[AgentPerformanceMetricsRead])
def get_agent_metrics(simulation_id: UUID = Path(...), db: Session = Depends(get_db)):
    metrics = get_agent_performance_metrics(db, simulation_id)
    return metrics

@router.websocket("/{simulation_id}/live")
async def websocket_analytics(websocket: WebSocket, simulation_id: UUID):
    await manager.connect(simulation_id, websocket)
    try:
        while True:
            # Keep connection alive, listen for messages if needed
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(simulation_id, websocket)
