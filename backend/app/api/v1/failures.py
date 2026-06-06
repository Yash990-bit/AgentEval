from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

# Relative imports within the backend package
from ..services.failure_engine import FailureInjector, FailureDetector
from ..models.failure_event import FailureEvent
from ..db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

class InjectionRequest(BaseModel):
    simulation_id: UUID
    target_agent_id: UUID  # ID of the agent to which the failure is applied
    failure_type: str  # e.g., 'hallucination', 'tool_failure', etc.
    probability: Optional[float] = None  # Override default probability if provided
    parameters: Optional[dict] = None  # Additional params for the injector

class FailureLogResponse(BaseModel):
    id: UUID
    simulation_id: UUID
    failure_type: str
    timestamp: str
    details: dict

@router.post("/inject", response_model=bool)
async def inject_failure(request: InjectionRequest, db: Session = Depends(get_db)) -> bool:
    """Register a failure injection for a given simulation and agent.
    Returns True if injection was registered successfully.
    """
    try:
        FailureInjector.inject(
            simulation_id=request.simulation_id,
            failure_type=request.failure_type,
            target_agent_id=str(request.target_agent_id),
            probability=request.probability if request.probability is not None else 0.1,
        )
        return True
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/logs/{simulation_id}", response_model=List[FailureLogResponse])
async def get_failure_logs(simulation_id: UUID, db: Session = Depends(get_db)):
    """Retrieve all failure events for a specific simulation."""
    events = db.query(FailureEvent).filter(FailureEvent.simulation_id == simulation_id).all()
    return [
        FailureLogResponse(
            id=event.id,
            simulation_id=event.simulation_id,
            failure_type=event.failure_type,
            timestamp=event.timestamp.isoformat(),
            details=event.details,
        )
        for event in events
    ]
