import datetime
from typing import List, Dict, Any

from .stm import ShortTermMemory
from .ltm import LongTermMemory, LTMItem
from .shared import SharedMemoryPool
from .episodic import EpisodicMemoryStore
from ..db.session import SessionLocal
from ..utils.embeddings import embed_text

class MemoryManager:
    """High‑level manager for all four memory layers.
    It holds per‑process STM and LTM instances and uses a SQLAlchemy
    session for the persistent layers.
    """
    def __init__(self):
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        self.db = SessionLocal()
        self.shared = SharedMemoryPool(self.db)
        self.episodic = EpisodicMemoryStore(self.db)
        # track the current simulation tick (should be set by the clock)
        self.current_tick = 0

    # ---------- STM ----------
    def store_stm(self, agent_id: str, content: str, tick: int, importance: float = 1.0):
        self.stm.add(agent_id, content, tick, importance)

    # ---------- Promotion ----------
    def promote_to_ltm(self, agent_id: str):
        """Promote eligible STM items to LTM.
        Eligibility: importance > 0.7 and access_count > 3.
        """
        items = list(self.stm.store.get(agent_id, []))
        for item in items:
            if item.importance > 0.7 and item.access_count > 3:
                embedding = embed_text(item.content)
                ltm_item = LTMItem(
                    content=item.content,
                    embedding=embedding,
                    tick_created=item.tick_created,
                    metadata={
                        "source_agent_id": agent_id,
                        "staleness": 0.0,
                    },
                )
                self.ltm.add_item(ltm_item)
                # optional removal from STM after promotion
                self.stm.store[agent_id].remove(item)

    # ---------- LTM Retrieval ----------
    def retrieve_ltm(self, query: str, top_k: int = 5) -> List[LTMItem]:
        embedding = embed_text(query)
        return self.ltm.search(embedding, top_k=top_k)

    # ---------- Shared Memory ----------
    def write_shared(self, simulation_id: int, agent_id: int, content: str, tags: List[str], trust_score: float):
        return self.shared.write(simulation_id, agent_id, content, tags, trust_score)

    def read_shared(self, simulation_id: int, agent_id: int):
        return self.shared.read(simulation_id, agent_id)

    # ---------- Episodic Memory ----------
    def store_episode(self, *, agent_id: int, simulation_id: int, tick: int,
                     episode_type: str, context_snapshot: Dict[str, Any],
                     outcome: str | None = None, emotional_valence: float = 0.0):
        return self.episodic.log(
            agent_id=agent_id,
            simulation_id=simulation_id,
            tick=tick,
            episode_type=episode_type,
            context_snapshot=context_snapshot,
            outcome=outcome,
            emotional_valence=emotional_valence,
        )

    def recall_episodes(self, *, agent_id: int, simulation_id: int, query: str, top_k: int = 5):
        embedding = embed_text(query)
        return self.episodic.recall(
            agent_id=agent_id,
            simulation_id=simulation_id,
            query_embedding=embedding,
            top_k=top_k,
        )

    # ---------- Decay ----------
    def decay(self, tick: int, decay_factor: float = 0.95):
        """Apply decay to STM items and increase LTM staleness.
        Called each simulation tick.
        """
        self.current_tick = tick
        self.stm.decay(tick, decay_factor)
        # LTM staleness: a simple update of a payload field via Qdrant
        # For simplicity we re‑insert with updated staleness value.
        # Real implementation would use Qdrant update API.
        # Here we iterate over all points (expensive) – placeholder.
        # Users should replace with proper filter‑update.
        # No action performed as this is a placeholder.

    # ---------- Metrics ----------
    def compute_metrics(self, agent_id: str, simulation_id: int) -> dict:
        from .metrics import compute_agent_metrics
        return compute_agent_metrics(agent_id, simulation_id, self)
