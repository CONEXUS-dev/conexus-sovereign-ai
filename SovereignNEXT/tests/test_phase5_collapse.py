"""
SovereignNEXT — Phase 5 Step 2a: Collapse Operator Unit Tests

Tests proving veto enforcement from constraints, margin from pole confidences,
veto locking on paradox-hold, audit record completeness, and backward
compatibility with Phase 4 decide_tension().

No LLM calls. No loop changes. Pure Python, pure state.
"""

import sys
import os

# Ensure SovereignNEXT is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from SovereignNEXT.state.emoji_vector import EmojiVector
from SovereignNEXT.state.paradox import (
    Paradox, Pole, ParadoxMetrics, ParadoxConstraints,
)
from SovereignNEXT.state.tension import Tension
from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.emoji_mutator import seed_initial_sequence
from SovereignNEXT.operators.collapse_operator import (
    decide_tension,
    decide_tension_pure,
    collapse_pure,
)


# =========================================================================
# Helpers
# =========================================================================

def _make_ev(ev_id="ev_test_001", entropy_seed=42):
    """Create a deterministic EmojiVector with known metrics."""
    seq = seed_initial_sequence("🧭", "🛡️", seed=entropy_seed)
    return EmojiVector(
        sequence=seq,
        pole_a_emoji="🧭",
        pole_b_emoji="🛡️",
        role="paradox_field",
        id=ev_id,
        paradox_id="paradox_test_001",
        last_updated="2026-03-04T00:00:00+00:00",
    )


def _make_paradox(
    paradox_id="paradox_test_001",
    ev_id="ev_test_001",
    conf_a=0.50,
    conf_b=0.50,
    collapse_veto=False,
    veto_reason="",
    entropy_threshold=0.70,
    balance_window=(0.35, 0.65),
):
    """Create a Paradox with configurable constraints and pole confidences."""
    return Paradox(
        pole_a=Pole(id="autonomy", emoji="🧭", confidence=conf_a),
        pole_b=Pole(id="control", emoji="🛡️", confidence=conf_b),
        status="open",
        id=paradox_id,
        timestamp="2026-03-04T00:00:00+00:00",
        metrics=ParadoxMetrics(tension_strength=0.84),
        constraints=ParadoxConstraints(
            collapse_veto=collapse_veto,
            veto_reason=veto_reason,
            entropy_threshold=entropy_threshold,
            balance_window=balance_window,
        ),
        emoji_vector_id=ev_id,
        claim_ids=["claim_0001", "claim_0002"],
    )


def _make_tension(
    tension_id="tension_test_001",
    ev_id="ev_test_001",
    pole_a_text="Autonomy is essential",
    pole_b_text="Control is essential",
):
    """Create a Tension linked to an emoji vector."""
    return Tension(
        pole_a=pole_a_text,
        pole_b=pole_b_text,
        relation_type="polarity",
        status="open",
        id=tension_id,
        timestamp="2026-03-04T00:00:00+00:00",
        source_claims=["claim_0001", "claim_0002"],
        emoji_vector_id=ev_id,
    )


def _make_state(
    conf_a=0.50,
    conf_b=0.50,
    collapse_veto=False,
    veto_reason="",
    entropy_threshold=0.70,
    balance_window=(0.35, 0.65),
):
    """Create a minimal SystemState with one tension, one paradox, one EV, two claims."""
    claim_a = Claim(
        text="Autonomy is essential",
        confidence=0.7,
        source="test",
        id="claim_0001",
        timestamp="2026-03-04T00:00:00+00:00",
    )
    claim_b = Claim(
        text="Control is essential",
        confidence=0.6,
        source="test",
        id="claim_0002",
        timestamp="2026-03-04T00:00:00+00:00",
    )
    ev = _make_ev()
    paradox = _make_paradox(
        conf_a=conf_a,
        conf_b=conf_b,
        collapse_veto=collapse_veto,
        veto_reason=veto_reason,
        entropy_threshold=entropy_threshold,
        balance_window=balance_window,
    )
    tension = _make_tension()

    return SystemState(
        claims=[claim_a, claim_b],
        tensions=[tension],
        paradoxes=[paradox],
        emoji_fields=[ev],
        mission_id="M_test",
        iteration=1,
    )


# =========================================================================
# Test 1: Veto enforcement from constraints
# =========================================================================

