# backend/app/tasks/detection.py
"""Celery task to run failure detection cycle for active simulations.
It opens a DB session, retrieves agents' latest state (placeholder implementation),
and invokes `run_detection_cycle` from the failure_engine.
"""

from celery import shared_task
from app.db.session import SessionLocal
from app.services.failure_engine import run_detection_cycle

# Placeholder: function to collect agents' state for a given simulation.
# In a real system this would query the simulation state store.
def get_agents_state(simulation_id):
    # Example mock data structure expected by run_detection_cycle:
    # [
    #   {"agent_id": "agent-1", "waiting_for": [], "trust_score": 0.8, "loop_count": 3},
    #   {"agent_id": "agent-2", "waiting_for": ["agent-1"], "trust_score": 0.6, "loop_count": 12},
    # ]
    return []  # TODO: replace with real state retrieval

@shared_task(name="run_failure_detection")
def run_failure_detection(simulation_id: str, tick: int):
    db = SessionLocal()
    try:
        agents_state = get_agents_state(simulation_id)
        run_detection_cycle(db, simulation_id, agents_state, tick)
        # ----- emergent behavior detection -----
        from app.services.emergent_engine import run_emergent_detection_cycle
        run_emergent_detection_cycle(db, simulation_id, tick)
    finally:
        db.close()
