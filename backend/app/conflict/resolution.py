# backend/app/conflict/resolution.py
"""Conflict auto-resolution rules."""

import datetime
from sqlalchemy.orm import Session
from app.db.models.relationship import AgentRelationship, RelationshipType
from app.config import RESOURCE_CAPACITY

def _get_agent_priority(agent_id: str, graph) -> float:
    """Helper to determine agent priority based on their role or state."""
    if agent_id not in graph.agents:
        return 1.0
    agent = graph.agents[agent_id]
    # Check if there is role-based priority
    role = getattr(agent, "role", "support").lower()
    role_weights = {
        "coordinator": 3.0,
        "executor": 2.5,
        "planner": 2.0,
        "researcher": 1.5,
        "analyst": 1.5,
        "support": 1.0,
    }
    return role_weights.get(role, 1.0)

def resolve_resource_conflict(conflict, db: Session, graph) -> None:
    """Resolves resource conflicts by allocating the capacity using priority-weighted round-robin."""
    agents_involved = conflict.agents_involved
    if not agents_involved:
        return

    # 1. Identify resource type from root cause
    resource_type = "compute_units"
    for r in ["compute_units", "api_calls", "tokens", "usd_budget"]:
        if r in conflict.root_cause:
            resource_type = r
            break

    # 2. Get total capacity
    total_capacity = RESOURCE_CAPACITY.get(resource_type, 10.0)

    # 3. Retrieve agent priorities
    priorities = {aid: _get_agent_priority(aid, graph) for aid in agents_involved}
    total_priority = sum(priorities.values())

    # 4. Allocate share of budget to each agent
    for aid in agents_involved:
        share = (priorities[aid] / total_priority) * total_capacity
        # Update in graph node state
        if aid in graph.agents:
            node = graph.agents[aid]
            if not hasattr(node.state, "resource_used"):
                node.state.resource_used = {}
            # Update the used resources budget
            used = node.state.resource_used
            if isinstance(used, dict):
                used[resource_type] = round(share, 2)

            # Ensure resource_budget dict exists and update it as well (expected by tests)
            if not hasattr(node.state, "resource_budget"):
                node.state.resource_budget = {}
            budget = node.state.resource_budget
            if isinstance(budget, dict):
                budget[resource_type] = round(share, 2)

def resolve_goal_conflict(conflict, db: Session, graph) -> None:
    """Resolves goal conflicts by pausing the lower-priority agent."""
    agents_involved = conflict.agents_involved
    if len(agents_involved) < 2:
        return

    # Find agent with lowest priority
    lowest_agent_id = min(agents_involved, key=lambda aid: _get_agent_priority(aid, graph))

    # Pause lower-priority agent (set status to sleeping)
    if lowest_agent_id in graph.agents:
        graph.agents[lowest_agent_id].state.status = "sleeping"

def resolve_trust_breakdown(conflict, db: Session, graph) -> None:
    """Mediate trust breakdown by injecting forced cooperation events and improving trust."""
    agents_involved = conflict.agents_involved
    if len(agents_involved) < 2:
        return

    agent_a_id = agents_involved[0]
    agent_b_id = agents_involved[1]

    # Boost trust score back up to 0.4 to start mediation
    # Query database and update AgentRelationship
    rel = db.query(AgentRelationship).filter(
        ((AgentRelationship.agent_a_id == agent_a_id) & (AgentRelationship.agent_b_id == agent_b_id)) |
        ((AgentRelationship.agent_a_id == agent_b_id) & (AgentRelationship.agent_b_id == agent_a_id))
    ).first()

    if rel:
        rel.trust_score = 0.4
        rel.relationship_type = RelationshipType.neutral
        db.add(rel)
        db.commit()

    # In graph trust scores, also boost
    if hasattr(graph, "trust_matrix"):
        graph.trust_matrix[(agent_a_id, agent_b_id)] = 0.4
        graph.trust_matrix[(agent_b_id, agent_a_id)] = 0.4
