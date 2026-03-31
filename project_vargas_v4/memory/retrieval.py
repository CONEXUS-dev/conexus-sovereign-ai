"""
VARGAS V4 Retrieval Module — Context Assembly Layer

Assembles context for the perception loop by querying all three ECP
stores and applying relevance filtering, deduplication, and priority
ordering. This is the bridge between raw memory retrieval and the
structured context that the perception loop consumes.

Reference: Master Blueprint Section 6, Section 12 — retrieval.py
"""

import logging
from typing import Any, Dict, List, Optional

from memory.memory_client import ECPMemoryClient

logger = logging.getLogger(__name__)

# Default retrieval limits per collection
DEFAULT_TRUTH_LIMIT = 10
DEFAULT_SYMBOL_LIMIT = 5
DEFAULT_CONTRADICTION_LIMIT = 5

# Minimum confidence to include in context
MIN_CONTEXT_CONFIDENCE = 0.3


class ContextRetriever:
    """Assembles structured context from ECP memory stores.

    The retriever is responsible for:
    1. Querying all three ECP stores with the input message
    2. Filtering by confidence and relevance
    3. Deduplicating overlapping results
    4. Ordering by retrieval priority
    5. Returning a structured context dict

    Attributes:
        client: The ECP memory client instance.
        truth_limit: Max truth entries to retrieve.
        symbol_limit: Max symbol entries to retrieve.
        contradiction_limit: Max contradiction entries to retrieve.
    """

    def __init__(
        self,
        client: ECPMemoryClient,
        truth_limit: int = DEFAULT_TRUTH_LIMIT,
        symbol_limit: int = DEFAULT_SYMBOL_LIMIT,
        contradiction_limit: int = DEFAULT_CONTRADICTION_LIMIT,
    ):
        self.client = client
        self.truth_limit = truth_limit
        self.symbol_limit = symbol_limit
        self.contradiction_limit = contradiction_limit

        logger.info(
            "[RETRIEVAL] Initialized: truth=%d symbol=%d contradiction=%d",
            truth_limit, symbol_limit, contradiction_limit,
        )

    def retrieve_context(
        self,
        query: str,
        filter_subtype: Optional[str] = None,
        min_confidence: float = MIN_CONTEXT_CONFIDENCE,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve structured context from all ECP stores.

        Args:
            query: The input message or search query.
            filter_subtype: Optional subtype filter applied to all collections.
            min_confidence: Minimum confidence threshold for inclusion.

        Returns:
            Dict with 'truth', 'symbol', and 'contradiction' lists,
            each containing memory dicts sorted by retrieval priority.
        """
        context = {"truth": [], "symbol": [], "contradiction": []}

        # Retrieve from each collection
        truth_raw = self._retrieve_collection(
            query, "ecp_truth", self.truth_limit, filter_subtype
        )
        symbol_raw = self._retrieve_collection(
            query, "ecp_symbol", self.symbol_limit, filter_subtype
        )
        contradiction_raw = self._retrieve_collection(
            query, "ecp_contradiction", self.contradiction_limit, filter_subtype
        )

        # Filter by confidence
        context["truth"] = self._filter_by_confidence(truth_raw, min_confidence)
        context["symbol"] = self._filter_by_confidence(symbol_raw, min_confidence)
        context["contradiction"] = self._filter_by_confidence(contradiction_raw, min_confidence)

        # Deduplicate within each collection
        context["truth"] = self._deduplicate(context["truth"])
        context["symbol"] = self._deduplicate(context["symbol"])
        context["contradiction"] = self._deduplicate(context["contradiction"])

        # Sort by retrieval priority
        for key in context:
            context[key] = sorted(
                context[key],
                key=lambda m: float(m.get("retrieval_priority", m.get("confidence", 0.0))),
                reverse=True,
            )

        total = sum(len(v) for v in context.values())
        logger.info(
            "[RETRIEVAL] Context assembled: %d truth, %d symbol, %d contradiction (%d total)",
            len(context["truth"]),
            len(context["symbol"]),
            len(context["contradiction"]),
            total,
        )

        return context

    def _retrieve_collection(
        self,
        query: str,
        collection: str,
        limit: int,
        filter_subtype: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve from a single ECP collection.

        Args:
            query: Search query.
            collection: Collection name.
            limit: Maximum results.
            filter_subtype: Optional subtype filter.

        Returns:
            List of memory dicts.
        """
        try:
            results = self.client.retrieve(
                query=query,
                collection=collection,
                top_k=limit,
                filter_subtype=filter_subtype,
                filter_status="active",
            )
            return results[:limit]
        except Exception as e:
            logger.warning(
                "[RETRIEVAL] Failed to retrieve from %s: %s", collection, e
            )
            return []

    @staticmethod
    def _filter_by_confidence(
        memories: List[Dict[str, Any]], min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Filter memories by minimum confidence threshold."""
        return [
            m for m in memories
            if float(m.get("confidence", 0.0)) >= min_confidence
        ]

    @staticmethod
    def _deduplicate(memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate memories by content hash or ID."""
        seen_ids = set()
        seen_hashes = set()
        unique = []

        for m in memories:
            mid = m.get("memory_id", "")
            source_hash = m.get("source_hash", "")

            if mid in seen_ids:
                continue
            if source_hash and source_hash in seen_hashes:
                continue

            seen_ids.add(mid)
            if source_hash:
                seen_hashes.add(source_hash)
            unique.append(m)

        return unique

    def retrieve_identity_context(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve core identity context — who am I, who is the user.

        This is called at the start of every perception loop turn
        to ensure the system knows its own identity and constraints.

        Returns:
            Context dict focused on identity-relevant memories.
        """
        return self.retrieve_context(
            query="VARGAS identity Derek Angell system principles constraints",
            min_confidence=0.7,
        )

    def retrieve_contradiction_context(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve active contradictions relevant to a query.

        Args:
            query: The input to match against.
            limit: Maximum contradictions to return.

        Returns:
            List of active contradiction memory dicts.
        """
        return self._retrieve_collection(
            query, "ecp_contradiction", limit
        )

    def summary(self) -> Dict[str, Any]:
        """Return retriever configuration summary."""
        return {
            "truth_limit": self.truth_limit,
            "symbol_limit": self.symbol_limit,
            "contradiction_limit": self.contradiction_limit,
            "min_confidence": MIN_CONTEXT_CONFIDENCE,
            "qdrant_available": self.client._qdrant_available,
        }
