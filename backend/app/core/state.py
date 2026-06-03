// backend/app/core/state.py
"""Global simulation state holder.

This module stores a single :class:`SimulationEngine` instance and a running flag.
It provides simple control functions that the FastAPI routes can call.  The
engine internally creates its own :class:`Environment`, so the state module does
not need to manage those objects directly.
"""

import threading
import time
from typing import Optional, Dict

from .engine import SimulationEngine

# Global variables – intentionally simple for the prototype
engine: Optional[SimulationEngine] = None
_running: bool = False
_thread: Optional[threading.Thread] = None


def _run_loop() -> None:
    """Background loop that advances the simulation each second.

    The loop respects the ``_running`` flag; it exits when the flag is cleared.
    """
    global engine
    while _running:
        if engine is None:
            engine = SimulationEngine()
        # Execute a tick – we ignore the returned payload here because the API
        # endpoints will request the latest state when needed.
        engine.run_tick()
        time.sleep(1)  # 1‑second simulation step; adjust as required.


def start_simulation() -> bool:
    """Start the background simulation thread.

    Returns ``True`` if the simulation was started, ``False`` if it was already
    running.
    """
    global _running, _thread, engine
    if _running:
        return False
    _running = True
    if engine is None:
        engine = SimulationEngine()
    _thread = threading.Thread(target=_run_loop, daemon=True)
    _thread.start()
    return True


def stop_simulation() -> bool:
    """Stop the background simulation thread.

    Returns ``True`` if the simulation was stopped, ``False`` if it was not
    running.
    """
    global _running, _thread
    if not _running:
        return False
    _running = False
    # Join the thread to ensure clean shutdown; timeout prevents hanging.
    if _thread:
        _thread.join(timeout=2)
    _thread = None
    return True


def step_simulation() -> Dict:
    """Execute a single tick and return the snapshot payload.
    """
    global engine
    if engine is None:
        engine = SimulationEngine()
    return engine.run_tick()


def get_state() -> Dict:
    """Return the latest simulation snapshot without advancing the clock.
    """
    global engine
    if engine is None:
        # Return an empty structure if nothing has been initialised yet.
        return {"agents": [], "links": [], "time": None, "resources": {}, "events": [], "hazards": []}
    return engine.run_tick()

"""End of state module."""
