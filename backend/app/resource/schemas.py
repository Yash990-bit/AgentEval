# backend/app/resource/schemas.py
"""Pydantic schemas for the Resource Management System.

These are used in the FastAPI endpoints for validation and response models.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, List, Any

from pydantic import BaseModel, Field

class ResourceType(str, Enum):
    COMPUTE_UNITS = "compute_units"
    API_CALLS = "api_calls"
    MEMORY_SLOTS = "memory_slots"
    TOKEN_BUDGET = "token_budget"
    USD_BUDGET = "usd_budget"

class ActionType(str, Enum):
    CONSUMED = "consumed"
    RESERVED = "reserved"
    RELEASED = "released"
    TRANSFERRED = "transferred"
    WASTED = "wasted"

class ResourceBudgetBase(BaseModel):
    agent_id: str = Field(..., description="Identifier of the agent")
    simulation_id: str = Field(..., description="Simulation UUID")
    compute_total: int = 0
    api_calls_total: int = 0
    memory_slots_total: int = 0
    tokens_total: int = 0
    usd_total: float = 0.0

class ResourceBudgetCreate(ResourceBudgetBase):
    pass

class ResourceBudgetRead(ResourceBudgetBase):
    id: str
    compute_used: int = 0
    api_calls_used: int = 0
    memory_slots_used: int = 0
    tokens_used: int = 0
    usd_spent: float = 0.0
    compute_reserved: int = 0
    api_calls_reserved: int = 0
    memory_slots_reserved: int = 0
    tokens_reserved: int = 0
    usd_reserved: float = 0.0
    efficiency_score: float = 0.0
    last_updated: datetime | None = None

    class Config:
        orm_mode = True

class ResourceEventBase(BaseModel):
    simulation_id: str
    agent_id: str
    resource_type: ResourceType
    action_type: ActionType
    amount: float
    tick: int
    metadata: Optional[Any] = None

class ResourceEventCreate(ResourceEventBase):
    pass

class ResourceEventRead(ResourceEventBase):
    id: str
    timestamp: datetime | None = None

    class Config:
        orm_mode = True