def test_veto_enforcement_from_constraints():
    """Paradox with collapse_veto=True + high entropy blocks commit."""
    state = _make_state(
        conf_a=0.80, conf_b=0.20,  # High margin — would commit without veto
        collapse_veto=True,
        veto_reason="entropy_above_threshold",
    )
    tension = state.tensions[0]

    # Verify the EV has high enough entropy for veto
    ev = state.emoji_fields[0]
    assert ev.entropy >= 0.70, f"Test setup: entropy {ev.entropy} < 0.70"

    action = decide_tension_pure(tension, state)

    assert action.decision == "paradox_hold", f"Expected paradox_hold, got {action.decision}"
    assert action.paradox_vetoed is True
    assert action.veto_source == "paradox_test_001"
    print("  PASS: Veto enforcement from constraints")


# =========================================================================
# Test 2: Veto respects collapse_veto=False
# =========================================================================

def test_veto_respects_false_flag():
    """Even with high entropy, no veto if collapse_veto=False."""
    state = _make_state(
        conf_a=0.80, conf_b=0.20,  # High margin — should commit
        collapse_veto=False,
    )
    tension = state.tensions[0]

    action = decide_tension_pure(tension, state)

    assert action.decision == "commit_to_a", f"Expected commit_to_a, got {action.decision}"
    assert action.paradox_vetoed is False
    assert action.veto_source is None
    print("  PASS: Veto respects collapse_veto=False")


# =========================================================================
# Test 3: Veto reads custom thresholds from paradox
# =========================================================================

def test_veto_reads_custom_thresholds():
    """Custom entropy_threshold on paradox overrides default behavior."""
    state = _make_state(
        conf_a=0.80, conf_b=0.20,
        collapse_veto=True,
        veto_reason="custom_threshold",
        entropy_threshold=1.01,  # Above max entropy (1.0) — veto condition never met
    )
    tension = state.tensions[0]

    ev = state.emoji_fields[0]
    assert ev.entropy <= 1.0, f"Test setup: entropy {ev.entropy} > 1.0"

    action = decide_tension_pure(tension, state)

    # Veto flag is True, but threshold not met → no veto
    assert action.decision == "commit_to_a", f"Expected commit_to_a, got {action.decision}"
    assert action.paradox_vetoed is False
    print("  PASS: Veto reads custom thresholds from paradox")


# =========================================================================
# Test 4: Margin from pole confidence
# =========================================================================

def test_margin_from_pole_confidence():
    """decide_tension_pure uses pole confidence, not rubric scores."""
    # Case 1: Equal confidence → margin=0.0 → paradox_hold (margin <= 0.10)
    state_eq = _make_state(conf_a=0.50, conf_b=0.50)
    action_eq = decide_tension_pure(state_eq.tensions[0], state_eq)
    assert action_eq.margin == 0.0, f"Expected margin 0.0, got {action_eq.margin}"
    assert action_eq.decision == "paradox_hold"

    # Case 2: Small difference → defer (0.10 < margin < 0.25)
    state_defer = _make_state(conf_a=0.60, conf_b=0.45)
    action_defer = decide_tension_pure(state_defer.tensions[0], state_defer)
    assert action_defer.margin == 0.15, f"Expected margin 0.15, got {action_defer.margin}"
    assert action_defer.decision == "defer"

    # Case 3: Large difference → commit (margin >= 0.25)
    state_commit = _make_state(conf_a=0.80, conf_b=0.20)
    action_commit = decide_tension_pure(state_commit.tensions[0], state_commit)
    assert action_commit.margin == 0.60, f"Expected margin 0.60, got {action_commit.margin}"
    assert action_commit.decision == "commit_to_a"

    # Case 4: B wins
    state_b = _make_state(conf_a=0.20, conf_b=0.80)
    action_b = decide_tension_pure(state_b.tensions[0], state_b)
    assert action_b.decision == "commit_to_b"

    print("  PASS: Margin from pole confidence")


# =========================================================================
# Test 5: Commit updates claim confidences
# =========================================================================

def test_commit_updates_confidences():
    """After commit, winning claim boosted and losing claim penalized."""
    state = _make_state(conf_a=0.80, conf_b=0.20)
    claim_a = state.get_claim("claim_0001")
    claim_b = state.get_claim("claim_0002")
    orig_conf_a = claim_a.confidence
    orig_conf_b = claim_b.confidence

    result = collapse_pure(state, seed=42)

    assert result.committed == 1
    # Winner (pole_a) should be boosted
    assert claim_a.confidence > orig_conf_a, (
        f"Winner confidence not boosted: {orig_conf_a} -> {claim_a.confidence}"
    )
    # Loser (pole_b) should be penalized
    assert claim_b.confidence < orig_conf_b, (
        f"Loser confidence not penalized: {orig_conf_b} -> {claim_b.confidence}"
    )
    print("  PASS: Commit updates claim confidences")


