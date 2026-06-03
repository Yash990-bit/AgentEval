import datetime
import random
from typing import List, Dict

# Simple clock that tracks simulation time
class SimulationClock:
    def __init__(self, start: datetime.datetime = None, step_seconds: int = 60):
        self.current_time = start or datetime.datetime.utcnow()
        self.step = datetime.timedelta(seconds=step_seconds)
    def advance(self):
        self.current_time += self.step

# Resource pool representing global resources
class ResourcePool:
    def __init__(self, total: float = 1000.0):
        self.total = total
        self.available = total
    def consume(self, amount: float):
        self.available = max(0.0, self.available - amount)
    def replenish(self, amount: float):
        self.available = min(self.total, self.available + amount)
    def to_dict(self) -> Dict:
        return {"total": self.total, "available": self.available}

# Simple event model
class Event:
    def __init__(self, name: str, impact: float, duration_ticks: int):
        self.name = name
        self.impact = impact  # positive or negative effect on resources
        self.remaining = duration_ticks
    def tick(self):
        self.remaining -= 1
    def is_active(self) -> bool:
        return self.remaining > 0
    def to_dict(self) -> Dict:
        return {"name": self.name, "impact": self.impact, "remaining": self.remaining}

# Hazard model similar to Event but may affect agents directly
class Hazard:
    def __init__(self, name: str, risk_increase: float, duration_ticks: int):
        self.name = name
        self.risk_increase = risk_increase
        self.remaining = duration_ticks
    def tick(self):
        self.remaining -= 1
    def is_active(self) -> bool:
        return self.remaining > 0
    def to_dict(self) -> Dict:
        return {"name": self.name, "risk_increase": self.risk_increase, "remaining": self.remaining}

# Event generator randomly creates events
class EventGenerator:
    def __init__(self, prob: float = 0.1):
        self.prob = prob
    def maybe_generate(self) -> List[Event]:
        events = []
        if random.random() < self.prob:
            # Example: resource scarcity event reduces resources by 5% for 3 ticks
            events.append(Event(name="Resource Scarcity", impact=-0.05, duration_ticks=3))
        return events

# Hazard generator randomly creates hazards
class HazardGenerator:
    def __init__(self, prob: float = 0.05):
        self.prob = prob
    def maybe_generate(self) -> List[Hazard]:
        hazards = []
        if random.random() < self.prob:
            hazards.append(Hazard(name="System Failure", risk_increase=0.1, duration_ticks=2))
        return hazards

# Central Environment class orchestrating clock, resources, events, hazards
class Environment:
    def __init__(self):
        self.clock = SimulationClock()
        self.resource_pool = ResourcePool()
        self.event_generator = EventGenerator()
        self.hazard_generator = HazardGenerator()
        self._active_events: List[Event] = []
        self._active_hazards: List[Hazard] = []

    def advance(self):
        # Advance time
        self.clock.advance()
        # Generate new events/hazards
        self._active_events.extend(self.event_generator.maybe_generate())
        self._active_hazards.extend(self.hazard_generator.maybe_generate())
        # Apply event impacts to resources
        for ev in list(self._active_events):
            self.resource_pool.consume(abs(ev.impact) * self.resource_pool.total) if ev.impact < 0 else self.resource_pool.replenish(ev.impact * self.resource_pool.total)
            ev.tick()
            if not ev.is_active():
                self._active_events.remove(ev)
        # Apply hazards – hazard effects will be inspected by SimulationEngine per‑agent
        for hz in list(self._active_hazards):
            hz.tick()
            if not hz.is_active():
                self._active_hazards.remove(hz)

    def is_scarcity_active(self) -> bool:
        # Return True if any active event named Resource Scarcity is present
        return any(ev.name == "Resource Scarcity" and ev.is_active() for ev in self._active_events)

    def active_events(self) -> List[Event]:
        return self._active_events

    def active_hazards(self) -> List[Hazard]:
        return self._active_hazards

    @property
    def current_time(self) -> datetime.datetime:
        return self.clock.current_time
