from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..db.session import get_db
from ..models.scenario import Scenario
from ..schemas.scenario import ScenarioCreate, ScenarioRead, ScenarioUpdate
from ..services.scenario_service import (
    get_scenario,
    list_scenarios,
    create_scenario,
    update_scenario,
    delete_scenario,
    fork_scenario,
)

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

@router.get("/", response_model=List[ScenarioRead])
def read_scenarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return list_scenarios(db, skip=skip, limit=limit)

@router.post("/", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
def create_new_scenario(payload: ScenarioCreate, db: Session = Depends(get_db)):
    return create_scenario(db, payload)

@router.get("/{scenario_id}", response_model=ScenarioRead)
def read_scenario(scenario_id: UUID, db=Depends(get_db)):
    scenario = get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

@router.put("/{scenario_id}", response_model=ScenarioRead)
def update_existing_scenario(scenario_id: UUID, payload: ScenarioUpdate, db=Depends(get_db)):
    try:
        return update_scenario(db, scenario_id, payload)
    except ValueError:
        raise HTTPException(status_code=404, detail="Scenario not found")

@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_scenario(scenario_id: UUID, db=Depends(get_db)):
    try:
        delete_scenario(db, scenario_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return None

@router.post("/{scenario_id}/fork", response_model=ScenarioRead)
def fork_existing_scenario(scenario_id: UUID, new_owner: UUID, db=Depends(get_db)):
    try:
        return fork_scenario(db, scenario_id, new_owner)
    except ValueError:
        raise HTTPException(status_code=404, detail="Scenario not found")

# Optional export/import endpoints
@router.get("/{scenario_id}/export", response_model=dict)
def export_scenario(scenario_id: UUID, db=Depends(get_db)):
    scenario = get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    # Convert ORM to dict (excluding internal fields)
    return {
        "id": str(scenario.id),
        "created_by": str(scenario.created_by),
        "name": scenario.name,
        "description": scenario.description,
        "scenario_type": scenario.scenario_type,
        "agent_configs": scenario.agent_configs,
        "environment_config": scenario.environment_config,
        "success_criteria": scenario.success_criteria,
        "tags": scenario.tags,
        "is_template": scenario.is_template,
        "is_public": scenario.is_public,
        "created_at": scenario.created_at.isoformat(),
        "updated_at": scenario.updated_at.isoformat(),
    }

@router.post("/import", response_model=ScenarioRead, status_code=status.HTTP_201_CREATED)
def import_scenario(payload: dict, db=Depends(get_db)):
    # Expect payload to follow the same structure as export
    from ..schemas.scenario import ScenarioCreate
    create_payload = ScenarioCreate(
        created_by=UUID(payload["created_by"]),
        name=payload["name"],
        description=payload.get("description"),
        scenario_type=payload["scenario_type"],
        agent_configs=payload.get("agent_configs", []),
        environment_config=payload.get("environment_config", {}),
        success_criteria=payload.get("success_criteria", {}),
        tags=payload.get("tags"),
        is_template=payload.get("is_template", False),
        is_public=payload.get("is_public", False),
    )
    return create_scenario(db, create_payload)
