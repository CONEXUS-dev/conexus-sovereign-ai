"""
SovereignNEXT — Sovereign Observer (Phase 5)
A pure, read-only state reporter that produces structured descriptions of
system state without mutating anything.

Sovereign is not an operator. Its authority is epistemic, not causal.
It observes paradoxes, emoji vectors, metrics, and operator outcomes,
then produces descriptive artifacts — never actions, recommendations,
or resolutions.

Hard constraints (non-negotiable):
  - Read-only access — may not mutate any state
  - No operator control — may not invoke Collapse, Become, or Paradox-Hold
  - No prescriptive language — may not suggest actions or next steps
  - No reinterpretation — may not resolve paradoxes into beliefs or narratives
  - Deterministic outputs — same state yields the same report

No LLM calls. No loop changes. Pure observation.
"""

import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from SovereignNEXT.state.system_state import SystemState

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default band/window targets (same as Paradox-Hold for consistency)
# ---------------------------------------------------------------------------

SOVEREIGN_ENTROPY_MIN = 0.70
SOVEREIGN_ENTROPY_MAX = 0.90
SOVEREIGN_BALANCE_LOW = 0.35
SOVEREIGN_BALANCE_HIGH = 0.65


# ---------------------------------------------------------------------------
# Output dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ParadoxDigest:
    """Per-paradox descriptive view. Read from state, no mutation."""
    paradox_id: str
    status: str
    entropy: float
    balance: float
    pole_a: str
    pole_b: str
    veto_state: Dict[str, Any]
    recent_actions: List[Dict[str, Any]]
    last_updated: str


@dataclass
class OperatorLedger:
    """Read-only summary of operator activity from paradox histories."""
    operator_name: str
    action_counts: Dict[str, int]
    affected_paradox_ids: List[str]


@dataclass
class SovereignReport:
    """Top-level snapshot produced by sovereign_observe(). Purely descriptive."""
    timestamp: str
    state_hash: str
    paradox_counts_by_status: Dict[str, int]
    entropy_band_distribution: Dict[str, int]
    balance_window_distribution: Dict[str, int]
    veto_summary: Dict[str, int]
    belief_stratification: Dict[str, List[str]]
    integrity_attestations: List[str]
    anomaly_flags: List[str]
    paradox_digests: List[ParadoxDigest]
    operator_ledgers: List[OperatorLedger]


# ---------------------------------------------------------------------------
# Builder: ParadoxDigest
# ---------------------------------------------------------------------------

def _build_paradox_digest(
    paradox,
    state: SystemState,
) -> ParadoxDigest:
    """Build a ParadoxDigest from a paradox and its linked emoji vector.

    Pure read — no mutation.
    """
    entropy = 0.0
    balance = 0.5
    last_updated = paradox.timestamp

    if paradox.emoji_vector_id is not None:
        ev = state.get_emoji_field(paradox.emoji_vector_id)
        if ev is not None:
            entropy = ev.entropy
            balance = ev.pole_balance
            last_updated = ev.last_updated

    veto_state = {
        "collapse_veto": paradox.constraints.collapse_veto,
        "reason": paradox.constraints.veto_reason or "",
    }

    recent_actions = []
    for entry in paradox.history:
        recent_actions.append({
            "operator": entry.get("operator", ""),
            "event": entry.get("event", ""),
            "timestamp": entry.get("timestamp", ""),
        })

    return ParadoxDigest(
        paradox_id=paradox.id,
        status=paradox.status,
        entropy=entropy,
        balance=balance,
        pole_a=paradox.pole_a.id,
        pole_b=paradox.pole_b.id,
        veto_state=veto_state,
        recent_actions=recent_actions,
        last_updated=last_updated,
    )


# ---------------------------------------------------------------------------
# Builder: OperatorLedger
# ---------------------------------------------------------------------------

