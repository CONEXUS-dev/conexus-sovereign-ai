"""
SovereignNEXT — Collapse Operator
Scores open tensions using a 4-dimension rubric (evidence, consistency, goal_fit,
memory_support), then commits, defers, or paradox-holds each tension based on
margin thresholds.

Spec source: ARCHITECTURE.md §2, §6 Decision 5; Derek–Pylo transcript lines 310–334,
1357–1391.

Collapse is PURELY STATE-TRANSFORMING (Pylo constraint 1):
  - Does NOT create or expand claims
  - Does NOT re-score embeddings
  - Does NOT alter graph topology (no new tensions, no new claims)
  - ONLY: scores tensions, decides, mutates emoji vectors, updates statuses,
    adjusts claim confidences on commit, logs rubric scores

Paradox-hold is TERMINAL for Phase 4 (Pylo constraint 2):
  - Once a tension is paradox-held, it exits untouched — no revisits in the same run

Decision thresholds (ARCHITECTURE.md Decision 5):
  - margin > 0.25  → commit (collapsed_to_a or collapsed_to_b)
  - margin < 0.10  → paradox-hold
  - else            → defer (stays open)

Paradox veto (ARCHITECTURE.md §2 ParadoxHold):
  - If tension is linked to a paradox whose emoji vector has entropy > 0.7 AND
    pole_balance in [0.35, 0.65] → force paradox-hold regardless of margin

Rubric weights (ARCHITECTURE.md Decision 5):
  - evidence: 0.30
  - consistency: 0.25
  - goal_fit: 0.25
  - memory_support: 0.20
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.state.tension import Tension
from SovereignNEXT.state.paradox import Paradox
from SovereignNEXT.state.emoji_vector import EmojiVector
from SovereignNEXT.operators.emoji_mutator import mutate_collapse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rubric weights (frozen spec)
# ---------------------------------------------------------------------------

RUBRIC_WEIGHTS = {
    "evidence": 0.30,
    "consistency": 0.25,
    "goal_fit": 0.25,
    "memory_support": 0.20,
}

# Decision thresholds
COMMIT_MARGIN = 0.25
PARADOX_HOLD_MARGIN = 0.10

# Paradox veto thresholds
PARADOX_VETO_ENTROPY = 0.7
PARADOX_VETO_BALANCE_LOW = 0.35
PARADOX_VETO_BALANCE_HIGH = 0.65

# Confidence adjustment on commit
CONFIDENCE_BOOST = 0.15
CONFIDENCE_PENALTY = 0.10


# ---------------------------------------------------------------------------
# LLM interface protocol
# ---------------------------------------------------------------------------

class LLMInterface(Protocol):
    def generate(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temp: float = ...,
        max_tokens: int = ...,
        **kwargs: Any,
    ) -> str: ...


# ---------------------------------------------------------------------------
# Scoring prompt
# ---------------------------------------------------------------------------

SCORING_SYSTEM_PROMPT = (
    "You are a precise tension evaluator. Given a tension between two poles (Pole A and Pole B), "
    "score EACH pole on four dimensions. Return ONLY valid JSON with no explanation.\n\n"
    "Dimensions:\n"
    "- evidence: How much evidence supports this pole? (0.0 to 1.0)\n"
    "- consistency: How consistent is this pole with other accepted claims? (0.0 to 1.0)\n"
    "- goal_fit: How well does this pole fit the system's goals? (0.0 to 1.0)\n"
    "- memory_support: How much support does this pole have from prior knowledge? (0.0 to 1.0)\n\n"
    "Return format:\n"
    '{"pole_a": {"evidence": 0.0, "consistency": 0.0, "goal_fit": 0.0, "memory_support": 0.0}, '
    '"pole_b": {"evidence": 0.0, "consistency": 0.0, "goal_fit": 0.0, "memory_support": 0.0}}'
)

SCORING_USER_TEMPLATE = (
    'Pole A: "{pole_a}"\n'
    'Pole B: "{pole_b}"\n'
    'Relation type: {relation_type}\n\n'
    "Score both poles on all four dimensions. Return ONLY the JSON object."
)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class TensionAction:
    """Record of the action taken on a single tension."""
    tension_id: str
    decision: str          # "commit_to_a", "commit_to_b", "defer", "paradox_hold"
    margin: float
    scores_a: Dict[str, float]
    scores_b: Dict[str, float]
    weighted_a: float
    weighted_b: float
    paradox_vetoed: bool = False
    veto_source: Optional[str] = None
    emoji_mutated: bool = False
    claims_updated: List[str] = field(default_factory=list)


@dataclass
class CollapseResult:
    """Full result of a single Collapse pass."""
    total_open: int = 0
    committed: int = 0
    deferred: int = 0
    paradox_held: int = 0
    skipped: int = 0
    errors: int = 0
    actions: List[TensionAction] = field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        return {
            "total_open": self.total_open,
            "committed": self.committed,
            "deferred": self.deferred,
            "paradox_held": self.paradox_held,
            "skipped": self.skipped,
            "errors": self.errors,
        }


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def _parse_rubric_json(raw: str) -> Optional[Dict[str, Dict[str, float]]]:
    """Parse LLM rubric response into structured scores."""
    # Try to find JSON in the response
    raw = raw.strip()
    # Find first { and last }
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        data = json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return None

    # Normalize key names — LLM may return "Pole A"/"Pole B" or "pole_a"/"pole_b"
    normalized = {}
    for key, val in data.items():
        lower = key.lower().replace(" ", "_")
        if lower in ("pole_a", "a"):
            normalized["pole_a"] = val
        elif lower in ("pole_b", "b"):
            normalized["pole_b"] = val
    data = normalized

    if "pole_a" not in data or "pole_b" not in data:
        return None

    for pole_key in ("pole_a", "pole_b"):
        pole = data[pole_key]
        if not isinstance(pole, dict):
            return None
        for dim in RUBRIC_WEIGHTS:
            if dim not in pole:
                pole[dim] = 0.5  # default if missing
            else:
                try:
                    pole[dim] = float(pole[dim])
                    pole[dim] = max(0.0, min(1.0, pole[dim]))
                except (TypeError, ValueError):
                    pole[dim] = 0.5

    return data


def _weighted_score(scores: Dict[str, float]) -> float:
    """Compute weighted score from rubric dimensions."""
    total = 0.0
    for dim, weight in RUBRIC_WEIGHTS.items():
        total += scores.get(dim, 0.5) * weight
    return total


def score_tension(
    tension: Tension,
    state: SystemState,
    llm: LLMInterface,
    model: str,
) -> Optional[Dict[str, Any]]:
    """Score a tension's two poles using the 4-dimension rubric via LLM.

    Returns dict with keys: pole_a, pole_b, weighted_a, weighted_b, margin
    or None if scoring fails.
    """
    user_prompt = SCORING_USER_TEMPLATE.format(
        pole_a=tension.pole_a,
        pole_b=tension.pole_b,
        relation_type=tension.relation_type,
    )

    try:
        raw = llm.generate(
            model=model,
            system_prompt=SCORING_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temp=0.0,
            max_tokens=512,
        )
    except Exception as e:
        logger.warning("Collapse scoring failed for %s: %s", tension.id, e)
        return None

    parsed = _parse_rubric_json(raw)
    if parsed is None:
        logger.warning(
            "Collapse scoring parse failed for %s, raw response: %.200s",
            tension.id, raw,
        )
        return None

    wa = _weighted_score(parsed["pole_a"])
    wb = _weighted_score(parsed["pole_b"])
    margin = abs(wa - wb)

    return {
        "pole_a": parsed["pole_a"],
        "pole_b": parsed["pole_b"],
        "weighted_a": round(wa, 4),
        "weighted_b": round(wb, 4),
        "margin": round(margin, 4),
    }


def _find_linked_paradox(
    tension: Tension,
    state: SystemState,
) -> Optional[Paradox]:
    """Find a paradox linked to this tension via emoji_vector_id."""
    if tension.emoji_vector_id is None:
        return None
    for p in state.paradoxes:
        if p.emoji_vector_id == tension.emoji_vector_id:
            return p
    return None


def _find_linked_emoji_vector(
    tension: Tension,
    state: SystemState,
) -> Optional[EmojiVector]:
    """Find the emoji vector linked to this tension."""
    if tension.emoji_vector_id is None:
        return None
    for ev in state.emoji_fields:
        if ev.id == tension.emoji_vector_id:
            return ev
    return None


def _check_paradox_veto(
    tension: Tension,
    state: SystemState,
) -> Optional[str]:
    """Check if paradox veto applies by reading authority from paradox.constraints.

    Phase 5: Veto authority lives on the paradox object, not in global constants.
    Returns the paradox ID (veto_source) if vetoed, else None.
    """
    ev = _find_linked_emoji_vector(tension, state)
    if ev is None:
        return None

    paradox = _find_linked_paradox(tension, state)
    if paradox is None:
        return None

    # Phase 5: Read veto authority from paradox constraints
    constraints = paradox.constraints
    if not constraints.collapse_veto:
        return None

    entropy = ev.entropy
    balance = ev.pole_balance
    threshold = constraints.entropy_threshold
    bal_low, bal_high = constraints.balance_window

    vetoed = (
        entropy >= threshold
        and bal_low <= balance <= bal_high
    )

    if vetoed:
        logger.info(
            "Paradox veto on %s (paradox=%s, entropy=%.3f, balance=%.3f, "
            "threshold=%.2f, window=[%.2f,%.2f])",
            tension.id, paradox.id, entropy, balance,
            threshold, bal_low, bal_high,
        )
        return paradox.id

    return None


def decide_tension(
    tension: Tension,
    scores: Dict[str, Any],
    state: SystemState,
) -> TensionAction:
    """Apply margin logic and paradox veto to decide commit/defer/paradox-hold.

    Returns a TensionAction recording the decision.
    """
    margin = scores["margin"]
    wa = scores["weighted_a"]
    wb = scores["weighted_b"]

    action = TensionAction(
        tension_id=tension.id,
        decision="defer",  # default
        margin=margin,
        scores_a=scores["pole_a"],
        scores_b=scores["pole_b"],
        weighted_a=wa,
        weighted_b=wb,
    )

    # Check paradox veto first
    veto_source = _check_paradox_veto(tension, state)
    if veto_source is not None:
        action.decision = "paradox_hold"
        action.paradox_vetoed = True
        action.veto_source = veto_source
        return action

    # Margin-based decision
    if margin > COMMIT_MARGIN:
        if wa > wb:
            action.decision = "commit_to_a"
        else:
            action.decision = "commit_to_b"
    elif margin < PARADOX_HOLD_MARGIN:
        action.decision = "paradox_hold"
    else:
        action.decision = "defer"

    return action


def decide_tension_pure(
    tension: Tension,
    state: SystemState,
) -> TensionAction:
    """Phase 5 pure-state decision: margin from pole confidences, no LLM.

    Reads margin directly from the linked paradox's pole confidences:
        margin = |pole_a.confidence - pole_b.confidence|

    If no linked paradox exists, margin defaults to 0.0 (defer).
    Same threshold logic as decide_tension(), same veto gate.
    """
    paradox = _find_linked_paradox(tension, state)

    if paradox is not None:
        conf_a = paradox.pole_a.confidence
        conf_b = paradox.pole_b.confidence
        margin = round(abs(conf_a - conf_b), 4)
    else:
        conf_a = 0.5
        conf_b = 0.5
        margin = 0.0

    action = TensionAction(
        tension_id=tension.id,
        decision="defer",
        margin=margin,
        scores_a={"confidence": conf_a},
        scores_b={"confidence": conf_b},
        weighted_a=conf_a,
        weighted_b=conf_b,
    )

    # Check paradox veto first (reads from constraints)
    veto_source = _check_paradox_veto(tension, state)
    if veto_source is not None:
        action.decision = "paradox_hold"
        action.paradox_vetoed = True
        action.veto_source = veto_source
        return action

    # Margin-based decision from pole confidences
    if margin >= COMMIT_MARGIN:
        if conf_a > conf_b:
            action.decision = "commit_to_a"
        else:
            action.decision = "commit_to_b"
    elif margin <= PARADOX_HOLD_MARGIN:
        action.decision = "paradox_hold"
    else:
        action.decision = "defer"

    return action


def _apply_commit(
    tension: Tension,
    action: TensionAction,
    state: SystemState,
    seed: Optional[int] = None,
) -> None:
    """Apply a commit decision: update tension status, mutate emoji vector,
    adjust claim confidences."""
    # Update tension status
    if action.decision == "commit_to_a":
        tension.status = "collapsed_to_a"
    else:
        tension.status = "collapsed_to_b"

    # Record rubric scores on tension
    tension.record_rubric(
        scores={"pole_a": action.scores_a, "pole_b": action.scores_b},
        decision=action.decision,
    )
    tension.record_event(
        event=action.decision,
        operator="collapse",
        margin=action.margin,
        weighted_a=action.weighted_a,
        weighted_b=action.weighted_b,
    )

    # Mutate linked emoji vector toward stability
    ev = _find_linked_emoji_vector(tension, state)
    if ev is not None:
        mutate_collapse(ev, seed=seed)
        action.emoji_mutated = True

    # Update linked paradox status if it exists
    paradox = _find_linked_paradox(tension, state)
    if paradox is not None:
        paradox.status = action.decision
        paradox.record_event(
            event=action.decision,
            operator="collapse",
            entropy=ev.entropy if ev else None,
            margin=action.margin,
        )
        paradox.record_rubric(
            scores={"pole_a": action.scores_a, "pole_b": action.scores_b},
            decision=action.decision,
        )

    # Adjust claim confidences (frozen spec: increase winner, decrease loser)
    winner_claims = []
    loser_claims = []
    for cid in tension.source_claims:
        claim = state.get_claim(cid)
        if claim is None:
            continue
        # Determine if this claim aligns with pole_a or pole_b
        # Use text matching against tension poles
        if action.decision == "commit_to_a":
            if claim.text == tension.pole_a or claim.text.startswith(tension.pole_a[:30]):
                winner_claims.append(claim)
            elif claim.text == tension.pole_b or claim.text.startswith(tension.pole_b[:30]):
                loser_claims.append(claim)
        else:
            if claim.text == tension.pole_b or claim.text.startswith(tension.pole_b[:30]):
                winner_claims.append(claim)
            elif claim.text == tension.pole_a or claim.text.startswith(tension.pole_a[:30]):
                loser_claims.append(claim)

    for c in winner_claims:
        c.confidence = min(1.0, c.confidence + CONFIDENCE_BOOST)
        action.claims_updated.append(f"{c.id}:+{CONFIDENCE_BOOST}")
    for c in loser_claims:
        c.confidence = max(0.0, c.confidence - CONFIDENCE_PENALTY)
        action.claims_updated.append(f"{c.id}:-{CONFIDENCE_PENALTY}")

    logger.info(
        "Collapse commit: %s -> %s (margin=%.3f, wa=%.3f, wb=%.3f, claims=%s)",
        tension.id, action.decision, action.margin,
        action.weighted_a, action.weighted_b,
        action.claims_updated,
    )


def _apply_paradox_hold(
    tension: Tension,
    action: TensionAction,
    state: SystemState,
) -> None:
    """Apply a paradox-hold decision: update tension status, log rubric."""
    tension.status = "paradox_held"

    tension.record_rubric(
        scores={"pole_a": action.scores_a, "pole_b": action.scores_b},
        decision="paradox_hold",
    )
    tension.record_event(
        event="paradox_hold",
        operator="collapse",
        margin=action.margin,
        paradox_vetoed=action.paradox_vetoed,
    )

    # Update linked paradox if it exists
    paradox = _find_linked_paradox(tension, state)
    if paradox is not None:
        paradox.status = "paradox_held"
        # Phase 5: Lock veto on paradox-hold
        paradox.constraints.collapse_veto = True
        if not paradox.constraints.veto_reason:
            paradox.constraints.veto_reason = "paradox_held"
        paradox.record_event(
            event="paradox_hold",
            operator="collapse",
            margin=action.margin,
            paradox_vetoed=action.paradox_vetoed,
            veto_locked=True,
        )

    logger.info(
        "Collapse paradox-hold: %s (margin=%.3f, vetoed=%s, veto_locked=%s)",
        tension.id, action.margin, action.paradox_vetoed,
        paradox.id if paradox else "no_paradox",
    )


def _apply_defer(
    tension: Tension,
    action: TensionAction,
) -> None:
    """Apply a defer decision: leave status open, log rubric."""
    # Status stays "open"
    tension.record_rubric(
        scores={"pole_a": action.scores_a, "pole_b": action.scores_b},
        decision="defer",
    )
    tension.record_event(
        event="defer",
        operator="collapse",
        margin=action.margin,
    )

    logger.info(
        "Collapse defer: %s (margin=%.3f)",
        tension.id, action.margin,
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def collapse_once(
    state: SystemState,
    llm: LLMInterface,
    model: str,
    seed: Optional[int] = None,
) -> CollapseResult:
    """Execute a single Collapse pass over all open tensions in state.

    This is the main entry point. It:
      1. Iterates all tensions with status="open"
      2. Scores each via LLM rubric
      3. Decides commit / defer / paradox-hold
      4. Applies the decision (status updates, emoji mutation, confidence changes)
      5. Returns a CollapseResult with full action log

    Args:
        state: SystemState to transform (mutated in place).
        llm: LLM client with generate() method.
        model: Model name for scoring.
        seed: Optional RNG seed for emoji mutation reproducibility.

    Returns:
        CollapseResult with counts and per-tension action log.
    """
    result = CollapseResult()

    # Collect open tensions (snapshot the list to avoid mutation during iteration)
    open_tensions = [t for t in state.tensions if t.status == "open"]
    result.total_open = len(open_tensions)

    logger.info(
        "Collapse pass starting: %d open tensions to evaluate",
        result.total_open,
    )

    for tension in open_tensions:
        # Score
        scores = score_tension(tension, state, llm, model)
        if scores is None:
            result.errors += 1
            logger.warning("Skipping %s due to scoring error", tension.id)
            continue

        # Decide
        action = decide_tension(tension, scores, state)

        # Apply
        if action.decision in ("commit_to_a", "commit_to_b"):
            _apply_commit(tension, action, state, seed=seed)
            result.committed += 1
        elif action.decision == "paradox_hold":
            _apply_paradox_hold(tension, action, state)
            result.paradox_held += 1
        elif action.decision == "defer":
            _apply_defer(tension, action)
            result.deferred += 1

        result.actions.append(action)

    logger.info(
        "Collapse pass complete: %d committed, %d deferred, %d paradox-held, %d errors",
        result.committed, result.deferred, result.paradox_held, result.errors,
    )

    return result


# ---------------------------------------------------------------------------
# Phase 5: Pure state Collapse (no LLM)
# ---------------------------------------------------------------------------

def collapse_pure(
    state: SystemState,
    seed: Optional[int] = None,
) -> CollapseResult:
    """Phase 5 Collapse: pure state transformer, no LLM calls.

    Evaluates all open tensions using pole confidences from linked paradox
    objects. Veto authority is read from paradox.constraints. Margin is
    computed as |pole_a.confidence - pole_b.confidence|.

    This is the Phase 5 replacement for collapse_once(). The Phase 4
    collapse_once() is preserved unchanged for backward compatibility.

    Args:
        state: SystemState to transform (mutated in place).
        seed: Optional RNG seed for emoji mutation reproducibility.

    Returns:
        CollapseResult with counts and per-tension action log.
    """
    result = CollapseResult()

    open_tensions = [t for t in state.tensions if t.status == "open"]
    result.total_open = len(open_tensions)

    logger.info(
        "Collapse-pure pass starting: %d open tensions to evaluate",
        result.total_open,
    )

    for tension in open_tensions:
        # Decide using pole confidences (no LLM)
        action = decide_tension_pure(tension, state)

        # Apply
        if action.decision in ("commit_to_a", "commit_to_b"):
            _apply_commit(tension, action, state, seed=seed)
            result.committed += 1
        elif action.decision == "paradox_hold":
            _apply_paradox_hold(tension, action, state)
            result.paradox_held += 1
        elif action.decision == "defer":
            _apply_defer(tension, action)
            result.deferred += 1

        result.actions.append(action)

    logger.info(
        "Collapse-pure pass complete: %d committed, %d deferred, "
        "%d paradox-held, %d errors",
        result.committed, result.deferred, result.paradox_held, result.errors,
    )

    return result
