import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session

from ..db.session import get_db
from .models import ResourceBudget, ResourceEvent
from .schemas import ResourceBudgetCreate, ResourceEventCreate

logger = logging.getLogger(__name__)

class ResourceCRUD:
    """Service layer providing CRUD operations for Resource Management System."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------- Budget Operations -------------------
    def get_budget(self, agent_id: str, simulation_id: str) -> Optional[ResourceBudget]:
        return (
            self.db.query(ResourceBudget)
            .filter_by(agent_id=agent_id, simulation_id=simulation_id)
            .first()
        )

    def create_budget(self, payload: ResourceBudgetCreate) -> ResourceBudget:
        budget = ResourceBudget(
            agent_id=payload.agent_id,
            simulation_id=payload.simulation_id,
            compute_total=payload.compute_total,
            api_calls_total=payload.api_calls_total,
            memory_slots_total=payload.memory_slots_total,
            tokens_total=payload.tokens_total,
            usd_total=payload.usd_total,
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def update_budget(self, budget: ResourceBudget, updates: ResourceBudgetCreate) -> ResourceBudget:
        for field, value in updates.dict(exclude_unset=True).items():
            setattr(budget, field, value)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    # ------------------- Event Operations -------------------
    def log_event(self, payload: ResourceEventCreate) -> ResourceEvent:
        event = ResourceEvent(
            simulation_id=payload.simulation_id,
            agent_id=payload.agent_id,
            resource_type=payload.resource_type,
            action_type=payload.action_type,
            amount=payload.amount,
            tick=payload.tick,
            metadata_=payload.metadata,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_events(
        self,
        simulation_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        start_tick: Optional[int] = None,
        end_tick: Optional[int] = None,
    ) -> List[ResourceEvent]:
        query = self.db.query(ResourceEvent)
        if simulation_id:
            query = query.filter_by(simulation_id=simulation_id)
        if agent_id:
            query = query.filter_by(agent_id=agent_id)
        if start_tick is not None:
            query = query.filter(ResourceEvent.tick >= start_tick)
        if end_tick is not None:
            query = query.filter(ResourceEvent.tick <= end_tick)
        return query.all()

    # ------------------- Reporting -------------------
    def report(self, **filters) -> Dict[str, Any]:
        events = self.get_events(**filters)
        report: Dict[str, Any] = {}
        for ev in events:
            rtype = ev.resource_type.value
            if rtype not in report:
                report[rtype] = {"consumed": 0, "reserved": 0, "released": 0, "transferred": 0, "wasted": 0}
            report[rtype][ev.action_type.value] = report[rtype].get(ev.action_type.value, 0) + ev.amount
        return report
