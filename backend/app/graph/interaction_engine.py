import datetime
from typing import Any, Dict, List, Set, Tuple

from ..utils.redis_pub import publish_event


class InteractionEngine:
    """In‑memory interaction engine for agent communication.

    This is a lightweight implementation suitable for unit testing and early
    development. It stores messages, resource budgets, and alliances in Python
    data structures. In production you would replace these with persistent DB
    calls.
    """

    def __init__(self, simulation_id: str):
        self.simulation_id = simulation_id
        # Store messages as a list of dicts
        self.messages: List[Dict[str, Any]] = []
        # Resource budgets per agent_id
        self.resource_budgets: Dict[str, Dict[str, Any]] = {}
        # Negotiations history
        self.negotiations: List[Dict[str, Any]] = []
        # Alliances stored as a set of frozenset pairs for quick lookup
        self.alliances: Set[frozenset] = set()

    # ---------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------
    def _ensure_budget(self, agent_id: str) -> Dict[str, Any]:
        """Return the budget dict for *agent_id*, creating a default one if
        it does not exist.
        """
        if agent_id not in self.resource_budgets:
            # Default budgets – generous for tests
            self.resource_budgets[agent_id] = {
                "compute_units": 0.0,
                "api_calls": 0,
                "tokens": 0,
                "usd_budget": 0.0,
            }
        return self.resource_budgets[agent_id]

    # ---------------------------------------------------------------------
    # Public interaction methods
    # ---------------------------------------------------------------------
    def send_message(
        self, sender_id: str, receiver_id: str, message_type: str, content: Any
    ) -> Dict[str, Any]:
        """Send a message from *sender_id* to *receiver_id*.

        The method validates that the sender has at least one API call left (cost
        = 1). It then records the message, updates the sender's ``api_calls``
        budget and publishes a ``message_sent`` event.
        """
        sender_budget = self._ensure_budget(sender_id)
        if sender_budget.get("api_calls", 0) < 1:
            raise ValueError("Sender does not have enough API call budget")
        # Consume one API call
        sender_budget["api_calls"] = sender_budget.get("api_calls", 0) - 1

        msg = {
            "simulation_id": self.simulation_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "type": message_type,
            "content": content,
        }
        self.messages.append(msg)
        publish_event(
            "message_sent",
            {
                "simulation_id": self.simulation_id,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "type": message_type,
            },
        )
        return msg

    def share_resource(
        self,
        sender_id: str,
        receiver_id: str,
        resource_type: str,
        amount: float,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Transfer *amount* of *resource_type* from *sender* to *receiver*.

        Raises ``ValueError`` if the sender does not have sufficient resources.
        """
        if resource_type not in {"compute_units", "api_calls", "tokens", "usd_budget"}:
            raise ValueError(f"Unsupported resource type: {resource_type}")
        sender_budget = self._ensure_budget(sender_id)
        receiver_budget = self._ensure_budget(receiver_id)
        if sender_budget.get(resource_type, 0) < amount:
            raise ValueError("Sender lacks sufficient resource balance")
        # Perform atomic transfer
        sender_budget[resource_type] = sender_budget.get(resource_type, 0) - amount
        receiver_budget[resource_type] = receiver_budget.get(resource_type, 0) + amount
        publish_event(
            "resource_transferred",
            {
                "simulation_id": self.simulation_id,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "resource_type": resource_type,
                "amount": amount,
            },
        )
        return sender_budget, receiver_budget

    def negotiate(
        self, initiator_id: str, target_id: str, offer_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record a negotiation offer from *initiator* to *target*.

        The current stub simply stores the proposal and emits an event – the
        target's decision logic will be implemented elsewhere.
        """
        negotiation = {
            "simulation_id": self.simulation_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "initiator_id": initiator_id,
            "target_id": target_id,
            "offer": offer_payload,
        }
        self.negotiations.append(negotiation)
        publish_event(
            "negotiation_received",
            {
                "simulation_id": self.simulation_id,
                "initiator_id": initiator_id,
                "target_id": target_id,
                "offer": offer_payload,
            },
        )
        return negotiation

    def form_alliance(self, agent_a_id: str, agent_b_id: str) -> frozenset:
        """Create a bilateral alliance between two agents.

        Alliances are stored as an unordered pair (frozenset) to avoid duplicate
        entries like (a,b) and (b,a).
        """
        alliance = frozenset({agent_a_id, agent_b_id})
        self.alliances.add(alliance)
        publish_event(
            "alliance_formed",
            {
                "simulation_id": self.simulation_id,
                "agents": list(alliance),
            },
        )
        return alliance
