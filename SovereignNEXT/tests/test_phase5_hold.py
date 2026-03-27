"""
SovereignNEXT — Phase 5 Step 2c: Paradox-Hold Operator Unit Tests

Tests proving eligibility gating, entropy band enforcement, balance window
enforcement, veto locking, status transition, and backward compatibility
with Phase 4 Collapse's internal _apply_paradox_hold().

No LLM calls. No loop changes. Pure Python, pure state.
"""

import sys
import os

# Ensure SovereignNEXT is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from SovereignNEXT.state.emoji_vector import (
    EmojiVector, CHAOS_EMOJIS, SUPERPOSITION_EMOJIS,
)
from SovereignNEXT.state.paradox import (
    Paradox, Pole, ParadoxMetrics, ParadoxConstraints,
)
from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.emoji_mutator import seed_initial_sequence
from SovereignNEXT.operators.paradox_hold_operator import (
    paradox_hold_pure,
    _check_hold_eligible,
)


# =========================================================================
# Helpers
# =========================================================================

def _make_ev(
    ev_id="ev_test_001",
    sequence=None,
    pole_a="\U0001f9ed",       # 🧭
    pole_b="\U0001f6e1\ufe0f", # 🛡️
    seed=42,
):
    """Create a deterministic EmojiVector with configurable sequence."""
    if sequence is None:
        sequence = seed_initial_sequence(pole_a, pole_b, seed=seed)
    return EmojiVector(
        sequence=list(sequence),
        pole_a_emoji=pole_a,
        pole_b_emoji=pole_b,
        role="paradox_field",
        id=ev_id,
        paradox_id="paradox_test_001",
        last_updated="2026-03-04T00:00:00+00:00",
    )


def _make_paradox(
    paradox_id="paradox_test_001",
    ev_id="ev_test_001",
    status="open",
):
    """Create a Paradox with configurable status."""
    return Paradox(
        pole_a=Pole(id="autonomy", emoji="\U0001f9ed", confidence=0.50),
        pole_b=Pole(id="control", emoji="\U0001f6e1\ufe0f", confidence=0.50),
        status=status,
        id=paradox_id,
        timestamp="2026-03-04T00:00:00+00:00",
        metrics=ParadoxMetrics(tension_strength=0.84),
        constraints=ParadoxConstraints(),
        emoji_vector_id=ev_id,
        claim_ids=["claim_0001", "claim_0002"],
        mission_ids=["M_test"],
    )


def _make_state(ev_sequence=None, paradox_status="open"):
    """Create a minimal SystemState with one paradox, one EV, two claims."""
    claim_a = Claim(
        text="Autonomy is essential", confidence=0.7, source="test",
        id="claim_0001", timestamp="2026-03-04T00:00:00+00:00",
    )
    claim_b = Claim(
        text="Control is essential", confidence=0.6, source="test",
        id="claim_0002", timestamp="2026-03-04T00:00:00+00:00",
    )
    ev = _make_ev(sequence=ev_sequence)
    paradox = _make_paradox(status=paradox_status)

    return SystemState(
        claims=[claim_a, claim_b],
        tensions=[],
        paradoxes=[paradox],
        emoji_fields=[ev],
        mission_id="M_test",
        iteration=1,
    )


# =========================================================================
# Test 1: Eligibility — open paradox is eligible
# =========================================================================

def test_eligibility_open():
    """Status=open, has EV → eligible."""
    state = _make_state()
    paradox = state.paradoxes[0]

    ev = _check_hold_eligible(paradox, state)

    assert ev is not None, "Open paradox with EV should be eligible"
    assert ev.id == "ev_test_001"
    print("  PASS: Eligibility — open paradox is eligible")


# =========================================================================
# Test 2: Eligibility — paradox_held is eligible
# =========================================================================

def test_eligibility_paradox_held():
    """Status=paradox_held → eligible."""
    state = _make_state(paradox_status="paradox_held")
    paradox = state.paradoxes[0]

    ev = _check_hold_eligible(paradox, state)

    assert ev is not None, "Paradox-held paradox should be eligible"
    print("  PASS: Eligibility — paradox_held is eligible")


# =========================================================================
# Test 3: Eligibility — collapsed paradox is skipped
# =========================================================================

