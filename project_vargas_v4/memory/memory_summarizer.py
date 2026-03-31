"""
VARGAS V4 Memory Summarizer — Compression Without Loss

Summarizes and compresses memory stores for context window efficiency.
When the number of stored memories grows beyond what can be injected
into a single perception loop turn, the summarizer provides compressed
representations that preserve signal.

The summarizer does NOT delete memories. It creates compressed views
for context injection while the full memories remain in the store.

Reference: Master Blueprint Section 6, Section 12 — memory_summarizer.py
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Maximum characters for a summary block
MAX_SUMMARY_LENGTH = 2000

# Maximum memories to include in a detailed summary
MAX_DETAILED_ENTRIES = 20


class MemorySummarizer:
    """Compresses ECP memory stores into context-efficient summaries.

    The summarizer operates on retrieval results from ECPMemoryClient,
    not directly on the stores. It takes a list of memory dicts and
    produces a compressed text or structured summary.

    Three summary modes:
    1. Statistical: counts, subtypes, confidence ranges
    2. Compressed: key facts extracted and deduped
    3. Detailed: full entries up to a limit

    Attributes:
        max_length: Maximum character length for text summaries.
        max_entries: Maximum entries for detailed mode.
    """

    def __init__(
        self,
        max_length: int = MAX_SUMMARY_LENGTH,
        max_entries: int = MAX_DETAILED_ENTRIES,
    ):
        self.max_length = max_length
        self.max_entries = max_entries
        logger.info("[MEMORY_SUMMARIZER] Initialized: max_length=%d", max_length)

    def summarize_collection(
        self,
        memories: List[Dict[str, Any]],
        collection_name: str,
        mode: str = "compressed",
    ) -> Dict[str, Any]:
        """Summarize a collection of memories.

        Args:
            memories: List of memory dicts from retrieval.
            collection_name: Name of the source collection.
            mode: 'statistical', 'compressed', or 'detailed'.

        Returns:
            Summary dict with text and metadata.
        """
        if mode == "statistical":
            return self._statistical_summary(memories, collection_name)
        elif mode == "detailed":
            return self._detailed_summary(memories, collection_name)
        else:
            return self._compressed_summary(memories, collection_name)

    def _statistical_summary(
        self, memories: List[Dict[str, Any]], collection_name: str
    ) -> Dict[str, Any]:
        """Generate a statistical overview of the collection."""
        if not memories:
            return {
                "collection": collection_name,
                "mode": "statistical",
                "count": 0,
                "text": f"{collection_name}: empty",
            }

        subtypes: Dict[str, int] = {}
        confidences: List[float] = []
        statuses: Dict[str, int] = {}

        for m in memories:
            st = m.get("memory_subtype", "unknown")
            subtypes[st] = subtypes.get(st, 0) + 1

            conf = m.get("confidence", 0.0)
            confidences.append(float(conf))

            status = m.get("status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        text = (
            f"{collection_name}: {len(memories)} entries, "
            f"avg confidence {avg_conf:.2f}, "
            f"subtypes: {subtypes}, "
            f"statuses: {statuses}"
        )

        return {
            "collection": collection_name,
            "mode": "statistical",
            "count": len(memories),
            "avg_confidence": round(avg_conf, 4),
            "subtypes": subtypes,
            "statuses": statuses,
            "text": text,
        }

    def _compressed_summary(
        self, memories: List[Dict[str, Any]], collection_name: str
    ) -> Dict[str, Any]:
        """Generate a compressed text summary extracting key facts."""
        if not memories:
            return {
                "collection": collection_name,
                "mode": "compressed",
                "count": 0,
                "text": f"{collection_name}: no entries",
            }

        # Sort by confidence descending
        sorted_memories = sorted(
            memories,
            key=lambda m: float(m.get("confidence", 0.0)),
            reverse=True,
        )

        fragments: List[str] = []
        total_length = 0

        for m in sorted_memories:
            content = m.get("content", "")
            subtype = m.get("memory_subtype", "")
            conf = float(m.get("confidence", 0.0))

            # For contradiction payloads, extract the core tension
            if collection_name == "ecp_contradiction":
                content = self._extract_contradiction_core(content)

            # Truncate individual entries
            if len(content) > 200:
                content = content[:197] + "..."

            fragment = f"[{subtype} c={conf:.1f}] {content}"

            if total_length + len(fragment) > self.max_length:
                break

            fragments.append(fragment)
            total_length += len(fragment) + 2

        text = "\n".join(fragments)

        return {
            "collection": collection_name,
            "mode": "compressed",
            "count": len(memories),
            "included": len(fragments),
            "text": text,
        }

    def _detailed_summary(
        self, memories: List[Dict[str, Any]], collection_name: str
    ) -> Dict[str, Any]:
        """Generate a detailed summary with full entries up to limit."""
        entries = []
        for m in memories[: self.max_entries]:
            entries.append({
                "memory_id": m.get("memory_id", ""),
                "subtype": m.get("memory_subtype", ""),
                "content": m.get("content", "")[:500],
                "confidence": float(m.get("confidence", 0.0)),
                "status": m.get("status", ""),
                "created_at": m.get("created_at", ""),
            })

        return {
            "collection": collection_name,
            "mode": "detailed",
            "count": len(memories),
            "included": len(entries),
            "entries": entries,
        }

    @staticmethod
    def _extract_contradiction_core(content: str) -> str:
        """Extract the core tension from a contradiction payload."""
        try:
            payload = json.loads(content) if isinstance(content, str) else content
            a = payload.get("statement_a", "")
            b = payload.get("statement_b", "")
            sev = payload.get("severity_score", 0.0)
            return f"{a} vs. {b} (severity={sev:.2f})"
        except (json.JSONDecodeError, TypeError, AttributeError):
            return content[:200] if content else ""

    def summarize_context(
        self,
        context: Dict[str, List[Dict[str, Any]]],
        mode: str = "compressed",
    ) -> Dict[str, Any]:
        """Summarize the full context dict from _retrieve_context.

        Args:
            context: Dict with 'truth', 'symbol', 'contradiction' lists.
            mode: Summary mode.

        Returns:
            Combined summary dict.
        """
        summaries = {}
        for collection_key, memories in context.items():
            collection_name = f"ecp_{collection_key}" if not collection_key.startswith("ecp_") else collection_key
            summaries[collection_key] = self.summarize_collection(
                memories, collection_name, mode
            )

        total_count = sum(s.get("count", 0) for s in summaries.values())

        return {
            "mode": mode,
            "total_memories": total_count,
            "collections": summaries,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
