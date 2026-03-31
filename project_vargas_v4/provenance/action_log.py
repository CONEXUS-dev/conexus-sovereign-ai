"""
VARGAS V4 Action Log — Tool Execution Provenance

Logs every tool execution attempt with full context: what was requested,
what tier it ran at, whether it succeeded, and what changed. This is
the primary audit trail for tool actions.

Reference: Master Blueprint Section 10 — action_log.py
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_LOG_DIR = ".audit_logs"


class ActionLog:
    """Provenance log for tool execution events.

    Every tool invocation — successful, failed, blocked, or pending —
    is recorded here with full context for post-hoc audit.

    Attributes:
        log_path: Path to the action log JSONL file.
        session_id: Current session identifier.
        entry_count: Number of entries logged this session.
    """

    def __init__(self, session_id: str, log_dir: str = DEFAULT_LOG_DIR):
        self.session_id = session_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / f"actions_{session_id[:8]}.jsonl"
        self.entry_count: int = 0
        logger.info("[ACTION_LOG] Initialized: %s", self.log_path)

    def log_execution(
        self,
        tool_name: str,
        status: str,
        trust_tier: int,
        parameters: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        request_id: str = "",
        approval_granted: bool = False,
        snapshot_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Log a tool execution event.

        Args:
            tool_name: Name of the tool executed.
            status: Execution status (SUCCESS, FAILED, BLOCKED, etc.).
            trust_tier: Trust tier of the action.
            parameters: Parameters passed to the tool.
            result: Execution result (if successful).
            error: Error message (if failed/blocked).
            request_id: Provenance request ID.
            approval_granted: Whether explicit approval was given.
            snapshot_id: Pre-action snapshot ID (if taken).

        Returns:
            The logged entry dict.
        """
        entry = {
            "event_type": "tool_execution",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "request_id": request_id,
            "tool_name": tool_name,
            "status": status,
            "trust_tier": trust_tier,
            "parameters": self._sanitize_params(parameters),
            "error": error,
            "approval_granted": approval_granted,
            "snapshot_id": snapshot_id,
        }

        # Include result summary (not full result to keep log size manageable)
        if result:
            entry["result_summary"] = {
                "success": result.get("success"),
                "keys": list(result.keys()),
            }

        self._write_entry(entry)
        self.entry_count += 1
        return entry

    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize parameters for logging (truncate large values)."""
        sanitized = {}
        for k, v in params.items():
            if isinstance(v, str) and len(v) > 500:
                sanitized[k] = v[:497] + "..."
            else:
                sanitized[k] = v
        return sanitized

    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """Write an entry to the JSONL log file."""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except Exception as e:
            logger.error("[ACTION_LOG] Write failed: %s", e)

    def get_recent(self, limit: int = 20) -> list:
        """Read the most recent log entries.

        Args:
            limit: Maximum entries to return.

        Returns:
            List of entry dicts (most recent last).
        """
        try:
            if not self.log_path.exists():
                return []
            lines = self.log_path.read_text(encoding="utf-8").strip().split("\n")
            entries = [json.loads(line) for line in lines[-limit:] if line.strip()]
            return entries
        except Exception as e:
            logger.warning("[ACTION_LOG] Read failed: %s", e)
            return []

    def summary(self) -> Dict[str, Any]:
        """Return action log status summary."""
        return {
            "log_path": str(self.log_path),
            "session_id": self.session_id[:8],
            "entries_this_session": self.entry_count,
        }
