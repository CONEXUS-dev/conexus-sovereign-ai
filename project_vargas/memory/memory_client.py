"""
Project Vargas Memory Client — Qdrant Vector Database

Three memory classes for a personal collaborator:
  - Identity: explicit user facts (name, story, preferences)
  - Behavioral: engagement patterns (decision style, pressure tolerance)
  - Attunement: tone/cadence/emotional calibration

Unlike the public Narthex memory (which restricts personal data),
Vargas is personal and private — content filters are relaxed.

All memory is corrigible: the user can correct or erase anything.
All memory has provenance: when it was created, what triggered it.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

COLLECTIONS = ["vargas_identity", "vargas_behavioral", "vargas_attunement"]
EMBEDDING_DIM = 3072  # Gemini embedding-001 dimension

# Memory types allowed per collection
IDENTITY_TYPES = [
    "name", "preference", "story", "background", "value",
    "relationship", "correction", "explicit_statement",
]

BEHAVIORAL_TYPES = [
    "decision_style", "pressure_response", "communication_preference",
    "work_pattern", "thinking_style", "avoidance_pattern",
    "engagement_rhythm", "challenge_tolerance", "observed_pattern",
]

ATTUNEMENT_TYPES = [
    "tone_preference", "cadence_preference", "symbol_resonance",
    "reflection_length", "silence_comfort", "challenge_tolerance",
    "directness_preference", "emotional_temperature",
    "emoji_vector",
]

TYPES_BY_COLLECTION = {
    "vargas_identity": IDENTITY_TYPES,
    "vargas_behavioral": BEHAVIORAL_TYPES,
    "vargas_attunement": ATTUNEMENT_TYPES,
}


class VargasMemoryClient:
    """Memory client for Project Vargas — personal, private, corrigible.

    Supports:
    - store(): Write a memory with provenance
    - retrieve(): Semantic search for relevant memories
    - forget(): Remove a memory by ID
    - list_memories(): Return all memories for a collection
    - reset(): Wipe a collection or all collections
    - health_check(): Verify Qdrant connectivity
    """

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        llm_bridge: Any = None,
    ):
        self._llm_bridge = llm_bridge
        self._qdrant = None
        self._qdrant_host = qdrant_host
        self._qdrant_port = qdrant_port
        self._qdrant_available = False
        self._fallback_stores: Dict[str, Dict[str, Any]] = {c: {} for c in COLLECTIONS}
        self._init_qdrant()

    def _init_qdrant(self):
        """Try to connect to Qdrant. Graceful fallback if unavailable."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            self._qdrant = QdrantClient(
                host=self._qdrant_host, port=self._qdrant_port, timeout=5
            )
            existing = {c.name for c in self._qdrant.get_collections().collections}
            for collection in COLLECTIONS:
                if collection not in existing:
                    self._qdrant.create_collection(
                        collection_name=collection,
                        vectors_config=VectorParams(
                            size=EMBEDDING_DIM, distance=Distance.COSINE
                        ),
                    )
                    logger.info("[MEMORY] Created Qdrant collection: %s", collection)
            self._qdrant_available = True
            logger.info("[MEMORY] Qdrant connected at %s:%d", self._qdrant_host, self._qdrant_port)
        except Exception as e:
            logger.warning("[MEMORY] Qdrant unavailable (%s) — using in-memory fallback", e)
            self._qdrant_available = False

    def _embed(self, text: str) -> list:
        """Generate embedding for text."""
        if self._llm_bridge is not None:
            return self._llm_bridge.embed(text)
        return [0.0] * EMBEDDING_DIM

    def store(
        self,
        collection: str,
        content: str,
        memory_type: str,
        confidence: float = 0.8,
        rationale: str = "",
        emoji_vector_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Store a memory with provenance. Returns memory ID or None."""
        if collection not in COLLECTIONS:
            logger.warning("[MEMORY] Invalid collection: %s", collection)
            return None

        allowed_types = TYPES_BY_COLLECTION.get(collection, [])
        if memory_type not in allowed_types:
            logger.warning("[MEMORY] Invalid type '%s' for collection '%s'", memory_type, collection)
            return None

        memory_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        payload = {
            "id": memory_id,
            "content": content,
            "type": memory_type,
            "confidence": confidence,
            "rationale": rationale,
            "created_at": now,
            "emoji_vector_id": emoji_vector_id,
            "collection": collection,
            "metadata": metadata or {},
        }

        if self._qdrant_available:
            try:
                from qdrant_client.models import PointStruct
                vector = self._embed(content)
                self._qdrant.upsert(
                    collection_name=collection,
                    points=[PointStruct(id=memory_id, vector=vector, payload=payload)],
                )
                logger.info("[MEMORY] Stored: collection=%s type=%s id=%s", collection, memory_type, memory_id)
                return memory_id
            except Exception as e:
                logger.warning("[MEMORY] Qdrant write failed: %s — using fallback", e)

        self._fallback_stores[collection][memory_id] = payload
        logger.info("[MEMORY] Stored (fallback): collection=%s type=%s id=%s", collection, memory_type, memory_id)
        return memory_id

    def retrieve(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Semantic search across one or all collections."""
        collections_to_search = [collection] if collection else COLLECTIONS
        results = []

        for coll in collections_to_search:
            if coll not in COLLECTIONS:
                continue

            if self._qdrant_available:
                try:
                    query_vector = self._embed(query)
                    response = self._qdrant.query_points(
                        collection_name=coll,
                        query=query_vector,
                        limit=top_k,
                    )
                    for hit in response.points:
                        results.append({
                            "id": hit.id,
                            "score": hit.score,
                            "content": hit.payload.get("content", ""),
                            "type": hit.payload.get("type", ""),
                            "collection": coll,
                            "created_at": hit.payload.get("created_at", ""),
                            "confidence": hit.payload.get("confidence", 0),
                        })
                    continue
                except Exception as e:
                    logger.warning("[MEMORY] Qdrant read failed for %s: %s", coll, e)

            # Fallback
            for v in self._fallback_stores.get(coll, {}).values():
                results.append({
                    "id": v["id"],
                    "score": 1.0,
                    "content": v["content"],
                    "type": v["type"],
                    "collection": coll,
                    "created_at": v["created_at"],
                    "confidence": v["confidence"],
                })

        # Keyword boost: if query words appear verbatim in memory content, boost score
        query_words = set(w.lower() for w in query.split() if len(w) > 3)
        if query_words:
            for r in results:
                content_lower = r["content"].lower()
                keyword_hits = sum(1 for w in query_words if w in content_lower)
                if keyword_hits > 0:
                    # Boost score by 0.1 per keyword hit (capped at 0.3)
                    boost = min(keyword_hits * 0.1, 0.3)
                    r["score"] = r.get("score", 0) + boost

        # Sort by score descending and limit
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

    def list_memories(self, collection: str) -> List[Dict[str, Any]]:
        """Return all memories in a collection."""
        if collection not in COLLECTIONS:
            return []

        if self._qdrant_available:
            try:
                response = self._qdrant.scroll(
                    collection_name=collection,
                    limit=100,
                )
                points = response[0] if response else []
                return [
                    {
                        "id": p.id,
                        "content": p.payload.get("content", ""),
                        "type": p.payload.get("type", ""),
                        "confidence": p.payload.get("confidence", 0),
                        "created_at": p.payload.get("created_at", ""),
                    }
                    for p in points
                ]
            except Exception as e:
                logger.warning("[MEMORY] Qdrant list failed for %s: %s", collection, e)

        return [
            {
                "id": v["id"],
                "content": v["content"],
                "type": v["type"],
                "confidence": v["confidence"],
                "created_at": v["created_at"],
            }
            for v in self._fallback_stores.get(collection, {}).values()
        ]

    def forget(self, memory_id: str, collection: Optional[str] = None) -> bool:
        """Remove a memory by ID. Searches all collections if none specified."""
        collections_to_check = [collection] if collection else COLLECTIONS

        for coll in collections_to_check:
            if self._qdrant_available:
                try:
                    self._qdrant.delete(
                        collection_name=coll,
                        points_selector=[memory_id],
                    )
                    logger.info("[MEMORY] Forgot: id=%s collection=%s", memory_id, coll)
                    return True
                except Exception as e:
                    logger.warning("[MEMORY] Qdrant delete failed: %s", e)

            if memory_id in self._fallback_stores.get(coll, {}):
                del self._fallback_stores[coll][memory_id]
                logger.info("[MEMORY] Forgot (fallback): id=%s collection=%s", memory_id, coll)
                return True

        return False

    def reset(self, collection: Optional[str] = None) -> bool:
        """Wipe a collection or all collections."""
        collections_to_reset = [collection] if collection else COLLECTIONS

        for coll in collections_to_reset:
            if coll not in COLLECTIONS:
                continue

            if self._qdrant_available:
                try:
                    from qdrant_client.models import Distance, VectorParams
                    self._qdrant.delete_collection(collection_name=coll)
                    self._qdrant.create_collection(
                        collection_name=coll,
                        vectors_config=VectorParams(
                            size=EMBEDDING_DIM, distance=Distance.COSINE
                        ),
                    )
                    logger.info("[MEMORY] Reset collection: %s", coll)
                except Exception as e:
                    logger.warning("[MEMORY] Qdrant reset failed for %s: %s", coll, e)

            self._fallback_stores[coll] = {}

        return True

    def summary(self) -> Dict[str, Any]:
        """Return a summary of all memory collections."""
        result = {}
        for coll in COLLECTIONS:
            memories = self.list_memories(coll)
            result[coll] = {
                "count": len(memories),
                "types": list(set(m["type"] for m in memories)),
            }
        return result

    def health_check(self) -> Dict[str, Any]:
        """Check memory system status."""
        return {
            "qdrant_available": self._qdrant_available,
            "backend": "qdrant" if self._qdrant_available else "in-memory-fallback",
            "collections": COLLECTIONS,
        }
