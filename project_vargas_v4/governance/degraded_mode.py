"""
VARGAS V4 Degraded Mode — Reduced Capability Runtime

When the constitution is incomplete but not tampered, the runtime enters
degraded mode. This limits available trust tiers and disables high-risk
operations while keeping the system useful for basic tasks.

Reference: Master Blueprint Section 10, Foundational Invariant §8
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Maximum trust tier in degraded mode
DEGRADED_MAX_TIER = 1

# Capabilities explicitly disabled in degraded mode
DISABLED_CAPABILITIES = [
    "execute_shell",
    "delete_file",
    "bulk_memory_operation",
    "system_configuration_change",
    "write_file",
    "modify_file",
]


class DegradedMode:
    """Enforces degraded mode constraints on the runtime.

    In degraded mode:
    - Only Tier 0 and Tier 1 actions are permitted
    - All mutation operations are blocked
    - Memory reads continue to work
    - The system must announce its degraded state
    - The system must explain what is wrong

    Attributes:
        active: Whether degraded mode is currently active.
        reason: Why degraded mode was entered.
        missing_components: List of missing constitutional components.
    """

    def __init__(self):
        self.active: bool = False
        self.reason: str = ""
        self.missing_components: List[str] = []
        self._blocked_actions: List[str] = []

    def activate(self, reason: str, missing: List[str] = None) -> Dict[str, Any]:
        """Activate degraded mode.

        Args:
            reason: Human-readable reason for entering degraded mode.
            missing: List of missing constitutional components.

        Returns:
            Activation report.
        """
        self.active = True
        self.reason = reason
        self.missing_components = missing or []
        self._blocked_actions = list(DISABLED_CAPABILITIES)

        logger.warning(
            "[DEGRADED_MODE] Activated: %s (missing: %s)",
            reason,
            ", ".join(self.missing_components) if self.missing_components else "none specified",
        )

        return {
            "mode": "DEGRADED",
            "active": True,
            "reason": reason,
            "missing_components": self.missing_components,
            "max_trust_tier": DEGRADED_MAX_TIER,
            "disabled_capabilities": DISABLED_CAPABILITIES,
        }

    def deactivate(self) -> Dict[str, Any]:
        """Deactivate degraded mode after constitution is restored.

        Returns:
            Deactivation report.
        """
        self.active = False
        prev_reason = self.reason
        self.reason = ""
        self.missing_components = []
        self._blocked_actions = []

        logger.info("[DEGRADED_MODE] Deactivated (was: %s)", prev_reason)

        return {
            "mode": "NORMAL",
            "active": False,
            "previous_reason": prev_reason,
        }

    def is_action_allowed(self, action_name: str, trust_tier: int) -> bool:
        """Check if an action is allowed in degraded mode.

        Args:
            action_name: Name of the action to check.
            trust_tier: Trust tier of the action.

        Returns:
            True if the action is allowed.
        """
        if not self.active:
            return True

        if trust_tier > DEGRADED_MAX_TIER:
            return False

        if action_name in self._blocked_actions:
            return False

        return True

    def get_announcement(self) -> str:
        """Generate the degraded mode announcement text.

        The system must announce its degraded state clearly.
        No hiding limitations. (Foundational Invariant §8)

        Returns:
            Announcement text for the user.
        """
        if not self.active:
            return ""

        lines = [
            "System is operating in DEGRADED mode.",
            f"Reason: {self.reason}",
            f"Maximum trust tier: {DEGRADED_MAX_TIER}",
            "High-risk operations are disabled until the constitution is restored.",
        ]

        if self.missing_components:
            lines.append(f"Missing: {', '.join(self.missing_components)}")

        return " ".join(lines)

    def summary(self) -> Dict[str, Any]:
        """Return degraded mode status summary."""
        return {
            "active": self.active,
            "reason": self.reason,
            "max_trust_tier": DEGRADED_MAX_TIER if self.active else None,
            "missing_components": self.missing_components,
            "disabled_capabilities": DISABLED_CAPABILITIES if self.active else [],
        }
