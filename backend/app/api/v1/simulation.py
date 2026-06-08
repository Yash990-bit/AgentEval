from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid

from ...core.engine import SimulationEngine, get_engine_from_store
from ...core.environment import Environment
from sqlalchemy.orm import Session
from ...dependencies import get_db, get_s3_client
from ...utils.s3_client import S3Client
from ...services.snapshot_recorder import record_snapshot
router = APIRouter(prefix="/simulation", tags=["simulation"])

# In‑memory store of agents for simplicity; in real app this would query DB
agent_store: Dict[str, Dict] = {}
engine: SimulationEngine = None
current_simulation_id: uuid.UUID = None


def _ensure_engine():
    global engine
    if engine is None:
        # Initialize with empty agents and a fresh environment
        engine = SimulationEngine([], Environment())

class StartSimulationRequest(BaseModel):
    agents: List[Dict]

@router.post("/start")
async def start_simulation(req: StartSimulationRequest):
    """Initialize the simulation with a list of agent definitions.
    Each agent dict should match the Agent schema fields (id, name, role, etc.)."""
    global agent_store, engine
    # Populate the in‑memory agent store
    agent_store = {str(agent["id"]): agent for agent in req.agents}
    # Re‑create engine with these agents
    engine = SimulationEngine(list(agent_store.values()))
    # Generate a new simulation ID for this run
    global current_simulation_id
    current_simulation_id = uuid.uuid4()
    return {"status": "started", "agent_count": len(agent_store), "simulation_id": str(current_simulation_id)}

@router.post("/step")
async def step_simulation(db: Session = Depends(get_db), s3: S3Client = Depends(get_s3_client)):
    """Advance the simulation by one tick, record snapshot, and return it."""
    _ensure_engine()
    snapshot = engine.run_tick()
    # Record snapshot to S3 and DB
    if current_simulation_id is not None:
        record_snapshot(db, s3, current_simulation_id, engine.tick_counter, snapshot)
        try:
            from app.services.analytics_service import compute_simulation_analytics
            from app.api.v1.analytics import manager as analytics_manager
            from fastapi.encoders import jsonable_encoder
            import asyncio

            analytics = compute_simulation_analytics(db, current_simulation_id, engine, engine.tick_counter)
            serialized_analytics = jsonable_encoder(analytics)
            asyncio.create_task(analytics_manager.broadcast(current_simulation_id, serialized_analytics))
        except Exception as e:
            # Do not block the simulation step if broadcasting fails
            pass
    return snapshot

@router.get("/state")
async def get_state():
    """Return the current simulation state without advancing the clock."""
    _ensure_engine()
    # Build a lightweight state from the engine (similar to run_tick but without advancing)
    state = {
        "time": engine.env.current_time.isoformat(),
        "resources": engine.env.resource_pool.to_dict(),
        "events": [e.to_dict() for e in engine.env.active_events()],
        "hazards": [h.to_dict() for h in engine.env.active_hazards()],
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "role": a.role,
                "objective": a.objective,
                "energy_score": round(a.energy_score, 2),
                "resource_budget": round(a.resource_budget, 2),
                "trust_score": round(a.trust_score, 2),
                "risk_score": round(a.risk_score, 2),
                "status": "active" if a.energy_score > 0 else "exhausted",
            }
            for a in engine.agents
        ],
        "links": engine._generate_links(),
    }
    return state


@router.get("/evaluations")
async def get_evaluations():
    """Evaluate agents based on the engine metrics and return rankings."""
    _ensure_engine()
    return engine.evaluate_agents()