# =========================================================================
# Test 6: Paradox-hold locks veto
# =========================================================================

def test_paradox_hold_locks_veto():
    """After paradox-hold, constraints.collapse_veto is True."""
    state = _make_state(conf_a=0.50, conf_b=0.50)  # Equal → paradox_hold
    paradox = state.paradoxes[0]

    assert paradox.constraints.collapse_veto is False, "Precondition: veto should start False"

    result = collapse_pure(state, seed=42)

    assert result.paradox_held == 1
    assert paradox.constraints.collapse_veto is True, "Veto not locked after paradox-hold"
    assert paradox.constraints.veto_reason == "paradox_held"
    assert paradox.status == "paradox_held"

    # Verify veto lock is recorded in paradox history
    lock_events = [
        h for h in paradox.history
        if h.get("veto_locked") is True
    ]
    assert len(lock_events) >= 1, "No veto_locked event in paradox history"

    print("  PASS: Paradox-hold locks veto")


# =========================================================================
# Test 7: Defer leaves state unchanged
# =========================================================================

def test_defer_leaves_state_unchanged():
    """Defer: no confidence change, no veto mutation, status stays open."""
    state = _make_state(conf_a=0.60, conf_b=0.45)  # margin=0.15 → defer
    paradox = state.paradoxes[0]
    claim_a = state.get_claim("claim_0001")
    claim_b = state.get_claim("claim_0002")
    orig_conf_a = claim_a.confidence
    orig_conf_b = claim_b.confidence
    orig_veto = paradox.constraints.collapse_veto

    result = collapse_pure(state, seed=42)

    assert result.deferred == 1
    assert state.tensions[0].status == "open"
    assert claim_a.confidence == orig_conf_a
    assert claim_b.confidence == orig_conf_b
    assert paradox.constraints.collapse_veto == orig_veto
    print("  PASS: Defer leaves state unchanged")


# =========================================================================
# Test 8: Veto source recorded in TensionAction
# =========================================================================

def test_veto_source_recorded():
    """TensionAction.veto_source contains the paradox ID when veto fires."""
    state = _make_state(
        conf_a=0.80, conf_b=0.20,
        collapse_veto=True,
        veto_reason="test_veto",
    )
    tension = state.tensions[0]

    action = decide_tension_pure(tension, state)

    assert action.veto_source == "paradox_test_001", (
        f"Expected veto_source='paradox_test_001', got '{action.veto_source}'"
    )
    assert action.paradox_vetoed is True

    # Non-vetoed action should have veto_source=None
    state_no_veto = _make_state(conf_a=0.80, conf_b=0.20, collapse_veto=False)
    action_no_veto = decide_tension_pure(state_no_veto.tensions[0], state_no_veto)
    assert action_no_veto.veto_source is None
    print("  PASS: Veto source recorded in TensionAction")


# =========================================================================
# Test 9: Full collapse_pure pass with mixed tensions
# =========================================================================

