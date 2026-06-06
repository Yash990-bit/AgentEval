from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.db.session import SessionLocal
from app.db.models.relationship import AgentRelationship, RelationshipType
from app.core.state import get_engine

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/simulations/{simulation_id}/messages", response_model=List[dict])
async def get_simulation_messages(simulation_id: str):
    """Return all messages for a given simulation ID."""
    engine = get_engine(simulation_id)
    return engine.messages

@router.get("/agents/{agent_id}/relationships", response_model=List[dict])
async def get_agent_relationships(agent_id: str, db: SessionLocal = Depends(get_db)):
    """Return all relationships involving the specified agent."""
    rels = db.query(AgentRelationship).filter(
        (AgentRelationship.agent_a_id == agent_id) | (AgentRelationship.agent_b_id == agent_id)
    ).all()
    return [
        {
            "id": str(r.id),
            "simulation_id": str(r.simulation_id),
            "agent_a_id": r.agent_a_id,
            "agent_b_id": r.agent_b_id,
            "relationship_type": r.relationship_type.value,
            "trust_score": r.trust_score,
            "interaction_count": r.interaction_count,
            "last_interaction_tick": r.last_interaction_tick,
        }
        for r in rels
    ]
