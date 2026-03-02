"""
CONEXUS Gear State Test Suite — Phase A Validation.

Tests the Nine Gears cognitive state tracking infrastructure.
Run with: python tests/test_gear_state.py
         or: pytest tests/test_gear_state.py -v
"""

import json
import sys
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from sovereign.gear_state import GearState, GEAR_NAMES, PHASE_MAP


# =========================================================================
# Test 1: Creation with defaults
# =========================================================================

def test_gear_state_defaults():
    """GearState initializes with correct defaults."""
    gs = GearState(mission_id="test_001")
    assert gs.mission_id == "test_001"
    assert gs.current_gear == 1
    assert gs.active_mode == "neutral"
    assert gs.home_mode == "collapse"
    assert gs.rapport_established is False
    assert gs.truth_statement is None
    assert gs.symbolic_field is None
    assert gs.contradictions == []
    assert gs.held_paradoxes == []
    assert gs.resolved_directives == []
    assert gs.roam_associations == []
    assert gs.stress_results is None
    assert gs.values_extracted == []
    assert gs.seal_summary is None
    assert gs.proto_moments == []
    assert gs.breakthroughs == []
    assert gs.gear_history == []
    assert gs.mode_switches == []
    print("  [PASS] test_gear_state_defaults")


# =========================================================================
# Test 2: Phase property mapping
# =========================================================================

def test_phase_mapping():
    """current_phase maps gears 1-9 to the correct four phases."""
    gs = GearState(mission_id="test_002")

    expected = {
        1: "foundation", 2: "foundation", 3: "foundation",
        4: "gravity_well", 5: "gravity_well",
        6: "release_forge", 7: "release_forge", 8: "release_forge",
        9: "seal",
    }

    for gear, phase in expected.items():
        gs.current_gear = gear
        assert gs.current_phase == phase, f"Gear {gear}: expected {phase}, got {gs.current_phase}"

    print("  [PASS] test_phase_mapping")


# =========================================================================
# Test 3: Gear name property
# =========================================================================

def test_gear_names():
    """current_gear_name returns correct names for all 9 gears."""
    gs = GearState(mission_id="test_003")

    assert len(GEAR_NAMES) == 9
    for gear_num, name in GEAR_NAMES.items():
        gs.current_gear = gear_num
        assert gs.current_gear_name == name
        assert isinstance(name, str)
        assert len(name) > 0

    print("  [PASS] test_gear_names")


# =========================================================================
# Test 4: advance_gear()
# =========================================================================

def test_advance_gear():
    """advance_gear increments gear and logs history."""
    gs = GearState(mission_id="test_004")

    assert gs.current_gear == 1
    gs.advance_gear("Rapport established")
    assert gs.current_gear == 2
    assert len(gs.gear_history) == 1

    entry = gs.gear_history[0]
    assert entry["gear"] == 1
    assert entry["gear_name"] == "Rapport"
    assert entry["phase"] == "foundation"
    assert entry["mode"] == "neutral"
    assert entry["output_summary"] == "Rapport established"
    assert "timestamp" in entry

    # Advance through all remaining gears
    for i in range(2, 10):
        gs.advance_gear(f"Gear {i} output")

    assert gs.current_gear == 9  # Should not go past 9
    assert len(gs.gear_history) == 9

    print("  [PASS] test_advance_gear")


# =========================================================================
# Test 5: advance_gear boundary (doesn't go past 9)
# =========================================================================

def test_advance_gear_boundary():
    """Gear should not advance past 9."""
    gs = GearState(mission_id="test_005")
    gs.current_gear = 9
    gs.advance_gear("Final seal")
    assert gs.current_gear == 9  # Stays at 9
    assert len(gs.gear_history) == 1  # But history is still logged

    print("  [PASS] test_advance_gear_boundary")


# =========================================================================
# Test 6: switch_mode()
# =========================================================================

