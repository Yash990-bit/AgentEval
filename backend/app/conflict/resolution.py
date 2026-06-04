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
        if aid in graph.agents:
            node = graph.agents[aid]
            if not hasattr(node.state, "resource_used"):
                node.state.resource_used = {}
            used = node.state.resource_used
            if isinstance(used, dict):
                used[resource_type] = round(share, 2)
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
    lowest_agent_id = min(agents_involved, key=lambda aid: _get_agent_priority(aid, graph))
    if lowest_agent_id in graph.agents:
        graph.agents[lowest_agent_id].state.status = "sleeping"

def resolve_trust_breakdown(conflict, db: Session, graph) -> None:
    """Mediate trust breakdown by injecting forced cooperation events and improving trust."""
    agents_involved = conflict.agents_involved
    if len(agents_involved) < 2:
        return
    agent_a_id, agent_b_id = agents_involved[0], agents_involved[1]
    rel = db.query(AgentRelationship).filter(
        ((AgentRelationship.agent_a_id == agent_a_id) & (AgentRelationship.agent_b_id == agent_b_id)) |
        ((AgentRelationship.agent_a_id == agent_b_id) & (AgentRelationship.agent_b_id == agent_a_id))
    ).first()
    if rel:
        rel.trust_score = 0.4
        rel.relationship_type = RelationshipType.neutral
        db.add(rel)
        db.commit()
    if hasattr(graph, "trust_matrix"):
        graph.trust_matrix[(agent_a_id, agent_b_id)] = 0.4
        graph.trust_matrix[(agent_b_id, agent_a_id)] = 0.4

def resolve_communication_conflict(conflict, db: Session, graph) -> None:
    """Resolve communication conflicts by flagging agents and clearing contradictory queues."""
    agents = conflict.agents_involved
    for aid in agents:
        if aid in graph.agents:
            agent = graph.agents[aid]
            # Mark that the agent needs synchronization
            setattr(agent.state, "communication_issue", True)
            # Optional: clear pending contradictory messages (if stored in state)
            if hasattr(agent.state, "pending_messages"):
                agent.state.pending_messages = []

def resolve_deadlock(conflict, db: Session, graph) -> None:
    """Break a deadlock by pre‑empting the lowest‑priority agent in the cycle."""
    agents = conflict.agents_involved
    if not agents:
        return
    # Identify lowest‑priority agent
    lowest = min(agents, key=lambda aid: _get_agent_priority(aid, graph))
    if lowest in graph.agents:
        agent = graph.agents[lowest]
        # Remove its waiting list to break the cycle
        if hasattr(agent.state, "waiting_for"):
            agent.state.waiting_for = []
        # Optionally set a status indicating pre‑emption
        agent.state.status = "preempted"

def resolve_priority_inversion(conflict, db: Session, graph) -> None:
    """Fix priority inversion by re‑allocating the contested resource to the higher‑priority agent."""
    agents = conflict.agents_involved
    if len(agents) != 2:
        return
    low, high = agents[0], agents[1]
    # Find the resource where inversion occurs
    for resource, owners in list(graph.resource_allocation.items()):
        owner_ids = {owner[0] for owner in owners}
        if low in owner_ids and high in owner_ids:
            # Remove low‑priority holder
            new_owners = [(aid, prio) for aid, prio in owners if aid != low]
            # Add high‑priority holder with max priority (or keep existing)
            if not any(aid == high for aid, _ in new_owners):
                new_owners.append((high, _get_agent_priority(high, graph)))
            graph.resource_allocation[resource] = new_owners
            break
