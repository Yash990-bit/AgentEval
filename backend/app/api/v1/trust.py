from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..services.trust_engine import get_trust_engine
from ..db.session import get_db

router = APIRouter()

class TrustEvent(BaseModel):
    simulation_id: str = Field(..., description="Simulation UUID")
    source_agent_id: str = Field(..., description="Source agent UUID")
    target_agent_id: str = Field(..., description="Target agent UUID")
    event_type: str = Field(..., description="One of the defined trust events")
    tick: int = Field(..., ge=0, description="Current simulation tick")

@router.post("/trust/event")
def apply_trust_event(event: TrustEvent, db: Session = get_db()):
    engine = get_trust_engine(db)
    try:
        engine.apply_event(
            simulation_id=event.simulation_id,
            source_agent_id=event.source_agent_id,
            target_agent_id=event.target_agent_id,
            event_type=event.event_type,
            tick=event.tick,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"msg": "event applied"}

@router.post("/trust/propagate")
def propagate(simulation_id: str, db: Session = get_db()):
    engine = get_trust_engine(db)
    engine.propagate_trust(simulation_id)
    return {"msg": "propagation completed"}

@router.post("/trust/decay")
def decay(simulation_id: str, current_tick: int, db: Session = get_db()):
    engine = get_trust_engine(db)
    engine.decay_trust(simulation_id, current_tick)
    return {"msg": "decay applied"}

@router.get("/trust/reputation")
def reputation(simulation_id: str, agent_id: str, db: Session = get_db()):
    engine = get_trust_engine(db)
    rep = engine.reputation(simulation_id, agent_id)
    return {"reputation": rep}

@router.get("/trust/influence")
def influence(simulation_id: str, agent_id: str, db: Session = get_db()):
    engine = get_trust_engine(db)
    inf = engine.influence(simulation_id, agent_id)
    return {"influence": inf}