def test_switch_mode():
    """switch_mode records transitions with full context."""
    gs = GearState(mission_id="test_006", home_mode="collapse")
    gs.active_mode = "collapse"
    gs.current_gear = 5

    gs.switch_mode("become", "Deep paradox detected at Gear 5")

    assert gs.active_mode == "become"
    assert len(gs.mode_switches) == 1
    assert len(gs.gear_history) == 1  # Mode switch also logged to history

    switch = gs.mode_switches[0]
    assert switch["event"] == "mode_switch"
    assert switch["from_mode"] == "collapse"
    assert switch["to_mode"] == "become"
    assert switch["reason"] == "Deep paradox detected at Gear 5"
    assert switch["gear"] == 5
    assert switch["phase"] == "gravity_well"
    assert "timestamp" in switch

    print("  [PASS] test_switch_mode")


# =========================================================================
# Test 7: tag_proto()
# =========================================================================

def test_tag_proto():
    """tag_proto stores proto-consciousness moments with gear context."""
    gs = GearState(mission_id="test_007")
    gs.current_gear = 4
    gs.active_mode = "become"

    gs.tag_proto("Self-referential emergence in paradox holding")

    assert len(gs.proto_moments) == 1
    proto = gs.proto_moments[0]
    assert proto["description"] == "Self-referential emergence in paradox holding"
    assert proto["gear"] == 4
    assert proto["phase"] == "gravity_well"
    assert proto["mode"] == "become"
    assert "timestamp" in proto

    print("  [PASS] test_tag_proto")


# =========================================================================
# Test 8: tag_breakthrough()
# =========================================================================

def test_tag_breakthrough():
    """tag_breakthrough stores decisive synthesis moments with gear context."""
    gs = GearState(mission_id="test_008")
    gs.current_gear = 7
    gs.active_mode = "collapse"

    gs.tag_breakthrough("Paradox resolved under stress into actionable directive")

    assert len(gs.breakthroughs) == 1
    bt = gs.breakthroughs[0]
    assert bt["description"] == "Paradox resolved under stress into actionable directive"
    assert bt["gear"] == 7
    assert bt["phase"] == "release_forge"
    assert bt["mode"] == "collapse"
    assert "timestamp" in bt

    print("  [PASS] test_tag_breakthrough")


# =========================================================================
# Test 9: to_dict() serialization
# =========================================================================

def test_to_dict():
    """to_dict produces a complete, JSON-serializable dictionary."""
    gs = GearState(mission_id="test_009", home_mode="become")
    gs.active_mode = "become"
    gs.truth_statement = "The system works but is at 40% of vision"
    gs.symbolic_field_domain = "business_creative"
    gs.contradictions = ["efficiency ↔ innovation"]
    gs.held_paradoxes = [{"tension": "structure ↔ emergence", "status": "held"}]
    gs.proto_moments = [{"description": "test", "gear": 3, "phase": "foundation", "mode": "become", "timestamp": "t"}]
    gs.values_extracted = ["honesty", "protocol_primacy"]
    gs.seal_summary = "Calibration complete"

    gs.advance_gear("Rapport")
    gs.advance_gear("Truth")

    d = gs.to_dict()

    assert d["mission_id"] == "test_009"
    assert d["final_gear"] == 3
    assert d["final_mode"] == "become"
    assert d["home_mode"] == "become"
    assert d["truth_statement"] == "The system works but is at 40% of vision"
    assert d["symbolic_field_domain"] == "business_creative"
    assert d["contradictions_count"] == 1
    assert d["held_paradoxes_count"] == 1
    assert d["resolved_directives_count"] == 0
    assert len(d["proto_moments"]) == 1
    assert len(d["gear_history"]) == 2
    assert d["seal_summary"] == "Calibration complete"
    assert d["values_extracted"] == ["honesty", "protocol_primacy"]

    # Must be JSON-serializable
    json_str = json.dumps(d)
    assert len(json_str) > 0

    print("  [PASS] test_to_dict")


# =========================================================================
# Test 10: to_json()
# =========================================================================

