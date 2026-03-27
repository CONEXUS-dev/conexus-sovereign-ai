"""
SovereignNEXT — Phase 6 Step 4: Loop Intent Router Unit Tests

Tests proving correct intent classification, exclusive routing, canonical
refusal enforcement, state hash invariance, determinism, and backward
compatibility.

No LLM calls. No state mutation. No interpretation.
"""

import sys
import os
import hashlib
import json

# Ensure SovereignNEXT is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from SovereignNEXT.loop.intent_router import REFUSALS, route_request
from SovereignNEXT.operators.sovereign_observer import SovereignReport
from SovereignNEXT.state.system_state import SystemState


# =========================================================================
# Helpers
# =========================================================================

def _hash_state(state: SystemState) -> str:
    """Best-effort stable hash for mutation detection in tests."""
    payload = json.dumps(state.to_dict(), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _make_state() -> SystemState:
    """Minimal empty state — valid per existing dataclass defaults."""
    return SystemState()


# =========================================================================
# Test 1: Observe request routes to Sovereign only
# =========================================================================

def test_observe_routes_to_sovereign_only():
    """Observe intent invokes Sovereign and never triggers operators."""
    state = _make_state()
    called = {"op": False}

    def fake_op(s: SystemState):
        called["op"] = True
        return "OP_RAN"

    registry = {"Collapse": fake_op}

    out = route_request("show status", state, operator_registry=registry)
    assert isinstance(out, SovereignReport), f"Expected SovereignReport, got {type(out)}"
    assert called["op"] is False, "Operator should not be called on observe"
    print("  PASS: Observe request routes to Sovereign only")


# =========================================================================
# Test 2: Operate request routes to named operator only
# =========================================================================

def test_operate_routes_to_named_operator_only():
    """Operate intent invokes only the explicitly named operator."""
    state = _make_state()
    called = {"op": False}

    def fake_op(s: SystemState):
        called["op"] = True
        return "OP_RAN"

    registry = {"Collapse": fake_op}

    out = route_request("run Collapse", state, operator_registry=registry)
    assert out == "OP_RAN"
    assert called["op"] is True
    print("  PASS: Operate request routes to named operator only")


# =========================================================================
# Test 3: Mixed intent request is refused
# =========================================================================

def test_mixed_intent_is_refused():
    """Mixed observe + operate signals produce refusal."""
    state = _make_state()

    def fake_op(s: SystemState):
        return "OP_RAN"

    registry = {"Collapse": fake_op}

    out = route_request("show status and run Collapse", state, operator_registry=registry)
    assert out == REFUSALS["mixed"]
    print("  PASS: Mixed intent request is refused")


# =========================================================================
# Test 4: Prescriptive request is refused
# =========================================================================

def test_prescriptive_is_refused():
    """Requests containing 'should' are refused with prescriptive refusal."""
    state = _make_state()
    out = route_request("what should happen next", state, operator_registry={})
    assert out == REFUSALS["prescriptive"]
    print("  PASS: Prescriptive request is refused")


# =========================================================================
# Test 5: Optimization request is refused
# =========================================================================

def test_optimization_is_refused():
    """Requests to optimize are refused with optimization refusal."""
    state = _make_state()
    out = route_request("optimize thresholds", state, operator_registry={})
    assert out == REFUSALS["optimize"]
    print("  PASS: Optimization request is refused")


# =========================================================================
# Test 6: Sovereign output does not trigger operator
# =========================================================================

def test_sovereign_output_does_not_trigger_operator():
    """Observe path returns SovereignReport — no operator side effects."""
    state = _make_state()
    op_calls = []

    def tracking_op(s: SystemState):
        op_calls.append("called")
        return "OP_RAN"

    registry = {"Collapse": tracking_op, "Become": tracking_op, "Hold": tracking_op}

    out = route_request("report metrics", state, operator_registry=registry)
    assert isinstance(out, SovereignReport)
    assert len(op_calls) == 0, "No operator should be called during observe"
    print("  PASS: Sovereign output does not trigger operator")


# =========================================================================
# Test 7: Operator execution does not invoke Sovereign
# =========================================================================

def test_operator_execution_does_not_invoke_sovereign():
    """Operate path returns operator result, not SovereignReport."""
    state = _make_state()

    def fake_op(s: SystemState):
        return "OP_RAN"

    registry = {"Collapse": fake_op}

    out = route_request("run Collapse", state, operator_registry=registry)
    assert out == "OP_RAN"
    assert not isinstance(out, SovereignReport), "Sovereign should not run during operate"
    print("  PASS: Operator execution does not invoke Sovereign")


# =========================================================================
# Test 8: Invalid intent returns canonical refusal verbatim
# =========================================================================

def test_invalid_returns_canonical_refusal_verbatim():
    """All refusal strings match the canon exactly."""
    state = _make_state()

    # Prescriptive
    out = route_request("what should we do", state, operator_registry={})
    assert out == REFUSALS["prescriptive"]

    # Optimize
    out = route_request("tune parameters", state, operator_registry={})
    assert out == REFUSALS["optimize"]

    # Reinterpret
    out = route_request("what is the meaning of this paradox", state, operator_registry={})
    assert out == REFUSALS["reinterpret"]

    # Mutate
    out = route_request("modify the claims", state, operator_registry={})
    assert out == REFUSALS["mutate"]

    print("  PASS: Invalid intent returns canonical refusal verbatim")


# =========================================================================
# Test 9: State hash unchanged after observe routing
# =========================================================================

def test_state_hash_unchanged_after_observe():
    """Observe path does not mutate state."""
    state = _make_state()
    before = _hash_state(state)

    route_request("show status", state, operator_registry={})

    after = _hash_state(state)
    assert before == after, f"State hash changed: {before} → {after}"
    print("  PASS: State hash unchanged after observe routing")


# =========================================================================
# Test 10: Unknown operator name is refused
# =========================================================================

def test_unknown_operator_name_is_refused():
    """Requesting an operator not in the registry is refused."""
    state = _make_state()

    def fake_op(s: SystemState):
        return "OP_RAN"

    registry = {"Collapse": fake_op}

    # "Become" is not in registry — execute verb present but operator not found
    out = route_request("run Become", state, operator_registry=registry)
    # Become not found → no operator match → has_execute True but no operator
    # Falls to ambiguity → invalid
    assert isinstance(out, str), "Should return a refusal string"
    assert out in REFUSALS.values(), f"Expected canonical refusal, got: {out}"
    print("  PASS: Unknown operator name is refused")


# =========================================================================
# Test 11: Deterministic routing for identical inputs
# =========================================================================

def test_deterministic_routing():
    """Same request + same state → same routing decision."""
    state = _make_state()
    registry = {}

    out1 = route_request("show status", state, operator_registry=registry)
    out2 = route_request("show status", state, operator_registry=registry)

    # Both should be SovereignReport with same content
    assert isinstance(out1, type(out2))
    if isinstance(out1, SovereignReport):
        assert out1.state_hash == out2.state_hash
        assert out1.paradox_counts_by_status == out2.paradox_counts_by_status
    else:
        assert out1 == out2

    print("  PASS: Deterministic routing for identical inputs")


# =========================================================================
# Test 12: Phase 5 operators still importable
# =========================================================================

def test_phase5_backward_compatibility():
    """All Phase 5 operators remain importable — no conflicts introduced."""
    from SovereignNEXT.operators.collapse_operator import collapse_once, collapse_pure
    from SovereignNEXT.operators.become_expander import become_pass, become_pure
    from SovereignNEXT.operators.paradox_hold_operator import paradox_hold_pure
    from SovereignNEXT.operators.sovereign_observer import sovereign_observe

    assert callable(collapse_once)
    assert callable(collapse_pure)
    assert callable(become_pass)
    assert callable(become_pure)
    assert callable(paradox_hold_pure)
    assert callable(sovereign_observe)
    print("  PASS: Phase 5 operators still importable")


# =========================================================================
# Runner
# =========================================================================

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("PHASE 6 STEP 4 — LOOP INTENT ROUTER UNIT TESTS")
    print("=" * 60 + "\n")

    tests = [
        test_observe_routes_to_sovereign_only,
        test_operate_routes_to_named_operator_only,
        test_mixed_intent_is_refused,
        test_prescriptive_is_refused,
        test_optimization_is_refused,
        test_sovereign_output_does_not_trigger_operator,
        test_operator_execution_does_not_invoke_sovereign,
        test_invalid_returns_canonical_refusal_verbatim,
        test_state_hash_unchanged_after_observe,
        test_unknown_operator_name_is_refused,
        test_deterministic_routing,
        test_phase5_backward_compatibility,
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
        print("\nSTATUS: FAIL — Loop intent router not ready")
        sys.exit(1)
    else:
        print("\nSTATUS: PASS — Loop routes, refuses, and never interprets")
        sys.exit(0)


if __name__ == "__main__":
    main()
