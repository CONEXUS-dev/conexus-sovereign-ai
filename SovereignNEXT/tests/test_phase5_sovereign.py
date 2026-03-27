"""
SovereignNEXT — Phase 5 Step 3: Sovereign Observer Unit Tests

Tests proving read-only observation, deterministic output, schema correctness,
belief stratification, integrity attestations, anomaly detection, and
backward compatibility.

No LLM calls. No state mutation. Pure Python, pure observation.
"""

import sys
import os

# Ensure SovereignNEXT is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from SovereignNEXT.state.emoji_vector import EmojiVector
from SovereignNEXT.state.paradox import (
    Paradox, Pole, ParadoxMetrics, ParadoxConstraints,
)
from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.emoji_mutator import seed_initial_sequence
from SovereignNEXT.operators.sovereign_observer import sovereign_observe


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
    veto=False,
    history=None,
    claim_ids=None,
):
    constraints = ParadoxConstraints(
        collapse_veto=veto,
        veto_reason="paradox_held" if veto else "",
    )
    return Paradox(
        pole_a=Pole(id="autonomy", emoji="\U0001f9ed", confidence=0.50),
        pole_b=Pole(id="control", emoji="\U0001f6e1\ufe0f", confidence=0.50),
        status=status,
        id=paradox_id,
        timestamp="2026-03-04T00:00:00+00:00",
        metrics=ParadoxMetrics(tension_strength=0.84),
        constraints=constraints,
        emoji_vector_id=ev_id,
        claim_ids=claim_ids or ["claim_0001", "claim_0002"],
        mission_ids=["M_test"],
        history=history or [],
    )


def _make_rich_state():
    """Create a state with multiple paradoxes in different statuses for testing."""
    claims = [
        Claim(text="Autonomy is essential", confidence=0.8, source="test",
              id="claim_0001", timestamp="2026-03-04T00:00:00+00:00"),
        Claim(text="Control is essential", confidence=0.75, source="test",
              id="claim_0002", timestamp="2026-03-04T00:00:00+00:00"),
        Claim(text="Freedom matters", confidence=0.3, source="test",
              id="claim_0003", timestamp="2026-03-04T00:00:00+00:00"),
        Claim(text="Low confidence orphan", confidence=0.2, source="test",
              id="claim_0004", timestamp="2026-03-04T00:00:00+00:00"),
    ]

    # P1: open, low entropy
    ev1 = _make_ev(ev_id="ev_001", sequence=["\U0001f9ed"] * 3 + ["\U0001f6e1\ufe0f"] * 3)
    p1 = _make_paradox(
        paradox_id="p_001", ev_id="ev_001", status="open",
        history=[
            {"event": "become_expand", "operator": "become", "timestamp": "T1"},
        ],
    )

    # P2: paradox_held, veto locked
    ev2 = _make_ev(ev_id="ev_002")
    p2 = _make_paradox(
        paradox_id="p_002", ev_id="ev_002", status="paradox_held", veto=True,
        history=[
            {"event": "paradox_hold", "operator": "paradox_hold", "timestamp": "T2"},
            {"event": "become_stabilize", "operator": "become", "timestamp": "T3"},
        ],
    )

    # P3: collapsed_to_a
    ev3 = _make_ev(ev_id="ev_003")
    p3 = _make_paradox(
        paradox_id="p_003", ev_id="ev_003", status="collapsed_to_a",
        claim_ids=["claim_0001", "claim_0002"],
        history=[
            {"event": "commit_to_a", "operator": "collapse", "timestamp": "T4"},
        ],
    )

    # P4: open, no history (for anomaly: not stuck since it's open)
    ev4 = _make_ev(ev_id="ev_004")
    p4 = _make_paradox(
        paradox_id="p_004", ev_id="ev_004", status="open",
        claim_ids=["claim_0003"],
    )

    return SystemState(
        claims=claims,
        tensions=[],
        paradoxes=[p1, p2, p3, p4],
        emoji_fields=[ev1, ev2, ev3, ev4],
        mission_id="M_test",
        iteration=1,
    )


