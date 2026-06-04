import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple

from ..utils.redis_pub import publish_event
from .agent_state import AgentState

# Helper to consume resources and energy
def _consume(state: Dict[str, Any], energy: float = 0.0, compute_units: float = 0.0, api_calls: int = 0, tokens: int = 0, usd: float = 0.0) -> Dict[str, Any]:
    """Update the agent's resource budget and energy score.
    Values are subtracted (clamped to >= 0). Returns a new state dict.
    """
    # Create a shallow copy of the state to avoid mutating the original
    new_state = state.copy()
    # Energy handling (subtract, clamp to >=0)
    new_state["energy_score"] = max(0.0, new_state.get("energy_score", 1.0) - energy)
    # Deep copy the resource_budget dict to avoid side‑effects on the input state
    budget = dict(new_state.get("resource_budget", {}))
    budget["compute_units"] = max(0.0, budget.get("compute_units", 0) - compute_units)
    budget["api_calls"] = max(0, budget.get("api_calls", 0) - api_calls)
    budget["tokens"] = max(0, budget.get("tokens", 0) - tokens)
    budget["usd_budget"] = max(0.0, budget.get("usd_budget", 0.0) - usd)
    new_state["resource_budget"] = budget
    return new_state

# 1. think – placeholder LLM reasoning (simulated)
def think(state: Dict[str, Any], input_data: Any) -> Dict[str, Any]:
    thought = {
        "id": str(uuid.uuid4()) if hasattr(uuid, "uuid4") else str(datetime.utcnow().timestamp()),
        "timestamp": datetime.utcnow().isoformat(),
        "content": str(input_data),
    }
    short_term = state.get("memory_short_term", [])[-19:]
    short_term.append(thought)
    new_state = _consume(state, energy=2.0, compute_units=0.1)
    new_state["memory_short_term"] = short_term
    # Apply hallucination injection if triggered
    try:
        from .failure_engine import HallucinationInjector, FailureInjector
        # First, register any custom hallucination probability (default 0.1)
        # Here we assume failure_type "hallucination" is used
        # Apply mutation to the output state (or specific fields)
        new_state = HallucinationInjector.maybe_hallucinate(
            simulation_id=state.get("simulation_id"),
            target_agent_id=state.get("agent_id"),
            original_output=new_state,
        )
    except Exception:
        # If imports fail or injector not available, ignore and proceed
        pass
    publish_event("thought_generated", {"agent_id": state.get("agent_id"), "thought": thought})
    return new_state

# 2. plan – decompose objective into steps (simple split)
def plan(state: Dict[str, Any], objective: str) -> Dict[str, Any]:
    # For simplicity, create a static plan regardless of objective
    static_plan = ["think", "communicate", "use_tool", "sleep"]
    new_state = _consume(state, energy=3.0, compute_units=0.2)
    new_state["current_plan"] = static_plan
    new_state["objective"] = objective
    publish_event("plan_created", {"agent_id": state.get("agent_id"), "plan": static_plan})
    return new_state

# 3. communicate – send a message
def communicate(state: Dict[str, Any], message: str, target_agent_id: str = None) -> Dict[str, Any]:
    outbox = state.get("messages_outbox", [])
    outbox.append({"timestamp": datetime.utcnow().isoformat(), "content": message, "target": target_agent_id})
    new_state = _consume(state, energy=1.0, api_calls=1)
    new_state["messages_outbox"] = outbox
    publish_event("message_sent", {"agent_id": state.get("agent_id"), "message": message, "target": target_agent_id})
    return new_state

# 4. use_tool – invoke a tool and store result
def use_tool(state: Dict[str, Any], tool_id: str, payload: Any) -> Dict[str, Any]:
    """Invoke a tool and store result, with optional injected failure.
    If a `tool_failure` injection is active for this agent/simulation, the tool call
    registers the failure and raises a `ToolTimeoutError` (or `ToolHTTPError`).
    """
    # Retrieve simulation and agent identifiers from state
    simulation_id = state.get("simulation_id")
    agent_id = state.get("agent_id")

    # Check for injected tool failure
    if simulation_id and agent_id and FailureInjector.is_triggered(simulation_id, agent_id, "tool_failure"):
        # Register the failure for cascading logic
        CascadingFailureHandler.register_failure(simulation_id, agent_id, tool_id)
        # Simulate a timeout error
        raise ToolTimeoutError(f"Injected tool failure for {tool_id} in simulation {simulation_id}")

    # Normal tool execution (placeholder logic)
    tools = state.get("tools_called", [])
    result = {"tool_id": tool_id, "payload": payload, "result": f"result_of_{tool_id}", "timestamp": datetime.utcnow().isoformat()}
    tools.append(result)
    new_state = _consume(state, energy=4.0, api_calls=1, compute_units=0.5)
    new_state["tools_called"] = tools
    publish_event("tool_used", {"agent_id": agent_id, "tool_id": tool_id, "payload": payload})
    return new_state

