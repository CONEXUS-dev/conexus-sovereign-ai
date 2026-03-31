"""
VARGAS V4 Memory Log — Memory Mutation Provenance

Logs every memory operation: store, correct, forget, and resolve.
Memory is corrigible, but every change must be traceable.

Nothing remembered may become unquestionable merely because it has
been stored. (Foundational Invariant §7)

Reference: Master Blueprint Section 10 — memory_log.py
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_LOG_DIR = ".audit_logs"


class MemoryLog:
    """Provenance log for memory operations.

    Tracks:
    - Stores: new memories created
    - Corrections: memories superseded with updated content
    - Forgets: memories removed by user command
    - Resolves: contradictions marked as resolved

    Attributes:
        log_path: Path to the memory log JSONL file.
        session_id: Current session identifier.
        entry_count: Number of entries this session.
    """

    def __init__(self, session_id: str, log_dir: str = DEFAULT_LOG_DIR):
        self.session_id = session_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / f"memory_{session_id[:8]}.jsonl"
        self.entry_count: int = 0
        logger.info("[MEMORY_LOG] Initialized: %s", self.log_path)

    def log_store(
        self,
        collection: str,
        memory_id: str,
        subtype: str,
        confidence: float,
        content_preview: str = "",
        source_hash: str = "",
        request_id: str = "",
    ) -> Dict[str, Any]:
        """Log a memory store operation."""
        entry = {
            "event_type": "memory_store",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "request_id": request_id,
            "collection": collection,
            "memory_id": memory_id,
            "subtype": subtype,
            "confidence": confidence,
            "content_preview": content_preview[:200],
            "source_hash": source_hash[:16] + "..." if source_hash else "",
        }
        self._write_entry(entry)
        return entry

    def log_correction(
        self,
        collection: str,
        old_memory_id: str,
        new_memory_id: str,
        reason: str,
        request_id: str = "",
    ) -> Dict[str, Any]:
        """Log a memory correction (supersede) operation."""
        entry = {
            "event_type": "memory_correction",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "request_id": request_id,
            "collection": collection,
            "old_memory_id": old_memory_id,
            "new_memory_id": new_memory_id,
            "reason": reason,
        }
        self._write_entry(entry)
        logger.info("[MEMORY_LOG] Correction: %s -> %s", old_memory_id[:8], new_memory_id[:8])
        return entry

    def log_forget(
        self,
        collection: str,
        memory_id: str,
        reason: str,
        request_id: str = "",
    ) -> Dict[str, Any]:
        """Log a memory forget (delete) operation."""
        entry = {
            "event_type": "memory_forget",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "request_id": request_id,
            "collection": collection,
            "memory_id": memory_id,
            "reason": reason,
        }
        self._write_entry(entry)
        logger.info("[MEMORY_LOG] Forget: %s in %s", memory_id[:8], collection)
        return entry

    def log_resolve(
        self,
        memory_id: str,
        resolution: str,
        request_id: str = "",
    ) -> Dict[str, Any]:
        """Log a contradiction resolution."""
        entry = {
            "event_type": "contradiction_resolve",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "request_id": request_id,
            "memory_id": memory_id,
            "resolution": resolution,
        }
        self._write_entry(entry)
        logger.info("[MEMORY_LOG] Resolve: %s", memory_id[:8])
        return entry

    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """Write an entry to the JSONL log file."""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
            self.entry_count += 1
        except Exception as e:
            logger.error("[MEMORY_LOG] Write failed: %s", e)

    def summary(self) -> Dict[str, Any]:
        """Return memory log status summary."""
        return {
            "log_path": str(self.log_path),
            "session_id": self.session_id[:8],
            "entries_this_session": self.entry_count,
        }
