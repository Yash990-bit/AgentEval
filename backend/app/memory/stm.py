from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List

@dataclass
class STMItem:
    content: str
    tick_created: int
    access_count: int = 0
    importance: float = 1.0
    last_access_tick: int = 0

class ShortTermMemory:
    def __init__(self, max_items: int = 20):
        self.max_items = max_items
        self.store: Dict[str, Deque[STMItem]] = {}

    def _ensure_agent(self, agent_id: str):
        if agent_id not in self.store:
            self.store[agent_id] = deque()

    def add(self, agent_id: str, content: str, tick: int, importance: float = 1.0):
        self._ensure_agent(agent_id)
        dq = self.store[agent_id]
        # Evict if needed (FIFO), but respect importance scores
        if len(dq) >= self.max_items:
            # Find least important item (lowest importance, then oldest)
            least = min(dq, key=lambda x: (x.importance, x.tick_created))
            dq.remove(least)
        dq.append(STMItem(content=content, tick_created=tick, importance=importance, last_access_tick=tick))

    def retrieve(self, agent_id: str, content: str, tick: int) -> STMItem | None:
        self._ensure_agent(agent_id)
        for item in self.store[agent_id]:
            if item.content == content:
                item.access_count += 1
                item.last_access_tick = tick
                return item
        return None

    def decay(self, current_tick: int, decay_factor: float = 0.95):
        for dq in self.store.values():
            for item in dq:
                elapsed = max(1, current_tick - item.last_access_tick)
                item.importance *= decay_factor ** elapsed
                item.last_access_tick = current_tick
