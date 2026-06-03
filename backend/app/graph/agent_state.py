from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class AgentState(BaseModel):
    """State payload stored on each LangGraph node for an agent.

    This model is serialisable (JSON) and will be persisted by LangGraph
    as the node "data" attribute.
    """
    agent_id: str = Field(..., description="UUID of the agent")
    memory_short_term: List[dict] = Field(default_factory=list, description="Recent observations, max 20 items")
    memory_long_term: List[str] = Field(default_factory=list, description="References to vector embeddings (ids) stored in Qdrant")
    current_plan: List[dict] = Field(default_factory=list, description="Ordered list of sub‑goals")
    current_action: Optional[str] = Field(default=None, description="Name of the action currently being executed")
    messages_outbox: List[dict] = Field(default_factory=list)
    messages_inbox: List[dict] = Field(default_factory=list)
    tools_called: List[dict] = Field(default_factory=list)
    resource_used: Dict[str, float] = Field(default_factory=lambda: {"compute_units": 0, "api_calls": 0, "tokens": 0, "usd_budget": 0.0})
    resource_budget: Dict[str, float] = Field(default_factory=dict)
    trust_scores: Dict[str, float] = Field(default_factory=dict)
    goal_stack: List[dict] = Field(default_factory=list)
    resource_requests: List[str] = Field(default_factory=list)
    waiting_for: List[str] = Field(default_factory=list)
    loop_count: int = 0
    last_error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