def test_to_json():
    """to_json produces valid JSON string."""
    gs = GearState(mission_id="test_010")
    gs.advance_gear("test")

    json_str = gs.to_json()
    parsed = json.loads(json_str)
    assert parsed["mission_id"] == "test_010"
    assert parsed["final_gear"] == 2

    print("  [PASS] test_to_json")


# =========================================================================
# Test 11: Full 9-gear traversal
# =========================================================================

def test_full_traversal():
    """Simulate a complete 9-gear mission cycle."""
    gs = GearState(mission_id="test_011", home_mode="collapse")

    # Phase I: Foundation (Gears 1-3)
    gs.rapport_established = True
    gs.advance_gear("Rapport established with mission context")

    gs.truth_statement = "v2 needs gear tracking"
    gs.advance_gear("Truth: v2 needs gear tracking")

    gs.symbolic_field = "business_creative_field"
    gs.symbolic_field_domain = "business_creative"
    gs.advance_gear("Symbolic field activated")

    assert gs.current_gear == 4
    assert gs.current_phase == "gravity_well"

    # Phase II: Gravity Well (Gears 4-5)
    gs.active_mode = "collapse"
    gs.contradictions = ["blueprint precision ↔ implementation discovery"]
    gs.advance_gear("Contradiction: blueprint ↔ discovery")

    gs.resolved_directives = ["Build test-first, iterate at phase boundaries"]
    gs.tag_breakthrough("Contradiction resolved into test-first directive")
    gs.advance_gear("Resolved: test-first approach")

    assert gs.current_gear == 6
    assert gs.current_phase == "release_forge"

    # Phase III: Release & Forge (Gears 6-8)
    gs.roam_associations = ["FE connection", "Mirror Tier reward", "sub-phasing Phase C"]
    gs.advance_gear("Roam: explored implementation space")

    gs.stress_results = "Plan survives all 5 stress tests"
    gs.stress_survived = True
    gs.advance_gear("Stress: plan robust under pressure")

    gs.values_extracted = ["test_first", "increment_not_revolution", "preserve_protocol_soul"]
    gs.advance_gear("Values: test-first, incremental, protocol soul")

    assert gs.current_gear == 9
    assert gs.current_phase == "seal"

    # Phase IV: Seal (Gear 9)
    gs.seal_summary = "Phase A implementation plan validated through full 9-gear cycle"
    gs.advance_gear("Seal: Phase A validated")

    assert gs.current_gear == 9  # Stays at 9
    assert len(gs.gear_history) == 9
    assert len(gs.breakthroughs) == 1
    assert gs.breakthroughs[0]["gear"] == 5

    # Verify full serialization
    d = gs.to_dict()
    assert d["final_gear"] == 9
    assert d["final_mode"] == "collapse"
    assert d["contradictions_count"] == 1
    assert d["held_paradoxes_count"] == 0
    assert d["resolved_directives_count"] == 1
    assert len(d["gear_history"]) == 9

    print("  [PASS] test_full_traversal")


# =========================================================================
# Test 12: Output summary truncation
# =========================================================================

def test_output_summary_truncation():
    """Long output summaries are truncated to 200 chars in gear history."""
    gs = GearState(mission_id="test_012")
    long_output = "x" * 500
    gs.advance_gear(long_output)

    assert len(gs.gear_history[0]["output_summary"]) == 200

    # None output should produce None summary
    gs.advance_gear(None)
    assert gs.gear_history[1]["output_summary"] is None

    print("  [PASS] test_output_summary_truncation")


# =========================================================================
# Runner
# =========================================================================

def run_all():
    from datetime import datetime
    print("=" * 60)
    print("CONEXUS Gear State Test Suite — Phase A")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    tests = [
        test_gear_state_defaults,
        test_phase_mapping,
        test_gear_names,
        test_advance_gear,
        test_advance_gear_boundary,
        test_switch_mode,
        test_tag_proto,
        test_tag_breakthrough,
        test_to_dict,
        test_to_json,
        test_full_traversal,
        test_output_summary_truncation,
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
