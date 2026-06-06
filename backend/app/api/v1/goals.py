from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.goal_manager import GoalManager
from app.models.goal import AgentGoal, GoalStatusEnum

router = APIRouter()

class GoalCreate(BaseModel):
    title: str = Field(..., description="Goal title")
    description: Optional[str] = Field(None, description="Goal description")
    priority: int = Field(5, description="Goal priority (lower is higher priority)")
    parent_goal_id: Optional[UUID] = Field(None, description="Parent goal ID if hierarchical")
    dependencies: Optional[List[UUID]] = Field(None, description="List of goal IDs this goal depends on")
    deadline_tick: Optional[int] = Field(None, description="Simulation tick by which the goal should be completed")
    required_resources: Optional[dict] = Field(None, description="Resource budget for this goal")
    simulation_id: UUID = Field(..., description="Simulation this goal belongs to")
    agent_id: UUID = Field(..., description="Agent that owns the goal")

class GoalResponse(BaseModel):
    id: UUID
    simulation_id: UUID
    agent_id: UUID
    title: str
    description: Optional[str]
    priority: int
    status: GoalStatusEnum
    progress_pct: float
    deadline_tick: Optional[int]
    required_resources: Optional[dict]

    class Config:
        orm_mode = True

@router.post("/goals", response_model=GoalResponse)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)):
    manager = GoalManager(db)
    goal = manager.create_goal(
        agent_id=payload.agent_id,
        simulation_id=payload.simulation_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        parent_goal_id=payload.parent_goal_id,
        dependencies=payload.dependencies,
        deadline_tick=payload.deadline_tick,
        required_resources=payload.required_resources,
    )
    return goal

@router.get("/goals", response_model=List[GoalResponse])
def list_goals(simulation_id: UUID, db: Session = Depends(get_db)):
    goals = db.query(AgentGoal).filter(AgentGoal.simulation_id == simulation_id).all()
    return goals

@router.get("/goals/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: UUID, db: Session = Depends(get_db)):
    goal = db.get(AgentGoal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal
