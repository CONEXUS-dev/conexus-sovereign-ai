"""
SovereignNEXT — Phase 5 Step 2b: Become Operator Unit Tests

Tests proving eligibility gating, entropy ceiling enforcement, emoji-vector
mutation, claim spawning, stabilization behavior, and backward compatibility
with Phase 4 become_pass().

No LLM calls. No loop changes. Pure Python, pure state.
"""

import sys
import os

# Ensure SovereignNEXT is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from SovereignNEXT.state.emoji_vector import EmojiVector, CHAOS_EMOJIS, SUPERPOSITION_EMOJIS
from SovereignNEXT.state.paradox import (
    Paradox, Pole, ParadoxMetrics, ParadoxConstraints,
)
from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.emoji_mutator import seed_initial_sequence
from SovereignNEXT.operators.become_expander import (
    become_pure,
    _check_become_eligible,
    _check_entropy_gate,
)


# =========================================================================
# Helpers
# =========================================================================

def _make_ev(ev_id="ev_test_001", seed=42):
    """Create a deterministic EmojiVector with known metrics."""
    seq = seed_initial_sequence("\U0001f9ed", "\U0001f6e1\ufe0f", seed=seed)
    return EmojiVector(
        sequence=seq,
        pole_a_emoji="\U0001f9ed",
        pole_b_emoji="\U0001f6e1\ufe0f",
        role="paradox_field",
        id=ev_id,
        paradox_id="paradox_test_001",
        last_updated="2026-03-04T00:00:00+00:00",
    )


def _make_paradox(
    paradox_id="paradox_test_001",
    ev_id="ev_test_001",
    status="open",
    conf_a=0.50,
    conf_b=0.50,
):
    """Create a Paradox with configurable status and pole confidences."""
    return Paradox(
        pole_a=Pole(id="autonomy", emoji="\U0001f9ed", confidence=conf_a),
        pole_b=Pole(id="control", emoji="\U0001f6e1\ufe0f", confidence=conf_b),
        status=status,
        id=paradox_id,
        timestamp="2026-03-04T00:00:00+00:00",
        metrics=ParadoxMetrics(tension_strength=0.84),
        constraints=ParadoxConstraints(),
        emoji_vector_id=ev_id,
        claim_ids=["claim_0001", "claim_0002"],
        mission_ids=["M_test"],
    )


def _make_state(
    paradox_status="open",
    conf_a=0.50,
    conf_b=0.50,
):
    """Create a minimal SystemState with one paradox, one EV, two claims."""
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
    paradox = _make_paradox(status=paradox_status, conf_a=conf_a, conf_b=conf_b)

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

def test_eligibility_open_paradox():
    """Status=open, has EV → eligible."""
    state = _make_state(paradox_status="open")
    paradox = state.paradoxes[0]

    ev = _check_become_eligible(paradox, state)

    assert ev is not None, "Open paradox with EV should be eligible"
    assert ev.id == "ev_test_001"
    print("  PASS: Eligibility — open paradox is eligible")


# =========================================================================
# Test 2: Eligibility — collapsed paradox is skipped
# =========================================================================

def test_eligibility_collapsed_skipped():
    """Status=collapsed_to_a → skip."""
    state = _make_state(paradox_status="collapsed_to_a")
    paradox = state.paradoxes[0]

    ev = _check_become_eligible(paradox, state)

    assert ev is None, "Collapsed paradox should not be eligible"
    print("  PASS: Eligibility — collapsed paradox is skipped")


# =========================================================================
# Test 3: Eligibility — paradox_held is eligible
# =========================================================================

def test_eligibility_paradox_held():
    """Status=paradox_held → eligible."""
    state = _make_state(paradox_status="paradox_held")
    paradox = state.paradoxes[0]

    ev = _check_become_eligible(paradox, state)

    assert ev is not None, "Paradox-held paradox should be eligible"
    print("  PASS: Eligibility — paradox_held is eligible")


# =========================================================================
# Test 4: Entropy gate — below ceiling → expand
# =========================================================================

def test_entropy_gate_below_ceiling():
    """Entropy < ceiling → decision=expand."""
    ev = _make_ev()
    # Our test EV has entropy=1.0 with seed=42 (4 distinct emojis, length 4)
    # Use a high ceiling that is above 1.0
    decision = _check_entropy_gate(ev, entropy_ceiling=1.01)

    assert decision == "expand", f"Expected 'expand', got '{decision}'"
    print("  PASS: Entropy gate — below ceiling → expand")


# =========================================================================
# Test 5: Entropy gate — at/above ceiling → stabilize
# =========================================================================

def test_entropy_gate_above_ceiling():
    """Entropy >= ceiling → decision=stabilize."""
    ev = _make_ev()
    # Our test EV has entropy=1.0; set ceiling at or below
    decision = _check_entropy_gate(ev, entropy_ceiling=0.95)

    assert decision == "stabilize", f"Expected 'stabilize', got '{decision}'"

    # Also test exact boundary
    decision_exact = _check_entropy_gate(ev, entropy_ceiling=1.0)
    assert decision_exact == "stabilize", f"Expected 'stabilize' at exact boundary, got '{decision_exact}'"

    print("  PASS: Entropy gate — at/above ceiling → stabilize")


