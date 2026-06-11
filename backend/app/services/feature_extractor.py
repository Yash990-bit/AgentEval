# backend/app/services/feature_extractor.py
import pandas as pd
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Any

from app.models.simulation_analytics import SimulationAnalytics
from app.models.agent_performance_metrics import AgentPerformanceMetrics
from app.models.goal import AgentGoal
from app.models.failure_event import FailureEvent

class FeatureExtractor:
    @staticmethod
    def extract_resource_exhaustion_features(db: Session, simulation_id: UUID) -> pd.DataFrame:
        """Extract historical resource usage rate features for a simulation."""
        analytics = db.query(SimulationAnalytics).filter_by(simulation_id=simulation_id).first()
        if not analytics:
            return pd.DataFrame()

        # Build feature dataset from resource units consumed
        # total_resource_units_consumed is a JSON/dict: {"cpu_units": 120, "api_calls": 40, "tokens": 8000}
        consumed = analytics.total_resource_units_consumed or {}
        ticks = max(analytics.total_ticks_run, 1)

        data = []
        for resource_type, amount in consumed.items():
            data.append({
                "tick": ticks,
                "resource_type": resource_type,
                "amount_consumed": float(amount),
                "consumption_rate": float(amount) / ticks,
                "total_agents": analytics.total_agents,
                "avg_efficiency_score": analytics.avg_efficiency_score,
            })
        
        return pd.DataFrame(data)

    @staticmethod
    def extract_conflict_probability_features(db: Session, simulation_id: UUID) -> pd.DataFrame:
        """Extract agent pairwise metrics for conflict risk training."""
        analytics = db.query(SimulationAnalytics).filter_by(simulation_id=simulation_id).first()
        agents = db.query(AgentPerformanceMetrics).filter_by(simulation_id=simulation_id).all()
        if not analytics or len(agents) < 2:
            return pd.DataFrame()

        data = []
        # Calculate pairwise metrics
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                a = agents[i]
                b = agents[j]
                
                trust_delta = abs(a.avg_trust_given - b.avg_trust_given)
                avg_resource_util = (a.resource_utilization_pct + b.resource_utilization_pct) / 2
                combined_messages = a.messages_sent + b.messages_sent
                avg_cooperation = (a.cooperation_score + b.cooperation_score) / 2
                
                data.append({
                    "simulation_id": str(simulation_id),
                    "agent_pair": f"{a.agent_id}-{b.agent_id}",
                    "trust_delta": trust_delta,
                    "avg_resource_utilization": avg_resource_util,
                    "combined_messages": combined_messages,
                    "avg_cooperation_score": avg_cooperation,
                    "tick": analytics.total_ticks_run,
                })
        return pd.DataFrame(data)

    @staticmethod
    def extract_goal_completion_features(db: Session, simulation_id: UUID) -> pd.DataFrame:
        """Extract features related to active agent goals."""
        goals = db.query(AgentGoal).filter_by(simulation_id=simulation_id).all()
        if not goals:
            return pd.DataFrame()

        data = []
        for g in goals:
            data.append({
                "goal_id": str(g.id),
                "agent_id": str(g.agent_id),
                "priority": g.priority,
                "deadline_tick": g.deadline_tick or 100,
                "progress_pct": g.progress_pct,
                "has_dependencies": 1.0 if g.dependencies else 0.0,
                "status": g.status.value if g.status else "pending",
            })
        return pd.DataFrame(data)

    @staticmethod
    def extract_agent_failure_risk_features(db: Session, simulation_id: UUID) -> pd.DataFrame:
        """Extract features relating to individual agent failure risk."""
        agents = db.query(AgentPerformanceMetrics).filter_by(simulation_id=simulation_id).all()
        if not agents:
            return pd.DataFrame()

        data = []
        for a in agents:
            data.append({
                "agent_id": str(a.agent_id),
                "efficiency_score": a.efficiency_score,
                "reliability_score": a.reliability_score,
                "risk_score": a.risk_score,
                "resource_utilization_pct": a.resource_utilization_pct,
                "failure_count": a.failure_count,
                "conflict_count": a.conflict_involvement_count,
            })
        return pd.DataFrame(data)
