"""
VARGAS V4 Symbol Store — ECP-Native Semantic Memory

The Symbol Store is the native dialect layer of VARGAS. It formalizes emoji
vectors, archetypes, recurring metaphors, symbolic motifs, project-specific
shorthand, mirror language, named conceptual structures, and any symbolic
compression layer that matters to how VARGAS thinks and speaks.

This store is not "just aesthetics." It is the bridge between abstract truth,
contradiction metabolism, and the actual language register of the system.

Without a Symbol Store, VARGAS risks becoming generic, over-literal, or
dependent on re-teaching its symbolic dialect every session.
"""

import logging
from typing import Any, Dict, List, Optional

from memory.memory_client import ECPMemoryClient, SYMBOL_SUBTYPES

logger = logging.getLogger(__name__)

COLLECTION = "ecp_symbol"


class SymbolStore:
    """ECP Symbol Store for VARGAS V4.

    Stores the system's native symbolic dialect: emoji vectors, archetypes,
    recurring metaphors, motifs, mirror tier language, dialect fragments,
    symbolic operators, and tone anchors.

    The rule is: if symbolic material changes how the runtime interprets
    or expresses, it belongs here.

    What belongs here:
    - Emoji vectors and their semantic payloads
    - Recurring metaphors
    - Named symbolic structures
    - Mirror tier language
    - Archetypal mappings
    - Project-specific compressed dialect
    - Stable symbolic reference objects that influence interpretation or tone

    What does NOT belong here:
    - Generic stylistic fluff
    - One-time poetic flourishes
    - Metaphor for metaphor's sake
    - Vague emotional residue
    - Temporary mood language
    - Symbolic language with no operational relevance
    """

    def __init__(self, client: ECPMemoryClient):
        self._client = client

    def store(
        self,
        content: str,
        subtype: str,
        confidence: float = 0.8,
        symbol_family: str = "general",
        dialect_weight: float = 0.5,
        tone_effect: str = "neutral",
        source_request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_scope: str = "vargas_v4",
        challenge_weight: float = 0.0,
    ) -> Optional[str]:
        """Store a symbolic memory.

        Args:
            content: The symbolic content (emoji vector payload, motif, etc).
            subtype: One of SYMBOL_SUBTYPES.
            confidence: Write confidence (0.0-1.0).
            symbol_family: Grouping key for related symbols
                (e.g. 'ecp_triad', 'sovereign', 'paradox').
            dialect_weight: How strongly this symbol shapes dialect (0.0-1.0).
            tone_effect: Effect on tone ('neutral', 'grounding', 'elevating',
                'sharpening', 'softening').
            source_request_id: Provenance link.
            session_id: Current session.
            project_scope: Scope boundary.
            challenge_weight: Challenge posture influence.

        Returns:
            memory_id on success, None on failure.
        """
        if subtype not in SYMBOL_SUBTYPES:
            logger.warning("[SYMBOL_STORE] Invalid subtype: %s", subtype)
            return None

        metadata = {
            "symbol_family": symbol_family,
            "dialect_weight": dialect_weight,
            "tone_effect": tone_effect,
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
                "[SYMBOL_STORE] Stored: subtype=%s family=%s id=%s",
                subtype, symbol_family, memory_id,
            )
        return memory_id

    def store_emoji_vector(
        self,
        emoji_payload: str,
        semantic_meaning: str,
        symbol_family: str = "emoji",
        dialect_weight: float = 0.7,
        confidence: float = 0.85,
        source_request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Optional[str]:
        """Convenience method for storing emoji vector entries.

        Args:
            emoji_payload: The emoji character(s) or sequence.
            semantic_meaning: What this emoji vector compresses semantically.
            symbol_family: Grouping key.
            dialect_weight: Dialect influence weight.
            confidence: Write confidence.
            source_request_id: Provenance link.
            session_id: Current session.

        Returns:
            memory_id on success, None on failure.
        """
        content = f"[EMOJI_VECTOR] {emoji_payload} :: {semantic_meaning}"
        return self.store(
            content=content,
            subtype="emoji_vector",
            confidence=confidence,
            symbol_family=symbol_family,
            dialect_weight=dialect_weight,
            tone_effect="neutral",
            source_request_id=source_request_id,
            session_id=session_id,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_subtype: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve symbols relevant to a query."""
        return self._client.retrieve(
            query=query,
            collection=COLLECTION,
            top_k=top_k,
            filter_subtype=filter_subtype,
            filter_status="active",
        )

    def retrieve_by_family(
        self,
        query: str,
        symbol_family: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve symbols filtered by family.

        Since Qdrant payload filtering is not implemented at the client level,
        this does a post-filter on retrieved results.
        """
        results = self.retrieve(query=query, top_k=top_k * 3)
        return [
            r for r in results
            if r.get("metadata", {}).get("symbol_family") == symbol_family
        ][:top_k]

    def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all symbols in the store."""
        return self._client.list_memories(COLLECTION, limit=limit)

    def forget(self, memory_id: str) -> bool:
        """Remove a symbol. User has ultimate authority."""
        return self._client.forget(memory_id, COLLECTION)

    def correct(self, memory_id: str, new_content: str, reason: str = "user_correction") -> Optional[str]:
        """Supersede a symbol with corrected content."""
        return self._client.correct(memory_id, new_content, COLLECTION, reason)

    def count(self) -> int:
        """Return the number of symbols stored."""
        return len(self.list_all())

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the symbol store."""
        memories = self.list_all()
        subtypes = {}
        families = {}
        for m in memories:
            st = m.get("memory_subtype", "unknown")
            subtypes[st] = subtypes.get(st, 0) + 1
            fam = m.get("metadata", {}).get("symbol_family", "unknown")
            families[fam] = families.get(fam, 0) + 1
        return {
            "collection": COLLECTION,
            "count": len(memories),
            "subtypes": subtypes,
            "families": families,
        }
