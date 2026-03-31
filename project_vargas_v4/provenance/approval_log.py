"""
VARGAS V4 Approval Log — Permission Escalation Provenance

Logs every approval request, grant, denial, and timeout. When a Tier 3
action requires explicit user approval, the full request-response cycle
is recorded here for audit.

Reference: Master Blueprint Section 10 — approval_log.py
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_LOG_DIR = ".audit_logs"

# Approval states
APPROVAL_REQUESTED = "REQUESTED"
APPROVAL_GRANTED = "GRANTED"
APPROVAL_DENIED = "DENIED"
APPROVAL_TIMEOUT = "TIMEOUT"
APPROVAL_CANCELLED = "CANCELLED"


class ApprovalLog:
    """Provenance log for approval request events.

    Tracks the full lifecycle of permission escalation:
    request → grant/deny/timeout → execution result.

    Attributes:
        log_path: Path to the approval log JSONL file.
        session_id: Current session identifier.
        pending_count: Number of currently pending approvals.
    """

    def __init__(self, session_id: str, log_dir: str = DEFAULT_LOG_DIR):
        self.session_id = session_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.log_dir / f"approvals_{session_id[:8]}.jsonl"
        self.pending_count: int = 0
        logger.info("[APPROVAL_LOG] Initialized: %s", self.log_path)

    def log_request(
        self,
        tool_name: str,
        trust_tier: int,
        reason: str,
        request_id: str = "",
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Log an approval request.

        Args:
            tool_name: Tool requiring approval.
            trust_tier: Trust tier of the action.
            reason: Why approval is needed.
            request_id: Provenance request ID.
            parameters: Tool parameters (sanitized).

        Returns:
            The logged entry dict.
        """
        entry = {
            "event_type": "approval_request",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "request_id": request_id,
            "tool_name": tool_name,
            "trust_tier": trust_tier,
            "status": APPROVAL_REQUESTED,
            "reason": reason,
            "parameters": parameters or {},
        }

        self._write_entry(entry)
        self.pending_count += 1
        logger.info("[APPROVAL_LOG] Request: %s (tier=%d)", tool_name, trust_tier)
        return entry

    def log_response(
        self,
        request_id: str,
        status: str,
        responder: str = "user",
        notes: str = "",
    ) -> Dict[str, Any]:
        """Log an approval response (grant, deny, timeout).

        Args:
            request_id: Original request ID.
            status: GRANTED, DENIED, TIMEOUT, or CANCELLED.
            responder: Who responded.
            notes: Additional context.

        Returns:
            The logged entry dict.
        """
        entry = {
            "event_type": "approval_response",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "request_id": request_id,
            "status": status,
            "responder": responder,
            "notes": notes,
        }

        self._write_entry(entry)
        if self.pending_count > 0:
            self.pending_count -= 1

        logger.info("[APPROVAL_LOG] Response: %s for %s by %s", status, request_id[:8], responder)
        return entry

    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """Write an entry to the JSONL log file."""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except Exception as e:
            logger.error("[APPROVAL_LOG] Write failed: %s", e)

    def summary(self) -> Dict[str, Any]:
        """Return approval log status summary."""
        return {
            "log_path": str(self.log_path),
            "session_id": self.session_id[:8],
            "pending_approvals": self.pending_count,
        }