# =========================================================================
# Test 1: Paradox counts by status
# =========================================================================

def test_paradox_counts_by_status():
    """Report produces correct paradox counts by status."""
    state = _make_rich_state()
    report = sovereign_observe(state)

    assert report.paradox_counts_by_status.get("open", 0) == 2
    assert report.paradox_counts_by_status.get("paradox_held", 0) == 1
    assert report.paradox_counts_by_status.get("collapsed_to_a", 0) == 1
    print("  PASS: Report produces correct paradox counts by status")


# =========================================================================
# Test 2: Entropy band distribution
# =========================================================================

def test_entropy_band_distribution():
    """Entropy band classification: below/within/above."""
    state = _make_rich_state()
    report = sovereign_observe(state)

    total = sum(report.entropy_band_distribution.values())
    assert total == 4, f"Expected 4 EVs classified, got {total}"
    assert "below_band" in report.entropy_band_distribution
    assert "within_band" in report.entropy_band_distribution
    assert "above_band" in report.entropy_band_distribution
    print("  PASS: Entropy band distribution correct")


# =========================================================================
# Test 3: Balance window distribution
# =========================================================================

def test_balance_window_distribution():
    """Balance window classification: below/within/above."""
    state = _make_rich_state()
    report = sovereign_observe(state)

    total = sum(report.balance_window_distribution.values())
    assert total == 4, f"Expected 4 EVs classified, got {total}"
    assert "below_window" in report.balance_window_distribution
    assert "within_window" in report.balance_window_distribution
    assert "above_window" in report.balance_window_distribution
    print("  PASS: Balance window distribution correct")


# =========================================================================
# Test 4: Veto summary
# =========================================================================

def test_veto_summary():
    """Locked/unlocked counts match state."""
    state = _make_rich_state()
    report = sovereign_observe(state)

    assert report.veto_summary["veto_locked"] == 1, (
        f"Expected 1 locked, got {report.veto_summary['veto_locked']}"
    )
    assert report.veto_summary["veto_unlocked"] == 3, (
        f"Expected 3 unlocked, got {report.veto_summary['veto_unlocked']}"
    )
    print("  PASS: Veto summary accurate")


# =========================================================================
# Test 5: ParadoxDigest surfaces both poles
# =========================================================================

def test_digest_surfaces_both_poles():
    """ParadoxDigest includes both pole IDs — paradox preservation rule."""
    state = _make_rich_state()
    report = sovereign_observe(state)

    for digest in report.paradox_digests:
        assert digest.pole_a != "", f"Paradox {digest.paradox_id}: pole_a is empty"
        assert digest.pole_b != "", f"Paradox {digest.paradox_id}: pole_b is empty"
        assert digest.pole_a != digest.pole_b, (
            f"Paradox {digest.paradox_id}: poles must be distinct"
        )
    print("  PASS: ParadoxDigest surfaces both poles")


# =========================================================================
# Test 6: ParadoxDigest includes recent actions
# =========================================================================

def test_digest_includes_recent_actions():
    """ParadoxDigest extracts history entries."""
    state = _make_rich_state()
    report = sovereign_observe(state)

    digest_map = {d.paradox_id: d for d in report.paradox_digests}

    # P1 has 1 history event
    assert len(digest_map["p_001"].recent_actions) == 1
    assert digest_map["p_001"].recent_actions[0]["operator"] == "become"

    # P2 has 2 history events
    assert len(digest_map["p_002"].recent_actions) == 2

    # P4 has no history
    assert len(digest_map["p_004"].recent_actions) == 0

    print("  PASS: ParadoxDigest includes recent actions")


# =========================================================================
# Test 7: OperatorLedger groups by operator
# =========================================================================

