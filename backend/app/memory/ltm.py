import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue, PointStruct
from pydantic import BaseModel

from ..config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION, QDRANT_URL, QDRANT_API_KEY

class LTMItem(BaseModel):
    content: str
    embedding: List[float]
    tick_created: int
    metadata: Dict[str, Any] = {}

class LongTermMemory:
    def __init__(self, collection_name: str = QDRANT_COLLECTION, dim: int = 1536):
        """Initialize Qdrant client and ensure collection exists.
        Args:
            collection_name: Name of the Qdrant collection.
            dim: Dimensionality of embedding vectors (default matches text‑embedding‑3‑small).
        """
        self.collection_name = collection_name
        self.dim = dim
        try:
            if QDRANT_URL:
                self.client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=1.0)
            else:
                self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, timeout=1.0)
            # Test connectivity
            self.client.get_collections()
        except Exception:
            # Fallback to local in-memory Qdrant client for testing and development
            self.client = QdrantClient(location=":memory:")

        # Create collection if it does not exist
        try:
            collections_list = self.client.get_collections().collections
            collection_names = [col.name for col in collections_list]
        except Exception:
            collection_names = []

        if collection_name not in collection_names:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def add_item(self, item: LTMItem) -> None:
        """Add a memory item to the vector store.
        The payload stores the raw content and metadata.
        """
        payload = {
            "content": item.content,
            "tick_created": item.tick_created,
            **item.metadata,
        }
        # Generate deterministic UUID based on content and tick
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{item.tick_created}:{item.content}"))
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=item.embedding,
                    payload=payload,
                )
            ],
        )

    def search(self, query_vector: List[float], top_k: int = 5, filter: Filter | None = None) -> List[LTMItem]:
        """Perform a similarity search and return LTMItem objects.
        """
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=filter,
            with_vectors=True,
        )
        items: List[LTMItem] = []
        for hit in response.points:
            payload = hit.payload or {}
            vector = hit.vector
            if isinstance(vector, dict):
                vector = list(vector.values())[0] if vector else [0.0] * self.dim
            elif vector is None:
                vector = [0.0] * self.dim

            items.append(
                LTMItem(
                    content=payload.get("content", ""),
                    embedding=vector,
                    tick_created=payload.get("tick_created", 0),
                    metadata={k: v for k, v in payload.items() if k not in {"content", "tick_created"}},
                )
            )
        return items
