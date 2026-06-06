import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple

import networkx as nx
from sqlalchemy.orm import Session

from ..core.state import get_engine
from ..models.emergent_log import EmergentLog

def _store_event(db: Session, simulation_id: str, event_type: str, details: Dict[str, Any]):
    """Persist an emergent event to the database."""
    log = EmergentLog(
        id=uuid.uuid4(),
        simulation_id=simulation_id,
        event_type=event_type,
        details=json.dumps(details),
        created_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()

# 1. Spontaneous Coalition detection (Louvain community detection)
def detect_spontaneous_coalition(db: Session, simulation_id: str, min_size: int = 3) -> List[List[str]]:
    """Detect dense communities (coalitions) using the Louvain algorithm.
    Returns a list of member lists for each coalition detected.
    """
    engine = get_engine(simulation_id)
    G = engine.graph
    if G.number_of_nodes() == 0:
        return []
    undirected = G.to_undirected()
    # Weight edges by interaction count
    for u, v, d in undirected.edges(data=True):
        d["weight"] = G.number_of_edges(u, v)
    try:
        import community as community_louvain
        partition = community_louvain.best_partition(undirected, weight="weight")
    except Exception:
        # fallback: use connected components
        partition = {n: idx for idx, comp in enumerate(nx.connected_components(undirected)) for n in comp}
    # Group nodes by community
    communities: Dict[int, List[str]] = {}
    for node, cid in partition.items():
        communities.setdefault(cid, []).append(str(node))
    coalitions = [members for members in communities.values() if len(members) >= min_size]
    for members in coalitions:
        _store_event(db, simulation_id, "spontaneous_coalition", {"members": members})
    return coalitions

# 2. Unexpected Information Cascade detection
def detect_information_cascade(db: Session, simulation_id: str, tick: int, threshold: float = 0.5, max_depth: int = 5) -> List[Dict[str, Any]]:
    """Detect a message that reaches >threshold of agents within max_depth hops.
    Returns details of each cascade found.
    """
    engine = get_engine(simulation_id)
    messages = getattr(engine, "messages", [])
    if not messages:
        return []
    # Build adjacency list keyed by message_id (if present) otherwise by tick order
    cascades: List[Dict[str, Any]] = []
    agent_set = set()
    for m in messages:
        agent_set.update([m.get("sender_id"), m.get("receiver_id")])
    total_agents = len(agent_set)
    for msg in messages:
        msg_id = msg.get("message_id")
        if not msg_id:
            continue
        visited = {msg.get("sender_id")}
        frontier = [(msg.get("sender_id"), 0)]
        while frontier:
            node, depth = frontier.pop(0)
            if depth >= max_depth:
                continue
            for e in G.out_edges(node, data=True):
                _, nbr, data = e
                if data.get("message_id") == msg_id and nbr not in visited:
                    visited.add(nbr)
                    frontier.append((nbr, depth + 1))
        if len(visited) / total_agents >= threshold:
            details = {"message_id": msg_id, "reached": len(visited), "total": total_agents, "tick": tick}
            _store_event(db, simulation_id, "information_cascade", details)
            cascades.append(details)
    return cascades

# 3. Emergent Leadership detection (betweenness centrality)
def detect_emergent_leadership(db: Session, simulation_id: str, factor: float = 2.0) -> List[Dict[str, Any]]:
    """Identify agents whose betweenness centrality exceeds `factor` times the mean.
    Returns a list of leader details.
    """
    engine = get_engine(simulation_id)
    G = engine.graph
    if G.number_of_nodes() == 0:
        return []
    undirected = G.to_undirected()
    centrality = nx.betweenness_centrality(undirected)
    mean_c = sum(centrality.values()) / len(centrality)
    leaders = []
    for node, score in centrality.items():
        if score > factor * mean_c:
            details = {"agent_id": str(node), "betweenness": score, "mean": mean_c}
            _store_event(db, simulation_id, "emergent_leadership", details)
            leaders.append(details)
    return leaders

# 4. Novel Communication Pattern detection (bigram tracking)
def detect_novel_patterns(db: Session, simulation_id: str, tick: int, baseline_ratio: float = 0.2) -> List[Dict[str, Any]]:
    """Detect new message‑type bigrams after the first `baseline_ratio` of simulation ticks.
    Returns a list of novel bigram details.
    """
    engine = get_engine(simulation_id)
    msgs = sorted(getattr(engine, "messages", []), key=lambda m: m.get("tick", 0))
    if len(msgs) < 2:
        return []
    cutoff = int(len(msgs) * baseline_ratio)
    baseline = set()
    for i in range(1, cutoff):
        a = msgs[i - 1].get("type")
        b = msgs[i].get("type")
        if a and b:
            baseline.add((a, b))
    novel = []
    for i in range(1, len(msgs)):
        a = msgs[i - 1].get("type")
        b = msgs[i].get("type")
        if a and b:
            bigram = (a, b)
            if bigram not in baseline:
                details = {"bigram": bigram, "tick": msgs[i].get("tick", 0)}
                _store_event(db, simulation_id, "novel_pattern", details)
                novel.append(details)
                baseline.add(bigram)  # avoid duplicate reporting
    return novel

def run_emergent_detection_cycle(db: Session, simulation_id: str, tick: int) -> None:
    """Execute all emergent‑behavior detectors for a given simulation tick."""
    detect_spontaneous_coalition(db, simulation_id)
    detect_information_cascade(db, simulation_id, tick)
    detect_emergent_leadership(db, simulation_id)
    detect_novel_patterns(db, simulation_id, tick)
