from typing import Dict, Optional

# Global mapping of simulation IDs to InteractionEngine instances
from ..graph.interaction_engine import InteractionEngine

engines: Dict[str, InteractionEngine] = {}

def get_engine(simulation_id: str) -> InteractionEngine:
    """Retrieve the InteractionEngine for a given simulation ID, creating it if necessary."""
    if simulation_id not in engines:
        # Initialize a new engine with empty agents and default environment
        engines[simulation_id] = InteractionEngine(simulation_id)
    return engines[simulation_id]

def create_engine(simulation_id: str, agents: list[Dict] = None) -> InteractionEngine:
    """Create (or replace) an InteractionEngine for a simulation ID with optional agents.
    The agents can be a list of dicts; they will be stored internally if needed.
    """
    engine = InteractionEngine(simulation_id)
    # Future: load agents into the engine if required.
    engines[simulation_id] = engine
    return engine
