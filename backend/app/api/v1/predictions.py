# backend/app/api/v1/predictions.py

"""Prediction Engine API endpoints.
Provides scikit-learn forecasts utilizing Redis caching and database storage.
"""

from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session
from typing import List, Dict

from ...dependencies import get_db
from ...services.prediction_engine import PredictionEngine

router = APIRouter(prefix="/predictions", tags=["predictions"])

@router.get("/{simulation_id}/resource_exhaustion", response_model=List[Dict])
def resource_exhaustion_forecast(
    simulation_id: UUID, db: Session = Depends(get_db)
):
    """Resource Exhaustion Forecast.
    Uses fitted LinearRegression model to project resource consumption.
    """
    try:
        return PredictionEngine.predict_resource_exhaustion(db, simulation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{simulation_id}/conflict_probability", response_model=List[Dict])
def conflict_probability_forecast(
    simulation_id: UUID, db: Session = Depends(get_db)
):
    """Conflict Probability Forecast.
    Uses fitted LogisticRegression model to predict pairwise agent conflict risks.
    """
    try:
        return PredictionEngine.predict_conflict_probability(db, simulation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{simulation_id}/goal_completion")
def goal_completion_forecast(
    simulation_id: UUID, db: Session = Depends(get_db)
):
    """Goal Completion Probability.
    Uses fitted RandomForestClassifier to estimate completion chance.
    """
    try:
        return PredictionEngine.predict_goal_completion(db, simulation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{simulation_id}/agent_failure_risk", response_model=List[Dict])
def agent_failure_risk_forecast(
    simulation_id: UUID, db: Session = Depends(get_db)
):
    """Agent Failure Risk.
    Uses GradientBoostingRegressor model to predict agent crash/failure risks.
    """
    try:
        return PredictionEngine.predict_agent_failure_risk(db, simulation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
