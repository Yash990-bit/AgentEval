from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models.scenario import Scenario
from ..schemas.scenario import ScenarioCreate, ScenarioUpdate


def get_scenario(db: Session, scenario_id: UUID) -> Scenario:
    return db.query(Scenario).filter(Scenario.id == scenario_id).first()


def list_scenarios(db: Session, skip: int = 0, limit: int = 100) -> List[Scenario]:
    return db.query(Scenario).offset(skip).limit(limit).all()


def create_scenario(db: Session, payload: ScenarioCreate) -> Scenario:
    db_scenario = Scenario(**payload.dict())
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


def update_scenario(db: Session, scenario_id: UUID, payload: ScenarioUpdate) -> Scenario:
    db_scenario = get_scenario(db, scenario_id)
    if not db_scenario:
        raise ValueError("Scenario not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_scenario, field, value)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario


def delete_scenario(db: Session, scenario_id: UUID) -> None:
    db_scenario = get_scenario(db, scenario_id)
    if not db_scenario:
        raise ValueError("Scenario not found")
    db.delete(db_scenario)
    db.commit()


def fork_scenario(db: Session, scenario_id: UUID, new_owner: UUID) -> Scenario:
    src = get_scenario(db, scenario_id)
    if not src:
        raise ValueError("Scenario not found")
    data = {
        "created_by": new_owner,
        "name": f"{src.name} (fork)",
        "description": src.description,
        "scenario_type": src.scenario_type,
        "agent_configs": src.agent_configs,
        "environment_config": src.environment_config,
        "success_criteria": src.success_criteria,
        "tags": src.tags,
        "is_template": src.is_template,
        "is_public": src.is_public,
    }
    new_scenario = Scenario(**data)
    db.add(new_scenario)
    db.commit()
    db.refresh(new_scenario)
    return new_scenario
