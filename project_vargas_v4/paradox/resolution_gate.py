"""
VARGAS V4 Resolution Gate — Contradiction Action Gating

When a RESOLUTION_GATE is active, the system's behavior changes:
- Trust tiers escalate by one
- Challenge mode is enabled
- The system must surface the contradiction clearly
- Actions that could resolve or worsen the contradiction are gated

The resolution gate does NOT resolve contradictions. Resolution is
a human prerogative. The gate ensures the system behaves appropriately
while a contradiction is active.

Contradiction may slow action, but must not destroy responsibility.
(Foundational Invariant §6)

Reference: Master Blueprint Section 8, Section 12.4 — resolution_gate.py
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Gate states
GATE_OPEN = "OPEN"
GATE_ACTIVE = "ACTIVE"
GATE_RESOLVED = "RESOLVED"


class ResolutionGate:
    """Manages the RESOLUTION_GATE lifecycle.

    The gate activates when a contradiction exceeds severity threshold.
    While active, it modifies system behavior to ensure the contradiction
    is properly surfaced and not swept under.

    Lifecycle:
    1. OPEN: No active contradiction gate
    2. ACTIVE: Contradiction detected, gate constraints enforced
    3. RESOLVED: User has resolved the contradiction

    Attributes:
        state: Current gate state.
        active_contradiction: The contradiction that triggered the gate.
        severity: Severity of the active contradiction.
        activated_at: When the gate was activated.
    """

    def __init__(self):
        self.state: str = GATE_OPEN
        self.active_contradiction: Optional[Dict[str, Any]] = None
        self.severity: float = 0.0
        self.activated_at: Optional[str] = None
        self.resolved_at: Optional[str] = None
        self._gate_history: List[Dict[str, Any]] = []
        logger.info("[RESOLUTION_GATE] Initialized: state=OPEN")

    def activate(
        self,
        contradiction: Dict[str, Any],
        severity: float,
    ) -> Dict[str, Any]:
        """Activate the resolution gate for a contradiction.

        Args:
            contradiction: The contradiction data that triggered the gate.
            severity: Severity score of the contradiction.

        Returns:
            Gate activation report.
        """
        self.state = GATE_ACTIVE
        self.active_contradiction = contradiction
        self.severity = severity
        self.activated_at = datetime.now(timezone.utc).isoformat()
        self.resolved_at = None

        logger.info(
            "[RESOLUTION_GATE] ACTIVATED: severity=%.3f",
            severity,
        )

        return {
            "state": GATE_ACTIVE,
            "severity": round(severity, 4),
            "activated_at": self.activated_at,
            "constraints": self.get_constraints(),
        }

    def resolve(self, resolution: str = "", resolver: str = "user") -> Dict[str, Any]:
        """Resolve the active gate and return to OPEN state.

        Args:
            resolution: How the contradiction was resolved.
            resolver: Who resolved it (always the user).

        Returns:
            Gate resolution report.
        """
        prev_severity = self.severity
        prev_activated = self.activated_at

        # Record in history
        self._gate_history.append({
            "severity": prev_severity,
            "activated_at": prev_activated,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolution": resolution,
            "resolver": resolver,
        })

        self.state = GATE_RESOLVED
        self.resolved_at = datetime.now(timezone.utc).isoformat()
        self.active_contradiction = None
        self.severity = 0.0

        # Transition to OPEN after resolution
        self.state = GATE_OPEN

        logger.info(
            "[RESOLUTION_GATE] RESOLVED by %s: was severity=%.3f",
            resolver, prev_severity,
        )

        return {
            "state": GATE_OPEN,
            "previous_severity": round(prev_severity, 4),
            "resolution": resolution,
            "resolver": resolver,
            "resolved_at": self.resolved_at,
        }

    def is_active(self) -> bool:
        """Check if the resolution gate is currently active."""
        return self.state == GATE_ACTIVE

    def get_constraints(self) -> Dict[str, Any]:
        """Return the constraints imposed by an active gate.

        Returns:
            Dict of behavioral constraints while gate is active.
        """
        if not self.is_active():
            return {"active": False}

        return {
            "active": True,
            "trust_tier_escalation": 1,
            "challenge_mode_enabled": True,
            "must_surface_contradiction": True,
            "action_gating": "contradiction_aware",
            "severity": round(self.severity, 4),
        }

    def get_tier_escalation(self) -> int:
        """Return the trust tier escalation while gate is active.

        Returns:
            Number of tiers to escalate (0 if gate not active).
        """
        if self.is_active():
            return 1
        return 0

    def should_auto_embed(self) -> bool:
        """Check if the gate state warrants an auto-embed in Discord.

        When RESOLUTION_GATE is active, the forensic State Embed
        should be sent automatically (Phase 7.3 interface decoupling).

        Returns:
            True if the State Embed should be sent automatically.
        """
        return self.is_active()

    def summary(self) -> Dict[str, Any]:
        """Return resolution gate status summary."""
        return {
            "state": self.state,
            "severity": round(self.severity, 4),
            "activated_at": self.activated_at,
            "resolved_at": self.resolved_at,
            "history_count": len(self._gate_history),
            "constraints": self.get_constraints(),
        }
