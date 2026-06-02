// backend/app/core/engine.py
"""LangGraph‑based simulation engine (simplified).

The engine operates on a collection of agents (from the in‑memory store or DB).
Each tick:
  • Lets every agent "think" and optionally "plan" – here we just decrement resources.
  • Updates energy, resource_budget, trust_score, risk_score.
  • Generates a list of links (a simple chain for demo).
The public API is the `SimulationEngine` class with a `run_tick()` method that returns the
current state as a dict suitable for JSON serialisation.
"""

import random
from typing import List, Dict

# Import the Pydantic model for an agent (used for typing only)
from ..models.agent import Agent as AgentSchema

class SimulationEngine:
    def __init__(self, agents: List[Dict] = None):
        # Accept a list of plain dicts or AgentSchema instances
        self.agents = [AgentSchema(**a) if isinstance(a, dict) else a for a in (agents or [])]

    def _apply_resources(self, agent: AgentSchema):
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
        Links are generated as ``{"source": id, "target": id}`` pairs.
        """
        if len(self.agents) < 2:
            return []
        links = []
        for src, tgt in zip(self.agents[:-1], self.agents[1:]):
            links.append({"source": src.id, "target": tgt.id})
        return links

    def run_tick(self) -> Dict:
        """Execute one simulation step.

        Returns a dict with two keys:
        - ``agents`` – list of agent dicts (id, name, role, objective, scores).
        - ``links`` – list of link dicts for D3 visualisation.
        """
        # Update each agent's internal state
        updated_agents = []
        for agent in self.agents:
            updated = self._apply_resources(agent)
            updated_agents.append(updated)
        self.agents = updated_agents

        # Prepare serialisable payload
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

        links_payload = self._generate_links()

        return {"agents": agents_payload, "links": links_payload}

# Helper to instantiate the engine from the global in‑memory store used by the API
def get_engine_from_store(agent_store: Dict[str, Dict]) -> SimulationEngine:
    agents = [agent_store[aid] for aid in agent_store]
    return SimulationEngine(agents)
