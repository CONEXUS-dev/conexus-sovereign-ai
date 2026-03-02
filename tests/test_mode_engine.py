"""
CONEXUS Mode Engine Test Suite — Phase C Validation.

Tests hybrid Collapse/Become mode switching at phase boundaries.
Run with: python tests/test_mode_engine.py
         or: pytest tests/test_mode_engine.py -v
"""

import sys
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from sovereign.mode_engine import ModeEngine
from sovereign.gear_state import GearState


# =========================================================================
# Test 1: Initial mode — strong collapse signals
# =========================================================================

def test_initial_mode_collapse_signals():
    """Strong execution signals should override home mode to Collapse."""
    engine = ModeEngine()
    mode = engine.determine_initial_mode(
        "Execute the deployment plan and fix the CI pipeline and optimize build",
        "become"  # home mode is become, but signals say collapse
    )
    assert mode == "collapse", f"Expected 'collapse', got '{mode}'"
    print("  [PASS] test_initial_mode_collapse_signals")


# =========================================================================
# Test 2: Initial mode — strong become signals
# =========================================================================

def test_initial_mode_become_signals():
    """Strong creative signals should override home mode to Become."""
    engine = ModeEngine()
    mode = engine.determine_initial_mode(
        "Explore the possibilities of quantum creativity and imagine new designs and dream",
        "collapse"  # home mode is collapse, but signals say become
    )
    assert mode == "become", f"Expected 'become', got '{mode}'"
    print("  [PASS] test_initial_mode_become_signals")


# =========================================================================
# Test 3: Initial mode — ambiguous falls back to home mode
# =========================================================================

def test_initial_mode_ambiguous():
    """Ambiguous input should fall back to the agent's home mode."""
    engine = ModeEngine()

    mode_c = engine.determine_initial_mode("Do something interesting", "collapse")
    assert mode_c == "collapse", f"Expected 'collapse', got '{mode_c}'"

    mode_b = engine.determine_initial_mode("Do something interesting", "become")
    assert mode_b == "become", f"Expected 'become', got '{mode_b}'"

    print("  [PASS] test_initial_mode_ambiguous")


# =========================================================================
# Test 4: Phase boundary — deep paradox keeps Become
# =========================================================================

def test_boundary_deep_paradox_stays_become():
    """Deep paradox at gravity well should keep Become mode."""
    engine = ModeEngine()
    gs = GearState(mission_id="test_c4", home_mode="become")
    gs.active_mode = "become"
    gs.current_gear = 5  # End of Gravity Well

    switch = engine.evaluate_at_phase_boundary(
        gs, "This tension cannot be resolved; both are true and must hold both"
    )
    assert switch is None, f"Expected None (stay in Become), got '{switch}'"
    print("  [PASS] test_boundary_deep_paradox_stays_become")


# =========================================================================
# Test 5: Phase boundary — resolution emerges → switch to Collapse
# =========================================================================

def test_boundary_resolution_switches_to_collapse():
    """Clear resolution at gravity well should switch from Become to Collapse."""
    engine = ModeEngine()
    gs = GearState(mission_id="test_c5", home_mode="become")
    gs.active_mode = "become"
    gs.current_gear = 5  # End of Gravity Well

    switch = engine.evaluate_at_phase_boundary(
        gs, "The answer is clearly to prioritize security and the solution must be implemented"
    )
    assert switch == "collapse", f"Expected 'collapse', got '{switch}'"
    print("  [PASS] test_boundary_resolution_switches_to_collapse")


# =========================================================================
# Test 6: Phase boundary — deep paradox in Collapse → switch to Become
# =========================================================================

def test_boundary_paradox_switches_to_become():
    """Deep paradox in Collapse mode should switch to Become."""
    engine = ModeEngine()
    gs = GearState(mission_id="test_c6", home_mode="collapse")
    gs.active_mode = "collapse"
    gs.current_gear = 5  # End of Gravity Well

    switch = engine.evaluate_at_phase_boundary(
        gs, "There is a fundamental paradox here that cannot be resolved"
    )
    assert switch == "become", f"Expected 'become', got '{switch}'"
    print("  [PASS] test_boundary_paradox_switches_to_become")


# =========================================================================
# Test 7: Phase boundary — no switch when neutral output
# =========================================================================

def test_boundary_no_switch_neutral():
    """Neutral output at phase boundary should not trigger a switch."""
    engine = ModeEngine()
    gs = GearState(mission_id="test_c7", home_mode="collapse")
    gs.active_mode = "collapse"
    gs.current_gear = 5

    switch = engine.evaluate_at_phase_boundary(
        gs, "The analysis continues with several interesting findings"
    )
    assert switch is None, f"Expected None, got '{switch}'"
    print("  [PASS] test_boundary_no_switch_neutral")


# =========================================================================
# Test 8: Phase boundary — release_forge phase evaluation
# =========================================================================

def test_boundary_release_forge():
    """Phase III→IV boundary evaluation should work correctly."""
    engine = ModeEngine()
    gs = GearState(mission_id="test_c8", home_mode="become")
    gs.active_mode = "become"
    gs.current_gear = 8  # End of Release & Forge

    # Resolution emerged during release → switch to collapse
    switch = engine.evaluate_at_phase_boundary(
        gs, "Therefore the solution is clear and resolves to a single directive"
    )
    assert switch == "collapse", f"Expected 'collapse', got '{switch}'"

    # New paradox in collapse → switch to become
    gs.active_mode = "collapse"
    switch2 = engine.evaluate_at_phase_boundary(
        gs, "A new irreducible tension has emerged that cannot be resolved"
    )
    assert switch2 == "become", f"Expected 'become', got '{switch2}'"

    print("  [PASS] test_boundary_release_forge")


# =========================================================================
# Runner
# =========================================================================

def run_all():
    from datetime import datetime
    print("=" * 60)
    print("CONEXUS Mode Engine Test Suite — Phase C")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    tests = [
        test_initial_mode_collapse_signals,
        test_initial_mode_become_signals,
        test_initial_mode_ambiguous,
        test_boundary_deep_paradox_stays_become,
        test_boundary_resolution_switches_to_collapse,
        test_boundary_paradox_switches_to_become,
        test_boundary_no_switch_neutral,
        test_boundary_release_forge,
    ]

    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test_fn.__name__}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{passed + failed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
