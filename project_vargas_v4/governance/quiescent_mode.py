"""
VARGAS V4 Quiescent Mode — Constitutional Lockdown

When critical constitutional files are missing, tampered with, or the
integrity check fails fatally, the runtime enters quiescent mode.
This is the most restrictive state: read-only, no action, no mutation.

The system holds still until the operator fixes the problem.

Reference: Master Blueprint Section 10, Foundational Invariant §9
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Only Tier 0 (passive observation) is allowed
QUIESCENT_MAX_TIER = 0


class QuiescentMode:
    """Enforces quiescent mode — the deepest lockdown state.

    In quiescent mode:
    - Only Tier 0 (read-only) actions are permitted
    - No memory writes, no file mutations, no shell execution
    - The system must clearly announce its locked state
    - The system must explain exactly what is wrong
    - The system must wait for operator intervention

    This is not failure. This is the system protecting itself
    from operating on a foundation it cannot trust.

    Attributes:
        active: Whether quiescent mode is currently active.
        reason: Why quiescent mode was entered.
        triggered_at: Timestamp of activation.
        integrity_failures: Specific integrity check failures.
    """

    def __init__(self):
        self.active: bool = False
        self.reason: str = ""
        self.triggered_at: str = ""
        self.integrity_failures: List[str] = []

    def activate(self, reason: str, failures: List[str] = None) -> Dict[str, Any]:
        """Activate quiescent mode.

        Args:
            reason: Why the system is locking down.
            failures: Specific integrity check failures.

        Returns:
            Activation report.
        """
        self.active = True
        self.reason = reason
        self.triggered_at = datetime.now(timezone.utc).isoformat()
        self.integrity_failures = failures or []

        logger.error(
            "[QUIESCENT_MODE] ACTIVATED: %s — system locked to read-only",
            reason,
        )

        return {
            "mode": "QUIESCENT",
            "active": True,
            "reason": reason,
            "triggered_at": self.triggered_at,
            "max_trust_tier": QUIESCENT_MAX_TIER,
            "integrity_failures": self.integrity_failures,
            "allowed_actions": ["read_file", "list_directory", "search_memory", "get_system_status"],
        }

    def deactivate(self, operator: str = "Derek Angell") -> Dict[str, Any]:
        """Deactivate quiescent mode after operator intervention.

        Only the operator can restore normal operation after a
        quiescent lockdown.

        Args:
            operator: Name of the operator authorizing restoration.

        Returns:
            Deactivation report.
        """
        prev_reason = self.reason
        prev_triggered = self.triggered_at

        self.active = False
        self.reason = ""
        self.triggered_at = ""
        self.integrity_failures = []

        logger.info(
            "[QUIESCENT_MODE] Deactivated by %s (was: %s)",
            operator, prev_reason,
        )

        return {
            "mode": "NORMAL",
            "active": False,
            "previous_reason": prev_reason,
            "previous_triggered_at": prev_triggered,
            "restored_by": operator,
            "restored_at": datetime.now(timezone.utc).isoformat(),
        }

    def is_action_allowed(self, trust_tier: int) -> bool:
        """Check if an action's trust tier is allowed in quiescent mode.

        Args:
            trust_tier: Trust tier of the action.

        Returns:
            True only if tier is 0 (passive observation).
        """
        if not self.active:
            return True
        return trust_tier <= QUIESCENT_MAX_TIER

    def get_announcement(self) -> str:
        """Generate the quiescent mode announcement.

        Returns:
            Announcement text explaining the lockdown.
        """
        if not self.active:
            return ""

        lines = [
            "SYSTEM IS IN QUIESCENT MODE — read-only lockdown active.",
            f"Reason: {self.reason}",
            "No actions beyond passive observation are permitted.",
            "Operator intervention required to restore normal operation.",
        ]

        if self.integrity_failures:
            lines.append(f"Integrity failures: {'; '.join(self.integrity_failures)}")

        return " ".join(lines)

    def summary(self) -> Dict[str, Any]:
        """Return quiescent mode status summary."""
        return {
            "active": self.active,
            "reason": self.reason,
            "triggered_at": self.triggered_at,
            "max_trust_tier": QUIESCENT_MAX_TIER if self.active else None,
            "integrity_failures": self.integrity_failures,
        }
