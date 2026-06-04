from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Import FastAPI DB dependency
from ...db.session import get_db

# Import resource manager and CRUD services
from ...services.resource_manager import ResourceManager
from ...resource.crud import ResourceCRUD

# Import Pydantic schemas for create/update
from ...resource.schemas import ResourceBudgetCreate, ResourceEventCreate

router = APIRouter()

# Dependency to provide ResourceManager instance
def get_manager(db: Session = Depends(get_db)) -> ResourceManager:
    return ResourceManager(db)

def get_crud(db: Session = Depends(get_db)) -> ResourceCRUD:
    return ResourceCRUD(db)

# ------------------- Budget Retrieval -------------------
@router.get("/resource/{agent_id}", response_model=Dict[str, Any])
def get_budget(
    agent_id: str,
    simulation_id: str,
    manager: ResourceManager = Depends(get_manager),
):
    budget = manager.get_budget(agent_id, simulation_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {
        "agent_id": str(budget.agent_id),
        "simulation_id": str(budget.simulation_id),
        "compute_total": budget.compute_total,
        "compute_used": budget.compute_used,
        "api_calls_total": budget.api_calls_total,
        "api_calls_used": budget.api_calls_used,
        "tokens_total": budget.tokens_total,
        "tokens_used": budget.tokens_used,
        "usd_total": budget.usd_total,
        "usd_spent": budget.usd_spent,
    }

# ------------------- Allocation -------------------
class AllocateRequest(BaseModel):
    simulation_id: str
    tick: int
    compute_units: int = 0
    api_calls: int = 0
    tokens: int = 0
    usd_budget: float = 0.0
    enforce: bool = True

@router.post("/resource/allocate/{agent_id}")
def allocate_resources(
    agent_id: str,
    req: AllocateRequest,
    manager: ResourceManager = Depends(get_manager),
):
    try:
        budget = manager.allocate(
            agent_id=agent_id,
            simulation_id=req.simulation_id,
            tick=req.tick,
            compute_units=req.compute_units,
            api_calls=req.api_calls,
            tokens=req.tokens,
            usd_budget=req.usd_budget,
            enforce=req.enforce,
        )
        return {"status": "allocated", "budget": budget}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------- Reporting -------------------
@router.get("/resource/report")
def resource_report(
    simulation_id: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    start_tick: Optional[int] = Query(None),
    end_tick: Optional[int] = Query(None),
    manager: ResourceManager = Depends(get_manager),
):
    report = manager.report(
        simulation_id=simulation_id,
        agent_id=agent_id,
        start_tick=start_tick,
        end_tick=end_tick,
    )
    return report

# ------------------- CRUD Endpoints -------------------
@router.post("/resource", response_model=Dict[str, Any])
def create_budget(
    payload: ResourceBudgetCreate,
    crud: ResourceCRUD = Depends(get_crud),
):
    budget = crud.create_budget(payload)
    return {"status": "created", "budget": budget}

@router.put("/resource/{agent_id}", response_model=Dict[str, Any])
def update_budget(
    agent_id: str,
    simulation_id: str,
    payload: ResourceBudgetCreate,
    crud: ResourceCRUD = Depends(get_crud),
):
    budget = crud.get_budget(agent_id, simulation_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    updated = crud.update_budget(budget, payload)
    return {"status": "updated", "budget": updated}

@router.post("/event", response_model=Dict[str, Any])
def log_event(
    payload: ResourceEventCreate,
    crud: ResourceCRUD = Depends(get_crud),
):
    event = crud.log_event(payload)
    return {"status": "logged", "event": event}

@router.get("/events", response_model=List[Dict[str, Any]])
def list_events(
    simulation_id: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    start_tick: Optional[int] = Query(None),
    end_tick: Optional[int] = Query(None),
    crud: ResourceCRUD = Depends(get_crud),
):
    return crud.get_events(
        simulation_id=simulation_id,
        agent_id=agent_id,
        start_tick=start_tick,
        end_tick=end_tick,
    )
