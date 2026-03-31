"""
VARGAS V4 E-Vector Controller — System Posture Manager

The E-Vector Controller manages the 4-dimensional posture of the sovereign
runtime. It is the bridge between the Paradox Engine (which computes deltas)
and the Provenance Logger (which records snapshots).

Reference: VARGAS V4 Master Blueprint, Section 5 — E-Vector Baseline
    Dimensions (from sovereign_state.json e_vector_baseline):
        - entropy: 0.5 (complexity tolerance)
        - challenge_threshold: 0.7 (intervention readiness)
        - initiative_threshold: 0.5 (action timing caution)
        - directness_index: 0.5 (communication plainness)

Hard Constraint: All dimensions are clamped to [0.0, 1.0]. No dimension
can ever drift outside this range regardless of the number or severity
of contradiction events.

The Controller does not decide what deltas to apply. That is the Paradox
Engine's job. The Controller only:
    1. Holds the current posture state
    2. Applies deltas with floor/ceiling enforcement
    3. Provides snapshots for the Provenance Logger
    4. Resets to baseline on session boundaries
"""

import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Dimension keys — must match sovereign_state.json e_vector_baseline
ENTROPY = "entropy"
CHALLENGE = "challenge_threshold"
INITIATIVE = "initiative_threshold"
DIRECTNESS = "directness_index"

DIMENSIONS = [ENTROPY, CHALLENGE, INITIATIVE, DIRECTNESS]

# Hard floors and ceilings
FLOOR = 0.0
CEILING = 1.0

# Default baseline from sovereign_state.json
DEFAULT_BASELINE: Dict[str, float] = {
    ENTROPY: 0.5,
    CHALLENGE: 0.7,
    INITIATIVE: 0.5,
    DIRECTNESS: 0.5,
}


