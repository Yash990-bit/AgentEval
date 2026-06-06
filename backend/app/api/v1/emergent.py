from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.emergent_engine import detect_spontaneous_coalition, detect_information_cascade, detect_emergent_leadership, detect_novel_patterns
from app.db.session import get_db
from app.models.emergent_log import EmergentLog
from typing import List

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class EmergentLogResponse(BaseModel):
    id: UUID
    simulation_id: UUID
    event_type: str
    details: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

router = APIRouter()

@router.get("/emergent/{simulation_id}", response_model=List[EmergentLogResponse])
def get_emergent_events(simulation_id: str, db: Session = Depends(get_db)):
    """Return all emergent events recorded for a simulation."""
    return db.query(EmergentLog).filter(EmergentLog.simulation_id == simulation_id).all()

@router.post("/emergent/{simulation_id}/run")
def run_emergent_detection(simulation_id: str, tick: int, db: Session = Depends(get_db)):
    """Execute emergent detection detectors for the given simulation tick."""
    from app.services.emergent_engine import run_emergent_detection_cycle
    run_emergent_detection_cycle(db, simulation_id, tick)
    return {"status": "completed", "simulation_id": simulation_id, "tick": tick}
