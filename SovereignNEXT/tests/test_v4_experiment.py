"""
SovereignNEXT — V4 Controlled Experiment Tests

Verifies that the frozen Phase 5 operators behave correctly on the
production-scale V3 snapshot (54 paradoxes, 327 tensions, 154 claims)
over 3 hash-chained cycles.

This is evidence verification, not new functionality.
Binary invariants only. No interpretation. No tuning.
"""

import sys
import os

# Ensure SovereignNEXT is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.sovereign_observer import SovereignReport

from SovereignNEXT.harness.v4_controlled_experiment import (
    load_v3_snapshot,
    run_v4_experiment,
    verify_v4_invariants,
    save_v4_artifacts,
    COLLAPSED_STATUSES,
)


# =========================================================================
# Helpers
# =========================================================================

SNAPSHOT_PATH = os.path.join(
    os.path.dirname(__file__),
    "v3_final_state_snapshot.json",
)

OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "tests",
)

# Cache the experiment result so we only run once
_cached_result = None
_cached_state = None


def _get_result():
    """Run the experiment once and cache."""
    global _cached_result, _cached_state
    if _cached_result is None:
        _cached_state, _, _ = load_v3_snapshot(SNAPSHOT_PATH)
        _cached_result = run_v4_experiment(SNAPSHOT_PATH)
    return _cached_result


# =========================================================================
# Test 1: V3 snapshot loads without error
# =========================================================================

def test_v3_snapshot_loads():
    """V3 snapshot deserializes into a valid SystemState."""
    state, input_hash, file_hash = load_v3_snapshot(SNAPSHOT_PATH)

    assert isinstance(state, SystemState)
    assert len(state.paradoxes) == 54, f"Expected 54 paradoxes, got {len(state.paradoxes)}"
    assert len(state.tensions) == 327, f"Expected 327 tensions, got {len(state.tensions)}"
    assert len(state.claims) == 154, f"Expected 154 claims, got {len(state.claims)}"
    assert len(state.emoji_fields) == 54, f"Expected 54 EVs, got {len(state.emoji_fields)}"

    assert len(input_hash) == 64, "content_hash should be 64-char hex"
    assert len(file_hash) == 64, "file_bytes_hash should be 64-char hex"

    # Determinism: reload and recompute
    _, input_hash2, _ = load_v3_snapshot(SNAPSHOT_PATH)
    assert input_hash == input_hash2, "content_hash must be deterministic on reload"

    print("  PASS: V3 snapshot loads without error")


# =========================================================================
# Test 2: 3-cycle run completes
# =========================================================================

def test_3_cycle_run_completes():
    """The experiment runs 3 full cycles without crashing."""
    result = _get_result()

    assert len(result.cycle_records) == 3, (
        f"Expected 3 cycle records, got {len(result.cycle_records)}"
    )
    assert result.final_report is not None, "Final Sovereign report missing"
    assert len(result.final_state_hash) == 64, "Final state hash missing"

    print("  PASS: 3-cycle run completes")


# =========================================================================
# Test 3: held_set from cycle 1 persists in cycles 2-3
# =========================================================================

def test_held_set_persistence():
    """Every paradox held after cycle 1 remains held in cycles 2-3."""
    result = _get_result()

    assert len(result.held_set_cycle1) > 0, (
        "No paradoxes were held after cycle 1 — experiment is vacuous"
    )

    for rec in result.cycle_records:
        if rec.cycle_number <= 1:
            continue
        for pid in result.held_set_cycle1:
            status = rec.paradox_statuses.get(pid)
            assert status == "paradox_held", (
                f"Cycle {rec.cycle_number}: {pid} status is '{status}', "
                f"expected 'paradox_held'"
            )

    print(f"  PASS: held_set persistence verified "
          f"({len(result.held_set_cycle1)} paradoxes held across 3 cycles)")


# =========================================================================
# Test 4: veto_set from cycle 1 never collapses in cycles 2-3
# =========================================================================

