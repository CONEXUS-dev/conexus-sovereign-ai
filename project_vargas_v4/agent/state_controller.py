"""
VARGAS V4 State Controller — Runtime State Management

Owns the live runtime state across the perception loop lifecycle.
Tracks the current E-Vector posture, contradiction state, boot mode,
active plan state, and session metadata in one coherent object.

The state controller does not make decisions — it holds the truth
about what the system's current state is.

Reference: Master Blueprint Section 12.4 — state_controller.py
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Runtime modes
MODE_NORMAL = "NORMAL"
MODE_DEGRADED = "DEGRADED"
MODE_QUIESCENT = "QUIESCENT"

# Contradiction states
WITNESS_MODE = "WITNESS_MODE"
RESOLUTION_GATE = "RESOLUTION_GATE"


class StateController:
    """Manages the coherent runtime state of VARGAS V4.

    The state controller aggregates:
    - Boot mode (NORMAL / DEGRADED / QUIESCENT)
    - E-Vector posture (entropy, challenge, initiative, directness)
    - Contradiction state (WITNESS_MODE / RESOLUTION_GATE)
    - Active plan status
    - Session metadata
    - Turn counter

    All other components read from this controller to understand
    the current system state. Only authorized components may write to it.

    Attributes:
        boot_mode: Current boot mode.
        e_vector: Current E-Vector posture snapshot.
        contradiction_state: Current contradiction state.
        session_id: Current session identifier.
        turn_count: Number of perception loop turns this session.
    """

    def __init__(self, session_id: str, boot_mode: str = MODE_NORMAL):
        self.session_id = session_id
        self.boot_mode = boot_mode
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.turn_count: int = 0

        # Posture state
        self.e_vector: Dict[str, float] = {
            "entropy": 0.5,
            "challenge_threshold": 0.7,
            "initiative_threshold": 0.5,
            "directness_index": 0.5,
        }

        # Contradiction state
        self.contradiction_state: str = WITNESS_MODE
        self.active_contradictions: int = 0
        self.last_severity: float = 0.0

        # Plan state
        self.has_active_plan: bool = False
        self.active_plan_id: Optional[str] = None
        self.active_plan_progress: str = ""

        # Last turn metadata
        self.last_intent: str = ""
        self.last_turn_at: Optional[str] = None

        logger.info(
            "[STATE_CTRL] Initialized: session=%s mode=%s",
            session_id[:8], boot_mode,
        )

    def begin_turn(self) -> int:
        """Signal the start of a new perception loop turn.

        Returns:
            The new turn number.
        """
        self.turn_count += 1
        self.last_turn_at = datetime.now(timezone.utc).isoformat()
        return self.turn_count

    def update_posture(self, e_vector: Dict[str, float]) -> None:
        """Update the E-Vector posture from the controller.

        Args:
            e_vector: New posture snapshot from EVectorController.
        """
        self.e_vector = dict(e_vector)

    def update_contradiction_state(
        self,
        state: str,
        active_count: int = 0,
        severity: float = 0.0,
    ) -> None:
        """Update contradiction evaluation state.

        Args:
            state: WITNESS_MODE or RESOLUTION_GATE.
            active_count: Number of active contradictions.
            severity: Maximum severity score.
        """
        self.contradiction_state = state
        self.active_contradictions = active_count
        self.last_severity = severity

    def update_plan_state(
        self,
        has_plan: bool,
        plan_id: Optional[str] = None,
        progress: str = "",
    ) -> None:
        """Update active plan tracking state.

        Args:
            has_plan: Whether a plan is active.
            plan_id: Active plan ID.
            progress: Progress string like "2/5".
        """
        self.has_active_plan = has_plan
        self.active_plan_id = plan_id
        self.active_plan_progress = progress

    def update_intent(self, intent: str) -> None:
        """Record the classified intent for the current turn.

        Args:
            intent: Intent category from IntentRouter.
        """
        self.last_intent = intent

    def set_boot_mode(self, mode: str) -> None:
        """Update the boot mode (used when transitioning states).

        Args:
            mode: NORMAL, DEGRADED, or QUIESCENT.
        """
        old_mode = self.boot_mode
        self.boot_mode = mode
        if old_mode != mode:
            logger.info("[STATE_CTRL] Boot mode changed: %s -> %s", old_mode, mode)

    def is_normal(self) -> bool:
        """Check if runtime is in normal mode."""
        return self.boot_mode == MODE_NORMAL

    def is_degraded(self) -> bool:
        """Check if runtime is in degraded mode."""
        return self.boot_mode == MODE_DEGRADED

    def is_quiescent(self) -> bool:
        """Check if runtime is in quiescent mode."""
        return self.boot_mode == MODE_QUIESCENT

    def get_max_allowed_tier(self) -> int:
        """Return the maximum allowed trust tier for the current mode."""
        if self.boot_mode == MODE_NORMAL:
            return 3
        elif self.boot_mode == MODE_DEGRADED:
            return 1
        return 0

    def snapshot(self) -> Dict[str, Any]:
        """Return a full state snapshot for provenance and diagnostics.

        Returns:
            Complete state dict.
        """
        return {
            "session_id": self.session_id,
            "boot_mode": self.boot_mode,
            "turn_count": self.turn_count,
            "started_at": self.started_at,
            "last_turn_at": self.last_turn_at,
            "e_vector": dict(self.e_vector),
            "contradiction_state": self.contradiction_state,
            "active_contradictions": self.active_contradictions,
            "last_severity": self.last_severity,
            "has_active_plan": self.has_active_plan,
            "active_plan_id": self.active_plan_id,
            "active_plan_progress": self.active_plan_progress,
            "last_intent": self.last_intent,
        }

    def summary(self) -> Dict[str, Any]:
        """Return compact state summary for status commands."""
        return {
            "mode": self.boot_mode,
            "turn": self.turn_count,
            "posture": self.e_vector,
            "contradiction": self.contradiction_state,
            "active_contradictions": self.active_contradictions,
            "plan_active": self.has_active_plan,
        }
