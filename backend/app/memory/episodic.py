# backend/app/memory/episodic.py
"""Episodic Memory Store helper.
Handles logging and recalling episodic memory records with semantic similarity.
"""

import json
from typing import List, Dict, Any
from app.models.episodic_memory import EpisodicMemory
from app.utils.embeddings import embed_text

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot_product = sum(x * y for x, y in zip(v1, v2))
    norm_v1 = sum(x * x for x in v1) ** 0.5
    norm_v2 = sum(x * x for x in v2) ** 0.5
    if not norm_v1 or not norm_v2:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

class EpisodicMemoryStore:
    def __init__(self, db_session):
        self.db = db_session

    def log(self, *, agent_id: str, simulation_id: Any, tick: int,
            episode_type: str, context_snapshot: Dict[str, Any],
            outcome: str | None = None, emotional_valence: float = 0.0) -> EpisodicMemory:
        """Log a new episode to the persistent store."""
        episode = EpisodicMemory(
            agent_id=agent_id,
            simulation_id=simulation_id,
            tick=tick,
            episode_type=episode_type,
            context_snapshot=context_snapshot,
            outcome=outcome,
            emotional_valence=emotional_valence
        )
        self.db.add(episode)
        self.db.commit()
        self.db.refresh(episode)
        return episode

    def recall(self, *, agent_id: str, simulation_id: Any, query_embedding: List[float], top_k: int = 5) -> List[EpisodicMemory]:
        """Recall episodes matching semantic query embedding.
        Uses deterministic text embeddings of episodic snapshots and cosine similarity.
        """
        # Fetch all episodes for this agent and simulation
        episodes = self.db.query(EpisodicMemory).filter(
            EpisodicMemory.agent_id == agent_id,
            EpisodicMemory.simulation_id == simulation_id
        ).all()

        scored_episodes = []
        for ep in episodes:
            # Create a string representation of the episode for embedding
            serialized_snapshot = json.dumps(ep.context_snapshot, sort_keys=True)
            text_to_embed = f"{ep.episode_type} {serialized_snapshot} {ep.outcome or ''}"
            ep_embedding = embed_text(text_to_embed)
            
            sim = cosine_similarity(query_embedding, ep_embedding)
            scored_episodes.append((sim, ep))

        # Sort by similarity descending
        scored_episodes.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored_episodes[:top_k]]