def test_veto_enforcement():
    """No vetoed paradox transitions to a collapsed status."""
    result = _get_result()

    assert len(result.veto_set_cycle1) > 0, (
        "No paradoxes had veto after cycle 1 — experiment is vacuous"
    )

    for rec in result.cycle_records:
        if rec.cycle_number <= 1:
            continue
        for pid in result.veto_set_cycle1:
            status = rec.paradox_statuses.get(pid)
            assert status not in COLLAPSED_STATUSES, (
                f"Cycle {rec.cycle_number}: {pid} collapsed despite veto "
                f"(status: '{status}')"
            )

    print(f"  PASS: Veto enforcement verified "
          f"({len(result.veto_set_cycle1)} vetoed paradoxes protected)")


# =========================================================================
# Test 5: State hashes chain correctly from input_hash
# =========================================================================

def test_hash_chain_integrity():
    """Each cycle produces a valid state hash and they form a chain."""
    result = _get_result()

    # Input hash exists
    assert len(result.input_content_hash) == 64
    assert len(result.file_bytes_hash) == 64

    # Each cycle has a hash
    hashes = [result.input_content_hash]
    for rec in result.cycle_records:
        assert len(rec.state_hash) == 64, (
            f"Cycle {rec.cycle_number}: missing state hash"
        )
        hashes.append(rec.state_hash)

    # Final hash matches last cycle
    assert result.final_state_hash == result.cycle_records[-1].state_hash, (
        "Final state hash doesn't match last cycle hash"
    )

    # At least cycle 1 hash differs from input (operators did something)
    assert hashes[1] != hashes[0], (
        "Cycle 1 hash equals input hash — operators had no effect"
    )

    print(f"  PASS: Hash chain integrity verified "
          f"({len(hashes)} hashes in chain)")


# =========================================================================
# Test 6: Sovereign reports collected, never fed back
# =========================================================================

def test_sovereign_isolation():
    """Sovereign reports exist at every checkpoint and are never fed back."""
    result = _get_result()

    for rec in result.cycle_records:
        assert isinstance(rec.sovereign_report, SovereignReport), (
            f"Cycle {rec.cycle_number}: expected SovereignReport"
        )
    assert isinstance(result.final_report, SovereignReport), (
        "Final observation should be SovereignReport"
    )

    # Full invariant verification passes
    failures = verify_v4_invariants(result)
    assert len(failures) == 0, f"Invariant failures: {failures}"

    print("  PASS: Sovereign isolation verified (all invariants pass)")


# =========================================================================
# Runner
# =========================================================================

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("V4 CONTROLLED EXPERIMENT — PRODUCTION-SCALE VERIFICATION")
    print("=" * 60 + "\n")

    tests = [
        test_v3_snapshot_loads,
        test_3_cycle_run_completes,
        test_held_set_persistence,
        test_veto_enforcement,
        test_hash_chain_integrity,
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

    # Print experiment summary
    result = _get_result()
    print(f"\n{'=' * 60}")
    print("EXPERIMENT SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Input hash:       {result.input_content_hash[:16]}...")
    print(f"  File bytes hash:  {result.file_bytes_hash[:16]}...")
    print(f"  Final state hash: {result.final_state_hash[:16]}...")
    print(f"  Held set (cycle 1): {len(result.held_set_cycle1)} paradoxes")
    print(f"  Veto set (cycle 1): {len(result.veto_set_cycle1)} paradoxes")
    for rec in result.cycle_records:
        from collections import Counter
        status_counts = dict(Counter(rec.paradox_statuses.values()))
        print(f"  Cycle {rec.cycle_number}: hash={rec.state_hash[:12]}... "
              f"statuses={status_counts}")

    # Save artifacts
    output_dir = os.path.join(os.path.dirname(__file__))
    saved = save_v4_artifacts(_cached_state, result, output_dir)
    print("\n  Artifacts saved:")
    for name, path in saved.items():
        print(f"    {name}: {os.path.basename(path)}")

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'=' * 60}")

    if failed > 0:
        print("\nSTATUS: FAIL — V4 invariants violated")
        sys.exit(1)
    else:
        print("\nSTATUS: PASS — Phase 5 operators verified at production scale")
        sys.exit(0)


if __name__ == "__main__":
    main()
