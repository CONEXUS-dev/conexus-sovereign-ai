"""
CONEXUS Memory Client — Qdrant Vector Database Abstraction

Handles embedding generation via GPT4All Embed4All and storage/retrieval
via Qdrant. Provides namespace-aware memory operations for the sovereign
AI system (episodic, semantic, sovereign_architecture, lineage).
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from agents.llm_client import LLMClient

logger = logging.getLogger(__name__)

NAMESPACES = ["episodic", "semantic", "sovereign_architecture", "lineage", "gear_states"]
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 via GPT4All Embed4All


class MemoryClient:
    def __init__(
        self,
        llm_client: LLMClient,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
    ):
        self.llm = llm_client
        self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)

    def ensure_collections(self) -> None:
        """Create Qdrant collections for all namespaces if they don't exist."""
        existing = {c.name for c in self.qdrant.get_collections().collections}
        for ns in NAMESPACES:
            if ns not in existing:
                self.qdrant.create_collection(
                    collection_name=ns,
                    vectors_config=VectorParams(
                        size=EMBEDDING_DIM, distance=Distance.COSINE
                    ),
                )
                logger.info("Created Qdrant collection: %s", ns)
            else:
                logger.debug("Collection already exists: %s", ns)

    def store(
        self,
        namespace: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Embed text and store in the specified namespace. Returns point ID."""
        if namespace not in NAMESPACES:
            raise ValueError(f"Invalid namespace: {namespace}. Must be one of {NAMESPACES}")

        vector = self.llm.embed(text)
        point_id = str(uuid.uuid4())
        payload = {
            "text": text,
            "namespace": namespace,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        }

        self.qdrant.upsert(
            collection_name=namespace,
            points=[
                PointStruct(id=point_id, vector=vector, payload=payload)
            ],
        )
        logger.info(
            "Stored memory in '%s': id=%s, text_len=%d",
            namespace, point_id, len(text),
        )
        return point_id

    def retrieve(
        self,
        namespace: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Semantic search in the specified namespace."""
        if namespace not in NAMESPACES:
            raise ValueError(f"Invalid namespace: {namespace}. Must be one of {NAMESPACES}")

        query_vector = self.llm.embed(query)
        response = self.qdrant.query_points(
            collection_name=namespace,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
        )

        memories = []
        for hit in response.points:
            memories.append({
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "metadata": {
                    k: v for k, v in hit.payload.items() if k != "text"
                },
            })

        logger.info(
            "Retrieved %d memories from '%s' for query_len=%d",
            len(memories), namespace, len(query),
        )
        return memories

    def store_memory_intent(self, memory_intent: Dict[str, Any]) -> Optional[str]:
        """
        Store a memory from an agent's memory_intent structure.
        Returns the point ID if stored, None if intent is not 'store'.
        """
        if memory_intent.get("intent") != "store":
            return None

        text = memory_intent.get("what", "")
        if not text:
            return None

        namespace = "episodic"  # Default namespace for agent outputs
        metadata = {
            k: v for k, v in memory_intent.items()
            if k not in ("intent", "what")
        }

        return self.store(namespace, text, metadata)

    def health_check(self) -> Dict[str, Any]:
        """Check Qdrant connectivity and collection status."""
        try:
            collections = self.qdrant.get_collections().collections
            collection_names = [c.name for c in collections]
            missing = [ns for ns in NAMESPACES if ns not in collection_names]
            return {
                "status": "ok" if not missing else "incomplete",
                "collections": collection_names,
                "missing": missing,
            }
        except Exception as e:
            logger.error("Memory health check failed: %s", e)
            return {
                "status": "error",
                "error": str(e),
            }
