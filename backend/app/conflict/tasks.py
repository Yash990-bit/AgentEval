# backend/app/conflict/tasks.py
"""Celery tasks for conflict detection."""

from ..celery_app import celery_app
from .detector import ConflictDetector
from ..core.state import get_engine, engines
from ..db.session import SessionLocal

@celery_app.task
def detect_conflicts(simulation_id: str):
    """Celery task to detect conflicts for a specific simulation."""
    db = SessionLocal()
    try:
        engine = get_engine(simulation_id)
        # Create detector using the engine's graph and run detection
        detector = ConflictDetector(db_session=db, graph=engine.graph)
        detector.detect()
    finally:
        db.close()

@celery_app.task
def detect_conflicts_periodic():
    """Celery periodic task to scan and detect conflicts for all active simulations."""
    db = SessionLocal()
    try:
        for sim_id, engine in engines.items():
            detector = ConflictDetector(db_session=db, graph=engine.graph)
            detector.detect()
    finally:
        db.close()
