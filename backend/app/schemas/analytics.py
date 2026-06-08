from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

class CompletionStatus(str, Enum):
    success = "success"
    partial_success = "partial_success"
    failure = "failure"
    timeout = "timeout"

class SimulationAnalyticsBase(BaseModel):
    simulation_id: UUID
    total_ticks_run: int
    total_agents: int
    total_goals: int
    overall_success_rate: float
    overall_failure_rate: float
    avg_efficiency_score: float
    avg_trust_score: float
    avg_intelligence_score: float = 0.0
    avg_cooperation_score: float = 0.0
    avg_reliability_score: float = 0.0
    avg_risk_score: float = 0.0
    total_conflicts_detected: int
    conflicts_auto_resolved: int
    conflicts_escalated: int
    total_emergent_behaviors: int
    total_resource_units_consumed: Dict[str, Any]
    total_waste_rate: float
    top_performing_agent_id: Optional[UUID] = None
    most_conflicted_agent_id: Optional[UUID] = None
    completion_status: CompletionStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True

class SimulationAnalyticsRead(SimulationAnalyticsBase):
    pass

class AgentPerformanceMetricsBase(BaseModel):
    id: UUID
    agent_id: UUID
    simulation_id: UUID
    goals_completed: int
    goals_failed: int
    goals_abandoned: int
    success_rate: float
    efficiency_score: float
    cooperation_score: float
    reliability_score: float
    intelligence_score: float = 0.0
    risk_score: float = 0.0
    composite_score: float = 0.0
    messages_sent: int
    messages_received: int
    resource_utilization_pct: float
    avg_trust_given: float
    avg_trust_received: float
    failure_count: int
    conflict_involvement_count: int
    overall_rank: int

    class Config:
        orm_mode = True

class AgentPerformanceMetricsRead(AgentPerformanceMetricsBase):
    pass
