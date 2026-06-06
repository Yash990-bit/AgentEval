import datetime
from typing import Any, Dict, List, Set, Tuple

from ..utils.redis_pub import publish_event
from fastapi import HTTPException
from ..socket import socket_manager

# Trust engine integration imports
from ..db.session import SessionLocal
from ..services import get_trust_engine


class InteractionEngine:
    """Interaction engine handling messages, resources, trust, and relationships.

    Trust updates follow the formulas:
    - Increase: ``new = min(old + delta, 1.0)``
    - Decrease: ``new = max(old + delta, 0.0)``
    where ``delta`` can be positive or negative.
    """

    def __init__(self, simulation_id: str):
        self.simulation_id = simulation_id
        self.messages: List[Dict[str, Any]] = []
        self.resource_budgets: Dict[str, Dict[str, Any]] = {}
        self.negotiations: List[Dict[str, Any]] = []
        self.alliances: Set[frozenset] = set()
        self.trust_scores: Dict[str, Dict[str, float]] = {}
        from .agent_graph import AgentGraph
        self.graph = AgentGraph(simulation_id)
        # Initialize DB session and TrustEngine
        self._db = SessionLocal()
        self.trust_engine = get_trust_engine(self._db)

    # ---------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------
    def _socket_emit(self, event: str, payload: Any):
        """Safely emit events to socket_manager checking for a running asyncio loop."""
        if socket_manager.app is not None:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(socket_manager.emit(event, payload))
            except RuntimeError:
                # No running event loop (e.g. running in synchronous tests)
                pass

    def _ensure_budget(self, agent_id: str) -> Dict[str, Any]:
        """Return (or create) a budget dict for *agent_id*.
        Default budget gives 100 API calls so that agents can send messages out of the box.
        """
        if agent_id not in self.resource_budgets:
            self.resource_budgets[agent_id] = {
                "compute_units": 0.0,
                "api_calls": 100,
                "tokens": 0,
                "usd_budget": 0.0,
            }
        return self.resource_budgets[agent_id]

    def _ensure_trust(self, agent_id: str) -> Dict[str, float]:
        if agent_id not in self.trust_scores:
            self.trust_scores[agent_id] = {}
        return self.trust_scores[agent_id]

    def _update_trust(self, source_id: str, target_id: str, delta: float):
        # Update in‑memory trust map for quick UI feedback
        trust = self._ensure_trust(source_id)
        old = trust.get(target_id, 0.5)  # neutral start
        new = min(max(old + delta, 0.0), 1.0)
        trust[target_id] = new
        # Persist the change via TrustEngine
        self.trust_engine.update_trust(source_id, target_id, new)
        payload = {
            "simulation_id": self.simulation_id,
            "source_id": source_id,
            "target_id": target_id,
            "old_trust": old,
            "new_trust": new,
            "delta": delta,
        }
        publish_event("trust_changed", payload)
        self._socket_emit("trust_changed", payload)

    # ---------------------------------------------------------------------
    # Core interaction methods
    # ---------------------------------------------------------------------
    def send_message(self, sender_id: str, receiver_id: str, message_type: str, content: Any) -> Dict[str, Any]:
        sender_budget = self._ensure_budget(sender_id)
        if sender_budget.get("api_calls", 0) < 1:
            raise HTTPException(status_code=400, detail="Sender does not have enough API call budget")
        sender_budget["api_calls"] -= 1
        msg = {
            "simulation_id": self.simulation_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "type": message_type,
            "content": content,
        }
        self.messages.append(msg)
        publish_event("message_sent", {
            "simulation_id": self.simulation_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "type": message_type,
        })
        self._socket_emit("new_message", msg)
        return msg

    def share_resource(self, sender_id: str, receiver_id: str, resource_type: str, amount: float) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if resource_type not in {"compute_units", "api_calls", "tokens", "usd_budget"}:
            raise HTTPException(status_code=400, detail=f"Unsupported resource type: {resource_type}")
        sender_budget = self._ensure_budget(sender_id)
        receiver_budget = self._ensure_budget(receiver_id)
        if sender_budget.get(resource_type, 0) < amount:
            raise HTTPException(status_code=400, detail="Sender lacks sufficient resource balance")
        sender_budget[resource_type] -= amount
        receiver_budget[resource_type] += amount
        publish_event("resource_transferred", {
            "simulation_id": self.simulation_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "resource_type": resource_type,
            "amount": amount,
        })
        # Trust gain for cooperation
        self._update_trust(sender_id, receiver_id, 0.05)
        self._socket_emit("resource_transferred", {
            "simulation_id": self.simulation_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "resource_type": resource_type,
            "amount": amount,
        })
        return sender_budget, receiver_budget

    def negotiate(self, initiator_id: str, target_id: str, offer_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a negotiation offer using NegotiationGraph.

        The NegotiationGraph class builds and compiles a LangGraph state graph
        representing the multi-round negotiation process.
        """
        from .negotiation_graph import NegotiationGraph
        graph = NegotiationGraph(self)
        negotiation = graph.propose(initiator_id, target_id, offer_payload)
        publish_event("negotiation_received", negotiation)
        self._socket_emit("negotiation_received", negotiation)
        return negotiation

    def form_alliance(self, agent_a_id: str, agent_b_id: str) -> frozenset:
        alliance = frozenset({agent_a_id, agent_b_id})
        self.alliances.add(alliance)
        # Boost mutual trust
        self._update_trust(agent_a_id, agent_b_id, 0.1)
        self._update_trust(agent_b_id, agent_a_id, 0.1)
        payload = {"simulation_id": self.simulation_id, "agents": list(alliance)}
        publish_event("alliance_formed", payload)
        self._socket_emit("alliance_formed", payload)
        return alliance

    def declare_rivalry(self, agent_a_id: str, agent_b_id: str) -> None:
        # Reduce trust
        self._update_trust(agent_a_id, agent_b_id, -0.15)
        self._update_trust(agent_b_id, agent_a_id, -0.15)
        payload = {
            "simulation_id": self.simulation_id,
            "agents": [agent_a_id, agent_b_id],
            "type": "rival",
        }
        publish_event("rivalry_declared", payload)
        self._socket_emit("rivalry_declared", payload)
        # Persist relationship to DB (unchanged)
        from ..db.session import SessionLocal
        from ..db.models.relationship import AgentRelationship
        import uuid
        db = SessionLocal()
        try:
            rel = AgentRelationship(
                simulation_id=uuid.UUID(self.simulation_id) if isinstance(self.simulation_id, str) else self.simulation_id,
                agent_a_id=agent_a_id,
                agent_b_id=agent_b_id,
                relationship_type="rival",
                trust_score=self.trust_scores.get(agent_a_id, {}).get(agent_b_id, 0.0),
                interaction_count=0,
                last_interaction_tick=0,
            )
            db.add(rel)
            db.commit()
        finally:
            db.close()