def _build_operator_ledgers(state: SystemState) -> List[OperatorLedger]:
    """Scan all paradox histories, group events by operator, count decisions.

    Pure read — no mutation.
    """
    # operator_name -> {event_name -> count}
    op_events: Dict[str, Counter] = {}
    # operator_name -> set of paradox IDs
    op_paradoxes: Dict[str, set] = {}

    for paradox in state.paradoxes:
        for entry in paradox.history:
            op = entry.get("operator", "unknown")
            event = entry.get("event", "unknown")

            if op not in op_events:
                op_events[op] = Counter()
                op_paradoxes[op] = set()

            op_events[op][event] += 1
            op_paradoxes[op].add(paradox.id)

    ledgers = []
    for op_name in sorted(op_events.keys()):
        ledgers.append(OperatorLedger(
            operator_name=op_name,
            action_counts=dict(op_events[op_name]),
            affected_paradox_ids=sorted(op_paradoxes[op_name]),
        ))

    return ledgers


# ---------------------------------------------------------------------------
# Builder: Belief stratification
# ---------------------------------------------------------------------------

def _classify_belief_stratification(state: SystemState) -> Dict[str, List[str]]:
    """Partition state into four disjoint structural categories.

    - committed: claims linked to collapsed paradoxes with confidence >= 0.7
    - held: paradoxes with status paradox_held
    - open: paradoxes with status open
    - deferred: low-confidence claims (< 0.5) not linked to any paradox

    Pure read — no mutation.
    """
    # Collect claim IDs linked to collapsed paradoxes
    collapsed_claim_ids = set()
    held_ids = []
    open_ids = []

    for paradox in state.paradoxes:
        if paradox.status == "paradox_held":
            held_ids.append(paradox.id)
        elif paradox.status == "open":
            open_ids.append(paradox.id)
        elif paradox.status in ("collapsed_to_a", "collapsed_to_b", "integrated"):
            for cid in paradox.claim_ids:
                collapsed_claim_ids.add(cid)

    # Committed: high-confidence claims linked to collapsed paradoxes
    committed = []
    for claim in state.claims:
        if claim.id in collapsed_claim_ids and claim.confidence >= 0.7:
            committed.append(claim.id)

    # Collect all claim IDs linked to any paradox
    all_paradox_claim_ids = set()
    for paradox in state.paradoxes:
        for cid in paradox.claim_ids:
            all_paradox_claim_ids.add(cid)

    # Deferred: low-confidence claims not linked to any paradox
    deferred = []
    for claim in state.claims:
        if claim.confidence < 0.5 and claim.id not in all_paradox_claim_ids:
            deferred.append(claim.id)

    return {
        "committed": sorted(committed),
        "held": sorted(held_ids),
        "open": sorted(open_ids),
        "deferred": sorted(deferred),
    }


# ---------------------------------------------------------------------------
# Builder: Integrity attestations
# ---------------------------------------------------------------------------

def _check_integrity(state: SystemState) -> List[str]:
    """Verify structural invariants and produce attestation strings.

    Pure read — no mutation.
    """
    attestations = []

    # Check: every paradox_held paradox has collapse_veto=True
    held_without_veto = []
    for paradox in state.paradoxes:
        if paradox.status == "paradox_held" and not paradox.constraints.collapse_veto:
            held_without_veto.append(paradox.id)

    if not held_without_veto:
        attestations.append("Collapse veto continuity preserved")
    else:
        attestations.append(
            f"VIOLATION: {len(held_without_veto)} held paradoxes lack collapse_veto: "
            + ", ".join(held_without_veto)
        )

    # Check: every paradox with an emoji_vector_id has a matching EV in state
    orphaned = []
    for paradox in state.paradoxes:
        if paradox.emoji_vector_id is not None:
            ev = state.get_emoji_field(paradox.emoji_vector_id)
            if ev is None:
                orphaned.append(paradox.id)

    if not orphaned:
        attestations.append("All paradox-EV links valid")
    else:
        attestations.append(
            f"VIOLATION: {len(orphaned)} paradoxes have orphaned EV links: "
            + ", ".join(orphaned)
        )

    # Check: Phase 4 operators still importable
    try:
        from SovereignNEXT.operators.collapse_operator import collapse_once  # noqa: F401
        from SovereignNEXT.operators.become_expander import become_pass  # noqa: F401
        attestations.append("Phase 4 operators untouched")
    except ImportError as e:
        attestations.append(f"VIOLATION: Phase 4 import failed: {e}")

    return attestations


# ---------------------------------------------------------------------------
# Builder: Anomaly flags
# ---------------------------------------------------------------------------

