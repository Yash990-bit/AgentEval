from sqlalchemy import Column, Integer, Float, String, DateTime, Enum as SAEnum, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from . import Base
import enum

class ResourceActionType(str, enum.Enum):
    CONSUMED = "consumed"
    RESERVED = "reserved"
    RELEASED = "released"
    TRANSFERRED = "transferred"
    WASTED = "wasted"
    BLOCKED = "blocked"

class ResourceBudget(Base):
    __tablename__ = "resource_budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, nullable=False)  # could be UUID string
    simulation_id = Column(String, nullable=False)

    compute_total = Column(Integer, default=0)
    compute_used = Column(Integer, default=0)
    compute_reserved = Column(Integer, default=0)

    api_calls_total = Column(Integer, default=0)
    api_calls_used = Column(Integer, default=0)

    tokens_total = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)

    usd_total = Column(Float, default=0.0)
    usd_spent = Column(Float, default=0.0)

    efficiency_score = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # optional relationship to events
    events = relationship("ResourceEvent", back_populates="budget", cascade="all, delete-orphan")

class ResourceEvent(Base):
    __tablename__ = "resource_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_id = Column(String, nullable=False)
    agent_id = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    action_type = Column(SAEnum(ResourceActionType), nullable=False)
    amount = Column(Float, nullable=False)
    tick = Column(Integer, nullable=False)
    metadata = Column(JSON, nullable=True)

    budget_id = Column(Integer, ForeignKey("resource_budgets.id"), nullable=True)
    budget = relationship("ResourceBudget", back_populates="events")
