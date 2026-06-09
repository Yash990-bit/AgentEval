# backend/app/api/v1/predictions.py

"""Prediction Engine API endpoints.
Provides simple forecast calculations based on existing analytics data.
The models are placeholders (linear regression, logistic regression, random forest, gradient boosting)
using available metrics from SimulationAnalytics and AgentPerformanceMetrics.
"""

from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session

from ...dependencies import get_db
from ...models.simulation_analytics import SimulationAnalytics
from ...models.agent_performance_metrics import AgentPerformanceMetrics

router = APIRouter(prefix="/predictions", tags=["predictions"])

# Helper to fetch analytics
def get_analytics(db: Session, sim_id: UUID) -> SimulationAnalytics:
    analytics = (
        db.query(SimulationAnalytics)
        .filter(SimulationAnalytics.simulation_id == sim_id)
        .first()
    )
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found for this simulation")
    return analytics

# Helper to fetch agent metrics
def get_agent_metrics(db: Session, sim_id: UUID):
    return (
        db.query(AgentPerformanceMetrics)
        .filter(AgentPerformanceMetrics.simulation_id == sim_id)
        .all()
    )

@router.get("/{simulation_id}/resource_exhaustion")
def resource_exhaustion_forecast(
    simulation_id: UUID, db: Session = Depends(get_db)
):
    """Resource Exhaustion Forecast.
    Uses a simple linear extrapolation based on total_resource_units_consumed.
    Returns the tick at which the most constrained resource is expected to be exhausted.
    """
    analytics = get_analytics(db, simulation_id)
    # Expect analytics.total_resource_units_consumed to be a dict like {"cpu": 120, "memory": 300}
    usage = analytics.total_resource_units_consumed or {}
    if not usage:
        raise HTTPException(status_code=400, detail="No resource usage data available")
    # Assume each resource has a fixed capacity of 1000 units for demo purposes
    capacity = 1000.0
    predictions = []
    for resource, consumed in usage.items():
        rate = consumed / max(analytics.total_ticks_run, 1)  # units per tick
        remaining = capacity - consumed
        predicted_tick = analytics.total_ticks_run + (remaining / rate if rate > 0 else float("inf"))
        predictions.append(
            {
                "resource_type": resource,
                "predicted_exhaustion_tick": int(predicted_tick),
                "confidence": 0.8,  # placeholder confidence
                "current_rate": rate,
                "projected_rate": rate * 1.05,  # simple projection
            }
        )
    return predictions

@router.get("/{simulation_id}/conflict_probability")
def conflict_probability_forecast(
    simulation_id: UUID, db: Session = Depends(get_db)
):
    """Conflict Probability Forecast.
    Utilises a logistic‑style calculation based on trust scores and recent conflict counts.
    """
    analytics = get_analytics(db, simulation_id)
    agents = get_agent_metrics(db, simulation_id)
    if not agents:
        raise HTTPException(status_code=400, detail="No agent metrics available")
    # Simple heuristic: higher trust_delta and resource pressure increase conflict chance
    results = []
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            a = agents[i]
            b = agents[j]
            # Calculate a synthetic trust delta (difference in avg trust given)
            trust_delta_recent = abs(a.avg_trust_given - b.avg_trust_given)
            # Resource pressure: average of resource utilisation percentages
            resource_pressure = (a.resource_utilization_pct + b.resource_utilization_pct) / 2
            # Goal competition: difference in goals completed
            goal_competition_score = abs(a.goals_completed - b.goals_completed)
            # Communication frequency: use messages_sent as proxy
            communication_frequency = (a.messages_sent + b.messages_sent) / 2
            # Logistic‑style score (sigmoid)
            x = (
                0.4 * trust_delta_recent
                + 0.3 * resource_pressure
                + 0.2 * goal_competition_score
                + 0.1 * communication_frequency
            )
            # Scale to 0–1 via sigmoid
            import math

            conflict_probability = 1 / (1 + math.exp(-x))
            results.append(
                {
                    "agent_pair": f"{a.agent_id}-{b.agent_id}",
                    "conflict_probability": round(conflict_probability, 3),
                    "predicted_conflict_type": "resource" if resource_pressure > 0.6 else "trust",
                    "expected_tick_range": [analytics.total_ticks_run, analytics.total_ticks_run + 20],
                }
            )
    return results

@router.get("/{simulation_id}/goal_completion")
def goal_completion_forecast(
    simulation_id: UUID, db: Session = Depends(get_db)
):
    """Goal Completion Probability.
    Uses a random‑forest‑style heuristic based on agent performance aggregates.
    """
    analytics = get_analytics(db, simulation_id)
    agents = get_agent_metrics(db, simulation_id)
    if not agents:
        raise HTTPException(status_code=400, detail="No agent metrics available")
    # Aggregate simple features
    total_progress = analytics.total_goals  # total goals attempted
    completed = sum(a.goals_completed for a in agents)
    resources_remaining = sum(a.resource_utilization_pct for a in agents) / max(1, len(agents))
    dependencies_complete = 1.0  # placeholder
    agent_energy = sum(a.efficiency_score for a in agents) / max(1, len(agents))
    ticks_to_deadline = 100 - analytics.total_ticks_run  # arbitrary deadline
    # Simple score
    score = (
        0.3 * (completed / max(1, total_progress))
        + 0.2 * resources_remaining
        + 0.2 * agent_energy
        + 0.2 * (dependencies_complete)
        + 0.1 * (ticks_to_deadline / 100)
    )
    completion_probability = min(1.0, max(0.0, score))
    expected_completion_tick = analytics.total_ticks_run + int((1 - completion_probability) * 20)
    # Identify risk factors (simple heuristic)
    risk_factors = []
    if resources_remaining < 0.3:
        risk_factors.append("low_resources")
    if agent_energy < 0.4:
        risk_factors.append("low_energy")
    if ticks_to_deadline < 10:
        risk_factors.append("tight_deadline")
    return {
        "goal_id": str(simulation_id),
        "completion_probability": round(completion_probability, 3),
        "expected_completion_tick": expected_completion_tick,
        "risk_factors": risk_factors,
    }

@router.get("/{simulation_id}/agent_failure_risk")
def agent_failure_risk_forecast(
    simulation_id: UUID, db: Session = Depends(get_db)
):
    """Agent Failure Risk.
    Gradient‑boosting‑style placeholder using recent failure history and risk scores.
    """
    agents = get_agent_metrics(db, simulation_id)
    if not agents:
        raise HTTPException(status_code=400, detail="No agent metrics available")
    results = []
    for a in agents:
        # Base risk from analytics (using avg risk score)
        base_risk = a.risk_score / 100.0
        # Recent failure history – placeholder as failure_count (currently 0 in model)
        recent_failures = a.failure_count
        # Simple boosted risk formula
        risk = base_risk * 0.7 + (recent_failures * 0.3)
        results.append(
            {
                "agent_id": str(a.agent_id),
                "failure_probability": round(min(1.0, risk), 3),
                "recent_failures": recent_failures,
                "risk_score": a.risk_score,
            }
        )
    return results