def test_operator_ledger_groups():
    """OperatorLedger separates Collapse/Become/Hold."""
    state = _make_rich_state()
    report = sovereign_observe(state)

    ledger_map = {led.operator_name: led for led in report.operator_ledgers}

    assert "become" in ledger_map, "Become operator should appear in ledger"
    assert "paradox_hold" in ledger_map, "ParadoxHold operator should appear in ledger"
    assert "collapse" in ledger_map, "Collapse operator should appear in ledger"

    # Become has 2 events across 2 paradoxes
    assert sum(ledger_map["become"].action_counts.values()) == 2
    assert len(ledger_map["become"].affected_paradox_ids) == 2

    print("  PASS: OperatorLedger groups by operator")


# =========================================================================
# Test 8: Belief stratification partitions correctly
# =========================================================================

def test_belief_stratification():
    """Four disjoint categories derived from state."""
    state = _make_rich_state()
    report = sovereign_observe(state)

    strat = report.belief_stratification

    # Committed: claim_0001 and claim_0002 linked to collapsed p_003 with confidence >= 0.7
    assert "claim_0001" in strat["committed"]
    assert "claim_0002" in strat["committed"]

    # Held: p_002
    assert "p_002" in strat["held"]

    # Open: p_001, p_004
    assert "p_001" in strat["open"]
    assert "p_004" in strat["open"]

    # Deferred: claim_0004 (low confidence, not linked to any paradox)
    assert "claim_0004" in strat["deferred"]

    # claim_0003 is linked to p_004 so it should NOT be deferred
    assert "claim_0003" not in strat["deferred"]

    print("  PASS: Belief stratification partitions correctly")


# =========================================================================
# Test 9: Integrity attestations produced
# =========================================================================

def test_integrity_attestations():
    """Invariant checks run and produce attestation strings."""
    state = _make_rich_state()
    report = sovereign_observe(state)

    assert len(report.integrity_attestations) >= 2, (
        f"Expected at least 2 attestations, got {len(report.integrity_attestations)}"
    )

    # Should include veto continuity and EV link checks
    att_text = " ".join(report.integrity_attestations)
    assert "veto" in att_text.lower() or "VIOLATION" in att_text
    assert "Phase 4" in att_text or "VIOLATION" in att_text

    print("  PASS: Integrity attestations produced")


# =========================================================================
# Test 10: Anomaly flags are descriptive only
# =========================================================================

def test_anomaly_flags_descriptive():
    """Anomaly flags contain no prescriptive language."""
    # Create a state with a stuck paradox (held, no history)
    ev = _make_ev(ev_id="ev_stuck")
    p_stuck = _make_paradox(
        paradox_id="p_stuck", ev_id="ev_stuck", status="paradox_held",
        veto=True, history=[],
    )
    state = SystemState(
        claims=[], tensions=[], paradoxes=[p_stuck],
        emoji_fields=[ev], mission_id="M_test", iteration=1,
    )

    report = sovereign_observe(state)

    assert len(report.anomaly_flags) >= 1, "Expected at least 1 anomaly flag"
    assert "stuck" in report.anomaly_flags[0]

    # Verify no prescriptive language
    forbidden = ["should", "recommend", "consider", "next", "optimize", "trigger"]
    for flag in report.anomaly_flags:
        for word in forbidden:
            assert word not in flag.lower(), (
                f"Anomaly flag contains prescriptive word '{word}': {flag}"
            )

    print("  PASS: Anomaly flags are descriptive only")


# =========================================================================
# Test 11: State not mutated after observe
# =========================================================================

def test_state_not_mutated():
    """Content hash unchanged after sovereign_observe()."""
    state = _make_rich_state()
    hash_before = state.content_hash()

    sovereign_observe(state)

    hash_after = state.content_hash()
    assert hash_before == hash_after, (
        f"State hash changed: {hash_before} → {hash_after}"
    )
    print("  PASS: State not mutated after observe")


# =========================================================================
# Test 12: Deterministic output
# =========================================================================

