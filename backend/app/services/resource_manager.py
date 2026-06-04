import logging
from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..db.models import ResourceBudget, ResourceEvent, Base
from ..db.session import get_db

logger = logging.getLogger(__name__)

class ResourceManager:
    """Service layer for managing resource budgets and events.

    All operations are scoped to a specific ``agent_id`` within a ``simulation_id``.
    The manager records an event for every mutation and enforces optional limits.
    """

    def __init__(self, db: Session):
        self.db = db

    @classmethod
    def get_instance(cls) -> "ResourceManager":
        """Factory that pulls a DB session from FastAPI dependencies.
        Usage in FastAPI routes::

            def get_manager(db: Session = Depends(get_db)):
                return ResourceManager(db)
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------
    # Budget CRUD
    # ---------------------------------------------------------------------
    def get_budget(self, agent_id: str, simulation_id: str) -> Optional[ResourceBudget]:
        return (
            self.db.query(ResourceBudget)
            .filter_by(agent_id=agent_id, simulation_id=simulation_id)
            .first()
        )

    def create_budget(
        self,
        agent_id: str,
        simulation_id: str,
        compute_total: int = 0,
        api_calls_total: int = 0,
        tokens_total: int = 0,
        usd_total: float = 0.0,
    ) -> ResourceBudget:
        budget = ResourceBudget(
            agent_id=agent_id,
            simulation_id=simulation_id,
            compute_total=compute_total,
            api_calls_total=api_calls_total,
            tokens_total=tokens_total,
            usd_total=usd_total,
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    # ---------------------------------------------------------------------
    # Allocation / Enforcement
    # ---------------------------------------------------------------------
    def _record_event(
        self,
        agent_id: str,
        simulation_id: str,
        resource_type: str,
        action_type: str,
        amount: int,
        tick: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        event = ResourceEvent(
            agent_id=agent_id,
            simulation_id=simulation_id,
            resource_type=resource_type,
            action_type=action_type,
            amount=amount,
            tick=tick,
            metadata=metadata,
        )
        self.db.add(event)
        self.db.commit()

    def allocate(
        self,
        agent_id: str,
        simulation_id: str,
        tick: int,
        compute_units: int = 0,
        api_calls: int = 0,
        tokens: int = 0,
        usd_budget: float = 0.0,
        enforce: bool = True,
    ) -> ResourceBudget:
        """Consume resources for an agent.

        If ``enforce`` is ``True`` a ``ValueError`` is raised when any limit would be exceeded.
        """
        budget = self.get_budget(agent_id, simulation_id)
        if not budget:
            # create a zeroed budget on‑the‑fly
            budget = self.create_budget(agent_id, simulation_id)

        # Helper to update a field safely
        def _apply(field: str, delta: int, total_field: str):
            used = getattr(budget, f"{field}_used") + delta
            total = getattr(budget, f"{field}_total")
            if enforce and total and used > total:
                raise ValueError(f"{field} budget exceeded: {used}/{total}")
            setattr(budget, f"{field}_used", used)
            self._record_event(
                agent_id,
                simulation_id,
                resource_type=field,
                action_type="consumed",
                amount=delta,
                tick=tick,
            )

        if compute_units:
            _apply("compute_units", compute_units, "compute_total")
        if api_calls:
            _apply("api_calls", api_calls, "api_calls_total")
        if tokens:
            _apply("tokens", tokens, "tokens_total")
        if usd_budget:
            # usd is stored as float, but the helper works with int; handle separately
            new_used = budget.usd_spent + usd_budget
            if enforce and budget.usd_total and new_used > budget.usd_total:
                raise ValueError(f"usd_budget exceeded: {new_used}/{budget.usd_total}")
            budget.usd_spent = new_used
            self._record_event(
                agent_id,
                simulation_id,
                resource_type="usd_budget",
                action_type="consumed",
                amount=int(usd_budget * 100),  # store as cents for integer arithmetic
                tick=tick,
            )

        budget.last_updated = datetime.utcnow()
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def release(
        self,
        agent_id: str,
        simulation_id: str,
        tick: int,
        compute_units: int = 0,
        api_calls: int = 0,
        tokens: int = 0,
        usd_budget: float = 0.0,
    ) -> ResourceBudget:
        """Release previously reserved resources back to the budget."""
        budget = self.get_budget(agent_id, simulation_id)
        if not budget:
            raise ValueError("Budget not found for release operation")

        def _apply(field: str, delta: int):
            used = getattr(budget, f"{field}_used") - delta
            if used < 0:
                used = 0
            setattr(budget, f"{field}_used", used)
            self._record_event(
                agent_id,
                simulation_id,
                resource_type=field,
                action_type="released",
                amount=delta,
                tick=tick,
            )

        if compute_units:
            _apply("compute_units", compute_units)
        if api_calls:
            _apply("api_calls", api_calls)  # corrected field name
        if tokens:
            _apply("tokens", tokens)
        if usd_budget:
            new_used = budget.usd_spent - usd_budget
            if new_used < 0:
                new_used = 0
            budget.usd_spent = new_used
            self._record_event(
                agent_id,
                simulation_id,
                resource_type="usd_budget",
                action_type="released",
                amount=int(usd_budget * 100),
                tick=tick,
            )
        budget.last_updated = datetime.utcnow()
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def report(
        self,
        simulation_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        start_tick: Optional[int] = None,
        end_tick: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Aggregate events for reporting.

        Returns a dictionary keyed by ``resource_type`` with total consumed, reserved, etc.
        """
        query = self.db.query(ResourceEvent)
        if simulation_id:
            query = query.filter_by(simulation_id=simulation_id)
        if agent_id:
            query = query.filter_by(agent_id=agent_id)
        if start_tick is not None:
            query = query.filter(ResourceEvent.tick >= start_tick)
        if end_tick is not None:
            query = query.filter(ResourceEvent.tick <= end_tick)
        events = query.all()
        report: Dict[str, Any] = {}
        for ev in events:
            rtype = ev.resource_type.value
            if rtype not in report:
                report[rtype] = {"consumed": 0, "reserved": 0, "released": 0, "transferred": 0, "wasted": 0}
            report[rtype][ev.action_type.value] = report[rtype].get(ev.action_type.value, 0) + ev.amount
        return report
