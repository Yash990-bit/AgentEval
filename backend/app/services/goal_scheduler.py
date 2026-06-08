import logging
from typing import List

from ..db.session import SessionLocal
from ..models.goal import AgentGoal, GoalStatusEnum
from .goal_manager import GoalManager

logger = logging.getLogger(__name__)

class GoalScheduler:
    
    """Runs on each simulation tick to advance goal states.

    - Starts pending goals whose dependencies are completed and resources are available.
    - Marks in‑progress goals as failed if deadline_tick is passed.
    - Can be extended to schedule periodic analytics.
    """

    def __init__(self, simulation_id: str):
        self.simulation_id = simulation_id
        self.db = SessionLocal()
        self.manager = GoalManager(self.db)

    def _dependencies_met(self, goal: AgentGoal) -> bool:
        if not goal.dependencies:
            return True
        # All dependent goals must be completed
        dep_goals = (
            self.db.query(AgentGoal)
            .filter(AgentGoal.id.in_(goal.dependencies))
            .all()
        )
        return all(g.status == GoalStatusEnum.completed for g in dep_goals)

    def _resources_available(self, goal: AgentGoal) -> bool:
        # Placeholder: always true; can be extended to check agent budgets
        return True

    def tick(self, current_tick: int) -> None:
        """Advance the state of goals for the configured simulation.

        Called by the simulation loop each tick.
        """
        try:
            # Start eligible pending goals
            pending_goals: List[AgentGoal] = (
                self.db.query(AgentGoal)
                .filter(
                    AgentGoal.simulation_id == self.simulation_id,
                    AgentGoal.status == GoalStatusEnum.pending,
                )
                .all()
            )
            for goal in pending_goals:
                if self._dependencies_met(goal) and self._resources_available(goal):
                    self.manager.start_goal(goal.id, current_tick)
                    logger.info("Started goal %s at tick %s", goal.id, current_tick)

            # Fail overdue in‑progress goals
            in_progress_goals: List[AgentGoal] = (
                self.db.query(AgentGoal)
                .filter(
                    AgentGoal.simulation_id == self.simulation_id,
                    AgentGoal.status == GoalStatusEnum.in_progress,
                    AgentGoal.deadline_tick.isnot(None),
                    AgentGoal.deadline_tick < current_tick,
                )
                .all()
            )
            for goal in in_progress_goals:
                self.manager.fail_goal(goal.id, reason="deadline missed", tick=current_tick)
                logger.warning("Goal %s failed due to deadline at tick %s", goal.id, current_tick)
        finally:
            self.db.close()
