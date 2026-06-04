# backend/app/conflict/detector.py
"""Conflict detection engine.
Runs each tick, checks all six conflict types, stores Conflict records,
publishes a Redis `conflict_detected` event, and triggers auto‑resolution.
"""

import json
import logging
from typing import List, Dict, Set, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import select

from ..utils.redis_pub import publish_event
from .models import Conflict, ConflictType, ConflictStatus
from .severity import compute_severity
from ..graph.agent_state import AgentState
from ..graph.agent_graph import AgentGraph
from ..config import (
    CONFLICT_DETECTION_TICK_INTERVAL,
    RESOURCE_CAPACITY,
    COMMUNICATION_WINDOW_TICKS,
)

logger = logging.getLogger(__name__)

# Lazy loaded embedding model
EMBEDDER = None

def get_embedder():
    global EMBEDDER
    if EMBEDDER is None:
        try:
            from sentence_transformers import SentenceTransformer
            EMBEDDER = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"Failed to load sentence_transformers: {e}. Falling back to keyword matching.")
    return EMBEDDER


class ConflictDetector:
    def __init__(self, db_session: Session, graph: AgentGraph, redis_pub=publish_event):
        self.db = db_session
        self.graph = graph
        self.redis_pub = redis_pub
        # sliding window for communication conflict
        self.message_history: List[Tuple[int, str, str, str]] = []  # (tick, sender, receiver, content)

    def _embed_goal(self, goal_text: str):
        embedder = get_embedder()
        if embedder is not None:
            try:
                import numpy as np
                return embedder.encode([goal_text])[0]
            except Exception:
                pass
        # Fallback word-set bag of words representation
        words = set(goal_text.lower().split())
        return words

    def _cosine_similarity(self, a, b) -> float:
        import numpy as np
        if isinstance(a, set) and isinstance(b, set):
            # Keyword Jaccard-like fallback
            if not a or not b:
                return 0.0
            return len(a.intersection(b)) / len(a.union(b))
        try:
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        except Exception:
            return 0.5  # neutral fallback

    # ---------------------------------------------------------------------
    # 1. Goal Conflict
    # ---------------------------------------------------------------------
    def _detect_goal_conflict(self, tick: int) -> List[Conflict]:
        conflicts = []
        agents = list(self.graph.agents.values())
        embeddings = {}
        for agent in agents:
            # check goal stack
            if not getattr(agent, "state", None) or not getattr(agent.state, "goal_stack", None):
                continue
            top_goal = agent.state.goal_stack[-1]
            desc = top_goal.get("description", "")
            embeddings[agent.id] = self._embed_goal(desc)
        ids = list(embeddings.keys())
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                sim = self._cosine_similarity(embeddings[ids[i]], embeddings[ids[j]])
                if sim < 0.3:
                    conflict = Conflict(
                        simulation_id=self.graph.simulation_id,
                        conflict_type=ConflictType.GOAL,
                        detected_at_tick=tick,
                        agents_involved=[ids[i], ids[j]],
                        severity_score=compute_severity(
                            resource_impact=0.0,
                            goal_criticality=1.0 - sim,  # higher conflict => higher criticality
                            trust_damage=0.0,
                            agents_affected=2,
                            total_agents=len(agents),
                        ),
                        root_cause="Goals are mutually exclusive (cosine similarity %.2f)" % sim,
                        suggested_resolution="Pause lower‑priority agent until goals diverge.",
                        status=ConflictStatus.ACTIVE,
                    )
                    conflicts.append(conflict)
        return conflicts

    # ---------------------------------------------------------------------
    # 2. Resource Conflict
    # ---------------------------------------------------------------------
    def _detect_resource_conflict(self, tick: int) -> List[Conflict]:
        conflicts = []
        demand: Dict[str, Set] = {}
        for agent in self.graph.agents.values():
            requests = getattr(agent.state, "resource_requests", [])
            for r_type in requests:
                demand.setdefault(r_type, set()).add(agent.id)
        for r_type, requesters in demand.items():
            supply = RESOURCE_CAPACITY.get(r_type, 0)
            if len(requesters) > supply:
                conflict = Conflict(
                    simulation_id=self.graph.simulation_id,
                    conflict_type=ConflictType.RESOURCE,
                    detected_at_tick=tick,
                    agents_involved=list(requesters),
                    severity_score=compute_severity(
                        resource_impact=1.0,
                        goal_criticality=0.0,
                        trust_damage=0.0,
                        agents_affected=len(requesters),
                        total_agents=len(self.graph.agents),
                    ),
                    root_cause=f"Resource '{r_type}' over‑requested ({len(requesters)}/{supply}).",
                    suggested_resolution="Allocate by priority‑weighted round‑robin.",
                    status=ConflictStatus.ACTIVE,
                )
                conflicts.append(conflict)
        return conflicts

    # ---------------------------------------------------------------------
    # 3. Communication Conflict
    # ---------------------------------------------------------------------
    def _detect_communication_conflict(self, tick: int) -> List[Conflict]:
        conflicts = []
        self.message_history = [msg for msg in self.message_history if msg[0] >= tick - COMMUNICATION_WINDOW_TICKS]
        msgs_by_receiver: Dict[str, Dict[str, Set]] = {}
        for t, sender, receiver, content in self.message_history:
            msgs_by_receiver.setdefault(receiver, {}).setdefault(content, set()).add(sender)
        for receiver, content_map in msgs_by_receiver.items():
            if len(content_map) > 1:  # more than one distinct payload
                involved = set()
                for senders in content_map.values():
                    involved.update(senders)
                conflict = Conflict(
                    simulation_id=self.graph.simulation_id,
                    conflict_type=ConflictType.COMMUNICATION,
                    detected_at_tick=tick,
                    agents_involved=list(involved),
                    severity_score=compute_severity(
                        resource_impact=0.0,
                        goal_criticality=0.0,
                        trust_damage=0.0,
                        agents_affected=len(involved),
                        total_agents=len(self.graph.agents),
                    ),
                    root_cause="Contradictory messages sent to the same agent.",
                    suggested_resolution="Synchronize message generation or add arbitration.",
                    status=ConflictStatus.ACTIVE,
                )
                conflicts.append(conflict)
        return conflicts

    # ---------------------------------------------------------------------
    # 4. Trust Breakdown
    # ---------------------------------------------------------------------
    def _detect_trust_breakdown(self, tick: int) -> List[Conflict]:
        conflicts = []
        for (a, b), trust in self.graph.trust_matrix.items():
            if trust < 0.2:
                conflict = Conflict(
                    simulation_id=self.graph.simulation_id,
                    conflict_type=ConflictType.TRUST,
                    detected_at_tick=tick,
                    agents_involved=[a, b],
                    severity_score=compute_severity(
                        resource_impact=0.0,
                        goal_criticality=0.0,
                        trust_damage=1.0 - trust,
                        agents_affected=2,
                        total_agents=len(self.graph.agents),
                    ),
                    root_cause=f"Trust fell below threshold ({trust:.2f}).",
                    suggested_resolution="Inject mediation (forced cooperation task).",
                    status=ConflictStatus.ACTIVE,
                )
                conflicts.append(conflict)
        return conflicts

    # ---------------------------------------------------------------------
    # 5. Deadlock
    # ---------------------------------------------------------------------
    def _detect_deadlock(self, tick: int) -> List[Conflict]:
        conflicts = []
        graph: Dict[str, Set[str]] = {}
        for agent in self.graph.agents.values():
            waiting_for = getattr(agent.state, "waiting_for", [])
            if waiting_for:
                graph.setdefault(agent.id, set()).update(waiting_for)
        visited: Set[str] = set()
        stack: Set[str] = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            stack.add(node)
            for nbr in graph.get(node, []):
                if nbr not in visited:
                    if dfs(nbr):
                        return True
                elif nbr in stack:
                    return True
            stack.remove(node)
            return False
            
        for node in graph:
            if node not in visited:
                if dfs(node):
                    involved = list(stack)
                    conflict = Conflict(
                        simulation_id=self.graph.simulation_id,
                        conflict_type=ConflictType.DEADLOCK,
                        detected_at_tick=tick,
                        agents_involved=involved,
                        severity_score=compute_severity(
                            resource_impact=0.0,
                            goal_criticality=0.0,
                            trust_damage=0.0,
                            agents_affected=len(involved),
                            total_agents=len(self.graph.agents),
                        ),
                        root_cause="Circular waiting detected among agents.",
                        suggested_resolution="Break the cycle by unblocking the lowest‑priority agent.",
                        status=ConflictStatus.ACTIVE,
                    )
                    conflicts.append(conflict)
        return conflicts

    # ---------------------------------------------------------------------
    # 6. Priority Inversion
    # ---------------------------------------------------------------------
    def _detect_priority_inversion(self, tick: int) -> List[Conflict]:
        conflicts = []
        for resource, owners in self.graph.resource_allocation.items():
            if not owners:
                continue
            highest = max(owners, key=lambda x: x[1])
            lowest = min(owners, key=lambda x: x[1])
            if lowest[1] < highest[1]:
                conflict = Conflict(
                    simulation_id=self.graph.simulation_id,
                    conflict_type=ConflictType.PRIORITY_INVERSION,
                    detected_at_tick=tick,
                    agents_involved=[lowest[0], highest[0]],
                    severity_score=compute_severity(
                        resource_impact=0.0,
                        goal_criticality=0.0,
                        trust_damage=0.0,
                        agents_affected=2,
                        total_agents=len(self.graph.agents),
                    ),
                    root_cause="Lower‑priority agent holds a resource needed by a higher‑priority one.",
                    suggested_resolution="Re‑allocate resource based on priority.",
                    status=ConflictStatus.ACTIVE,
                )
                conflicts.append(conflict)
        return conflicts

    # ---------------------------------------------------------------------
    # Public entry point
    # ---------------------------------------------------------------------
    def detect(self, tick: int = None) -> List[Conflict]:
        """Run all detection routines for the current simulation tick."""
        if tick is None:
            tick = getattr(self.graph, "current_tick", 0)

        all_conflicts: List[Conflict] = []
        all_conflicts.extend(self._detect_goal_conflict(tick))
        all_conflicts.extend(self._detect_resource_conflict(tick))
        all_conflicts.extend(self._detect_communication_conflict(tick))
        all_conflicts.extend(self._detect_trust_breakdown(tick))
        all_conflicts.extend(self._detect_deadlock(tick))
        all_conflicts.extend(self._detect_priority_inversion(tick))

        for conflict in all_conflicts:
            self.db.add(conflict)
            self.db.flush()  # get PK
            payload = {
                "id": str(conflict.id),
                "simulation_id": str(conflict.simulation_id),
                "type": conflict.conflict_type.value,
                "tick": conflict.detected_at_tick,
                "agents": [str(a) for a in conflict.agents_involved],
                "severity": conflict.severity_score,
                "root_cause": conflict.root_cause,
                "suggested_resolution": conflict.suggested_resolution,
                "status": conflict.status.value,
            }
            # Publish over Redis channel
            self.redis_pub(event_type="conflict_detected", details=payload)
            # Broadcast to WebSocket manager
            import asyncio
            try:
                from app.api.v1.conflicts import manager
                # Broadcast payload as JSON string
                asyncio.create_task(manager.broadcast(json.dumps(payload)))
            except Exception:
                pass
            # Auto‑resolution where applicable
            self._auto_resolve(conflict)
        self.db.commit()
        return all_conflicts

    def _auto_resolve(self, conflict: Conflict) -> None:
        from .resolution import (
            resolve_resource_conflict,
            resolve_goal_conflict,
            resolve_trust_breakdown,
            resolve_communication_conflict,
            resolve_deadlock,
            resolve_priority_inversion,
        )
        if conflict.conflict_type == ConflictType.RESOURCE:
            resolve_resource_conflict(conflict, self.db, self.graph)
            conflict.status = ConflictStatus.AUTO_RESOLVED
        elif conflict.conflict_type == ConflictType.GOAL:
            resolve_goal_conflict(conflict, self.db, self.graph)
            conflict.status = ConflictStatus.AUTO_RESOLVED
        elif conflict.conflict_type == ConflictType.TRUST:
            resolve_trust_breakdown(conflict, self.db, self.graph)
            conflict.status = ConflictStatus.AUTO_RESOLVED
        elif conflict.conflict_type == ConflictType.COMMUNICATION:
            resolve_communication_conflict(conflict, self.db, self.graph)
            conflict.status = ConflictStatus.AUTO_RESOLVED
        elif conflict.conflict_type == ConflictType.DEADLOCK:
            resolve_deadlock(conflict, self.db, self.graph)
            conflict.status = ConflictStatus.AUTO_RESOLVED
        elif conflict.conflict_type == ConflictType.PRIORITY_INVERSION:
            resolve_priority_inversion(conflict, self.db, self.graph)
            conflict.status = ConflictStatus.AUTO_RESOLVED
