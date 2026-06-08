
"""LangGraph‑based simulation engine with environment integration.

The engine operates on a collection of agents (from the in‑memory store or DB).
Each tick:
  • Applies resource budgeting and updates scores.
  • Reacts to environment events (handled by Environment).
  • Generates a simple chain of links for D3 visualisation.

Public API: `SimulationEngine` with `run_tick()` returning a dict suitable for JSON.
"""

import random
from typing import List, Dict

# Pydantic model for an agent (used for typing only)
from ..models.agent import Agent as AgentSchema

# Environment class (defined in backend/app/core/environment.py)
from .environment import Environment


class SimulationEngine:
    def __init__(self, agents: List[Dict] = None, env: Environment = None):
        # Accept a list of plain dicts or AgentSchema instances
        self.agents = [AgentSchema(**a) if isinstance(a, dict) else a for a in (agents or [])]
        self.env = env or Environment()
        self.tick_counter = 0

    def _apply_resources(self, agent: AgentSchema) -> AgentSchema:
        """Simple deterministic resource budgeting.
        - Energy drops by 5‑15 each tick.
        - Resource budget drops by 1‑5.
        - Trust slightly decays, risk increases a little.
        """
        agent.energy_score = max(0, agent.energy_score - random.randint(5, 15))
        agent.resource_budget = max(0, agent.resource_budget - random.uniform(1, 5))
        agent.trust_score = max(0.0, min(1.0, agent.trust_score - 0.01))
        agent.risk_score = min(1.0, agent.risk_score + 0.01)
        return agent

    def _generate_links(self) -> List[Dict]:
        """Create a simple chain of links for visualization.
        Links are ``{"source": id, "target": id}`` pairs.
        """
        if len(self.agents) < 2:
            return []
        links: List[Dict] = []
        for src, tgt in zip(self.agents[:-1], self.agents[1:]):
            links.append({"source": src.id, "target": tgt.id})
        return links

    def run_tick(self) -> Dict:
        """Execute one simulation step.

        Returns a dict with keys:
        - ``agents`` – list of agent dicts (id, name, role, objective, scores, status).
        - ``links`` – list of link dicts for D3 visualisation.
        - ``time`` – current simulation time from Environment.
        - ``resources`` – snapshot of the global resource pool.
        - ``events`` – any active events this tick.
        - ``hazards`` – any active hazards this tick.
        """
        # Let the environment advance its clock and possibly generate events/hazards
        self.env.advance()
        self.tick_counter += 1

        # Apply environment effects to each agent (e.g., scarcity)
        for agent in self.agents:
            # Example: if a scarcity event is active, further decrease resources
            if self.env.is_scarcity_active():
                agent.resource_budget = max(0, agent.resource_budget - random.uniform(0.5, 2.0))

        # Update each agent's internal state
        updated_agents: List[AgentSchema] = []
        for agent in self.agents:
            updated = self._apply_resources(agent)
            updated_agents.append(updated)
        self.agents = updated_agents

        agents_payload = [
            {
                "id": a.id,
                "name": a.name,
                "role": a.role,
                "objective": a.objective,
                "energy_score": round(a.energy_score, 2),
                "resource_budget": round(a.resource_budget, 2),
                "trust_score": round(a.trust_score, 2),
                "risk_score": round(a.risk_score, 2),
                "status": "active" if a.energy_score > 0 else "exhausted",
            }
            for a in self.agents
        ]

        return {
            "agents": agents_payload,
            "links": self._generate_links(),
            "time": self.env.current_time.isoformat(),
            "resources": self.env.resource_pool.to_dict(),
            "events": [e.to_dict() for e in self.env.active_events()],
            "hazards": [h.to_dict() for h in self.env.active_hazards()],
        }
    def evaluate_agents(self) -> Dict:
        """Compute evaluation scores for each agent.

        Returns a dict with keys:
        - `agents` – list of agent evaluation dicts (id, scores, composite, rank).
        - `summary` – overall stats (average scores, etc.).
        """
        evaluations = []
        for a in self.agents:
            intelligence = 0.4 * (a.goals_completed / max(1, a.total_goals) * 100) + 0.3 * a.plan_quality + 0.3 * a.reasoning_depth
            cooperation = 0.5 * (a.alliance_count / max(1, a.possible_alliances) * 100) + 0.3 * a.avg_trust_given + 0.2 * a.resource_sharing_rate
            reliability = 0.4 * (100 - a.failure_rate) + 0.4 * a.deadline_hit_rate + 0.2 * (100 - a.hallucination_rate)
            efficiency = 0.5 * a.resource_efficiency + 0.3 * a.goal_completion_speed_normalized + 0.2 * (100 - a.waste_rate)
            risk = 0.3 * a.conflict_involvement_rate + 0.3 * a.escalation_rate + 0.4 * a.failure_propagation_score
            
            # Composite score (risk is lower = better, so invert it for composite)
            composite = (
                0.25 * intelligence +
                0.20 * cooperation +
                0.20 * reliability +
                0.20 * efficiency +
                0.15 * (100 - risk)
            )
            evaluations.append({
                "id": a.id,
                "name": a.name,
                "intelligence": round(intelligence, 2),
                "cooperation": round(cooperation, 2),
                "reliability": round(reliability, 2),
                "efficiency": round(efficiency, 2),
                "risk": round(risk, 2),
                "composite": round(composite, 2),
            })
            
        # Rank agents by composite score descending
        evaluations.sort(key=lambda x: x["composite"], reverse=True)
        for rank, ev in enumerate(evaluations, start=1):
            ev["rank"] = rank
            
        # Compute summary averages
        if evaluations:
            summary = {
                "avg_intelligence": round(sum(e["intelligence"] for e in evaluations) / len(evaluations), 2),
                "avg_cooperation": round(sum(e["cooperation"] for e in evaluations) / len(evaluations), 2),
                "avg_reliability": round(sum(e["reliability"] for e in evaluations) / len(evaluations), 2),
                "avg_efficiency": round(sum(e["efficiency"] for e in evaluations) / len(evaluations), 2),
                "avg_risk": round(sum(e["risk"] for e in evaluations) / len(evaluations), 2),
                "avg_composite": round(sum(e["composite"] for e in evaluations) / len(evaluations), 2),
            }
        else:
            summary = {}
            
        return {"agents": evaluations, "summary": summary}


# Helper to instantiate the engine from the global in‑memory store used by the API
def get_engine_from_store(agent_store: Dict[str, Dict]) -> SimulationEngine:
    agents = [agent_store[aid] for aid in agent_store]
    return SimulationEngine(agents)
