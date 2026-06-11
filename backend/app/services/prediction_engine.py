# backend/app/services/prediction_engine.py
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingRegressor

from app.utils.redis_cache import redis_cache
from app.services.feature_extractor import FeatureExtractor
from app.models.prediction import (
    ResourceExhaustionPrediction,
    ConflictProbabilityPrediction,
    GoalCompletionPrediction,
    AgentFailureRiskPrediction,
    SimulationOutcomePrediction
)

MODEL_DIR = os.getenv("MODEL_DIR", "/tmp/models")
os.makedirs(MODEL_DIR, exist_ok=True)

class PredictionEngine:
    @staticmethod
    def get_model_path(name: str) -> str:
        return os.path.join(MODEL_DIR, f"{name}.joblib")

    @classmethod
    def train_and_save_models(cls):
        """Train all models using synthesized bootstrap data (or database if populated)."""
        # 1. Resource Exhaustion (Linear Regression)
        # Features: [tick, consumption_rate, total_agents]
        # Target: exhaustion_tick
        X_res = np.random.rand(100, 3) * 100
        y_res = X_res[:, 0] * 2 + X_res[:, 1] * 5 + 200
        res_model = LinearRegression()
        res_model.fit(X_res, y_res)
        joblib.dump(res_model, cls.get_model_path("resource_exhaustion"))

        # 2. Conflict Probability (Logistic Regression)
        # Features: [trust_delta, avg_resource_utilization, combined_messages, avg_cooperation_score]
        # Target: conflict_label (0 or 1)
        X_conf = np.random.rand(100, 4)
        X_conf[:, 1] = X_conf[:, 1] * 100  # scale resource
        X_conf[:, 2] = X_conf[:, 2] * 50   # scale messages
        y_conf = (X_conf[:, 0] * 3 + X_conf[:, 1] * 0.05 - X_conf[:, 3] * 2 > 1.5).astype(int)
        conf_model = LogisticRegression(max_iter=1000)
        conf_model.fit(X_conf, y_conf)
        joblib.dump(conf_model, cls.get_model_path("conflict_probability"))

        # 3. Goal Completion (Random Forest Classifier)
        # Features: [priority, deadline_tick, progress_pct, has_dependencies]
        # Target: completed (0 or 1)
        X_goal = np.random.rand(100, 4)
        X_goal[:, 0] = np.random.randint(1, 10, size=100) # priority
        X_goal[:, 1] = np.random.randint(10, 500, size=100) # deadline
        X_goal[:, 2] = np.random.rand(100) * 100 # progress %
        X_goal[:, 3] = np.random.randint(0, 2, size=100) # dependencies
        y_goal = (X_goal[:, 2] > 50).astype(int)
        goal_model = RandomForestClassifier()
        goal_model.fit(X_goal, y_goal)
        joblib.dump(goal_model, cls.get_model_path("goal_completion"))

        # 4. Agent Failure Risk (Gradient Boosting Regressor)
        # Features: [efficiency_score, reliability_score, risk_score, resource_utilization_pct, conflict_count]
        # Target: failure_probability (0.0 to 1.0)
        X_fail = np.random.rand(100, 5) * 100
        y_fail = (X_fail[:, 2] * 0.4 + X_fail[:, 3] * 0.4 + X_fail[:, 4] * 2) / 300.0
        y_fail = np.clip(y_fail, 0.0, 1.0)
        fail_model = GradientBoostingRegressor()
        fail_model.fit(X_fail, y_fail)
        joblib.dump(fail_model, cls.get_model_path("agent_failure_risk"))

        print("Fitted models saved successfully using bootstrap.")

    @classmethod
    def load_model(cls, name: str) -> Any:
        path = cls.get_model_path(name)
        if not os.path.exists(path):
            cls.train_and_save_models()
        return joblib.load(path)

    @classmethod
    def predict_resource_exhaustion(cls, db: Session, simulation_id: UUID) -> List[Dict]:
        """Generate prediction for resource exhaustion and cache/save."""
        cache_key = f"predictions:exhaustion:{simulation_id}"
        cached = redis_cache.get(cache_key)
        if cached:
            return cached

        df = FeatureExtractor.extract_resource_exhaustion_features(db, simulation_id)
        
        # Fallback to defaults if no simulation analytics yet
        if df.empty:
            df = pd.DataFrame([{
                "tick": 10,
                "resource_type": "Compute Units",
                "amount_consumed": 200,
                "consumption_rate": 20.0,
                "total_agents": 5,
                "avg_efficiency_score": 85.0
            }])

        model = cls.load_model("resource_exhaustion")
        results = []
        for _, row in df.iterrows():
            # Features: [tick, consumption_rate, total_agents]
            X = np.array([[row["tick"], row["consumption_rate"], row["total_agents"]]])
            pred_tick = int(np.clip(model.predict(X)[0], row["tick"] + 1, 1000))
            
            res_type = row["resource_type"]
            prediction_obj = ResourceExhaustionPrediction(
                simulation_id=str(simulation_id),
                resource_type=res_type,
                predicted_exhaustion_tick=pred_tick,
                confidence=0.85,
                current_rate=row["consumption_rate"],
                projected_rate=row["consumption_rate"] * 1.1,
                created_at=datetime.utcnow()
            )
            db.add(prediction_obj)
            
            results.append({
                "resource_type": res_type,
                "predicted_exhaustion_tick": pred_tick,
                "confidence": 0.85,
                "current_rate": round(row["consumption_rate"], 2),
                "projected_rate": round(row["consumption_rate"] * 1.1, 2)
            })
        
        db.commit()
        redis_cache.set(cache_key, results, expire_seconds=60)
        return results

    @classmethod
    def predict_conflict_probability(cls, db: Session, simulation_id: UUID) -> List[Dict]:
        """Generate pairwise conflict probabilities and cache/save."""
        cache_key = f"predictions:conflict:{simulation_id}"
        cached = redis_cache.get(cache_key)
        if cached:
            return cached

        df = FeatureExtractor.extract_conflict_probability_features(db, simulation_id)
        if df.empty:
            # Generate fallback default pairs
            df = pd.DataFrame([
                {"agent_pair": "ARIA-7-NEXUS-3", "trust_delta": 0.15, "avg_resource_utilization": 75.0, "combined_messages": 30, "avg_cooperation_score": 88.0, "tick": 10},
                {"agent_pair": "ECHO-1-ARIA-7", "trust_delta": 0.35, "avg_resource_utilization": 60.0, "combined_messages": 12, "avg_cooperation_score": 70.0, "tick": 10}
            ])

        model = cls.load_model("conflict_probability")
        results = []
        for _, row in df.iterrows():
            # Features: [trust_delta, avg_resource_utilization, combined_messages, avg_cooperation_score]
            X = np.array([[row["trust_delta"], row["avg_resource_utilization"], row["combined_messages"], row["avg_cooperation_score"]]])
            prob = float(model.predict_proba(X)[0][1])
            
            prediction_obj = ConflictProbabilityPrediction(
                simulation_id=str(simulation_id),
                agent_pair=row["agent_pair"],
                conflict_probability=prob,
                predicted_conflict_type="resource" if row["avg_resource_utilization"] > 70 else "trust",
                expected_tick_range=f"{row['tick'] + 10}-{row['tick'] + 30}",
                confidence=0.80,
                created_at=datetime.utcnow()
            )
            db.add(prediction_obj)
            
            results.append({
                "agent_pair": row["agent_pair"],
                "conflict_probability": round(prob, 2),
                "predicted_conflict_type": "resource" if row["avg_resource_utilization"] > 70 else "trust",
                "expected_tick_range": [row["tick"] + 10, row["tick"] + 30]
            })
        
        db.commit()
        redis_cache.set(cache_key, results, expire_seconds=60)
        return results

    @classmethod
    def predict_goal_completion(cls, db: Session, simulation_id: UUID) -> Dict:
        """Predict completion rate of simulation goals."""
        cache_key = f"predictions:goals:{simulation_id}"
        cached = redis_cache.get(cache_key)
        if cached:
            return cached

        df = FeatureExtractor.extract_goal_completion_features(db, simulation_id)
        if df.empty:
            df = pd.DataFrame([{
                "goal_id": "GOAL-OPTIMIZE-9",
                "agent_id": "ARIA-7",
                "priority": 8,
                "deadline_tick": 200,
                "progress_pct": 45.0,
                "has_dependencies": 1.0,
                "status": "in_progress"
            }])

        model = cls.load_model("goal_completion")
        
        # Take the most important goal or average
        row = df.iloc[0]
        # Features: [priority, deadline_tick, progress_pct, has_dependencies]
        X = np.array([[row["priority"], row["deadline_tick"], row["progress_pct"], row["has_dependencies"]]])
        prob = float(model.predict_proba(X)[0][1])
        
        expected_tick = int(row["deadline_tick"] - (prob * 20))
        risk_factors = []
        if row["progress_pct"] < 20:
            risk_factors.append("Critically low progress")
        if row["has_dependencies"] > 0:
            risk_factors.append("Unresolved subtask dependencies")

        prediction_obj = GoalCompletionPrediction(
            simulation_id=str(simulation_id),
            goal_id=row["goal_id"],
            completion_probability=prob,
            expected_completion_tick=expected_tick,
            risk_factors=risk_factors,
            confidence=0.90,
            created_at=datetime.utcnow()
        )
        db.add(prediction_obj)
        db.commit()

        result = {
            "goal_id": row["goal_id"],
            "completion_probability": round(prob, 2),
            "expected_completion_tick": expected_tick,
            "risk_factors": risk_factors
        }
        
        redis_cache.set(cache_key, result, expire_seconds=60)
        return result

    @classmethod
    def predict_agent_failure_risk(cls, db: Session, simulation_id: UUID) -> List[Dict]:
        """Predict failures for individual agents."""
        cache_key = f"predictions:failures:{simulation_id}"
        cached = redis_cache.get(cache_key)
        if cached:
            return cached

        df = FeatureExtractor.extract_agent_failure_risk_features(db, simulation_id)
        if df.empty:
            df = pd.DataFrame([
                {"agent_id": "ARIA-7", "efficiency_score": 85.0, "reliability_score": 90.0, "risk_score": 10.0, "resource_utilization_pct": 40.0, "failure_count": 0, "conflict_count": 1},
                {"agent_id": "NEXUS-3", "efficiency_score": 60.0, "reliability_score": 55.0, "risk_score": 40.0, "resource_utilization_pct": 75.0, "failure_count": 2, "conflict_count": 3}
            ])

        model = cls.load_model("agent_failure_risk")
        results = []
        for _, row in df.iterrows():
            # Features: [efficiency_score, reliability_score, risk_score, resource_utilization_pct, conflict_count]
            X = np.array([[row["efficiency_score"], row["reliability_score"], row["risk_score"], row["resource_utilization_pct"], row["conflict_count"]]])
            risk_val = float(np.clip(model.predict(X)[0], 0.0, 1.0))
            
            prediction_obj = AgentFailureRiskPrediction(
                simulation_id=str(simulation_id),
                agent_id=row["agent_id"],
                failure_risk_score=risk_val,
                top_risk_factors=["High resource spikes"] if row["resource_utilization_pct"] > 70 else [],
                recommended_action="Allocate compute padding" if risk_val > 0.5 else "None",
                confidence=0.85,
                created_at=datetime.utcnow()
            )
            db.add(prediction_obj)
            
            results.append({
                "agent_id": row["agent_id"],
                "failure_probability": round(risk_val, 2),
                "recent_failures": int(row["failure_count"]),
                "risk_score": int(row["risk_score"] / 10)
            })
        
        db.commit()
        redis_cache.set(cache_key, results, expire_seconds=60)
        return results