# 5. negotiate – request resource from another agent (simple record)
def negotiate(state: Dict[str, Any], proposal: Dict[str, Any]) -> Dict[str, Any]:
    inbox = state.get("messages_inbox", [])
    inbox.append({"timestamp": datetime.utcnow().isoformat(), "proposal": proposal})
    new_state = _consume(state, energy=2.5, api_calls=1)
    new_state["messages_inbox"] = inbox
    publish_event("negotiation_received", {"agent_id": state.get("agent_id"), "proposal": proposal})
    return new_state

# 6. cooperate – share memory/result with another agent
def cooperate(state: Dict[str, Any], partner_id: str, shared_data: Any) -> Dict[str, Any]:
    outbox = state.get("messages_outbox", [])
    outbox.append({"timestamp": datetime.utcnow().isoformat(), "type": "cooperate", "partner": partner_id, "data": shared_data})
    # Consume only compute_units and API calls, do not subtract energy
    new_state = _consume(state, compute_units=0.2)
    # Increase energy modestly, capped at 1.0
    new_state["energy_score"] = min(1.0, new_state.get("energy_score", 0.0) + 0.1)
    new_state["messages_outbox"] = outbox
    publish_event("cooperation", {"agent_id": state.get("agent_id"), "partner_id": partner_id, "data": shared_data})
    return new_state

# 7. compete – attempt to acquire a contested resource
def compete(state: Dict[str, Any], opponent_id: str, stake: float) -> Dict[str, Any]:
    energy_change = stake * 0.01
    # Subtract energy once via _consume
    new_state = _consume(state, energy=energy_change, compute_units=0.1)
    # Energy score already reduced by _consume, no further subtraction needed
    publish_event("competition", {"agent_id": state.get("agent_id"), "opponent_id": opponent_id, "stake": stake, "energy_change": energy_change})
    return new_state

# 8. sleep – recover energy over N ticks (simulated here as immediate boost)
def sleep(state: Dict[str, Any], ticks: int = 1) -> Dict[str, Any]:
    recovery = 0.05 * ticks
    new_state = state.copy()
    new_state["energy_score"] = min(1.0, new_state.get("energy_score", 0.0) + recovery)
    new_state["status"] = "sleeping"
    publish_event("agent_sleep", {"agent_id": state.get("agent_id"), "ticks": ticks, "recovery": recovery})
    return new_state

# 9. escalate – flag a problem
def escalate(state: Dict[str, Any], issue: str) -> Dict[str, Any]:
    new_state = _consume(state, energy=1.0, api_calls=1)
    new_state["status"] = "failed"
    publish_event("issue_escalated", {"agent_id": state.get("agent_id"), "issue": issue})
    return new_state

# 10. fail – terminate with failure record
def fail(state: Dict[str, Any], reason: str) -> Dict[str, Any]:
    new_state = state.copy()
    new_state["status"] = "failed"
    new_state["failure_reason"] = reason
    publish_event("agent_failed", {"agent_id": state.get("agent_id"), "reason": reason})
    return new_state

# Mapping for dynamic dispatch (optional helper)
ACTION_MAP = {
    "think": think,
    "plan": plan,
    "communicate": communicate,
    "use_tool": use_tool,
    "negotiate": negotiate,
    "cooperate": cooperate,
    "compete": compete,
    "sleep": sleep,
    "escalate": escalate,
    "fail": fail,
}

def execute_action(state: Dict[str, Any], action_name: str, *args, **kwargs) -> Dict[str, Any]:
    if action_name not in ACTION_MAP:
        raise ValueError(f"Unsupported action: {action_name}")
    return ACTION_MAP[action_name](state, *args, **kwargs)


class AgentGraphNode:
    """Wrapper node for an agent within the AgentGraph, encapsulating their current AgentState."""
    def __init__(self, agent_id: str, state: AgentState = None):
        self.id = agent_id
        self.state = state or AgentState(agent_id=agent_id)


class AgentGraph:
    """Simulation graph containing all active agent states, trust scores, and resource allocations."""
    def __init__(self, simulation_id: str):
        # Store simulation_id as a UUID object for ORM compatibility
        try:
            self.simulation_id = uuid.UUID(simulation_id)
        except Exception:
            # If already a UUID, keep as is
            self.simulation_id = simulation_id
        self.current_tick: int = 0
        self.agents: Dict[str, AgentGraphNode] = {}
        self.trust_matrix: Dict[Tuple[str, str], float] = {}
        self.resource_allocation: Dict[str, List[Tuple[str, float]]] = {}