def test_full_collapse_pure_pass():
    """End-to-end collapse_pure with vetoed, committed, deferred, and held tensions."""
    # Build state with 4 tensions, each targeting a different outcome
    claim_a = Claim(text="Autonomy is essential", confidence=0.7, source="test",
                    id="claim_0001", timestamp="2026-03-04T00:00:00+00:00")
    claim_b = Claim(text="Control is essential", confidence=0.6, source="test",
                    id="claim_0002", timestamp="2026-03-04T00:00:00+00:00")

    # Tension 1: vetoed (collapse_veto=True, high entropy, balanced)
    ev1 = _make_ev(ev_id="ev_001")
    p1 = _make_paradox(paradox_id="p_001", ev_id="ev_001",
                       conf_a=0.80, conf_b=0.20, collapse_veto=True,
                       veto_reason="entropy_above_threshold")
    t1 = _make_tension(tension_id="t_001", ev_id="ev_001")

    # Tension 2: commit (high margin, no veto)
    ev2 = _make_ev(ev_id="ev_002")
    p2 = _make_paradox(paradox_id="p_002", ev_id="ev_002",
                       conf_a=0.80, conf_b=0.20, collapse_veto=False)
    t2 = _make_tension(tension_id="t_002", ev_id="ev_002")

    # Tension 3: defer (margin in defer band, no veto)
    ev3 = _make_ev(ev_id="ev_003")
    p3 = _make_paradox(paradox_id="p_003", ev_id="ev_003",
                       conf_a=0.60, conf_b=0.45, collapse_veto=False)
    t3 = _make_tension(tension_id="t_003", ev_id="ev_003")

    # Tension 4: paradox_hold (equal confidence, no veto)
    ev4 = _make_ev(ev_id="ev_004")
    p4 = _make_paradox(paradox_id="p_004", ev_id="ev_004",
                       conf_a=0.50, conf_b=0.50, collapse_veto=False)
    t4 = _make_tension(tension_id="t_004", ev_id="ev_004")

    state = SystemState(
        claims=[claim_a, claim_b],
        tensions=[t1, t2, t3, t4],
        paradoxes=[p1, p2, p3, p4],
        emoji_fields=[ev1, ev2, ev3, ev4],
        mission_id="M_test",
        iteration=1,
    )

    result = collapse_pure(state, seed=42)

    assert result.total_open == 4
    assert result.paradox_held == 2, f"Expected 2 paradox_held, got {result.paradox_held}"
    assert result.committed == 1, f"Expected 1 committed, got {result.committed}"
    assert result.deferred == 1, f"Expected 1 deferred, got {result.deferred}"

    # Verify specific actions
    action_map = {a.tension_id: a for a in result.actions}

    assert action_map["t_001"].paradox_vetoed is True
    assert action_map["t_001"].veto_source == "p_001"
    assert action_map["t_001"].decision == "paradox_hold"

    assert action_map["t_002"].decision == "commit_to_a"
    assert action_map["t_002"].paradox_vetoed is False

    assert action_map["t_003"].decision == "defer"

    assert action_map["t_004"].decision == "paradox_hold"
    assert action_map["t_004"].paradox_vetoed is False  # Not vetoed, just low margin

    # Verify veto locked on paradox-held paradoxes
    assert p1.constraints.collapse_veto is True  # Was already True
    assert p4.constraints.collapse_veto is True   # Newly locked

    print("  PASS: Full collapse_pure pass with mixed tensions")


# =========================================================================
# Test 10: Phase 4 decide_tension still works (backward compat)
# =========================================================================

def test_phase4_decide_tension_backward_compat():
    """Phase 4 decide_tension() works unchanged with LLM-style score dicts."""
    state = _make_state(collapse_veto=False)
    tension = state.tensions[0]

    # Simulate LLM rubric scores (Phase 4 style)
    scores = {
        "pole_a": {"evidence": 0.8, "consistency": 0.7, "goal_fit": 0.6, "memory_support": 0.5},
        "pole_b": {"evidence": 0.3, "consistency": 0.4, "goal_fit": 0.5, "memory_support": 0.4},
        "weighted_a": 0.665,
        "weighted_b": 0.395,
        "margin": 0.27,
    }

    action = decide_tension(tension, scores, state)

    # margin=0.27 > COMMIT_MARGIN(0.25) and weighted_a > weighted_b → commit_to_a
    assert action.decision == "commit_to_a", f"Expected commit_to_a, got {action.decision}"
    assert action.margin == 0.27
    assert action.scores_a == scores["pole_a"]
    assert action.scores_b == scores["pole_b"]
    assert action.paradox_vetoed is False
    assert action.veto_source is None

    # Phase 4 with veto (collapse_veto now must be True for veto to fire)
    state_veto = _make_state(collapse_veto=True, veto_reason="test")
    action_veto = decide_tension(state_veto.tensions[0], scores, state_veto)
    assert action_veto.decision == "paradox_hold"
    assert action_veto.paradox_vetoed is True
    assert action_veto.veto_source == "paradox_test_001"

    print("  PASS: Phase 4 decide_tension backward compatibility")


# =========================================================================
# Runner
# =========================================================================

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("PHASE 5 STEP 2a — COLLAPSE OPERATOR UNIT TESTS")
    print("=" * 60 + "\n")

    tests = [
        test_veto_enforcement_from_constraints,
        test_veto_respects_false_flag,
        test_veto_reads_custom_thresholds,
        test_margin_from_pole_confidence,
        test_commit_updates_confidences,
        test_paradox_hold_locks_veto,
        test_defer_leaves_state_unchanged,
        test_veto_source_recorded,
        test_full_collapse_pure_pass,
        test_phase4_decide_tension_backward_compat,
    ]

    passed = 0
    failed = 0

    for test_fn in tests:
        name = test_fn.__name__
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'=' * 60}")

    if failed > 0:
        print("\nSTATUS: FAIL — Collapse operator not ready")
        sys.exit(1)
    else:
        print("\nSTATUS: PASS — Collapse operator is a pure state transformer")
        sys.exit(0)


if __name__ == "__main__":
    main()
