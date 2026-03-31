"""
VARGAS V4 ECP-Native Memory Client — Qdrant Vector Database

Three ECP semantic stores that directly mirror the Emotional Calibration Protocol:
  - ecp_truth: durable realities, constraints, and core project definitions
  - ecp_symbol: emoji vectors, dialect fragments, archetypes, and compressed motifs
  - ecp_contradiction: unresolved paradoxes stored as structured runtime fuel

This is the V4 breakthrough: memory is no longer outside the ECP and translated
into it later. Memory IS the protocol. VARGAS stores reality as Truth, symbolic
resonance as Symbol, and unresolved tension as Contradiction.

All memory is corrigible: the user can correct or erase anything.
All memory has provenance: when it was created, what triggered it.
"""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# --- ECP-Native Collections ---
ECP_COLLECTIONS = ["ecp_truth", "ecp_symbol", "ecp_contradiction"]
EMBEDDING_DIM = 3072  # Gemini embedding-001 dimension

# Subtypes allowed per ECP collection
TRUTH_SUBTYPES = [
    "user_constraint", "project_definition", "system_principle",
    "relationship_boundary", "architectural_fact", "runtime_rule",
    "preference", "long_horizon_goal",
]

SYMBOL_SUBTYPES = [
    "emoji_vector", "archetype", "motif", "metaphor",
    "mirror_tier", "dialect_fragment", "symbolic_operator", "tone_anchor",
]

CONTRADICTION_SUBTYPES = [
    "declared_vs_observed", "goal_conflict", "architectural_drift",
    "execution_gap", "value_conflict", "timing_conflict",
    "identity_conflict", "trust_conflict",
]

SUBTYPES_BY_COLLECTION = {
    "ecp_truth": TRUTH_SUBTYPES,
    "ecp_symbol": SYMBOL_SUBTYPES,
    "ecp_contradiction": CONTRADICTION_SUBTYPES,
}


