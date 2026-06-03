from __future__ import annotations

from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, Json

class AgentRole(str, Enum):
    researcher = "researcher"
    planner = "planner"
    executor = "executor"
    analyst = "analyst"
    coordinator = "coordinator"
    support = "support"
    custom = "custom"

class AgentStatus(str, Enum):
    idle = "idle"
    running = "running"
    sleeping = "sleeping"
    failed = "failed"
    completed = "completed"

class ResourceBudget(BaseModel):
    compute_units: int = Field(..., ge=0)
    api_calls: int = Field(..., ge=0)
    tokens: int = Field(..., ge=0)
    usd_budget: float = Field(..., ge=0)

class AgentBase(BaseModel):
    name: str = Field(..., max_length=100)
    role: AgentRole
    objective: str = Field(..., max_length=500)
    tools: List[str] = Field(default_factory=list)
    resource_budget: ResourceBudget
    trust_score: float = Field(default=0.5, ge=0.0, le=1.0)
    energy_score: float = Field(default=1.0, ge=0.0, le=1.0)
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    status: AgentStatus = AgentStatus.idle

class AgentCreate(AgentBase):
    pass

class AgentRead(AgentBase):
    id: UUID
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    class Config:
        orm_mode = True
