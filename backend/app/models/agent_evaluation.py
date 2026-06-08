from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class AgentEvaluation(Base):
    __tablename__ = "agent_evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    agent_template_id = Column(String, nullable=False, index=True)

    intelligence_score = Column(Float, nullable=False)
    cooperation_score = Column(Float, nullable=False)
    reliability_score = Column(Float, nullable=False)
    efficiency_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    composite_score = Column(Float, nullable=False)
    tier = Column(String(2), nullable=False)
    rank_in_simulation = Column(Integer, nullable=False)
    narrative_summary = Column(String(500))
    computed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Optional relationships (if other tables exist)
    # simulation = relationship('Simulation', back_populates='evaluations')
    # agent = relationship('Agent', back_populates='evaluations')
    # template = relationship('AgentTemplate', back_populates='evaluations')
