import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..models.goal import AgentGoal, GoalStatusEnum

class GoalManager:
    """Service handling the lifecycle of agent goals."""

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------
    def _get_goal(self, goal_id: uuid.UUID) -> AgentGoal:
        goal = self.db.get(AgentGoal, goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")
        return goal

    # ---------------------------------------------------------------------
    # CRUD & state transitions
    # ---------------------------------------------------------------------
    def create_goal(
        self,
        agent_id: uuid.UUID,
        simulation_id: uuid.UUID,
        title: str,
        description: Optional[str] = None,
        priority: int = 5,
        parent_goal_id: Optional[uuid.UUID] = None,
        dependencies: Optional[List[uuid.UUID]] = None,
        deadline_tick: Optional[int] = None,
        required_resources: Optional[Dict[str, Any]] = None,
    ) -> AgentGoal:
        goal = AgentGoal(
            id=uuid.uuid4(),
            agent_id=agent_id,
            simulation_id=simulation_id,
            title=title,
            description=description,
            priority=priority,
            parent_goal_id=parent_goal_id,
            dependencies=dependencies,
            deadline_tick=deadline_tick,
            required_resources=required_resources or {"compute_units": 0, "api_calls": 0, "tokens": 0},
            status=GoalStatusEnum.pending,
            progress_pct=0.0,
        )
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def start_goal(self, goal_id: uuid.UUID, tick: int) -> AgentGoal:
        goal = self._get_goal(goal_id)
        if goal.status != GoalStatusEnum.pending:
            raise ValueError("Goal can only be started from pending state")
        goal.status = GoalStatusEnum.in_progress
        goal.started_tick = tick
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def update_progress(self, goal_id: uuid.UUID, progress_pct: float) -> AgentGoal:
        goal = self._get_goal(goal_id)
        if goal.status != GoalStatusEnum.in_progress:
            raise ValueError("Can only update progress on in_progress goals")
        goal.progress_pct = max(0.0, min(100.0, progress_pct))
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def complete_goal(self, goal_id: uuid.UUID, tick: int, notes: Optional[str] = None) -> AgentGoal:
        goal = self._get_goal(goal_id)
        if goal.status != GoalStatusEnum.in_progress:
            raise ValueError("Can only complete in_progress goals")
        goal.status = GoalStatusEnum.completed
        goal.completed_tick = tick
        goal.completion_notes = notes
        goal.progress_pct = 100.0
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def block_goal(self, goal_id: uuid.UUID) -> AgentGoal:
        goal = self._get_goal(goal_id)
        if goal.status != GoalStatusEnum.in_progress:
            raise ValueError("Can only block in_progress goals")
        goal.status = GoalStatusEnum.blocked
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def abandon_goal(self, goal_id: uuid.UUID, tick: int, reason: Optional[str] = None) -> AgentGoal:
        goal = self._get_goal(goal_id)
        if goal.status not in (GoalStatusEnum.in_progress, GoalStatusEnum.blocked, GoalStatusEnum.pending):
            raise ValueError("Can only abandon pending/in_progress/blocked goals")
        goal.status = GoalStatusEnum.abandoned
        goal.abandoned_tick = tick
        goal.abandonment_reason = reason
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def fail_goal(self, goal_id: uuid.UUID, tick: int) -> AgentGoal:
        goal = self._get_goal(goal_id)
        if goal.status not in (GoalStatusEnum.in_progress, GoalStatusEnum.pending, GoalStatusEnum.blocked):
            raise ValueError("Can only fail pending/in_progress/blocked goals")
        goal.status = GoalStatusEnum.failed
        goal.completed_tick = tick
        self.db.commit()
        self.db.refresh(goal)
        return goal