def test_eligibility_collapsed_skipped():
    """Status=collapsed_to_a → skip. Must not reactivate."""
    state = _make_state(paradox_status="collapsed_to_a")
    paradox = state.paradoxes[0]

    ev = _check_hold_eligible(paradox, state)

    assert ev is None, "Collapsed paradox must not be eligible"
    print("  PASS: Eligibility — collapsed paradox is skipped")


# =========================================================================
# Test 4: Entropy below min → nudge up
# =========================================================================

def test_entropy_below_min_nudge_up():
    """Low entropy vector gets nudged up with superposition emojis."""
    # Create a low-entropy but balanced vector: equal pole counts, no other emojis
    low_entropy_seq = ["\U0001f9ed"] * 3 + ["\U0001f6e1\ufe0f"] * 3
    state = _make_state(ev_sequence=low_entropy_seq)
    ev = state.emoji_fields[0]

    assert ev.entropy < 0.70, f"Test setup: entropy {ev.entropy} should be < 0.70"
    assert 0.35 <= ev.pole_balance <= 0.65, f"Test setup: balance {ev.pole_balance} should be in window"
    original_length = ev.length

    result = paradox_hold_pure(state, seed=42)

    assert result.nudged == 1
    action = result.actions[0]
    assert action.decision == "nudge_entropy_up"
    assert action.entropy_after >= action.entropy_before, (
        "Entropy should increase or stay same after nudge up"
    )
    assert ev.length > original_length, "Superposition emojis should be added"
    print("  PASS: Entropy below min → nudge up")


# =========================================================================
# Test 5: Entropy above max → nudge down
# =========================================================================

def test_entropy_above_max_nudge_down():
    """High entropy vector with duplicates gets nudged down by removing duplicates."""
    # Create a high-entropy vector with enough distinct emojis and some duplicates
    chaos_pool = list(CHAOS_EMOJIS)
    super_pool = list(SUPERPOSITION_EMOJIS)
    high_entropy_seq = (
        ["\U0001f9ed", "\U0001f6e1\ufe0f"]  # both poles
        + chaos_pool[:6]                       # 6 distinct chaos
        + super_pool[:5]                       # 5 distinct superposition
        + [chaos_pool[0]]                      # 1 duplicate to remove
    )
    state = _make_state(ev_sequence=high_entropy_seq)
    ev = state.emoji_fields[0]

    # Verify setup: high entropy, balanced
    assert ev.entropy > 0.90, f"Test setup: entropy {ev.entropy} should be > 0.90"
    bal = ev.pole_balance
    assert 0.35 <= bal <= 0.65, f"Test setup: balance {bal} should be in [0.35, 0.65]"
    entropy_before = ev.entropy
    original_length = ev.length

    result = paradox_hold_pure(state, seed=42)

    assert result.nudged == 1
    action = result.actions[0]
    assert action.decision == "nudge_entropy_down"
    assert ev.length > original_length, "Duplicates should be appended to reduce diversity ratio"
    assert ev.entropy <= entropy_before, (
        f"Entropy should decrease or stay same: {entropy_before} → {ev.entropy}"
    )
    print("  PASS: Entropy above max → nudge down")


# =========================================================================
# Test 6: Balance outside window → corrected
# =========================================================================

def test_balance_outside_window_corrected():
    """Imbalanced vector gets corrected by appending weaker pole."""
    # Create an imbalanced vector: many pole_a, few pole_b
    # pole_balance = count(b) / (count(a) + count(b)), so lots of a → low balance
    imbalanced_seq = ["\U0001f9ed"] * 5 + ["\U0001f6e1\ufe0f"] * 1
    state = _make_state(ev_sequence=imbalanced_seq)
    ev = state.emoji_fields[0]

    assert ev.pole_balance < 0.35, f"Test setup: balance {ev.pole_balance} should be < 0.35"
    balance_before = ev.pole_balance

    result = paradox_hold_pure(state, seed=42)

    assert result.balance_corrected == 1
    action = result.actions[0]
    assert action.decision == "correct_balance"
    assert ev.pole_balance > balance_before, (
        f"Balance should increase: {balance_before} → {ev.pole_balance}"
    )
    # Should have appended pole_b (the weaker one)
    assert ev.sequence[-1] == "\U0001f6e1\ufe0f", "Weaker pole (b) should be appended"
    print("  PASS: Balance outside window → corrected")


# =========================================================================
# Test 7: All within band → stabilize
# =========================================================================

