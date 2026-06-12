import datetime
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func, and_, or_

from app.models.trust import AgentTrustEdge
from app.db.models import Base

class TrustEngine:
    """Engine to manage trust relationships between agents.

    All trust edges are stored in the ``agent_trust_edges`` table.
    Each edge record contains the current ``trust_score`` and ``influence_score`` as well as
    a ``history`` JSONB array that records every change with its tick.
    """

    def __init__(self, session: Session):
        self.session = session

    # ---------------------------------------------------------------------
    # Trust change rules
    # ---------------------------------------------------------------------
    _CHANGE_MAP: Dict[str, float] = {
        "cooperation_success": 0.05,
        "message_accepted": 0.03,
        "resource_shared": 0.08,
        "alliance_formed": 0.10,
        "message_rejected": -0.05,
        "negotiation_broken": -0.10,
        "resource_conflict": -0.15,
        "deception_detected": -0.20,
        "betrayal": -0.30,
    }

    def apply_event(
        self,
        simulation_id: str,
        source_agent_id: str,
        target_agent_id: str,
        event_type: str,
        tick: int,
    ) -> None:
        """Apply a single trust‑changing event.

        Parameters
        ----------
        simulation_id: str
            Identifier of the simulation.
        source_agent_id: str
            The agent that initiates the interaction.
        target_agent_id: str
            The agent that receives the interaction.
        event_type: str
            One of the keys in ``_CHANGE_MAP``.
        tick: int
            Current simulation tick.
        """
        delta = self._CHANGE_MAP.get(event_type)
        if delta is None:
            raise ValueError(f"Unknown trust event type: {event_type}")

        # Fetch or create the edge
        edge: AgentTrustEdge | None = self.session.execute(
            select(AgentTrustEdge)
            .where(
                AgentTrustEdge.simulation_id == simulation_id,
                AgentTrustEdge.source_agent_id == source_agent_id,
                AgentTrustEdge.target_agent_id == target_agent_id,
            )
        ).scalar_one_or_none()

        if edge is None:
            edge = AgentTrustEdge(
                simulation_id=simulation_id,
                source_agent_id=source_agent_id,
                target_agent_id=target_agent_id,
                trust_score=max(0.0, min(1.0, delta)),
                influence_score=0.0,
                last_updated_tick=tick,
                history=[{"tick": tick, "score": max(0.0, min(1.0, delta))}],
            )
            self.session.add(edge)
        else:
            # Update trust score, clamp between 0 and 1
            new_score = max(0.0, min(1.0, edge.trust_score + delta))
            edge.trust_score = new_score
            edge.last_updated_tick = tick
            # Append to history JSONB array
            new_history = list(edge.history) if isinstance(edge.history, list) else []
            new_history.append({"tick": tick, "score": new_score})
            edge.history = new_history
        self.session.flush()

    def update_trust(self, simulation_id: str, source_agent_id: str, target_agent_id: str, new_score: float) -> None:
        edge: AgentTrustEdge | None = self.session.execute(
            select(AgentTrustEdge)
            .where(
                AgentTrustEdge.simulation_id == simulation_id,
                AgentTrustEdge.source_agent_id == source_agent_id,
                AgentTrustEdge.target_agent_id == target_agent_id,
            )
        ).scalar_one_or_none()

        if edge is None:
            edge = AgentTrustEdge(
                simulation_id=simulation_id,
                source_agent_id=source_agent_id,
                target_agent_id=target_agent_id,
                trust_score=new_score,
                influence_score=0.0,
                last_updated_tick=0,
                history=[{"tick": 0, "score": new_score}],
            )
            self.session.add(edge)
        else:
            edge.trust_score = new_score
            new_history = list(edge.history) if isinstance(edge.history, list) else []
            new_history.append({"tick": edge.last_updated_tick, "score": new_score})
            edge.history = new_history
        self.session.flush()

    # ---------------------------------------------------------------------
    # Trust propagation (3‑hop rule)
    # ---------------------------------------------------------------------
    def propagate_trust(self, simulation_id: str) -> None:
        """Apply the 3‑hop ambient trust rule.

        If A trusts B (>0.6) and B trusts C (>0.6), then A gains +0.02 trust in C.
        """
        # Alias the table for clearer joins
        Edge = AgentTrustEdge
        subq = (
            select(
                Edge.source_agent_id.label("a"),
                Edge.target_agent_id.label("b"),
                Edge.trust_score.label("ab_score"),
            )
            .where(Edge.simulation_id == simulation_id, Edge.trust_score > 0.6)
        ).subquery()

        join_q = (
            select(
                subq.c.a,
                Edge.target_agent_id.label("c"),
                Edge.trust_score.label("bc_score"),
            )
            .join(
                Edge,
                and_(
                    Edge.source_agent_id == subq.c.b,
                    Edge.simulation_id == simulation_id,
                    Edge.trust_score > 0.6,
                ),
            )
        )

        for a, c, _ in self.session.execute(join_q):
            # Apply +0.02 if edge (a,c) exists or create it
            edge = self.session.execute(
                select(Edge)
                .where(
                    Edge.simulation_id == simulation_id,
                    Edge.source_agent_id == a,
                    Edge.target_agent_id == c,
                )
            ).scalar_one_or_none()
            if edge:
                edge.trust_score = max(0.0, min(1.0, edge.trust_score + 0.02))
                edge.last_updated_tick = edge.last_updated_tick  # keep same tick
                new_history = list(edge.history) if isinstance(edge.history, list) else []
                new_history.append({"tick": edge.last_updated_tick, "score": edge.trust_score})
                edge.history = new_history
            else:
                new_edge = AgentTrustEdge(
                    simulation_id=simulation_id,
                    source_agent_id=a,
                    target_agent_id=c,
                    trust_score=0.02,
                    influence_score=0.0,
                    last_updated_tick=0,
                    history=[{"tick": 0, "score": 0.02}],
                )
                self.session.add(new_edge)
        self.session.flush()

    # ---------------------------------------------------------------------
    # Trust decay (no interaction for 15 ticks)
    # ---------------------------------------------------------------------
    def decay_trust(self, simulation_id: str, current_tick: int) -> None:
        """Decay edges that have been idle for 15 ticks.

        For every tick beyond the idle window the trust score decays by 0.01.
        """
        Edge = AgentTrustEdge
        idle_edges = self.session.execute(
            select(Edge)
            .where(
                Edge.simulation_id == simulation_id,
                current_tick - Edge.last_updated_tick >= 15,
            )
        ).scalars()
        for edge in idle_edges:
            decay_amount = 0.01 * (current_tick - edge.last_updated_tick - 14)
            edge.trust_score = max(0.0, edge.trust_score - decay_amount)
            # Note: we keep the original ``last_updated_tick`` so future decay is incremental.
            new_history = list(edge.history) if isinstance(edge.history, list) else []
            new_history.append({"tick": current_tick, "score": edge.trust_score})
            edge.history = new_history
        self.session.flush()

    def get_all_edges(self, simulation_id: str) -> List[AgentTrustEdge]:
        """Return all trust edges for a simulation."""
        return (
            self.session.execute(
                select(AgentTrustEdge).where(AgentTrustEdge.simulation_id == simulation_id)
            )
            .scalars()
            .all()
        )
    # ---------------------------------------------------------------------
    # Reputation calculation
    # ---------------------------------------------------------------------
    def reputation(self, simulation_id: str, agent_id: str) -> float:
        """Weighted average of all incoming trust edges, multiplied by endorsement bonus.

        endorsement_bonus = 0.05 * number_of_agents_with_trust > 0.8
        """
        Edge = AgentTrustEdge
        incoming = self.session.execute(
            select(Edge.trust_score)
            .where(
                Edge.simulation_id == simulation_id,
                Edge.target_agent_id == agent_id,
            )
        ).scalars().all()
        if not incoming:
            return 0.0
        avg = sum(incoming) / len(incoming)
        # Count endorsers with trust > 0.8 towards *any* target (including this agent)
        endorsers = self.session.execute(
            select(func.count(Edge.source_agent_id))
            .where(
                Edge.simulation_id == simulation_id,
                Edge.trust_score > 0.8,
            )
        ).scalar()
        bonus = 0.05 * endorsers
        return avg * (1 + bonus)

    # ---------------------------------------------------------------------
    # Influence calculation
    # ---------------------------------------------------------------------
    def influence(self, simulation_id: str, agent_id: str) -> float:
        """Sum of outgoing trust edges multiplied by the target's resource budget ratio.

        ``resource_budget_ratio`` must be provided by the caller; here we assume a helper
        function ``get_resource_budget_ratio`` exists elsewhere in the codebase.
        """
        Edge = AgentTrustEdge
        outgoing = self.session.execute(
            select(Edge.target_agent_id, Edge.trust_score)
            .where(
                Edge.simulation_id == simulation_id,
                Edge.source_agent_id == agent_id,
            )
        ).all()
        total = 0.0
        for target_id, trust in outgoing:
            ratio = self._resource_budget_ratio(simulation_id, target_id)
            total += trust * ratio
        return total

    # ---------------------------------------------------------------------
    # Helper – placeholder for resource budget ratio lookup
    # ---------------------------------------------------------------------
    def _resource_budget_ratio(self, simulation_id: str, agent_id: str) -> float:
        """Placeholder: return a dummy ratio (1.0) if real data is unavailable.
        Replace with a real lookup against the ``agents`` table or other source.
        """
        return 1.0