class EVectorController:
    """Manages the 4-dimensional E-Vector posture of the VARGAS V4 runtime.

    The E-Vector represents the system's current operational posture:
        - entropy: How much complexity/uncertainty the system tolerates.
          Higher = more comfortable with ambiguity.
        - challenge_threshold: How readily the system challenges the user.
          Lower = more willing to surface contradictions.
        - initiative_threshold: How cautious the system is before acting.
          Higher = more careful, slower to initiate.
        - directness_index: How plainly the system communicates.
          Higher = more direct, less hedging.

    The Controller enforces hard floors (0.0) and ceilings (1.0) on all
    dimensions. No amount of accumulated deltas can push a dimension
    outside this range.

    Attributes:
        baseline: The starting posture loaded from sovereign_state.json.
        current: The live posture after all applied deltas.
        delta_history: Ordered list of all deltas applied this session.
    """

    def __init__(self, config_path: str = "config/sovereign_state.json"):
        """Initialize from sovereign state configuration.

        Loads the e_vector_baseline from sovereign_state.json. If the file
        is missing or malformed, falls back to blueprint defaults.

        Args:
            config_path: Path to sovereign_state.json.
        """
        self.baseline: Dict[str, float] = dict(DEFAULT_BASELINE)
        self.current: Dict[str, float] = dict(DEFAULT_BASELINE)
        self.delta_history: List[Dict[str, Any]] = []
        self._session_start: str = datetime.now(timezone.utc).isoformat()
        self._delta_count: int = 0

        self._load_baseline(config_path)

        logger.info(
            "[E_VECTOR_CTRL] Initialized: %s",
            {dim: round(v, 4) for dim, v in self.current.items()},
        )

    def _load_baseline(self, config_path: str) -> None:
        """Load baseline dimensions from sovereign state.

        Args:
            config_path: Path to sovereign_state.json.
        """
        path = Path(config_path)
        if not path.exists():
            logger.warning(
                "[E_VECTOR_CTRL] Config not found at %s — using defaults",
                config_path,
            )
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)

            e_vector_config = config.get("e_vector_baseline", {})

            for dim in DIMENSIONS:
                if dim in e_vector_config:
                    value = float(e_vector_config[dim])
                    value = max(FLOOR, min(CEILING, value))
                    self.baseline[dim] = value
                    self.current[dim] = value

            logger.info(
                "[E_VECTOR_CTRL] Baseline loaded from %s", config_path
            )
        except Exception as e:
            logger.warning(
                "[E_VECTOR_CTRL] Failed to load baseline: %s — using defaults", e
            )

    @staticmethod
    def _clamp(value: float) -> float:
        """Enforce hard floor (0.0) and ceiling (1.0).

        Args:
            value: Raw dimension value.

        Returns:
            Clamped value in [0.0, 1.0].
        """
        return max(FLOOR, min(CEILING, value))

    def apply_delta(
        self,
        delta: Dict[str, float],
        source: str = "paradox_engine",
    ) -> Dict[str, Any]:
        """Apply an E-Vector delta to the current posture.

        Accepts the output of ParadoxEngine.calculate_e_vector_delta().
        Each dimension is adjusted by the corresponding delta value, then
        clamped to [0.0, 1.0].

        Unknown dimension keys in the delta are silently ignored.

        Args:
            delta: Dict mapping dimension names to float adjustments.
                Expected keys: entropy, challenge_threshold,
                initiative_threshold, directness_index.
            source: Origin of the delta for audit trail.

        Returns:
            Dict containing:
                - applied: True if any dimension was changed
                - old_posture: Dict of posture before delta
                - new_posture: Dict of posture after delta
                - delta_applied: Dict of actual changes (after clamping)
                - source: Origin string
        """
        old_posture = dict(self.current)
        actual_changes: Dict[str, float] = {}

        for dim in DIMENSIONS:
            if dim not in delta:
                continue

            old_value = self.current[dim]
            raw_new = old_value + delta[dim]
            clamped_new = self._clamp(raw_new)
            self.current[dim] = clamped_new

            actual_change = clamped_new - old_value
            if abs(actual_change) > 1e-10:
                actual_changes[dim] = round(actual_change, 6)

        applied = len(actual_changes) > 0

        # Record in history
        history_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "requested_delta": {k: round(v, 6) for k, v in delta.items() if k in DIMENSIONS},
            "actual_delta": actual_changes,
            "old_posture": {k: round(v, 6) for k, v in old_posture.items()},
            "new_posture": {k: round(v, 6) for k, v in self.current.items()},
            "clamped": any(
                abs((old_posture[d] + delta.get(d, 0.0)) - self.current[d]) > 1e-10
                for d in DIMENSIONS
                if d in delta
            ),
        }
        self.delta_history.append(history_entry)
        self._delta_count += 1

        if applied:
            logger.info(
                "[E_VECTOR_CTRL] Delta applied from %s: %s",
                source, actual_changes,
            )
        else:
            logger.debug(
                "[E_VECTOR_CTRL] Delta from %s produced no change", source
            )

        return {
            "applied": applied,
            "old_posture": old_posture,
            "new_posture": dict(self.current),
            "delta_applied": actual_changes,
            "source": source,
        }

    def get_current_posture(self) -> Dict[str, float]:
        """Return the current E-Vector posture for the Provenance Logger.

        This is the method that the ProvenanceLogger calls to populate
        the e_vector_snapshot field of each provenance entry.

        Returns:
            Dict with the 4 E-Vector dimensions rounded to 6 decimal places.
        """
        return {dim: round(self.current[dim], 6) for dim in DIMENSIONS}

    def get_baseline(self) -> Dict[str, float]:
        """Return the baseline E-Vector posture.

        Returns:
            Dict with the 4 baseline dimension values.
        """
        return dict(self.baseline)

    def reset_to_baseline(self, reason: str = "session_boundary") -> Dict[str, Any]:
        """Reset all dimensions to baseline values.

        Called at session boundaries to prevent drift accumulation
        across sessions. The reset is recorded in delta history.

        Args:
            reason: Why the reset occurred (for audit trail).

        Returns:
            Dict containing old_posture, new_posture, and reason.
        """
        old_posture = dict(self.current)
        self.current = dict(self.baseline)

        reset_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "reset_to_baseline",
            "reason": reason,
            "old_posture": {k: round(v, 6) for k, v in old_posture.items()},
            "new_posture": {k: round(v, 6) for k, v in self.current.items()},
        }
        self.delta_history.append(reset_entry)

        logger.info("[E_VECTOR_CTRL] Reset to baseline: %s", reason)

        return {
            "old_posture": old_posture,
            "new_posture": dict(self.current),
            "reason": reason,
        }

    def get_distance_from_baseline(self) -> float:
        """Calculate Euclidean distance from baseline for drift monitoring.

        A distance of 0.0 means the posture is at baseline. Higher values
        indicate accumulated drift from contradiction events.

        Returns:
            Euclidean distance as a float.
        """
        sum_sq: float = 0.0
        for dim in DIMENSIONS:
            diff = self.current[dim] - self.baseline[dim]
            sum_sq += diff * diff
        return round(math.sqrt(sum_sq), 6)

    def get_dimension_drifts(self) -> Dict[str, float]:
        """Return per-dimension drift from baseline.

        Positive = above baseline, negative = below baseline.

        Returns:
            Dict mapping dimension names to signed drift values.
        """
        return {
            dim: round(self.current[dim] - self.baseline[dim], 6)
            for dim in DIMENSIONS
        }

    def is_at_floor_or_ceiling(self) -> Dict[str, Optional[str]]:
        """Check if any dimension is pinned at a hard boundary.

        Returns:
            Dict mapping dimension names to 'floor', 'ceiling', or None.
        """
        result: Dict[str, Optional[str]] = {}
        for dim in DIMENSIONS:
            val = self.current[dim]
            if val <= FLOOR + 1e-10:
                result[dim] = "floor"
            elif val >= CEILING - 1e-10:
                result[dim] = "ceiling"
            else:
                result[dim] = None
        return result

    def get_delta_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return recent delta history entries.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            List of delta history dicts, most recent last.
        """
        return self.delta_history[-limit:] if self.delta_history else []

    def get_delta_count(self) -> int:
        """Return total number of deltas applied this session."""
        return self._delta_count

    def summary(self) -> Dict[str, Any]:
        """Return comprehensive controller state for diagnostics.

        Returns:
            Dict with current posture, baseline, drift, history count,
            and boundary status.
        """
        return {
            "current_posture": self.get_current_posture(),
            "baseline": self.get_baseline(),
            "distance_from_baseline": self.get_distance_from_baseline(),
            "dimension_drifts": self.get_dimension_drifts(),
            "boundary_status": self.is_at_floor_or_ceiling(),
            "delta_count": self._delta_count,
            "session_start": self._session_start,
        }
