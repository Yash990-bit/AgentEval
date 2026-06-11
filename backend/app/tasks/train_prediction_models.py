# backend/app/tasks/train_prediction_models.py
from celery import shared_task
from uuid import UUID

from app.db.session import SessionLocal
from app.services.prediction_engine import PredictionEngine
from app.models.simulation_analytics import SimulationAnalytics

@shared_task(name="train_prediction_models_task")
def train_prediction_models_task():
    """Celery task to periodically train models and compute predictions for active simulations."""
    db = SessionLocal()
    try:
        # Re-train models with the latest data
        PredictionEngine.train_and_save_models()

        # Update predictions for active simulations
        simulations = db.query(SimulationAnalytics.simulation_id).distinct().all()
        for (sim_id,) in simulations:
            if isinstance(sim_id, str):
                sim_uuid = UUID(sim_id)
            else:
                sim_uuid = sim_id
            
            # Predict resource exhaustion, conflict probability, goal completion, and failure risks
            PredictionEngine.predict_resource_exhaustion(db, sim_uuid)
            PredictionEngine.predict_conflict_probability(db, sim_uuid)
            PredictionEngine.predict_goal_completion(db, sim_uuid)
            PredictionEngine.predict_agent_failure_risk(db, sim_uuid)
            
    except Exception as e:
        print(f"Error in train_prediction_models_task: {e}")
    finally:
        db.close()
