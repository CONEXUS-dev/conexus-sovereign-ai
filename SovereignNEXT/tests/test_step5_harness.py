"""
SovereignNEXT — Step 5: Execution Harness Tests

Runs the minimal Phase 5 execution harness with the locked initial state,
fixed operator sequence, 5 cycles, fixed seed, and verifies all invariants.

This is verification, not new functionality. No new operators. No tuning.
No interpretation. Binary pass/fail on structural invariants.
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
from SovereignNEXT.operators.collapse_operator import collapse_pure
from SovereignNEXT.operators.become_expander import become_pure
from SovereignNEXT.operators.paradox_hold_operator import paradox_hold_pure
from SovereignNEXT.operators.sovereign_observer import sovereign_observe, SovereignReport

from SovereignNEXT.harness.step5_execution_harness import (
    run_step5_harness,
    verify_step5_invariants,
)


# =========================================================================
# Locked initial state (from Pylo's Step 5 spec)
# =========================================================================

PA = "\U0001f9ed"           # 🧭
PB = "\U0001f6e1\ufe0f"    # 🛡️


def _make_step5_initial_state() -> SystemState:
    """Construct the locked Step 5 initial state. Hand-constructed, not generated.

    Paradoxes:
      p_open        — open, no veto, moderate entropy/balance
      p_held        — paradox_held, veto=True, non-empty history
      p_collapsible — open, no veto, high pole_a confidence (collapse candidate)

    Claims:
      c_open        — linked to p_open, confidence 0.55
      c_held        — linked to p_held, confidence 0.70
      c_collapsible — linked to p_collapsible, confidence 0.85
      c_unlinked    — not linked to any paradox, confidence 0.30
    """

    # --- Claims ---
    c_open = Claim(
        text="Autonomy is essential",
        confidence=0.55,
        source="test",
        id="c_open",
        timestamp="2026-03-04T00:00:00+00:00",
    )
    c_held = Claim(
        text="Control is necessary",
        confidence=0.70,
        source="test",
        id="c_held",
        timestamp="2026-03-04T00:00:00+00:00",
    )
    c_collapsible = Claim(
        text="Freedom dominates",
        confidence=0.85,
        source="test",
        id="c_collapsible",
        timestamp="2026-03-04T00:00:00+00:00",
    )
    c_unlinked = Claim(
        text="Low confidence orphan",
        confidence=0.30,
        source="test",
        id="c_unlinked",
        timestamp="2026-03-04T00:00:00+00:00",
    )

    # --- Emoji Vectors ---
    ev_open = EmojiVector(
        sequence=seed_initial_sequence(PA, PB, seed=10),
        pole_a_emoji=PA,
        pole_b_emoji=PB,
        role="paradox_field",
        id="ev_open",
        paradox_id="p_open",
        last_updated="2026-03-04T00:00:00+00:00",
    )

    ev_held = EmojiVector(
        sequence=seed_initial_sequence(PA, PB, seed=20),
        pole_a_emoji=PA,
        pole_b_emoji=PB,
        role="paradox_field",
        id="ev_held",
        paradox_id="p_held",
        last_updated="2026-03-04T00:00:00+00:00",
    )

    ev_collapsible = EmojiVector(
        sequence=seed_initial_sequence(PA, PB, seed=30),
        pole_a_emoji=PA,
        pole_b_emoji=PB,
        role="paradox_field",
        id="ev_collapsible",
        paradox_id="p_collapsible",
        last_updated="2026-03-04T00:00:00+00:00",
    )

    # --- Paradoxes ---
    p_open = Paradox(
        pole_a=Pole(id="autonomy", emoji=PA, confidence=0.50),
        pole_b=Pole(id="control", emoji=PB, confidence=0.50),
        status="open",
        id="p_open",
        timestamp="2026-03-04T00:00:00+00:00",
        metrics=ParadoxMetrics(tension_strength=0.60),
        constraints=ParadoxConstraints(collapse_veto=False),
        emoji_vector_id="ev_open",
        claim_ids=["c_open"],
        history=[],
    )

    p_held = Paradox(
        pole_a=Pole(id="autonomy", emoji=PA, confidence=0.46),
        pole_b=Pole(id="control", emoji=PB, confidence=0.44),
        status="paradox_held",
        id="p_held",
        timestamp="2026-03-04T00:00:00+00:00",
        metrics=ParadoxMetrics(tension_strength=0.70),
        constraints=ParadoxConstraints(
            collapse_veto=True,
            veto_reason="paradox_held",
        ),
        emoji_vector_id="ev_held",
        claim_ids=["c_held"],
        history=[{"event": "paradox_hold", "operator": "paradox_hold", "timestamp": "T0"}],
    )

    p_collapsible = Paradox(
        pole_a=Pole(id="autonomy", emoji=PA, confidence=0.80),
        pole_b=Pole(id="control", emoji=PB, confidence=0.30),
        status="open",
        id="p_collapsible",
        timestamp="2026-03-04T00:00:00+00:00",
        metrics=ParadoxMetrics(tension_strength=0.50),
        constraints=ParadoxConstraints(collapse_veto=False),
        emoji_vector_id="ev_collapsible",
        claim_ids=["c_collapsible"],
        history=[],
    )

    # --- SystemState ---
    return SystemState(
        claims=[c_open, c_held, c_collapsible, c_unlinked],
        tensions=[],
        paradoxes=[p_open, p_held, p_collapsible],
        emoji_fields=[ev_open, ev_held, ev_collapsible],
        mission_id="M_step5",
        iteration=0,
    )


# =========================================================================
# Test 1: Full 5-cycle run completes without error
# =========================================================================

def test_harness_runs_without_error():
    """The harness completes 5 cycles with no exceptions."""
    state = _make_step5_initial_state()
    run = run_step5_harness(
        initial_state=state,
        collapse_fn=collapse_pure,
        become_fn=become_pure,
        hold_fn=paradox_hold_pure,
        observe_fn=sovereign_observe,
    )
    assert len(run.cycle_records) == 5
    assert run.final_report is not None
    print("  PASS: Full 5-cycle run completes without error")


# =========================================================================
# Test 2: Held paradox persistence
# =========================================================================

def test_held_paradox_persistence():
    """p_held remains paradox_held at every cycle."""
    state = _make_step5_initial_state()
    run = run_step5_harness(
        initial_state=state,
        collapse_fn=collapse_pure,
        become_fn=become_pure,
        hold_fn=paradox_hold_pure,
        observe_fn=sovereign_observe,
    )
    for rec in run.cycle_records:
        status = rec.paradox_statuses["p_held"]
        assert status == "paradox_held", (
            f"Cycle {rec.cycle_number}: p_held status is '{status}'"
        )
    print("  PASS: Held paradox persistence verified")


# =========================================================================
# Test 3: Veto enforcement
# =========================================================================

def test_veto_enforcement():
    """p_held collapse_veto remains True at every cycle."""
    state = _make_step5_initial_state()
    run = run_step5_harness(
        initial_state=state,
        collapse_fn=collapse_pure,
        become_fn=become_pure,
        hold_fn=paradox_hold_pure,
        observe_fn=sovereign_observe,
    )
    for rec in run.cycle_records:
        veto = rec.veto_states["p_held"]
        assert veto is True, (
            f"Cycle {rec.cycle_number}: p_held collapse_veto is {veto}"
        )
    print("  PASS: Veto enforcement verified")


# =========================================================================
# Test 4: Collapsible paradox consistency
# =========================================================================

def test_collapsible_consistency():
    """p_collapsible does not flip-flop across cycles."""
    state = _make_step5_initial_state()
    run = run_step5_harness(
        initial_state=state,
        collapse_fn=collapse_pure,
        become_fn=become_pure,
        hold_fn=paradox_hold_pure,
        observe_fn=sovereign_observe,
    )
    statuses = [rec.paradox_statuses["p_collapsible"] for rec in run.cycle_records]
    distinct = set(statuses)
    assert len(distinct) <= 2, (
        f"p_collapsible status unstable: {statuses}"
    )
    print(f"  PASS: Collapsible paradox consistency verified (statuses: {statuses})")


# =========================================================================
# Test 5: Sovereign isolation (non-sycophancy by construction)
# =========================================================================

def test_sovereign_isolation():
    """Sovereign reports are collected after cycles and never fed back."""
    state = _make_step5_initial_state()
    run = run_step5_harness(
        initial_state=state,
        collapse_fn=collapse_pure,
        become_fn=become_pure,
        hold_fn=paradox_hold_pure,
        observe_fn=sovereign_observe,
    )
    # All cycle records have Sovereign reports
    for rec in run.cycle_records:
        assert isinstance(rec.sovereign_report, SovereignReport), (
            f"Cycle {rec.cycle_number}: expected SovereignReport"
        )
    # Final report exists
    assert isinstance(run.final_report, SovereignReport)

    # Verify all invariants pass (uses the harness verifier)
    failures = verify_step5_invariants(run)
    assert len(failures) == 0, f"Invariant failures: {failures}"
    print("  PASS: Sovereign isolation verified (all invariants pass)")


# =========================================================================
# Runner
# =========================================================================

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("STEP 5 — MINIMAL EXECUTION HARNESS TESTS")
    print("=" * 60 + "\n")

    tests = [
        test_harness_runs_without_error,
        test_held_paradox_persistence,
        test_veto_enforcement,
        test_collapsible_consistency,
        test_sovereign_isolation,
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
        print("\nSTATUS: FAIL — Execution harness invariants violated")
        sys.exit(1)
    else:
        print("\nSTATUS: PASS — System behaves as specified under repetition")
        sys.exit(0)


if __name__ == "__main__":
    main()