# =========================================================================
# Test 6: Expand mutates emoji vector
# =========================================================================

def test_expand_mutates_emoji_vector():
    """After expand, sequence grows and contains chaos/superposition emojis."""
    state = _make_state()
    ev = state.emoji_fields[0]
    original_length = ev.length

    # Use high ceiling so expand fires
    result = become_pure(state, entropy_ceiling=1.01, seed=42)

    assert result.expanded == 1
    assert ev.length > original_length, (
        f"Sequence should grow: {original_length} → {ev.length}"
    )
    # New emojis should be from chaos or superposition set
    new_emojis = ev.sequence[original_length:]
    chaos_or_super = CHAOS_EMOJIS | SUPERPOSITION_EMOJIS
    for emoji in new_emojis:
        assert emoji in chaos_or_super, (
            f"New emoji '{emoji}' not in chaos/superposition set"
        )
    print("  PASS: Expand mutates emoji vector")


# =========================================================================
# Test 7: Expand respects vector length limit
# =========================================================================

def test_expand_respects_length_limit():
    """Sequence not extended beyond vector_length_limit."""
    state = _make_state()
    ev = state.emoji_fields[0]
    original_length = ev.length

    # Set limit to current length — mutation should be skipped
    result = become_pure(state, entropy_ceiling=1.01, vector_length_limit=original_length, seed=42)

    assert result.expanded == 1  # Action is still "expand", just no mutation
    assert ev.length == original_length, (
        f"Sequence should not grow beyond limit: {ev.length} > {original_length}"
    )
    # But claims should still be spawned
    assert result.claims_spawned == 2

    print("  PASS: Expand respects vector length limit")


# =========================================================================
# Test 8: Expand spawns low-confidence claims
# =========================================================================

def test_expand_spawns_claims():
    """Two new claims at confidence 0.3, tagged correctly."""
    state = _make_state()
    original_claim_count = len(state.claims)

    result = become_pure(state, entropy_ceiling=1.01, seed=42)

    assert result.claims_spawned == 2
    assert len(state.claims) == original_claim_count + 2

    # Check new claims
    new_claims = state.claims[original_claim_count:]
    for c in new_claims:
        assert c.confidence == 0.3, f"Expected confidence 0.3, got {c.confidence}"
        assert "expanded_by_become" in c.tags
        assert "proposal" in c.tags
        assert c.source == "become_pure"
        assert c.operator == "become"
        assert c.parent_id is not None

    # One should reference pole_a, one pole_b
    texts = {c.text for c in new_claims}
    assert any("autonomy" in t for t in texts), "No claim for pole_a (autonomy)"
    assert any("control" in t for t in texts), "No claim for pole_b (control)"

    print("  PASS: Expand spawns low-confidence claims")


# =========================================================================
# Test 9: Stabilize does not spawn claims
# =========================================================================

def test_stabilize_no_claims():
    """No new claims when stabilizing, entropy maintained."""
    state = _make_state()
    original_claim_count = len(state.claims)
    ev = state.emoji_fields[0]
    original_length = ev.length

    # Set ceiling below current entropy so stabilize fires
    result = become_pure(state, entropy_ceiling=0.50, seed=42)

    assert result.stabilized == 1
    assert result.expanded == 0
    assert result.claims_spawned == 0
    assert len(state.claims) == original_claim_count

    # Vector should have grown (superposition emojis added)
    assert ev.length > original_length, "Stabilize should still mutate the vector"

    # Check history event
    paradox = state.paradoxes[0]
    stabilize_events = [h for h in paradox.history if h.get("event") == "become_stabilize"]
    assert len(stabilize_events) == 1

    print("  PASS: Stabilize does not spawn claims")


# =========================================================================
# Test 10: Full become_pure pass with mixed paradoxes
# =========================================================================

