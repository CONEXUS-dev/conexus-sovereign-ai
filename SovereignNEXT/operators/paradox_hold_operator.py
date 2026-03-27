"""
SovereignNEXT — Paradox-Hold Operator (Phase 5)
A pure state-stabilizing operator that locks paradoxes into a productive
entropy/balance band and enforces veto persistence across time.

Paradox-Hold is neither Collapse nor Become. It exists to lock contradiction
into a productive band and prevent the system from "eventually resolving
everything" simply because time passes.

This operator:
  - Enforces entropy within a target band [0.70, 0.90]
  - Enforces pole balance within a window [0.35, 0.65]
  - Locks veto constraints on the paradox object
  - Mutates emoji vectors toward stability (superposition only, never collapse-aligned)
  - Never touches claims, margins, or resolution logic
  - Emits a structured audit record per paradox acted on

No LLM calls. No loop changes. Pure state transformation.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional

from SovereignNEXT.state.emoji_vector import EmojiVector
from SovereignNEXT.state.paradox import Paradox
from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.emoji_mutator import mutate_paradox_hold

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default stabilization targets
# ---------------------------------------------------------------------------

HOLD_ENTROPY_MIN = 0.70
HOLD_ENTROPY_MAX = 0.90
HOLD_BALANCE_LOW = 0.35
HOLD_BALANCE_HIGH = 0.65


# ---------------------------------------------------------------------------
# Audit dataclasses
# ---------------------------------------------------------------------------

@dataclass
class HoldAction:
    """Record of the action taken on a single paradox by Paradox-Hold."""
    paradox_id: str
    decision: str           # "stabilize", "nudge_entropy_up", "nudge_entropy_down", "correct_balance", "skip"
    entropy_before: float
    entropy_after: float
    balance_before: float
    balance_after: float
    veto_locked: bool = False
    status_before: str = ""
    status_after: str = ""
    skip_reason: Optional[str] = None


@dataclass
class HoldResult:
    """Full result of a single paradox_hold_pure() pass."""
    total_eligible: int = 0
    stabilized: int = 0
    nudged: int = 0
    balance_corrected: int = 0
    skipped: int = 0
    actions: List[HoldAction] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------

def _check_hold_eligible(
    paradox: Paradox,
    state: SystemState,
) -> Optional[EmojiVector]:
    """Check if a paradox is eligible for Paradox-Hold action.

    Paradox-Hold may act if:
      - Status is 'open' or 'paradox_held'
      - Has a linked emoji vector in state

    Must NOT reactivate collapsed or integrated paradoxes.

    Returns the linked EmojiVector if eligible, else None.
    """
    if paradox.status not in ("open", "paradox_held"):
        return None

    if paradox.emoji_vector_id is None:
        return None

    for ev in state.emoji_fields:
        if ev.id == paradox.emoji_vector_id:
            return ev

    return None


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def _evaluate_hold_action(
    ev: EmojiVector,
    entropy_min: float = HOLD_ENTROPY_MIN,
    entropy_max: float = HOLD_ENTROPY_MAX,
    balance_low: float = HOLD_BALANCE_LOW,
    balance_high: float = HOLD_BALANCE_HIGH,
) -> str:
    """Determine which hold action to take based on current metrics.

    Priority: balance correction > entropy nudging > stabilize.
    A paradox losing its dual character is more urgent than entropy drift.

    Returns one of: "correct_balance", "nudge_entropy_up", "nudge_entropy_down", "stabilize"
    """
    balance = ev.pole_balance

    # Balance correction takes priority
    if balance < balance_low or balance > balance_high:
        return "correct_balance"

    entropy = ev.entropy

    if entropy < entropy_min:
        return "nudge_entropy_up"

    if entropy > entropy_max:
        return "nudge_entropy_down"

    return "stabilize"


# ---------------------------------------------------------------------------
# Apply logic
# ---------------------------------------------------------------------------

def _apply_hold(
    paradox: Paradox,
    ev: EmojiVector,
    decision: str,
    entropy_min: float = HOLD_ENTROPY_MIN,
    entropy_max: float = HOLD_ENTROPY_MAX,
    balance_low: float = HOLD_BALANCE_LOW,
    balance_high: float = HOLD_BALANCE_HIGH,
    seed: Optional[int] = None,
) -> HoldAction:
    """Apply a Paradox-Hold action to a paradox and its emoji vector.

    Handles all four decision types:
      - stabilize: standard mutate_paradox_hold (superposition emojis)
      - nudge_entropy_up: mutate_paradox_hold (superposition emojis increase entropy)
      - nudge_entropy_down: append duplicates of the most common non-pole emoji
      - correct_balance: append the weaker pole's emoji once
    """
    entropy_before = ev.entropy
    balance_before = ev.pole_balance
    status_before = paradox.status

    if decision == "stabilize":
        mutate_paradox_hold(ev, seed=seed)

    elif decision == "nudge_entropy_up":
        # Superposition emojis increase diversity → higher entropy
        mutate_paradox_hold(ev, seed=seed)

    elif decision == "nudge_entropy_down":
        # Add duplicates of the most common non-pole emoji to reduce diversity ratio
        _reduce_entropy_by_duplication(ev, count=2)

    elif decision == "correct_balance":
        # Append the weaker pole's emoji to pull balance toward 0.5
        _correct_balance(ev)

    entropy_after = ev.entropy
    balance_after = ev.pole_balance

    # Set status to paradox_held
    paradox.status = "paradox_held"

    # Lock veto with current thresholds
    paradox.constraints.collapse_veto = True
    paradox.constraints.veto_reason = "paradox_held"
    paradox.constraints.entropy_threshold = entropy_min
    paradox.constraints.balance_window = (balance_low, balance_high)

    # Record history
    paradox.record_event(
        event="paradox_hold",
        operator="paradox_hold",
        entropy=entropy_after,
        entropy_before=entropy_before,
        balance_before=balance_before,
        balance_after=balance_after,
        decision=decision,
        veto_locked=True,
    )

    action = HoldAction(
        paradox_id=paradox.id,
        decision=decision,
        entropy_before=entropy_before,
        entropy_after=entropy_after,
        balance_before=balance_before,
        balance_after=balance_after,
        veto_locked=True,
        status_before=status_before,
        status_after="paradox_held",
    )

    logger.info(
        "Paradox-Hold %s: %s (entropy %.3f→%.3f, balance %.3f→%.3f, veto=locked)",
        decision, paradox.id,
        entropy_before, entropy_after,
        balance_before, balance_after,
    )

    return action


# ---------------------------------------------------------------------------
# Mutation helpers
# ---------------------------------------------------------------------------

def _reduce_entropy_by_duplication(ev: EmojiVector, count: int = 2) -> None:
    """Reduce entropy by appending duplicates of the most common non-pole emoji.

    Adding copies of an already-present emoji increases its frequency share,
    making the distribution less uniform and lowering normalized Shannon entropy.

    This respects the Phase 5 constraint that Paradox-Hold must not introduce
    collapse-aligned (stable) symbols. It also never removes emojis.

    If no non-pole emojis exist, appends a superposition emoji instead.
    """
    from collections import Counter
    pole_emojis = {ev.pole_a_emoji, ev.pole_b_emoji}
    non_pole = [e for e in ev.sequence if e not in pole_emojis]

    if non_pole:
        # Find the most common non-pole emoji and duplicate it
        most_common = Counter(non_pole).most_common(1)[0][0]
        ev.sequence.extend([most_common] * count)
    else:
        # No non-pole emojis — add a superposition emoji as a safe fallback
        from SovereignNEXT.state.emoji_vector import SUPERPOSITION_EMOJIS
        fallback = sorted(SUPERPOSITION_EMOJIS)[0]
        ev.sequence.extend([fallback] * count)


def _correct_balance(ev: EmojiVector) -> None:
    """Append the weaker pole's emoji to pull balance toward 0.5.

    pole_balance = count(pole_b) / (count(pole_a) + count(pole_b))
    If balance < 0.5, pole_b is underrepresented → append pole_b
    If balance > 0.5, pole_a is underrepresented → append pole_a
    If exactly 0.5, no correction needed (append superposition instead for safety)
    """
    balance = ev.pole_balance
    if balance < 0.5:
        ev.sequence.append(ev.pole_b_emoji)
    elif balance > 0.5:
        ev.sequence.append(ev.pole_a_emoji)
    # If exactly 0.5, no correction needed — balance is perfect


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def paradox_hold_pure(
    state: SystemState,
    entropy_min: float = HOLD_ENTROPY_MIN,
    entropy_max: float = HOLD_ENTROPY_MAX,
    balance_low: float = HOLD_BALANCE_LOW,
    balance_high: float = HOLD_BALANCE_HIGH,
    seed: Optional[int] = None,
) -> HoldResult:
    """Phase 5 Paradox-Hold: pure state stabilizer, no LLM calls.

    Iterates all paradox objects in state, checks eligibility, evaluates
    entropy and balance metrics, then applies stabilization, nudging, or
    balance correction. Locks veto constraints on every acted-on paradox.

    This is the Phase 5 standalone Paradox-Hold operator. The existing
    _apply_paradox_hold() in collapse_operator.py is preserved unchanged.

    Args:
        state: SystemState to transform (mutated in place).
        entropy_min: Lower bound of target entropy band.
        entropy_max: Upper bound of target entropy band.
        balance_low: Lower bound of balance window.
        balance_high: Upper bound of balance window.
        seed: Optional RNG seed for emoji mutation reproducibility.

    Returns:
        HoldResult with counts and per-paradox action log.
    """
    result = HoldResult()

    logger.info(
        "Paradox-Hold pass starting: %d paradoxes to evaluate "
        "(entropy=[%.2f,%.2f], balance=[%.2f,%.2f])",
        len(state.paradoxes), entropy_min, entropy_max,
        balance_low, balance_high,
    )

    for paradox in state.paradoxes:
        # Step 1: Eligibility
        ev = _check_hold_eligible(paradox, state)
        if ev is None:
            skip_reason = (
                f"status={paradox.status}"
                if paradox.status not in ("open", "paradox_held")
                else "no_emoji_vector"
            )
            action = HoldAction(
                paradox_id=paradox.id,
                decision="skip",
                entropy_before=0.0,
                entropy_after=0.0,
                balance_before=0.0,
                balance_after=0.0,
                skip_reason=skip_reason,
                status_before=paradox.status,
                status_after=paradox.status,
            )
            result.actions.append(action)
            result.skipped += 1
            continue

        result.total_eligible += 1

        # Step 2: Evaluate
        decision = _evaluate_hold_action(
            ev, entropy_min, entropy_max, balance_low, balance_high,
        )

        # Step 3: Apply
        action = _apply_hold(
            paradox, ev, decision,
            entropy_min=entropy_min,
            entropy_max=entropy_max,
            balance_low=balance_low,
            balance_high=balance_high,
            seed=seed,
        )
        result.actions.append(action)

        if decision == "stabilize":
            result.stabilized += 1
        elif decision in ("nudge_entropy_up", "nudge_entropy_down"):
            result.nudged += 1
        elif decision == "correct_balance":
            result.balance_corrected += 1

    logger.info(
        "Paradox-Hold pass complete: %d eligible, %d stabilized, %d nudged, "
        "%d balance-corrected, %d skipped",
        result.total_eligible, result.stabilized, result.nudged,
        result.balance_corrected, result.skipped,
    )

    return result