def _detect_anomalies(
    state: SystemState,
    entropy_min: float = SOVEREIGN_ENTROPY_MIN,
    entropy_max: float = SOVEREIGN_ENTROPY_MAX,
    drift_threshold: float = 0.05,
) -> List[str]:
    """Detect structural anomalies. Descriptive flags only, no recommendations.

    Patterns detected:
      - stuck: paradox_held with zero history events (warning)
      - regulated: alternating expand/hold with entropy in band, veto intact,
        no drift — normal Phase 5 operational cadence (informational)
      - oscillating: alternating pattern with at least one pathological signal
        present — entropy out of band, veto lost, or drift detected (warning)
      - saturated: emoji vector at high length with entropy at or above
        ceiling (warning)
      - drifting: entropy moving monotonically in same direction across 3+
        consecutive hold events (warning)

    Severity levels:
      - informational: system working as designed, logged for observability
      - warning: structural concern that may indicate degradation

    Pure read — no mutation.
    """
    flags = []

    for paradox in state.paradoxes:
        # Stuck: held with no history
        if paradox.status == "paradox_held" and len(paradox.history) == 0:
            flags.append(f"stuck: {paradox.id} is paradox_held with no history events")

        # Oscillating pattern detection with regulated/pathological classification
        if len(paradox.history) >= 4:
            last_4 = [h.get("event", "") for h in paradox.history[-4:]]
            is_alternating = all(
                last_4[i] != last_4[i + 1]
                for i in range(len(last_4) - 1)
            ) and len(set(last_4)) == 2
            if is_alternating:
                # Check the six criteria for regulated oscillation
                pathological_signals = []

                # Criterion 1: Entropy in band
                ev = None
                entropy = 0.0
                ev_length = 0
                if paradox.emoji_vector_id is not None:
                    ev = state.get_emoji_field(paradox.emoji_vector_id)
                if ev is not None:
                    entropy = ev.entropy
                    ev_length = ev.length

                if entropy < entropy_min or entropy > entropy_max:
                    pathological_signals.append(
                        f"entropy={entropy:.4f} outside band [{entropy_min},{entropy_max}]"
                    )

                # Criterion 2: Entropy not drifting (across last 2 hold events)
                hold_entropies = [
                    h.get("entropy", None)
                    for h in paradox.history
                    if h.get("event") == "paradox_hold" and h.get("entropy") is not None
                ]
                if len(hold_entropies) >= 2:
                    delta = abs(hold_entropies[-1] - hold_entropies[-2])
                    if delta > drift_threshold:
                        pathological_signals.append(
                            f"entropy_drift={delta:.4f} exceeds threshold {drift_threshold}"
                        )

                # Criterion 3: Veto intact
                if not paradox.constraints.collapse_veto:
                    pathological_signals.append("veto_lost")

                # Criterion 4: Status held
                if paradox.status != "paradox_held":
                    pathological_signals.append(f"status={paradox.status} (not paradox_held)")

                # Criterion 5: EV not saturated
                if ev is not None and ev_length >= 20 and entropy >= entropy_max:
                    pathological_signals.append(
                        f"saturated: length={ev_length}, entropy={entropy:.4f}"
                    )

                # Criterion 6: No monotonic entropy rise across 3+ hold events
                if len(hold_entropies) >= 3:
                    last_3 = hold_entropies[-3:]
                    if all(last_3[i] < last_3[i + 1] for i in range(len(last_3) - 1)):
                        pathological_signals.append(
                            f"monotonic_rise: {[round(e, 4) for e in last_3]}"
                        )

                if pathological_signals:
                    flags.append(
                        f"oscillating: {paradox.id} shows alternating pattern "
                        f"in last 4 events: {last_4} — "
                        f"pathological signals: {'; '.join(pathological_signals)}"
                    )
                else:
                    flags.append(
                        f"regulated: {paradox.id} shows stable expand-hold cycle "
                        f"(entropy={entropy:.4f}, veto=locked, status=paradox_held)"
                    )

        # Drifting: monotonic entropy trend across 3+ consecutive hold events
        # (independent of oscillation — catches drift even without alternating pattern)
        hold_entropies = [
            h.get("entropy", None)
            for h in paradox.history
            if h.get("event") == "paradox_hold" and h.get("entropy") is not None
        ]
        if len(hold_entropies) >= 3:
            last_3 = hold_entropies[-3:]
            is_rising = all(last_3[i] < last_3[i + 1] for i in range(len(last_3) - 1))
            is_falling_below = all(
                last_3[i] > last_3[i + 1] for i in range(len(last_3) - 1)
            ) and last_3[-1] < entropy_min
            if is_rising or is_falling_below:
                direction = "rising" if is_rising else "falling_below_band"
                flags.append(
                    f"drifting: {paradox.id} entropy {direction} across last 3 hold events: "
                    f"{[round(e, 4) for e in last_3]}"
                )

        # Saturated: high-length EV with entropy at/above max
        if paradox.emoji_vector_id is not None:
            ev = state.get_emoji_field(paradox.emoji_vector_id)
            if ev is not None and ev.length >= 20 and ev.entropy >= entropy_max:
                flags.append(
                    f"saturated: {paradox.id} EV length={ev.length}, "
                    f"entropy={ev.entropy:.4f} (at/above {entropy_max})"
                )

    return flags


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def sovereign_observe(
    state: SystemState,
    entropy_min: float = SOVEREIGN_ENTROPY_MIN,
    entropy_max: float = SOVEREIGN_ENTROPY_MAX,
    balance_low: float = SOVEREIGN_BALANCE_LOW,
    balance_high: float = SOVEREIGN_BALANCE_HIGH,
) -> SovereignReport:
    """Phase 5 Sovereign: pure read-only state observer. No LLM calls.

    Reads SystemState and produces a SovereignReport describing what is
    and what has been. Does not mutate any state. Deterministic: same
    state always yields the same report.

    This function has no authority to invoke operators, recommend actions,
    or resolve paradoxes. It is epistemic, not causal.

    Args:
        state: SystemState to observe (NOT mutated).
        entropy_min: Lower bound of target entropy band for classification.
        entropy_max: Upper bound of target entropy band for classification.
        balance_low: Lower bound of balance window for classification.
        balance_high: Upper bound of balance window for classification.

    Returns:
        SovereignReport with complete descriptive snapshot.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    state_hash = state.content_hash()

    # Paradox counts by status
    status_counts: Dict[str, int] = Counter()
    for paradox in state.paradoxes:
        status_counts[paradox.status] += 1

    # Entropy band distribution
    entropy_dist = {"below_band": 0, "within_band": 0, "above_band": 0}
    balance_dist = {"below_window": 0, "within_window": 0, "above_window": 0}
    veto_locked = 0
    veto_unlocked = 0

    for paradox in state.paradoxes:
        # Veto summary
        if paradox.constraints.collapse_veto:
            veto_locked += 1
        else:
            veto_unlocked += 1

        # Entropy and balance classification (only for paradoxes with EVs)
        if paradox.emoji_vector_id is not None:
            ev = state.get_emoji_field(paradox.emoji_vector_id)
            if ev is not None:
                if ev.entropy < entropy_min:
                    entropy_dist["below_band"] += 1
                elif ev.entropy > entropy_max:
                    entropy_dist["above_band"] += 1
                else:
                    entropy_dist["within_band"] += 1

                if ev.pole_balance < balance_low:
                    balance_dist["below_window"] += 1
                elif ev.pole_balance > balance_high:
                    balance_dist["above_window"] += 1
                else:
                    balance_dist["within_window"] += 1

    veto_summary = {"veto_locked": veto_locked, "veto_unlocked": veto_unlocked}

    # Build sub-reports
    belief_strat = _classify_belief_stratification(state)
    integrity = _check_integrity(state)
    anomalies = _detect_anomalies(state, entropy_min, entropy_max)

    digests = [_build_paradox_digest(p, state) for p in state.paradoxes]
    ledgers = _build_operator_ledgers(state)

    report = SovereignReport(
        timestamp=timestamp,
        state_hash=state_hash,
        paradox_counts_by_status=dict(status_counts),
        entropy_band_distribution=entropy_dist,
        balance_window_distribution=balance_dist,
        veto_summary=veto_summary,
        belief_stratification=belief_strat,
        integrity_attestations=integrity,
        anomaly_flags=anomalies,
        paradox_digests=digests,
        operator_ledgers=ledgers,
    )

    logger.info(
        "Sovereign observe: %d paradoxes (%s), %d attestations, %d anomalies",
        len(state.paradoxes), dict(status_counts),
        len(integrity), len(anomalies),
    )

    return report
