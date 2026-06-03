from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END

# Import using relative path
from .interaction_engine import InteractionEngine

class NegotiationState(TypedDict):
    initiator_id: str
    target_id: str
    status: str  # "proposed", "accepted", "rejected", "countered", "completed", "failed"
    offer: Dict[str, Any]
    history: List[Dict[str, Any]]
    rounds: int
    max_rounds: int
    error: str

class NegotiationGraph:
    """Stateful negotiation engine implemented using LangGraph.

    The graph routes offers between initiator and target, simulating evaluations
    based on mutual trust, proposing counter-offers, and applying resource
    transfers on successful agreement.
    """

    def __init__(self, engine: InteractionEngine):
        self.engine = engine
        self.graph = self._build_graph()

    def evaluate_offer(self, state: NegotiationState) -> NegotiationState:
        """Evaluates the offer from the target's perspective based on their trust in the initiator."""
        initiator_id = state["initiator_id"]
        target_id = state["target_id"]
        offer = state["offer"]
        rounds = state["rounds"]

        # Target checks their trust in the initiator
        trust = self.engine.trust_scores.get(target_id, {}).get(initiator_id, 0.5)

        if trust >= 0.7:
            state["status"] = "accepted"
        elif trust < 0.3:
            state["status"] = "rejected"
        else:
            # Generate a counter offer by decreasing amount requested (if amount exists)
            counter_offer = offer.copy()
            if "amount" in counter_offer:
                counter_offer["amount"] = round(counter_offer["amount"] * 0.5, 2)
            counter_offer["counter_by"] = target_id
            state["offer"] = counter_offer
            state["status"] = "countered"
            state["rounds"] = rounds + 1
            state["history"].append({
                "round": rounds,
                "actor": target_id,
                "action": "counter",
                "offer": counter_offer
            })
        return state

    def evaluate_counter(self, state: NegotiationState) -> NegotiationState:
        """Evaluates the counter-offer from the initiator's perspective."""
        initiator_id = state["initiator_id"]
        target_id = state["target_id"]
        offer = state["offer"]
        rounds = state["rounds"]

        # Initiator checks their trust in the target
        trust = self.engine.trust_scores.get(initiator_id, {}).get(target_id, 0.5)

        if trust >= 0.5:
            state["status"] = "accepted"
        else:
            if rounds < state["max_rounds"]:
                # Initiator counters target's counter-offer (compromise at 75% of current value)
                counter_offer = offer.copy()
                if "amount" in counter_offer:
                    counter_offer["amount"] = round(counter_offer["amount"] * 0.75, 2)
                counter_offer["counter_by"] = initiator_id
                state["offer"] = counter_offer
                state["status"] = "countered"
                state["rounds"] = rounds + 1
                state["history"].append({
                    "round": rounds,
                    "actor": initiator_id,
                    "action": "counter",
                    "offer": counter_offer
                })
            else:
                state["status"] = "rejected"
        return state

    def apply_outcome(self, state: NegotiationState) -> NegotiationState:
        """Applies side-effects based on final agreement status: resource transfers and trust score updates."""
        status = state["status"]
        initiator_id = state["initiator_id"]
        target_id = state["target_id"]
        offer = state["offer"]

        if status == "accepted":
            resource_type = offer.get("resource_type")
            amount = offer.get("amount", 0.0)
            if resource_type and amount > 0:
                try:
                    # In a resource request, target transfers to initiator
                    self.engine.share_resource(
                        sender_id=target_id,
                        receiver_id=initiator_id,
                        resource_type=resource_type,
                        amount=amount
                    )
                except Exception as e:
                    state["status"] = "failed"
                    state["error"] = str(e)
                    return state

            # Increase mutual trust
            self.engine._update_trust(target_id, initiator_id, 0.05)
            self.engine._update_trust(initiator_id, target_id, 0.05)
        elif status in ("rejected", "failed"):
            # Decrease mutual trust
            self.engine._update_trust(target_id, initiator_id, -0.05)
            self.engine._update_trust(initiator_id, target_id, -0.05)

        # Log final outcome to engine's negotiations
        record = {
            "initiator_id": initiator_id,
            "target_id": target_id,
            "status": state["status"],
            "offer": offer,
            "rounds": state["rounds"],
            "history": state["history"],
            "error": state.get("error")
        }
        self.engine.negotiations.append(record)
        return state

    def route_offer(self, state: NegotiationState) -> str:
        """Conditional routing logic after offer evaluation."""
        if state["status"] == "accepted":
            return "accept"
        elif state["status"] == "rejected":
            return "reject"
        else:
            return "counter"

    def route_counter(self, state: NegotiationState) -> str:
        """Conditional routing logic after counter-offer evaluation."""
        if state["status"] == "accepted":
            return "accept"
        elif state["status"] == "rejected":
            return "reject"
        else:
            return "counter"

    def _build_graph(self):
        workflow = StateGraph(NegotiationState)
        workflow.add_node("evaluate_offer", self.evaluate_offer)
        workflow.add_node("evaluate_counter", self.evaluate_counter)
        workflow.add_node("apply_outcome", self.apply_outcome)

        workflow.set_entry_point("evaluate_offer")

        workflow.add_conditional_edges(
            "evaluate_offer",
            self.route_offer,
            {
                "accept": "apply_outcome",
                "reject": "apply_outcome",
                "counter": "evaluate_counter"
            }
        )

        workflow.add_conditional_edges(
            "evaluate_counter",
            self.route_counter,
            {
                "accept": "apply_outcome",
                "reject": "apply_outcome",
                "counter": "evaluate_offer"
            }
        )

        workflow.add_edge("apply_outcome", END)
        return workflow.compile()

    def propose(self, initiator_id: str, target_id: str, offer_payload: dict) -> dict:
        """Submit a proposal and run the LangGraph negotiation flow."""
        initial_state = {
            "initiator_id": initiator_id,
            "target_id": target_id,
            "status": "proposed",
            "offer": offer_payload,
            "history": [
                {
                    "round": 1,
                    "actor": initiator_id,
                    "action": "propose",
                    "offer": offer_payload
                }
            ],
            "rounds": 1,
            "max_rounds": 5,
            "error": None
        }
        final_state = self.graph.invoke(initial_state)
        # Extract the final record
        return {
            "initiator_id": initiator_id,
            "target_id": target_id,
            "status": final_state["status"],
            "offer": final_state["offer"],
            "rounds": final_state["rounds"],
            "history": final_state["history"],
            "error": final_state.get("error")
        }
