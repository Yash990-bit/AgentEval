# backend/app/utils/embeddings.py
"""Simple embedding helper.
Replace `embed_text` with a real model (e.g., Gemini text‑embedding‑3‑small) when available.
"""
import random
from typing import List

def embed_text(text: str, dim: int = 1536) -> List[float]:
    """Return a deterministic pseudo‑embedding for *text*.
    For demo/testing we use a seeded random vector based on the string hash.
    """
    rnd = random.Random(hash(text))
    return [rnd.random() for _ in range(dim)]