def test_full_become_pure_pass():
    """End-to-end with expanded, stabilized, and skipped paradoxes."""
    # Build state with 4 paradoxes targeting different outcomes
    claim_a = Claim(text="Autonomy is essential", confidence=0.7, source="test",
                    id="claim_0001", timestamp="2026-03-04T00:00:00+00:00")
    claim_b = Claim(text="Control is essential", confidence=0.6, source="test",
                    id="claim_0002", timestamp="2026-03-04T00:00:00+00:00")

    # Paradox 1: open, low entropy → expand
    # Use a sequence with repeated emojis to keep entropy low
    ev1_seq = ["\U0001f9ed", "\U0001f9ed", "\U0001f9ed", "\U0001f6e1\ufe0f"]
    ev1 = EmojiVector(sequence=ev1_seq, pole_a_emoji="\U0001f9ed",
                      pole_b_emoji="\U0001f6e1\ufe0f", id="ev_001",
                      last_updated="2026-03-04T00:00:00+00:00")
    assert ev1.entropy < 0.95, f"Test setup: ev1 entropy {ev1.entropy} should be < 0.95"
    p1 = _make_paradox(paradox_id="p_001", ev_id="ev_001", status="open")

    # Paradox 2: paradox_held, high entropy → stabilize (entropy=1.0)
    ev2 = _make_ev(ev_id="ev_002")  # entropy=1.0
    assert ev2.entropy >= 0.95, f"Test setup: ev2 entropy {ev2.entropy} should be >= 0.95"
    p2 = _make_paradox(paradox_id="p_002", ev_id="ev_002", status="paradox_held")

    # Paradox 3: collapsed_to_a → skip
    ev3 = _make_ev(ev_id="ev_003")
    p3 = _make_paradox(paradox_id="p_003", ev_id="ev_003", status="collapsed_to_a")

    # Paradox 4: open, no emoji vector → skip
    p4 = Paradox(
        pole_a=Pole(id="freedom", emoji="\U0001f9ed"),
        pole_b=Pole(id="order", emoji="\U0001f6e1\ufe0f"),
        status="open",
        id="p_004",
        timestamp="2026-03-04T00:00:00+00:00",
        emoji_vector_id=None,  # No EV
    )

    state = SystemState(
        claims=[claim_a, claim_b],
        tensions=[],
        paradoxes=[p1, p2, p3, p4],
        emoji_fields=[ev1, ev2, ev3],
        mission_id="M_test",
        iteration=1,
    )

    result = become_pure(state, entropy_ceiling=0.95, seed=42)

    assert result.total_eligible == 2, f"Expected 2 eligible, got {result.total_eligible}"
    assert result.expanded == 1, f"Expected 1 expanded, got {result.expanded}"
    assert result.stabilized == 1, f"Expected 1 stabilized, got {result.stabilized}"
    assert result.skipped == 2, f"Expected 2 skipped, got {result.skipped}"
    assert result.claims_spawned == 2, f"Expected 2 claims spawned, got {result.claims_spawned}"

    # Verify action map
    action_map = {a.paradox_id: a for a in result.actions}

    assert action_map["p_001"].decision == "expand"
    assert action_map["p_001"].claims_spawned == 2

    assert action_map["p_002"].decision == "stabilize"
    assert action_map["p_002"].claims_spawned == 0

    assert action_map["p_003"].decision == "skip"
    assert action_map["p_003"].skip_reason == "status=collapsed_to_a"

    assert action_map["p_004"].decision == "skip"
    assert action_map["p_004"].skip_reason == "no_emoji_vector"

    print("  PASS: Full become_pure pass with mixed paradoxes")


# =========================================================================
# Test 11: Phase 4 become_pass still importable (backward compat)
# =========================================================================

def test_phase4_become_pass_importable():
    """Phase 4 become_pass() family still importable — no contamination."""
    from SovereignNEXT.operators.become_expander import (
        become_pass,
        become_pass_targeted,
        become_pass_adaptive,
        expand_claim,
        select_targeted_claims,
    )
    # Just verify they exist and are callable
    assert callable(become_pass)
    assert callable(become_pass_targeted)
    assert callable(become_pass_adaptive)
    assert callable(expand_claim)
    assert callable(select_targeted_claims)
    print("  PASS: Phase 4 become_pass still importable")


# =========================================================================
# Test 12: Audit record completeness
# =========================================================================

def test_audit_record_complete():
    """BecomeAction has correct entropy_before/after, decision, counts."""
    state = _make_state()
    ev = state.emoji_fields[0]
    entropy_before = ev.entropy

    result = become_pure(state, entropy_ceiling=1.01, seed=42)

    assert len(result.actions) == 1
    action = result.actions[0]

    assert action.paradox_id == "paradox_test_001"
    assert action.decision == "expand"
    assert action.entropy_before == entropy_before
    assert action.entropy_after == ev.entropy
    assert action.vector_length_before == 4  # seed_initial_sequence produces 4 emojis
    assert action.vector_length_after == ev.length
    assert action.claims_spawned == 2
    assert action.skip_reason is None

    # Verify paradox history was updated
    paradox = state.paradoxes[0]
    expand_events = [h for h in paradox.history if h.get("event") == "become_expand"]
    assert len(expand_events) == 1
    assert "entropy_before" in expand_events[0]
    assert "claims_spawned" in expand_events[0]

    print("  PASS: Audit record completeness")


# =========================================================================
# Runner
# =========================================================================

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("PHASE 5 STEP 2b — BECOME OPERATOR UNIT TESTS")
    print("=" * 60 + "\n")

    tests = [
        test_eligibility_open_paradox,
        test_eligibility_collapsed_skipped,
        test_eligibility_paradox_held,
        test_entropy_gate_below_ceiling,
        test_entropy_gate_above_ceiling,
        test_expand_mutates_emoji_vector,
        test_expand_respects_length_limit,
        test_expand_spawns_claims,
        test_stabilize_no_claims,
        test_full_become_pure_pass,
        test_phase4_become_pass_importable,
        test_audit_record_complete,
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
        print("\nSTATUS: FAIL — Become operator not ready")
        sys.exit(1)
    else:
        print("\nSTATUS: PASS — Become operator is a pure state transformer")
        sys.exit(0)


if __name__ == "__main__":
    main()