class ECPMemoryClient:
    """ECP-native memory client for VARGAS V4 — semantic, corrigible, class-aware.

    The governing memory law:
    Store only what materially improves future truth, symbolic continuity,
    contradiction awareness, or execution quality.

    Supports:
    - store(): Write a memory with ECP-native metadata and provenance
    - retrieve(): Class-aware semantic search across one or all collections
    - forget(): Remove a memory by ID (corrigibility)
    - correct(): Supersede a memory with a corrected version
    - list_memories(): Return all memories for a collection
    - reset(): Wipe a collection or all collections
    - health_check(): Verify Qdrant connectivity and collection state
    - summarize_collection(): LLM-driven compression preserving ECP shape
    """

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        llm_bridge: Any = None,
    ):
        self._llm_bridge = llm_bridge
        self._qdrant = None
        self._qdrant_host = qdrant_host
        self._qdrant_port = qdrant_port
        self._qdrant_url = qdrant_url
        self._qdrant_api_key = qdrant_api_key
        self._qdrant_available = False
        self._fallback_stores: Dict[str, Dict[str, Any]] = {
            c: {} for c in ECP_COLLECTIONS
        }
        self._init_qdrant()

    def _init_qdrant(self):
        """Try to connect to Qdrant. Graceful fallback if unavailable."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            if self._qdrant_url:
                self._qdrant = QdrantClient(
                    url=self._qdrant_url,
                    api_key=self._qdrant_api_key,
                    timeout=5,
                )
            else:
                self._qdrant = QdrantClient(
                    host=self._qdrant_host, port=self._qdrant_port, timeout=5
                )

            existing = {c.name for c in self._qdrant.get_collections().collections}
            for collection in ECP_COLLECTIONS:
                if collection not in existing:
                    self._qdrant.create_collection(
                        collection_name=collection,
                        vectors_config=VectorParams(
                            size=EMBEDDING_DIM, distance=Distance.COSINE
                        ),
                    )
                    logger.info("[ECP_MEMORY] Created collection: %s", collection)
            self._qdrant_available = True
            target = self._qdrant_url or f"{self._qdrant_host}:{self._qdrant_port}"
            logger.info("[ECP_MEMORY] Qdrant connected at %s", target)
        except Exception:
            target = self._qdrant_url or f"{self._qdrant_host}:{self._qdrant_port}"
            logger.warning(
                "[ECP_MEMORY] Qdrant not reachable at %s — "
                "start with: docker run -d -p 6333:6333 qdrant/qdrant",
                target,
            )
            logger.warning(
                "[ECP_MEMORY] Using in-memory fallback "
                "(memories will not persist across restarts)"
            )
            self._qdrant_available = False

    def _embed(self, text: str) -> list:
        """Generate embedding vector for text."""
        if self._llm_bridge is not None:
            return self._llm_bridge.embed(text)
        return [0.0] * EMBEDDING_DIM

    def store(
        self,
        collection: str,
        content: str,
        subtype: str,
        confidence: float = 0.8,
        source_request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_scope: str = "vargas_v4",
        challenge_weight: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Store a memory with ECP-native metadata and provenance.

        Args:
            collection: One of ecp_truth, ecp_symbol, ecp_contradiction.
            content: The semantic content to store (text for truth/symbol,
                     JSON string for contradiction).
            subtype: Must be valid for the target collection.
            confidence: Write confidence (0.0–1.0).
            source_request_id: Provenance link to the originating request.
            session_id: Current session identifier.
            project_scope: Scope boundary for retrieval filtering.
            challenge_weight: How much this memory should influence challenge posture.
            metadata: Additional class-specific metadata.

        Returns:
            memory_id (str) on success, None on failure.
        """
        if collection not in ECP_COLLECTIONS:
            logger.warning("[ECP_MEMORY] Invalid collection: %s", collection)
            return None

        allowed = SUBTYPES_BY_COLLECTION.get(collection, [])
        if subtype not in allowed:
            logger.warning(
                "[ECP_MEMORY] Invalid subtype '%s' for collection '%s'",
                subtype, collection,
            )
            return None

        memory_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        source_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        payload = {
            "memory_id": memory_id,
            "memory_class": collection,
            "memory_subtype": subtype,
            "content": content,
            "source_hash": source_hash,
            "confidence": confidence,
            "status": "active",
            "corrigible": True,
            "created_at": now,
            "updated_at": now,
            "source_request_id": source_request_id,
            "session_id": session_id,
            "project_scope": project_scope,
            "challenge_weight": challenge_weight,
            "retrieval_priority": confidence,
            "metadata": metadata or {},
        }

        if self._qdrant_available:
            try:
                from qdrant_client.models import PointStruct

                vector = self._embed(content)
                self._qdrant.upsert(
                    collection_name=collection,
                    points=[
                        PointStruct(
                            id=memory_id, vector=vector, payload=payload
                        )
                    ],
                )
                logger.info(
                    "[ECP_MEMORY] Stored: collection=%s subtype=%s id=%s",
                    collection, subtype, memory_id,
                )
                return memory_id
            except Exception as e:
                logger.warning(
                    "[ECP_MEMORY] Qdrant write failed: %s — using fallback", e
                )

        self._fallback_stores[collection][memory_id] = payload
        logger.info(
            "[ECP_MEMORY] Stored (fallback): collection=%s subtype=%s id=%s",
            collection, subtype, memory_id,
        )
        return memory_id

    def retrieve(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 5,
        filter_subtype: Optional[str] = None,
        filter_status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Class-aware semantic search across one or all ECP collections.

        Args:
            query: Search query text.
            collection: Restrict to one collection, or None for all.
            top_k: Maximum results to return.
            filter_subtype: Optional subtype filter.
            filter_status: Optional status filter (e.g. 'active').

        Returns:
            List of memory dicts sorted by relevance score descending.
        """
        collections_to_search = [collection] if collection else ECP_COLLECTIONS
        results = []

        for coll in collections_to_search:
            if coll not in ECP_COLLECTIONS:
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
                        p = hit.payload
                        if filter_subtype and p.get("memory_subtype") != filter_subtype:
                            continue
                        if filter_status and p.get("status") != filter_status:
                            continue
                        results.append({
                            "memory_id": hit.id,
                            "score": hit.score,
                            "content": p.get("content", ""),
                            "memory_class": coll,
                            "memory_subtype": p.get("memory_subtype", ""),
                            "confidence": p.get("confidence", 0),
                            "status": p.get("status", "active"),
                            "challenge_weight": p.get("challenge_weight", 0),
                            "created_at": p.get("created_at", ""),
                            "metadata": p.get("metadata", {}),
                        })
                    continue
                except Exception as e:
                    logger.warning(
                        "[ECP_MEMORY] Qdrant read failed for %s: %s", coll, e
                    )

            for v in self._fallback_stores.get(coll, {}).values():
                if filter_subtype and v.get("memory_subtype") != filter_subtype:
                    continue
                if filter_status and v.get("status") != filter_status:
                    continue
                results.append({
                    "memory_id": v["memory_id"],
                    "score": 1.0,
                    "content": v["content"],
                    "memory_class": coll,
                    "memory_subtype": v.get("memory_subtype", ""),
                    "confidence": v.get("confidence", 0),
                    "status": v.get("status", "active"),
                    "challenge_weight": v.get("challenge_weight", 0),
                    "created_at": v.get("created_at", ""),
                    "metadata": v.get("metadata", {}),
                })

        query_words = {w.lower() for w in query.split() if len(w) > 3}
        if query_words:
            for r in results:
                content_lower = r["content"].lower()
                keyword_hits = sum(1 for w in query_words if w in content_lower)
                if keyword_hits > 0:
                    boost = min(keyword_hits * 0.1, 0.3)
                    r["score"] = r.get("score", 0) + boost

        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

    def forget(self, memory_id: str, collection: Optional[str] = None) -> bool:
        """Remove a memory by ID. Corrigibility: user has ultimate authority."""
        collections_to_check = [collection] if collection else ECP_COLLECTIONS

        for coll in collections_to_check:
            if self._qdrant_available:
                try:
                    self._qdrant.delete(
                        collection_name=coll,
                        points_selector=[memory_id],
                    )
                    logger.info(
                        "[ECP_MEMORY] Forgot: id=%s collection=%s", memory_id, coll
                    )
                    return True
                except Exception as e:
                    logger.warning("[ECP_MEMORY] Qdrant delete failed: %s", e)

            if memory_id in self._fallback_stores.get(coll, {}):
                del self._fallback_stores[coll][memory_id]
                logger.info(
                    "[ECP_MEMORY] Forgot (fallback): id=%s collection=%s",
                    memory_id, coll,
                )
                return True

        return False

    def correct(
        self,
        memory_id: str,
        new_content: str,
        collection: Optional[str] = None,
        reason: str = "user_correction",
    ) -> Optional[str]:
        """Supersede a memory with corrected content. Returns new memory ID."""
        collections_to_check = [collection] if collection else ECP_COLLECTIONS

        for coll in collections_to_check:
            old_payload = None

            if self._qdrant_available:
                try:
                    response = self._qdrant.retrieve(
                        collection_name=coll,
                        ids=[memory_id],
                    )
                    if response:
                        old_payload = response[0].payload
                except Exception:
                    pass

            if not old_payload and memory_id in self._fallback_stores.get(coll, {}):
                old_payload = self._fallback_stores[coll][memory_id]

            if old_payload:
                self.forget(memory_id, coll)
                new_id = self.store(
                    collection=coll,
                    content=new_content,
                    subtype=old_payload.get("memory_subtype", "user_constraint"),
                    confidence=old_payload.get("confidence", 0.8),
                    source_request_id=old_payload.get("source_request_id"),
                    session_id=old_payload.get("session_id"),
                    project_scope=old_payload.get("project_scope", "vargas_v4"),
                    challenge_weight=old_payload.get("challenge_weight", 0.0),
                    metadata={
                        **old_payload.get("metadata", {}),
                        "supersedes": memory_id,
                        "correction_reason": reason,
                    },
                )
                logger.info(
                    "[ECP_MEMORY] Corrected: old=%s new=%s reason=%s",
                    memory_id, new_id, reason,
                )
                return new_id

        logger.warning("[ECP_MEMORY] Correct failed: memory %s not found", memory_id)
        return None

    def list_memories(
        self,
        collection: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Return all memories in a collection."""
        if collection not in ECP_COLLECTIONS:
            return []

        if self._qdrant_available:
            try:
                response = self._qdrant.scroll(
                    collection_name=collection,
                    limit=limit,
                )
                points = response[0] if response else []
                return [
                    {
                        "memory_id": p.id,
                        "content": p.payload.get("content", ""),
                        "memory_subtype": p.payload.get("memory_subtype", ""),
                        "confidence": p.payload.get("confidence", 0),
                        "status": p.payload.get("status", "active"),
                        "created_at": p.payload.get("created_at", ""),
                        "metadata": p.payload.get("metadata", {}),
                    }
                    for p in points
                ]
            except Exception as e:
                logger.warning(
                    "[ECP_MEMORY] Qdrant list failed for %s: %s", collection, e
                )

        return [
            {
                "memory_id": v["memory_id"],
                "content": v["content"],
                "memory_subtype": v.get("memory_subtype", ""),
                "confidence": v.get("confidence", 0),
                "status": v.get("status", "active"),
                "created_at": v.get("created_at", ""),
                "metadata": v.get("metadata", {}),
            }
            for v in self._fallback_stores.get(collection, {}).values()
        ]

    def reset(self, collection: Optional[str] = None) -> bool:
        """Wipe a collection or all collections."""
        collections_to_reset = [collection] if collection else ECP_COLLECTIONS

        for coll in collections_to_reset:
            if coll not in ECP_COLLECTIONS:
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
                    logger.info("[ECP_MEMORY] Reset collection: %s", coll)
                except Exception as e:
                    logger.warning(
                        "[ECP_MEMORY] Qdrant reset failed for %s: %s", coll, e
                    )

            self._fallback_stores[coll] = {}

        return True

    def summary(self) -> Dict[str, Any]:
        """Return a summary of all ECP memory collections."""
        result = {}
        for coll in ECP_COLLECTIONS:
            memories = self.list_memories(coll)
            result[coll] = {
                "count": len(memories),
                "subtypes": list({m["memory_subtype"] for m in memories}),
            }
        return result

    def summarize_collection(
        self,
        collection: str,
        max_entries: int = 50,
        keep_recent: int = 10,
    ) -> Optional[str]:
        """Compress old memories preserving ECP shape.

        Summaries must preserve Truth continuity, Symbol continuity,
        and Contradiction continuity. Compression must not flatten
        contradictions into generic prose or symbolic material
        into generic explanation.
        """
        if not self._llm_bridge:
            logger.warning("[ECP_MEMORY] No LLM bridge — cannot summarize")
            return None

        memories = self.list_memories(collection)
        if len(memories) <= max_entries:
            return None

        memories.sort(key=lambda m: m.get("created_at", ""))

        cutoff = len(memories) - keep_recent
        old_memories = memories[:cutoff]
        if not old_memories:
            return None

        entries_text = "\n".join(
            f"- [{m.get('memory_subtype', 'unknown')}] {m['content']}"
            for m in old_memories
        )

        class_label = collection.replace("ecp_", "")
        prompt = (
            f"You are compressing {len(old_memories)} {class_label} memory entries.\n"
            f"Preserve all important facts, patterns, and semantic structure.\n"
            f"For truth: preserve constraints and durable realities.\n"
            f"For symbol: preserve dialect fragments and motifs exactly.\n"
            f"For contradiction: preserve structured tension (statement_a vs statement_b).\n"
            f"Output a single paragraph (max 500 words).\n\n"
            f"Entries to compress:\n{entries_text}"
        )

        try:
            summary_text = self._llm_bridge.generate(
                model=self._llm_bridge.default_model,
                system_prompt="You are an ECP memory compression assistant. Preserve class shape.",
                user_prompt=prompt,
                temp=0.3,
                max_tokens=1024,
            ).strip()

            if not summary_text:
                logger.warning("[ECP_MEMORY] Summarization returned empty result")
                return None

            summary_id = self.store(
                collection=collection,
                content=f"[SUMMARY of {len(old_memories)} entries] {summary_text}",
                subtype=old_memories[0].get("memory_subtype", SUBTYPES_BY_COLLECTION[collection][0]),
                confidence=0.9,
                metadata={
                    "is_summary": True,
                    "compressed_count": len(old_memories),
                },
            )

            deleted = 0
            for m in old_memories:
                if self.forget(m["memory_id"], collection):
                    deleted += 1

            logger.info(
                "[ECP_MEMORY] Summarized %s: compressed %d entries into 1 (deleted %d)",
                collection, len(old_memories), deleted,
            )
            return summary_id

        except Exception as e:
            logger.error("[ECP_MEMORY] Summarization failed for %s: %s", collection, e)
            return None

    def run_summarization_pass(self, max_entries: int = 50, keep_recent: int = 10):
        """Run summarization across all ECP collections that exceed thresholds."""
        for coll in ECP_COLLECTIONS:
            result = self.summarize_collection(coll, max_entries, keep_recent)
            if result:
                logger.info("[ECP_MEMORY] Collection %s summarized -> %s", coll, result)

    def health_check(self) -> Dict[str, Any]:
        """Check ECP memory system status."""
        return {
            "qdrant_available": self._qdrant_available,
            "backend": "qdrant" if self._qdrant_available else "in-memory-fallback",
            "collections": ECP_COLLECTIONS,
            "architecture": "ecp_native_v4",
        }
