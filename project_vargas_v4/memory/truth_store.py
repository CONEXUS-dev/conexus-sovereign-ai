"""
VARGAS V4 Truth Store — ECP-Native Semantic Memory

The Truth Store is the durable semantic layer that holds what is actually real
in the collaboration. It replaces the older "Identity Store" as the primary
anchor layer.

The question for Truth Store is not "Is this about identity?"
The question is: "Is this something that the system must treat as real
until explicitly corrected?"

Truth Store must remain disciplined. If it gets polluted, the entire system
becomes unstable.
"""

import logging
from typing import Any, Dict, List, Optional

from memory.memory_client import ECPMemoryClient, TRUTH_SUBTYPES

logger = logging.getLogger(__name__)

COLLECTION = "ecp_truth"

# Truth-specific confidence floor: only high-confidence writes
TRUTH_CONFIDENCE_FLOOR = 0.8


class TruthStore:
    """ECP Truth Store for VARGAS V4.

    Stores durable realities, constraints, stated goals, declared operating
    principles, architectural truths, and stable collaboration boundaries.

    Write policy: Truth writes require high confidence. A new memory should
    only be written if it is explicitly stated as durable, foundational to
    the system or project, repeatedly evidenced, or so structurally important
    that forgetting it would cause real drift.

    What belongs here:
    - Long-term project definitions
    - Stable system boundaries
    - Durable user constraints
    - Declared project goals
    - Hard no-go zones
    - Stable technical assumptions
    - Persistent facts about the working relationship

    What does NOT belong here:
    - Session moods
    - Local frustration
    - One-off mistakes
    - Symbolic motifs (use SymbolStore)
    - Emergent contradictions (use ContradictionStore)
    - Temporary working state
    """

    def __init__(self, client: ECPMemoryClient):
        self._client = client

    def store(
        self,
        content: str,
        subtype: str,
        confidence: float = 0.9,
        truth_scope: str = "global",
        durability: str = "permanent",
        authority_level: str = "declared",
        source_request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_scope: str = "vargas_v4",
        challenge_weight: float = 0.0,
    ) -> Optional[str]:
        """Store a truth with enforced confidence floor.

        Args:
            content: The durable reality or constraint to store.
            subtype: One of TRUTH_SUBTYPES.
            confidence: Write confidence (enforced >= 0.8).
            truth_scope: 'global', 'project', or 'session'.
            durability: 'permanent', 'long_term', or 'until_corrected'.
            authority_level: 'declared', 'inferred', or 'observed'.
            source_request_id: Provenance link.
            session_id: Current session.
            project_scope: Scope boundary.
            challenge_weight: Challenge posture influence.

        Returns:
            memory_id on success, None on failure.
        """
        if subtype not in TRUTH_SUBTYPES:
            logger.warning("[TRUTH_STORE] Invalid subtype: %s", subtype)
            return None

        if confidence < TRUTH_CONFIDENCE_FLOOR:
            logger.warning(
                "[TRUTH_STORE] Confidence %.2f below floor %.2f — rejecting write",
                confidence, TRUTH_CONFIDENCE_FLOOR,
            )
            return None

        metadata = {
            "truth_scope": truth_scope,
            "durability": durability,
            "authority_level": authority_level,
        }

        memory_id = self._client.store(
            collection=COLLECTION,
            content=content,
            subtype=subtype,
            confidence=confidence,
            source_request_id=source_request_id,
            session_id=session_id,
            project_scope=project_scope,
            challenge_weight=challenge_weight,
            metadata=metadata,
        )

        if memory_id:
            logger.info(
                "[TRUTH_STORE] Stored: subtype=%s scope=%s durability=%s id=%s",
                subtype, truth_scope, durability, memory_id,
            )
        return memory_id

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_subtype: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve truths relevant to a query."""
        return self._client.retrieve(
            query=query,
            collection=COLLECTION,
            top_k=top_k,
            filter_subtype=filter_subtype,
            filter_status="active",
        )

    def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all truths in the store."""
        return self._client.list_memories(COLLECTION, limit=limit)

    def forget(self, memory_id: str) -> bool:
        """Remove a truth. User has ultimate authority."""
        return self._client.forget(memory_id, COLLECTION)

    def correct(self, memory_id: str, new_content: str, reason: str = "user_correction") -> Optional[str]:
        """Supersede a truth with corrected content."""
        return self._client.correct(memory_id, new_content, COLLECTION, reason)

    def count(self) -> int:
        """Return the number of truths stored."""
        return len(self.list_all())

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the truth store."""
        memories = self.list_all()
        subtypes = {}
        for m in memories:
            st = m.get("memory_subtype", "unknown")
            subtypes[st] = subtypes.get(st, 0) + 1
        return {
            "collection": COLLECTION,
            "count": len(memories),
            "subtypes": subtypes,
        }
