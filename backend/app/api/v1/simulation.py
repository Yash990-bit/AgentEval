from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from ...core.engine import SimulationEngine, get_engine_from_store
from ...core.environment import Environment

router = APIRouter(prefix="/simulation", tags=["simulation"])

# In‑memory store of agents for simplicity; in real app this would query DB
agent_store: Dict[str, Dict] = {}
engine: SimulationEngine = None

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
    return {"status": "started", "agent_count": len(agent_store)}

@router.post("/step")
async def step_simulation():
    """Advance the simulation by one tick and return the snapshot."""
    _ensure_engine()
    snapshot = engine.run_tick()
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