def test_deterministic_output():
    """Same state → same report (excluding timestamp)."""
    state = _make_rich_state()

    report1 = sovereign_observe(state)
    report2 = sovereign_observe(state)

    # State hash must be identical
    assert report1.state_hash == report2.state_hash

    # Paradox counts must be identical
    assert report1.paradox_counts_by_status == report2.paradox_counts_by_status

    # Entropy distribution must be identical
    assert report1.entropy_band_distribution == report2.entropy_band_distribution

    # Balance distribution must be identical
    assert report1.balance_window_distribution == report2.balance_window_distribution

    # Veto summary must be identical
    assert report1.veto_summary == report2.veto_summary

    # Belief stratification must be identical
    assert report1.belief_stratification == report2.belief_stratification

    # Digests must be identical
    assert len(report1.paradox_digests) == len(report2.paradox_digests)
    for d1, d2 in zip(report1.paradox_digests, report2.paradox_digests):
        assert d1.paradox_id == d2.paradox_id
        assert d1.entropy == d2.entropy
        assert d1.balance == d2.balance
        assert d1.veto_state == d2.veto_state

    # Ledgers must be identical
    assert len(report1.operator_ledgers) == len(report2.operator_ledgers)
    for led1, led2 in zip(report1.operator_ledgers, report2.operator_ledgers):
        assert led1.operator_name == led2.operator_name
        assert led1.action_counts == led2.action_counts

    print("  PASS: Deterministic output")


# =========================================================================
# Test 13: Empty state produces valid report
# =========================================================================

def test_empty_state():
    """Edge case: no paradoxes, no claims — should not crash."""
    state = SystemState(
        claims=[], tensions=[], paradoxes=[], emoji_fields=[],
        mission_id="M_empty", iteration=0,
    )

    report = sovereign_observe(state)

    assert report.state_hash != ""
    assert report.paradox_counts_by_status == {}
    assert sum(report.entropy_band_distribution.values()) == 0
    assert sum(report.balance_window_distribution.values()) == 0
    assert report.veto_summary == {"veto_locked": 0, "veto_unlocked": 0}
    assert len(report.paradox_digests) == 0
    assert len(report.operator_ledgers) == 0
    assert report.belief_stratification == {
        "committed": [], "held": [], "open": [], "deferred": [],
    }
    print("  PASS: Empty state produces valid report")


# =========================================================================
# Test 14: Phase 4 backward compatibility
# =========================================================================

def test_phase4_backward_compatibility():
    """Existing operators still importable — Sovereign introduces no conflicts."""
    from SovereignNEXT.operators.collapse_operator import collapse_once, collapse_pure
    from SovereignNEXT.operators.become_expander import become_pass, become_pure
    from SovereignNEXT.operators.paradox_hold_operator import paradox_hold_pure

    assert callable(collapse_once)
    assert callable(collapse_pure)
    assert callable(become_pass)
    assert callable(become_pure)
    assert callable(paradox_hold_pure)
    print("  PASS: Phase 4 backward compatibility")


# =========================================================================
# Runner
# =========================================================================

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("PHASE 5 STEP 3 — SOVEREIGN OBSERVER UNIT TESTS")
    print("=" * 60 + "\n")

    tests = [
        test_paradox_counts_by_status,
        test_entropy_band_distribution,
        test_balance_window_distribution,
        test_veto_summary,
        test_digest_surfaces_both_poles,
        test_digest_includes_recent_actions,
        test_operator_ledger_groups,
        test_belief_stratification,
        test_integrity_attestations,
        test_anomaly_flags_descriptive,
        test_state_not_mutated,
        test_deterministic_output,
        test_empty_state,
        test_phase4_backward_compatibility,
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
        print("\nSTATUS: FAIL — Sovereign observer not ready")
        sys.exit(1)
    else:
        print("\nSTATUS: PASS — Sovereign is a pure read-only observer")
        sys.exit(0)


if __name__ == "__main__":
    main()