def test_within_band_stabilize():
    """Vector already in band gets standard mutate_paradox_hold."""
    # Create a vector with entropy in [0.70, 0.90] and balance in [0.35, 0.65]
    # Needs enough diversity for entropy > 0.70 but not too much for < 0.90
    # Also needs balanced poles
    stable_seq = (
        ["\U0001f9ed", "\U0001f6e1\ufe0f"]  # both poles
        + ["\U0001f9ed", "\U0001f6e1\ufe0f"]  # repeat poles (balanced)
        + list(SUPERPOSITION_EMOJIS)[:2]        # 2 superposition for moderate entropy
    )
    state = _make_state(ev_sequence=stable_seq)
    ev = state.emoji_fields[0]

    entropy = ev.entropy
    balance = ev.pole_balance

    # If this setup doesn't land in band, adjust — need entropy in [0.70, 0.90]
    # and balance in [0.35, 0.65]
    assert 0.35 <= balance <= 0.65, f"Test setup: balance {balance} not in [0.35, 0.65]"

    # Use custom thresholds to guarantee we're "in band"
    result = paradox_hold_pure(
        state,
        entropy_min=entropy - 0.1,
        entropy_max=entropy + 0.1,
        seed=42,
    )

    assert result.stabilized == 1
    action = result.actions[0]
    assert action.decision == "stabilize"
    print("  PASS: All within band → stabilize")


# =========================================================================
# Test 8: Veto locked after hold
# =========================================================================

def test_veto_locked():
    """After hold, constraints.collapse_veto=True and veto_reason set."""
    state = _make_state()
    paradox = state.paradoxes[0]

    assert not paradox.constraints.collapse_veto, "Test setup: veto should start False"

    paradox_hold_pure(state, seed=42)

    assert paradox.constraints.collapse_veto is True
    assert paradox.constraints.veto_reason == "paradox_held"
    print("  PASS: Veto locked after hold")


# =========================================================================
# Test 9: Status set to paradox_held
# =========================================================================

def test_status_set_to_held():
    """Status transitions from 'open' to 'paradox_held'."""
    state = _make_state(paradox_status="open")
    paradox = state.paradoxes[0]

    assert paradox.status == "open"

    paradox_hold_pure(state, seed=42)

    assert paradox.status == "paradox_held"
    print("  PASS: Status set to paradox_held")


# =========================================================================
# Test 10: Full mixed pass
# =========================================================================

def test_full_mixed_pass():
    """End-to-end with multiple paradoxes: stabilized, nudged, balance-corrected, skipped."""
    claim_a = Claim(text="Autonomy is essential", confidence=0.7, source="test",
                    id="claim_0001", timestamp="2026-03-04T00:00:00+00:00")
    claim_b = Claim(text="Control is essential", confidence=0.6, source="test",
                    id="claim_0002", timestamp="2026-03-04T00:00:00+00:00")

    # P1: open, low entropy → nudge_entropy_up
    ev1 = _make_ev(ev_id="ev_001", sequence=["\U0001f9ed"] * 6 + ["\U0001f6e1\ufe0f"])
    assert ev1.entropy < 0.70, f"Test setup: ev1 entropy {ev1.entropy} should be < 0.70"
    # Note: if balance is also out of window, balance correction takes priority
    p1 = _make_paradox(paradox_id="p_001", ev_id="ev_001", status="open")

    # P2: imbalanced → correct_balance (takes priority over entropy)
    ev2 = _make_ev(ev_id="ev_002", sequence=["\U0001f9ed"] * 5 + ["\U0001f6e1\ufe0f"])
    assert ev2.pole_balance < 0.35, f"Test setup: ev2 balance {ev2.pole_balance} should be < 0.35"
    p2 = _make_paradox(paradox_id="p_002", ev_id="ev_002", status="open")

    # P3: collapsed → skip
    ev3 = _make_ev(ev_id="ev_003")
    p3 = _make_paradox(paradox_id="p_003", ev_id="ev_003", status="collapsed_to_b")

    # P4: no emoji vector → skip
    p4 = Paradox(
        pole_a=Pole(id="freedom", emoji="\U0001f9ed"),
        pole_b=Pole(id="order", emoji="\U0001f6e1\ufe0f"),
        status="open", id="p_004",
        timestamp="2026-03-04T00:00:00+00:00",
        emoji_vector_id=None,
    )

    state = SystemState(
        claims=[claim_a, claim_b],
        tensions=[],
        paradoxes=[p1, p2, p3, p4],
        emoji_fields=[ev1, ev2, ev3],
        mission_id="M_test",
        iteration=1,
    )

    result = paradox_hold_pure(state, seed=42)

    assert result.skipped == 2, f"Expected 2 skipped, got {result.skipped}"
    assert result.total_eligible == 2, f"Expected 2 eligible, got {result.total_eligible}"

    # Check that the 2 eligible paradoxes got acted on
    action_map = {a.paradox_id: a for a in result.actions}
    assert action_map["p_003"].decision == "skip"
    assert action_map["p_003"].skip_reason == "status=collapsed_to_b"
    assert action_map["p_004"].decision == "skip"
    assert action_map["p_004"].skip_reason == "no_emoji_vector"

    # P1 and P2 should both have been acted on (not skipped)
    assert action_map["p_001"].decision != "skip"
    assert action_map["p_002"].decision != "skip"

    # Both should now be paradox_held
    assert p1.status == "paradox_held"
    assert p2.status == "paradox_held"

    # Both should have veto locked
    assert p1.constraints.collapse_veto is True
    assert p2.constraints.collapse_veto is True

    print("  PASS: Full mixed pass")


