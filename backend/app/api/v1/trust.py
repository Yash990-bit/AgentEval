from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.services import get_trust_engine
from app.db.session import get_db

router = APIRouter()

class TrustEvent(BaseModel):
    simulation_id: str = Field(..., description="Simulation UUID")
    source_agent_id: str = Field(..., description="Source agent UUID")
    target_agent_id: str = Field(..., description="Target agent UUID")
    event_type: str = Field(..., description="One of the defined trust events")
    tick: int = Field(..., ge=0, description="Current simulation tick")

@router.post("/trust/event")
def apply_trust_event(event: TrustEvent, db: Session = Depends(get_db)):
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
    try:
        engine.apply_event(
            simulation_id=event.simulation_id,
            source_agent_id=event.source_agent_id,
            target_agent_id=event.target_agent_id,
            event_type=event.event_type,

@router.get("/trust/edges")
def get_trust_edges(simulation_id: str = Query(...), db: Session = Depends(get_db)):
    engine = get_trust_engine(db)
    edges = engine.get_all_edges(simulation_id)
    return [{"source": e.source_agent_id, "target": e.target_agent_id, "trust_score": e.trust_score, "influence_score": e.influence_score} for e in edges]

@router.post("/trust/propagate")
def propagate(simulation_id: str = Query(...), db: Session = Depends(get_db)):
    engine = get_trust_engine(db)
    engine.propagate_trust(simulation_id)
    return {"msg": "propagation completed"}

@router.post("/trust/decay")
def decay(simulation_id: str = Query(...), current_tick: int = Query(...), db: Session = Depends(get_db)):
    engine = get_trust_engine(db)
    engine.decay_trust(simulation_id, current_tick)
    return {"msg": "decay applied"}

@router.get("/trust/reputation")
def reputation(simulation_id: str = Query(...), agent_id: str = Query(...), db: Session = Depends(get_db)):
    engine = get_trust_engine(db)
    rep = engine.reputation(simulation_id, agent_id)
    return {"reputation": rep}

@router.get("/trust/influence")
def influence(simulation_id: str = Query(...), agent_id: str = Query(...), db: Session = Depends(get_db)):
    engine = get_trust_engine(db)
    inf = engine.influence(simulation_id, agent_id)
    return {"influence": inf}

@router.get("/simulations/{id}/trust-network")
def get_trust_network(id: str, db: Session = Depends(get_db)):
    engine = get_trust_engine(db)
    edges = engine.get_all_edges(id)
    
    agent_ids = set()
    for edge in edges:
        agent_ids.add(edge.source_agent_id)
        agent_ids.add(edge.target_agent_id)
        
    agent_names = {}
    if agent_ids:
        from app.db.models import AgentModel
        import uuid
        uuid_list = []
        for aid in agent_ids:
            try:
                uuid_list.append(uuid.UUID(aid))
            except ValueError:
                pass
        if uuid_list:
            db_agents = db.query(AgentModel).filter(AgentModel.id.in_(uuid_list)).all()
            for a in db_agents:
                agent_names[str(a.id)] = a.name
                
    nodes = []
    for aid in agent_ids:
        rep = engine.reputation(id, aid)
        inf = engine.influence(id, aid)
        nodes.append({
            "id": aid,
            "name": agent_names.get(aid, aid),
            "reputation": rep,
            "influence": inf
        })
        
    edges_payload = []
    for edge in edges:
        edges_payload.append({
            "source": edge.source_agent_id,
            "target": edge.target_agent_id,
            "trust_score": edge.trust_score,
            "influence_score": edge.influence_score
        })
        
    return {"nodes": nodes, "edges": edges_payload}

@router.get("/agents/{id}/trust-history")
def get_trust_history(id: str, simulation_id: str = Query(...), db: Session = Depends(get_db)):
    from app.models.trust import AgentTrustEdge
    edges = db.query(AgentTrustEdge).filter(
        AgentTrustEdge.simulation_id == simulation_id,
        (AgentTrustEdge.source_agent_id == id) | (AgentTrustEdge.target_agent_id == id)
    ).all()
    
    history = []
    for edge in edges:
        history.append({
            "source": edge.source_agent_id,
            "target": edge.target_agent_id,
            "history": edge.history
        })
    return history
