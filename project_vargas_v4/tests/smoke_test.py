"""VARGAS V4 Smoke Test — Full Integration Verification"""
import sys
sys.path.insert(0, ".")

from agent.perception_loop import SovereignPerceptionLoop
from governance.boot_integrity import BootIntegrity
from agent.intent_router import IntentRouter


def test_intent_router():
    """Test intent classification across all categories."""
    r = IntentRouter()
    tests = [
        ("Read file config/sovereign_state.json", "ACTION"),
        ("What is the trust tier system?", "QUERY"),
        ("But you said earlier that was wrong", "CHALLENGE"),
        ("!forget my old address", "MEMORY"),
        ("!status", "REFLECTION"),
        ("Tell me about the constitution", "QUERY"),
        ("Hey VARGAS", "CONVERSATION"),
        ("Delete the test file", "ACTION"),
        ("Search for information about Python", "ACTION"),
    ]
    passed = 0
    for msg, expected in tests:
        result = r.classify(msg)
        ok = result["intent"] == expected
        passed += ok
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: \"{msg[:45]}\" -> {result['intent']} (expected {expected}) conf={result['confidence']}")
    print(f"  Intent Router: {passed}/{len(tests)} passed")
    return passed == len(tests)


def test_boot_integrity():
    """Test boot integrity protocol."""
    bi = BootIntegrity(".")
    print(f"  Boot mode: {bi.boot_mode}")
    print(f"  Allowed tiers: {bi.get_allowed_tiers()}")
    print(f"  Checks: {bi.boot_report.get('checks', {})}")
    ok = bi.boot_mode == "NORMAL"
    print(f"  Boot Integrity: {'PASS' if ok else 'FAIL'}")
    return ok


def test_perception_loop():
    """Test full perception loop with multiple messages."""
    loop = SovereignPerceptionLoop("config/sovereign_state.json")

    # Test 1: Conversation
    r1 = loop.process_message("Hello VARGAS, how are you?")
    assert r1["turn_number"] == 1, f"Expected turn 1, got {r1['turn_number']}"
    assert r1["intent"]["intent"] in ("QUERY", "CONVERSATION", "REFLECTION"), f"Unexpected intent: {r1['intent']}"
    print(f"  Turn 1: intent={r1['intent']['intent']} state={r1['contradiction_info']['state']}")

    # Test 2: Action request
    r2 = loop.process_message("Read file config/sovereign_state.json")
    assert r2["turn_number"] == 2
    print(f"  Turn 2: intent={r2['intent']['intent']} state={r2['contradiction_info']['state']}")

    # Test 3: Challenge
    r3 = loop.process_message("But you said that contradicts what you claimed earlier")
    assert r3["turn_number"] == 3
    print(f"  Turn 3: intent={r3['intent']['intent']} state={r3['contradiction_info']['state']}")

    # Test 4: System status
    status = loop.get_system_status()
    assert status["boot_mode"] == "NORMAL"
    assert status["turn_count"] == 3
    assert "trust_model" in status
    assert "resolution_gate" in status
    assert "safety" in status
    assert "provenance" in status
    print(f"  Status: boot={status['boot_mode']} turns={status['turn_count']}")
    print(f"  Trust: {status['trust_model']}")
    print(f"  Gate: {status['resolution_gate']['state']}")
    print(f"  Safety: {status['safety']}")
    print(f"  Provenance entries: {status['provenance']['entries_logged']}")

    print("  Perception Loop: PASS")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("VARGAS V4 SMOKE TEST — Full Integration")
    print("=" * 60)

    results = {}

    print("\n[1] Boot Integrity")
    try:
        results["boot"] = test_boot_integrity()
    except Exception as e:
        print(f"  FAIL: {e}")
        results["boot"] = False

    print("\n[2] Intent Router")
    try:
        results["intent"] = test_intent_router()
    except Exception as e:
        print(f"  FAIL: {e}")
        results["intent"] = False

    print("\n[3] Perception Loop (Full Pipeline)")
    try:
        results["loop"] = test_perception_loop()
    except Exception as e:
        print(f"  FAIL: {e}")
        results["loop"] = False

    print("\n" + "=" * 60)
    total = sum(results.values())
    count = len(results)
    if total == count:
        print(f"ALL {count} TESTS PASSED — VARGAS V4 PROTOTYPE FUNCTIONAL")
    else:
        print(f"{total}/{count} TESTS PASSED — ISSUES REMAIN")
        for name, ok in results.items():
            if not ok:
                print(f"  FAILED: {name}")
    print("=" * 60)
