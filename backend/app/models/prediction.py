from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.db.models import Base

class ResourceExhaustionPrediction(Base):
    __tablename__ = "resource_exhaustion_predictions"
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String, index=True, nullable=False)
    resource_type = Column(String, nullable=False)
    predicted_exhaustion_tick = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    current_rate = Column(Float, nullable=False)
    projected_rate = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)

class ConflictProbabilityPrediction(Base):
    __tablename__ = "conflict_probability_predictions"
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String, index=True, nullable=False)
    agent_pair = Column(String, nullable=False)  # e.g., "agentA-agentB"
    conflict_probability = Column(Float, nullable=False)
    predicted_conflict_type = Column(String, nullable=False)
    expected_tick_range = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)

class GoalCompletionPrediction(Base):
    __tablename__ = "goal_completion_predictions"
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String, index=True, nullable=False)
    goal_id = Column(String, nullable=False)
    completion_probability = Column(Float, nullable=False)
    expected_completion_tick = Column(Integer, nullable=False)
    risk_factors = Column(JSON, nullable=False)  # list of strings
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)

class AgentFailureRiskPrediction(Base):
    __tablename__ = "agent_failure_risk_predictions"
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String, index=True, nullable=False)
    agent_id = Column(String, nullable=False)
    failure_risk_score = Column(Float, nullable=False)
    top_risk_factors = Column(JSON, nullable=False)  # list of strings
    recommended_action = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)

class SimulationOutcomePrediction(Base):
    __tablename__ = "simulation_outcome_predictions"
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String, index=True, nullable=False)
    predicted_outcome = Column(String, nullable=False)  # success / partial_success / failure
    confidence = Column(Float, nullable=False)
    key_risks = Column(JSON, nullable=False)  # list of strings
    suggested_interventions = Column(JSON, nullable=False)  # list of strings
    created_at = Column(DateTime, nullable=False)
