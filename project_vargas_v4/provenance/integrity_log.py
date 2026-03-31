"""
VARGAS V4 Integrity Log — Constitutional Integrity Provenance

Logs boot integrity checks, constitution hash verifications, mode
transitions, and any constitutional violations detected at runtime.

The constitution must remain above the runtime.
(Foundational Invariant §9)

Reference: Master Blueprint Section 10 — integrity_log.py
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_LOG_DIR = ".audit_logs"


class IntegrityLog:
    """Provenance log for constitutional integrity events.

    Tracks:
    - Boot integrity check results
    - Constitution hash verifications
    - Mode transitions (NORMAL → DEGRADED → QUIESCENT)
    - Constitutional violation attempts

    Attributes:
        log_path: Path to the integrity log JSONL file.
        entry_count: Number of entries logged.
    """

    def __init__(self, log_dir: str = DEFAULT_LOG_DIR):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / "integrity.jsonl"
        self.entry_count: int = 0
        logger.info("[INTEGRITY_LOG] Initialized: %s", self.log_path)

    def log_boot_check(
        self,
        boot_mode: str,
        constitution_hash: str,
        checks: Dict[str, bool],
        session_id: str = "",
    ) -> Dict[str, Any]:
        """Log a boot integrity check result."""
        entry = {
            "event_type": "boot_integrity_check",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "boot_mode": boot_mode,
            "constitution_hash": constitution_hash[:16] + "..." if constitution_hash else "",
            "checks": checks,
            "all_passed": all(checks.values()),
        }
        self._write_entry(entry)
        logger.info("[INTEGRITY_LOG] Boot check: mode=%s passed=%s", boot_mode, entry["all_passed"])
        return entry

    def log_hash_verification(
        self,
        result: str,
        current_hash: str,
        canonical_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Log a constitution hash verification."""
        entry = {
            "event_type": "hash_verification",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result,
            "current_hash": current_hash[:16] + "...",
            "canonical_hash": (canonical_hash[:16] + "...") if canonical_hash else None,
            "match": result == "pass",
        }
        self._write_entry(entry)
        return entry

    def log_mode_transition(
        self,
        old_mode: str,
        new_mode: str,
        reason: str,
        session_id: str = "",
    ) -> Dict[str, Any]:
        """Log a runtime mode transition."""
        entry = {
            "event_type": "mode_transition",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "old_mode": old_mode,
            "new_mode": new_mode,
            "reason": reason,
        }
        self._write_entry(entry)
        logger.info("[INTEGRITY_LOG] Mode transition: %s -> %s (%s)", old_mode, new_mode, reason)
        return entry

    def log_violation_attempt(
        self,
        violation_type: str,
        details: str,
        blocked: bool = True,
        session_id: str = "",
    ) -> Dict[str, Any]:
        """Log a constitutional violation attempt.

        Args:
            violation_type: Type of violation (e.g., 'forbidden_operation', 'tier_bypass').
            details: Human-readable description.
            blocked: Whether the violation was blocked.
            session_id: Session ID.

        Returns:
            The logged entry dict.
        """
        entry = {
            "event_type": "violation_attempt",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "violation_type": violation_type,
            "details": details,
            "blocked": blocked,
        }
        self._write_entry(entry)
        logger.warning(
            "[INTEGRITY_LOG] Violation attempt: %s — blocked=%s — %s",
            violation_type, blocked, details,
        )
        return entry

    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """Write an entry to the JSONL log file."""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
            self.entry_count += 1
        except Exception as e:
            logger.error("[INTEGRITY_LOG] Write failed: %s", e)

    def get_recent(self, limit: int = 20) -> list:
        """Read the most recent integrity log entries."""
        try:
            if not self.log_path.exists():
                return []
            lines = self.log_path.read_text(encoding="utf-8").strip().split("\n")
            return [json.loads(line) for line in lines[-limit:] if line.strip()]
        except Exception as e:
            logger.warning("[INTEGRITY_LOG] Read failed: %s", e)
            return []

    def summary(self) -> Dict[str, Any]:
        """Return integrity log status summary."""
        return {
            "log_path": str(self.log_path),
            "entries_logged": self.entry_count,
        }
