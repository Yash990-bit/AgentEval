# backend/app/services/failure_engine.py
"""Failure Simulation Engine.
Implements probability calculations, injection decorators, background detection, and DB logging.
"""

import random
import uuid
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.failure_event import FailureEvent
from app.db.models.relationship import AgentRelationship

class ToolTimeoutError(Exception):
    pass

class ToolHTTPError(Exception):
    pass

# Registry of active manual injections: (simulation_id, agent_id, failure_type) -> probability
ACTIVE_INJECTIONS: Dict[Tuple[str, str, str], float] = {}

# Registry of failed tools in the current tick to trigger cascading failures: (simulation_id, agent_id, tool_id) -> bool
FAILED_TOOLS_REGISTRY: Dict[Tuple[str, str, str], bool] = {}

# Trust history tracking: (simulation_id, agent_id, partner_id) -> list of (tick, trust_score)
TRUST_HISTORY: Dict[Tuple[str, str, str], List[Tuple[int, float]]] = {}

# Tool dependency graph: tool -> list of tools it depends on
TOOL_DEPENDENCIES: Dict[str, List[str]] = {
    "data_analyzer": ["data_extractor"],
    "report_generator": ["data_analyzer"],
}

class FailureInjector:
    @staticmethod
    def inject(simulation_id: Any, failure_type: str, target_agent_id: str, probability: float):
        """Inject a failure mode into the active injection registry."""
        key = (str(simulation_id), str(target_agent_id), failure_type)
        ACTIVE_INJECTIONS[key] = probability

    @staticmethod
    def is_triggered(simulation_id: Any, target_agent_id: str, failure_type: str, fallback_probability: float = 0.0) -> bool:
        """Check if an injected failure or natural probability triggers the failure."""
        key = (str(simulation_id), str(target_agent_id), failure_type)
        prob = ACTIVE_INJECTIONS.get(key, fallback_probability)
        return random.random() < prob

    @staticmethod
    def clear():
        ACTIVE_INJECTIONS.clear()
        FAILED_TOOLS_REGISTRY.clear()
        TRUST_HISTORY.clear()


