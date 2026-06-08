from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Optional
import uuid

from ..models.simulation_analytics import SimulationAnalytics
from ..models.agent_performance_metrics import AgentPerformanceMetrics
from ..core.engine import SimulationEngine

def compute_simulation_analytics(db: Session, simulation_id: UUID, engine: SimulationEngine, tick: int) -> SimulationAnalytics:
    """Compute and persist aggregated analytics for a simulation using the evaluation engine."""
    eval_result = engine.evaluate_agents()
    summary = eval_result["summary"]
    agents_data = eval_result["agents"]

    # Save agent metrics
    metrics_list = []
    for a_eval in agents_data:
        agent_obj = next((ag for ag in engine.agents if ag.id == a_eval["id"]), None)
        
        metric = AgentPerformanceMetrics(
            id=uuid.uuid4(),
            agent_id=UUID(a_eval["id"]),
            simulation_id=simulation_id,
            intelligence_score=a_eval["intelligence"],
            cooperation_score=a_eval["cooperation"],
            reliability_score=a_eval["reliability"],
            efficiency_score=a_eval["efficiency"],
            risk_score=a_eval["risk"],
            composite_score=a_eval["composite"],
            overall_rank=a_eval["rank"],
            goals_completed=getattr(agent_obj, "goals_completed", 0) if agent_obj else 0,
            goals_failed=getattr(agent_obj, "goals_failed", 0) if agent_obj else 0,
            goals_abandoned=0,
            success_rate=(getattr(agent_obj, "goals_completed", 0) / max(1, getattr(agent_obj, "total_goals", 1))) if agent_obj else 0.0,
            messages_sent=len(getattr(agent_obj, "outbox", [])) if agent_obj else 0,
            messages_received=len(getattr(agent_obj, "inbox", [])) if agent_obj else 0,
            resource_utilization_pct=getattr(agent_obj, "resource_efficiency", 0.0) if agent_obj else 0.0,
            avg_trust_given=getattr(agent_obj, "avg_trust_given", 0.0) if agent_obj else 0.0,
            avg_trust_received=0.0,
            failure_count=0,
            conflict_involvement_count=0
        )
        db.add(metric)
        metrics_list.append(metric)

    top_agent = next((m for m in metrics_list if m.overall_rank == 1), None)
    
    analytics = SimulationAnalytics(
        simulation_id=simulation_id,
        total_ticks_run=tick,
        total_agents=len(engine.agents),
        total_goals=sum(m.goals_completed + m.goals_failed for m in metrics_list),
        overall_success_rate=summary.get("avg_intelligence", 0.0), # Example mapping
        overall_failure_rate=100.0 - summary.get("avg_reliability", 100.0),
        avg_intelligence_score=summary.get("avg_intelligence", 0.0),
        avg_cooperation_score=summary.get("avg_cooperation", 0.0),
        avg_reliability_score=summary.get("avg_reliability", 0.0),
        avg_efficiency_score=summary.get("avg_efficiency", 0.0),
        avg_risk_score=summary.get("avg_risk", 0.0),
        avg_trust_score=sum(m.avg_trust_given for m in metrics_list) / max(1, len(metrics_list)),
        total_conflicts_detected=0,
        conflicts_auto_resolved=0,
        conflicts_escalated=0,
        total_emergent_behaviors=0,
        total_resource_units_consumed={},
        total_waste_rate=0.0,
        top_performing_agent_id=top_agent.agent_id if top_agent else None,
        most_conflicted_agent_id=None,
        completion_status="success",
    )
    
    existing_sim = db.query(SimulationAnalytics).filter_by(simulation_id=simulation_id).first()
    if existing_sim:
        db.delete(existing_sim)
        
    # Delete old metrics for this sim
    db.query(AgentPerformanceMetrics).filter_by(simulation_id=simulation_id).delete()
        
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    return analytics

def get_agent_performance_metrics(db: Session, simulation_id: UUID) -> List[AgentPerformanceMetrics]:
    return db.query(AgentPerformanceMetrics).filter_by(simulation_id=simulation_id).all()
