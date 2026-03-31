"""
VARGAS V4 Trust Model — Bounded Autonomy Enforcement

Enforces the trust tier system at runtime. Every action request passes
through the trust model, which validates the tier, checks boot mode
constraints, and determines whether the action can proceed.

Broad power requires visible restraint.
(Foundational Invariant §8)

Reference: Master Blueprint Section 9, Section 12.4 — trust_model.py
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Trust tier definitions
TIER_0_PASSIVE = 0
TIER_1_LOW_RISK = 1
TIER_2_SNAPSHOT = 2
TIER_3_APPROVAL = 3
TIER_4_FORBIDDEN = 4

TIER_NAMES = {
    0: "passive_observation",
    1: "low_risk_auto",
    2: "snapshot_required",
    3: "explicit_approval",
    4: "forbidden",
}


class TrustModel:
    """Enforces bounded autonomy through the trust tier system.

    The trust model answers one question: "Is this action allowed
    right now, given the current boot mode and tier constraints?"

    It does NOT execute actions. It gates them.

    Attributes:
        max_allowed_tier: Maximum tier allowed by current boot mode.
        contradiction_escalation: Whether contradiction is active (escalates tier).
    """

    def __init__(self, max_allowed_tier: int = 3):
        self.max_allowed_tier = max_allowed_tier
        self.contradiction_escalation: bool = False
        self._denied_count: int = 0
        self._approved_count: int = 0
        logger.info("[TRUST_MODEL] Initialized: max_tier=%d", max_allowed_tier)

    def check_action(
        self,
        tool_name: str,
        trust_tier: int,
        approval_granted: bool = False,
        snapshot_taken: bool = False,
        confidence: float = 1.0,
    ) -> Dict[str, Any]:
        """Check whether an action is allowed.

        Args:
            tool_name: Name of the tool.
            trust_tier: Required trust tier for this tool.
            approval_granted: Whether user has approved this action.
            snapshot_taken: Whether a pre-action snapshot exists.
            confidence: Action confidence (low confidence escalates tier).

        Returns:
            Dict with allowed, reason, and effective_tier.
        """
        effective_tier = trust_tier

        # Low confidence escalation (Blueprint: escalate one tier when confidence < 0.5)
        if confidence < 0.5 and effective_tier < TIER_4_FORBIDDEN:
            effective_tier += 1
            logger.info("[TRUST_MODEL] Tier escalated for low confidence: %d -> %d", trust_tier, effective_tier)

        # Contradiction escalation
        if self.contradiction_escalation and effective_tier < TIER_4_FORBIDDEN:
            effective_tier += 1
            logger.info("[TRUST_MODEL] Tier escalated for active contradiction: %d -> %d", trust_tier, effective_tier)

        # Forbidden — always blocked
        if effective_tier >= TIER_4_FORBIDDEN:
            self._denied_count += 1
            return {
                "allowed": False,
                "reason": f"Forbidden operation: {tool_name}",
                "effective_tier": TIER_4_FORBIDDEN,
                "original_tier": trust_tier,
            }

        # Boot mode constraint
        if effective_tier > self.max_allowed_tier:
            self._denied_count += 1
            return {
                "allowed": False,
                "reason": f"Tier {effective_tier} exceeds boot mode max {self.max_allowed_tier}",
                "effective_tier": effective_tier,
                "original_tier": trust_tier,
            }

        # Tier 3: requires approval
        if effective_tier >= TIER_3_APPROVAL and not approval_granted:
            return {
                "allowed": False,
                "reason": "Tier 3 action requires explicit user approval",
                "effective_tier": effective_tier,
                "original_tier": trust_tier,
                "pending_approval": True,
            }

        # Tier 2: requires snapshot
        if effective_tier >= TIER_2_SNAPSHOT and not snapshot_taken:
            return {
                "allowed": False,
                "reason": "Tier 2+ action requires pre-action snapshot",
                "effective_tier": effective_tier,
                "original_tier": trust_tier,
                "requires_snapshot": True,
            }

        # Allowed
        self._approved_count += 1
        return {
            "allowed": True,
            "reason": "Action permitted",
            "effective_tier": effective_tier,
            "original_tier": trust_tier,
        }

    def set_contradiction_escalation(self, active: bool) -> None:
        """Enable or disable contradiction-based tier escalation.

        Args:
            active: Whether a RESOLUTION_GATE is active.
        """
        self.contradiction_escalation = active
        if active:
            logger.info("[TRUST_MODEL] Contradiction escalation ACTIVE")

    def set_max_tier(self, max_tier: int) -> None:
        """Update the maximum allowed tier (e.g., on mode transition).

        Args:
            max_tier: New maximum allowed tier.
        """
        old = self.max_allowed_tier
        self.max_allowed_tier = max_tier
        if old != max_tier:
            logger.info("[TRUST_MODEL] Max tier changed: %d -> %d", old, max_tier)

    def get_tier_name(self, tier: int) -> str:
        """Get the human-readable name for a tier."""
        return TIER_NAMES.get(tier, f"unknown_tier_{tier}")

    def summary(self) -> Dict[str, Any]:
        """Return trust model status summary."""
        return {
            "max_allowed_tier": self.max_allowed_tier,
            "contradiction_escalation": self.contradiction_escalation,
            "approved_count": self._approved_count,
            "denied_count": self._denied_count,
        }