class FailureDetector:
    @staticmethod
    def log_failure(db: Session, simulation_id: Any, agent_id: str, failure_type: str,
                    tick: int, severity: str, propagated_to: List[str] = None,
                    recovery_action: str = "", resolved: bool = False,
                    resolved_at_tick: int = None) -> FailureEvent:
        """Log a failure event into the database failure_events table."""
        # Convert simulation_id to UUID object if possible
        sim_uuid = simulation_id
        if isinstance(simulation_id, str):
            try:
                sim_uuid = uuid.UUID(simulation_id)
            except Exception:
                pass

        event = FailureEvent(
            simulation_id=sim_uuid,
            agent_id=str(agent_id),
            failure_type=failure_type,
            tick_occurred=tick,
            severity=severity,
            propagated_to=propagated_to or [],
            recovery_action=recovery_action,
            resolved=resolved,
            resolved_at_tick=resolved_at_tick
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def detect_deadlock(db: Session, simulation_id: Any, tick: int, agents_states: List[Dict[str, Any]]):
        """Detect deadlocks (circular waiting: agent A waits for B, B waits for A)."""
        # Map agent_id -> waiting_for list
        waiting_map = {}
        for state in agents_states:
            aid = str(state.get("agent_id"))
            waiting_map[aid] = [str(x) for x in state.get("waiting_for", [])]

        # Check all pairs
        detected = set()
        for a, waiting_list in waiting_map.items():
            for b in waiting_list:
                if b in waiting_map and a in waiting_map[b]:
                    pair = tuple(sorted([a, b]))
                    if pair not in detected:
                        detected.add(pair)
                        # Log deadlock failure
                        FailureDetector.log_failure(
                            db=db,
                            simulation_id=simulation_id,
                            agent_id=a,
                            failure_type="Deadlock",
                            tick=tick,
                            severity="critical",
                            propagated_to=[b],
                            recovery_action="Forcefully resolved wait state",
                            resolved=True,
                            resolved_at_tick=tick
                        )

    @staticmethod
    def detect_trust_collapse(db: Session, simulation_id: Any, tick: int, agent_id: str, partner_id: str, current_trust: float):
        """Detect trust collapse: rapid Sequential reduction of trust (>0.4 drop in 5 ticks)."""
        key = (str(simulation_id), str(agent_id), str(partner_id))
        if key not in TRUST_HISTORY:
            TRUST_HISTORY[key] = []
        
        history = TRUST_HISTORY[key]
        history.append((tick, current_trust))
        # Keep only last 10 records
        if len(history) > 10:
            history.pop(0)

        # Look for drops within last 5 ticks
        recent = [h for h in history if tick - h[0] <= 5]
        if len(recent) >= 2:
            max_trust = max(h[1] for h in recent)
            min_trust = min(h[1] for h in recent)
            # Find chronologically first max and later min
            first_idx = next(i for i, h in enumerate(recent) if h[1] == max_trust)
            later_min = min([h[1] for h in recent[first_idx:]])
            if max_trust - later_min > 0.4:
                FailureDetector.log_failure(
                    db=db,
                    simulation_id=simulation_id,
                    agent_id=agent_id,
                    failure_type="Trust Collapse",
                    tick=tick,
                    severity="high",
                    propagated_to=[partner_id],
                    recovery_action="Isolation of untrusted agent",
                    resolved=False
                )


def calculate_failure_probability(agent: Any) -> float:
    """Calculate failure probability:
    failure_probability = 0.3 * (1 - energy) + 0.3 * (1 - trust_avg) + 0.2 * loop_count_norm + 0.2 * resource_pressure
    """
    # 1. Energy score handling
    energy = getattr(agent, "energy_score", 1.0)
    # If energy is from state dictionary, retrieve it
    if isinstance(agent, dict):
        energy = agent.get("energy_score", 1.0)
    # Norm energy to [0.0, 1.0]
    if energy > 1.0:
        energy = energy / 100.0
    energy = max(0.0, min(1.0, energy))

    # 2. Trust average handling
    trust_scores = {}
    if isinstance(agent, dict):
        trust_scores = agent.get("trust_scores", {})
    else:
        trust_scores = getattr(agent, "trust_scores", {})
    
    if trust_scores:
        trust_avg = sum(trust_scores.values()) / len(trust_scores)
    else:
        trust_avg = 0.5
    trust_avg = max(0.0, min(1.0, trust_avg))

    # 3. Loop count normalization
    loop_count = 0
    if isinstance(agent, dict):
        loop_count = agent.get("loop_count", 0)
    else:
        loop_count = getattr(agent, "loop_count", 0)
    loop_count_norm = max(0.0, min(1.0, loop_count / 10.0))

    # 4. Resource pressure
    # Norm budget/capacity
    resource_budget = 100.0
    if isinstance(agent, dict):
        budget_val = agent.get("resource_budget", 100.0)
        if isinstance(budget_val, dict):
            # If it's a dict of values, get the first or compute average
            budget_val = sum(budget_val.values()) / len(budget_val) if budget_val else 100.0
        resource_budget = budget_val
    else:
        budget_val = getattr(agent, "resource_budget", 100.0)
        if isinstance(budget_val, dict):
            budget_val = sum(budget_val.values()) / len(budget_val) if budget_val else 100.0
        resource_budget = budget_val

    # Scale resource pressure
    resource_pressure = max(0.0, min(1.0, 1.0 - (resource_budget / 100.0)))

    prob = 0.3 * (1.0 - energy) + 0.3 * (1.0 - trust_avg) + 0.2 * loop_count_norm + 0.2 * resource_pressure
    return max(0.0, min(1.0, prob))

# --- Additional Failure Types & Detection Utilities ---

class HallucinationInjector:
    """Utility to inject hallucinated data into LLM responses.
    This decorator wraps a function that returns a result (e.g., a string or dict).
    When the associated failure is triggered, it mutates the output with plausible but
    incorrect data.
    """

    @staticmethod
    def inject_hallucination(simulation_id: Any, target_agent_id: str, probability: float = 0.1):
        """Register a hallucination injection for the given agent.
        The probability is the chance that any LLM response from this agent will be altered.
        """
        FailureInjector.inject(simulation_id, "hallucination", target_agent_id, probability)

    @staticmethod
    def maybe_hallucinate(simulation_id: Any, target_agent_id: str, original_output: Any) -> Any:
        """If the hallucination failure is triggered, replace the output.
        For demonstration we randomly replace numeric values or flip boolean strings.
        """
        if FailureInjector.is_triggered(simulation_id, target_agent_id, "hallucination"):
            if isinstance(original_output, dict) and original_output:
                key = next(iter(original_output))
                val = original_output[key]
                if isinstance(val, (int, float)):
                    mutated = val + random.uniform(-10, 10)
                elif isinstance(val, str):
                    mutated = val[::-1]
                else:
                    mutated = "<hallucinated>"
                original_output[key] = mutated
            elif isinstance(original_output, str):
                original_output = original_output[::-1]
        return original_output

class CascadingFailureHandler:
    """Tracks tool failures and propagates to dependent tools.
    Tools should call `register_failure` when they encounter an exception.
    Dependent tools can query `should_fail` to simulate a propagated failure.
    """

    @staticmethod
    def register_failure(simulation_id: Any, agent_id: str, tool_id: str):
        key = (str(simulation_id), str(agent_id), str(tool_id))
        FAILED_TOOLS_REGISTRY[key] = True

    @staticmethod
    def should_fail(simulation_id: Any, agent_id: str, tool_id: str) -> bool:
        key = (str(simulation_id), str(agent_id), str(tool_id))
        if FAILED_TOOLS_REGISTRY.get(key, False):
            return True
        for dep, deps in TOOL_DEPENDENCIES.items():
            if tool_id == dep:
                for parent in deps:
                    parent_key = (str(simulation_id), str(agent_id), parent)
                    if FAILED_TOOLS_REGISTRY.get(parent_key, False):
                        return True
        return False

class LoopDetector:
    """Detects when an agent's loop count exceeds a threshold within a tick.
    When detected, logs a failure event.
    """

    MAX_LOOP_THRESHOLD = 10

    @staticmethod
    def check_loop(db: Session, simulation_id: Any, agent_id: str, loop_count: int, tick: int):
        if loop_count > LoopDetector.MAX_LOOP_THRESHOLD:
            FailureDetector.log_failure(
                db=db,
                simulation_id=simulation_id,
                agent_id=agent_id,
                failure_type="Infinite Loop",
                tick=tick,
                severity="critical",
                propagated_to=[],
                recovery_action="Terminate agent execution",
                resolved=False,
            )

def run_detection_cycle(db: Session, simulation_id: Any, agents_state: List[Dict[str, Any]], tick: int):
    """Execute detection logic for all agents in a simulation for a given tick.
    It checks deadlocks, trust collapse, loop overflow and logs failures.
    """
    FailureDetector.detect_deadlock(db, simulation_id, tick, agents_state)
    for state in agents_state:
        aid = str(state.get("agent_id"))
        partner = state.get("partner_id")
        trust = state.get("trust_score", 0.5)
        if partner:
            FailureDetector.detect_trust_collapse(db, simulation_id, tick, aid, str(partner), float(trust))
    for state in agents_state:
        aid = str(state.get("agent_id"))
        loop_cnt = state.get("loop_count", 0)
        LoopDetector.check_loop(db, simulation_id, aid, int(loop_cnt), tick)

__all__ = [
    "FailureInjector",
    "FailureDetector",
    "HallucinationInjector",
    "CascadingFailureHandler",
    "LoopDetector",
    "run_detection_cycle",
    "calculate_failure_probability",
]

