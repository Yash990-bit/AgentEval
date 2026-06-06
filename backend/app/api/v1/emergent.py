from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..services.emergent_engine import detect_spontaneous_coalition, detect_information_cascade, detect_emergent_leadership, detect_novel_patterns
from ..db.session import get_db
from ..models.emergent_log import EmergentLog
from typing import List

router = APIRouter()

@router.get("/emergent/{simulation_id}", response_model=List[EmergentLog])
def get_emergent_events(simulation_id: str, db: Session = Depends(get_db)):
    """Return all emergent events recorded for a simulation."""
    return db.query(EmergentLog).filter(EmergentLog.simulation_id == simulation_id).all()