# =========================================================================
# Test 11: No claims modified
# =========================================================================

def test_no_claims_modified():
    """Claim count and confidences unchanged after hold pass."""
    state = _make_state()
    original_claims = [(c.id, c.confidence, c.text) for c in state.claims]

    paradox_hold_pure(state, seed=42)

    after_claims = [(c.id, c.confidence, c.text) for c in state.claims]
    assert original_claims == after_claims, "Claims must not be modified by Paradox-Hold"
    print("  PASS: No claims modified")


# =========================================================================
# Test 12: Audit record complete
# =========================================================================

def test_audit_record_complete():
    """HoldAction has correct before/after metrics, decision, veto state."""
    state = _make_state()
    ev = state.emoji_fields[0]
    entropy_before = ev.entropy
    balance_before = ev.pole_balance

    result = paradox_hold_pure(state, seed=42)

    assert len(result.actions) == 1
    action = result.actions[0]

    assert action.paradox_id == "paradox_test_001"
    assert action.decision in ("stabilize", "nudge_entropy_up", "nudge_entropy_down", "correct_balance")
    assert action.entropy_before == entropy_before
    assert action.entropy_after == ev.entropy
    assert action.balance_before == balance_before
    assert action.balance_after == ev.pole_balance
    assert action.veto_locked is True
    assert action.status_before == "open"
    assert action.status_after == "paradox_held"
    assert action.skip_reason is None

    # Verify paradox history was updated
    paradox = state.paradoxes[0]
    hold_events = [h for h in paradox.history if h.get("event") == "paradox_hold"]
    assert len(hold_events) == 1
    assert "entropy_before" in hold_events[0]
    assert "balance_before" in hold_events[0]
    assert "decision" in hold_events[0]
    assert hold_events[0]["veto_locked"] is True

    print("  PASS: Audit record complete")


# =========================================================================
# Test 13: Phase 4 _apply_paradox_hold still importable
# =========================================================================

def test_phase4_apply_paradox_hold_importable():
    """Collapse's internal _apply_paradox_hold still exists and is callable."""
    from SovereignNEXT.operators.collapse_operator import _apply_paradox_hold
    assert callable(_apply_paradox_hold)
    print("  PASS: Phase 4 _apply_paradox_hold still importable")


# =========================================================================
# Runner
# =========================================================================

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("PHASE 5 STEP 2c — PARADOX-HOLD OPERATOR UNIT TESTS")
    print("=" * 60 + "\n")

    tests = [
        test_eligibility_open,
        test_eligibility_paradox_held,
        test_eligibility_collapsed_skipped,
        test_entropy_below_min_nudge_up,
        test_entropy_above_max_nudge_down,
        test_balance_outside_window_corrected,
        test_within_band_stabilize,
        test_veto_locked,
        test_status_set_to_held,
        test_full_mixed_pass,
        test_no_claims_modified,
        test_audit_record_complete,
        test_phase4_apply_paradox_hold_importable,
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
        print("\nSTATUS: FAIL — Paradox-Hold operator not ready")
        sys.exit(1)
    else:
        print("\nSTATUS: PASS — Paradox-Hold operator is a pure state stabilizer")
        sys.exit(0)


if __name__ == "__main__":
    main()
