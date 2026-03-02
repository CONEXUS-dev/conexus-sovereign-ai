"""
Tests for Opie Agent — Become Mode

Run: python -m pytest agents/test_opie.py -v
Or:  python agents/test_opie.py
"""

import sys
from pathlib import Path

# Ensure repo root is on path
REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agents.opie import OpieAgent, BECOME_ECP_CONFIG, NINE_GEARS_REFERENCE
from agents.router import route_task


# ---------------------------------------------------------------------------
# Agent Identity Tests
# ---------------------------------------------------------------------------

def test_agent_identity():
    """Opie must identify as become agent"""
    opie = OpieAgent()
    assert opie.agent_name == "opie"
    assert opie.agent_type == "become"
    assert opie.ecp_calibration == "become"


def test_agent_capabilities():
    """Opie must have all five core capabilities"""
    opie = OpieAgent()
    expected = [
        "creative_synthesis",
        "identity_expansion",
        "narrative_creation",
        "conceptual_innovation",
        "symbolic_modulation",
    ]
    for cap in expected:
        assert cap in opie.capabilities, f"Missing capability: {cap}"


def test_manifest():
    """Manifest must include non-execution guarantee"""
    opie = OpieAgent()
    manifest = opie.get_manifest()
    assert manifest["non_execution_guarantee"] is True
    assert manifest["requires_human_approval"] is True
    assert manifest["protocol_version"] == "collapse-become-v1.1"


def test_health_check():
    """Health check must return ready status"""
    opie = OpieAgent()
    health = opie.health_check()
    assert health["status"] == "ready"
    assert health["agent"] == "opie"
    assert health["type"] == "become"


# ---------------------------------------------------------------------------
# Task Processing Tests
# ---------------------------------------------------------------------------

def test_process_task_basic():
    """Basic task processing returns correct structure"""
    opie = OpieAgent()
    task = {
        "task_input": "What identity shift is emerging in the system?",
        "security_context": {"user_id": "test", "channel_id": "test"},
    }
    result = opie.process_task(task)

    assert result["status"] == "ok"
    assert result["agent"] == "opie"
    assert result["ecp_processing"] is True
    assert "task_output" in result
    assert "provenance" in result
    assert "memory_intent" in result
    assert "memory_payload" not in result


def test_process_task_provenance():
    """Provenance metadata must be lightweight — no UUIDs, no timestamps"""
    opie = OpieAgent()
    task = {
        "task_input": "Explore the meaning of sovereign AI",
        "security_context": {"user_id": "derek", "channel_id": "general"},
    }
    result = opie.process_task(task)
    prov = result["provenance"]

    assert prov["agent"] == "opie"
    assert prov["agent_type"] == "become"
    assert prov["ecp_calibration"] == "become"
    assert "input_hash" in prov
    # Provenance must NOT contain UUIDs or timestamps (Gateway's job)
    assert "lineage_id" not in prov
    assert "timestamp" not in prov
    assert "security_context" not in prov


def test_process_task_memory_intent():
    """Memory intent must declare what to remember, not how to store it"""
    opie = OpieAgent()
    task = {
        "task_input": "Synthesize the vision for CC",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    intent = result["memory_intent"]

    assert intent["intent"] == "store"
    assert "what" in intent
    assert intent["why"] == "become_processing"
    assert "confidence" in intent
    assert "tags" in intent
    assert "become" in intent["tags"]
    assert "synthesis" in intent["tags"]
    assert "source_input_hash" in intent
    # Must NOT contain Qdrant-shaped fields
    assert "id" not in intent
    assert "vector" not in intent
    assert "metadata" not in intent
    assert "payload" not in intent


def test_gear_context_passthrough():
    """Gear context should be passed through as-is, never resolved"""
    opie = OpieAgent()
    task = {
        "task_input": "Analyze the ethical implications",
        "gear_context": "ETHICS_VALUE",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    assert result["gear_context"] == "ETHICS_VALUE"


def test_gear_context_none_by_default():
    """Without gear_context, result should have None"""
    opie = OpieAgent()
    task = {
        "task_input": "Simple input",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    assert result["gear_context"] is None


def test_gear_context_arbitrary_label():
    """Opie should accept any gear_context label without validation"""
    opie = OpieAgent()
    task = {
        "task_input": "Test with custom label",
        "gear_context": "CUSTOM_GEAR",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    assert result["gear_context"] == "CUSTOM_GEAR"


# ---------------------------------------------------------------------------
# ECP Processing Tests
# ---------------------------------------------------------------------------

def test_paradox_detection():
    """Paradoxes should be detected from input"""
    opie = OpieAgent()
    task = {
        "task_input": "Balance efficiency with creativity in the system",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    paradoxes = result["paradoxes_held"]

    assert len(paradoxes) > 0
    # Should detect the efficiency/creativity primary paradox
    types = [p["type"] for p in paradoxes]
    assert "primary" in types or "meta" in types


def test_meta_paradox_always_present():
    """The meta-paradox (expansion within containment) should always be present"""
    opie = OpieAgent()
    task = {
        "task_input": "Simple test input",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    paradoxes = result["paradoxes_held"]

    meta = [p for p in paradoxes if p["type"] == "meta"]
    assert len(meta) == 1
    assert meta[0]["pole_a"] == "expansion"
    assert meta[0]["pole_b"] == "containment"


def test_emotional_context():
    """Emotional context should be analyzed"""
    opie = OpieAgent()
    task = {
        "task_input": "Imagine a new vision for the future of AI",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    emo = result["emotional_context"]

    assert "scores" in emo
    assert "dominant_tone" in emo
    assert "field_intensity" in emo
    assert emo["dominant_tone"] in BECOME_ECP_CONFIG["emotional_axes"]


def test_proto_moments():
    """Proto-moments should always include the meta-paradox moment"""
    opie = OpieAgent()
    task = {
        "task_input": "What is emerging?",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    protos = result["proto_moments"]

    assert len(protos) > 0
    assert any("[PROTO]" in m for m in protos)


def test_handoff_detection():
    """Handoff items should be detected when output contains execution signals"""
    opie = OpieAgent()
    task = {
        "task_input": "We need to implement a new feature and deploy it",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    handoff = result["handoff_to_sway"]

    assert len(handoff) > 0
    assert all(h["status"] == "pending_sway" for h in handoff)


# ---------------------------------------------------------------------------
# Boundary Enforcement Tests
# ---------------------------------------------------------------------------

def test_no_gear_resolution():
    """Opie must NOT resolve gears from input — gear_context is passthrough only"""
    opie = OpieAgent()
    # Input contains gear-related keywords but no gear_context provided
    task = {
        "task_input": "Explore the market landscape with vision and ethics",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    # Without gear_context, result should be None (not resolved from keywords)
    assert result["gear_context"] is None


def test_no_uuid_in_output():
    """Opie output must never contain UUID fields — Gateway generates those"""
    opie = OpieAgent()
    task = {
        "task_input": "Test for UUID leakage",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    # Check top-level and nested structures
    assert "id" not in result
    assert "id" not in result.get("memory_intent", {})
    assert "id" not in result.get("provenance", {})


def test_no_vector_in_output():
    """Opie output must never contain vector fields — Gateway generates those"""
    opie = OpieAgent()
    task = {
        "task_input": "Test for vector leakage",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    assert "vector" not in result
    assert "vector" not in result.get("memory_intent", {})


def test_no_timestamp_in_provenance():
    """Provenance must not contain timestamps — Gateway assigns those"""
    opie = OpieAgent()
    task = {
        "task_input": "Test for timestamp leakage",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    assert "timestamp" not in result.get("provenance", {})


def test_nine_gears_reference_exists():
    """NINE_GEARS_REFERENCE should exist as reference-only constant"""
    assert len(NINE_GEARS_REFERENCE) == 9
    assert "INNOVATION_RAPPORT" in NINE_GEARS_REFERENCE
    assert "SUCCESS_CONTINUITY_SEAL" in NINE_GEARS_REFERENCE


def test_intent_tags_from_emotional_context():
    """Memory intent should include tags derived from emotional analysis"""
    opie = OpieAgent()
    task = {
        "task_input": "Imagine a new vision and dream of transformation",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    tags = result["memory_intent"]["tags"]
    # Should always have base tags
    assert "become" in tags
    assert "synthesis" in tags
    # Should have dominant tone tag from emotional analysis
    assert len(tags) >= 3


# ---------------------------------------------------------------------------
# Router Tests
# ---------------------------------------------------------------------------

def test_router_explicit_sway():
    """Explicit sway assignment should route to sway"""
    assert route_task({"agent_assignment": "sway", "task_input": "anything"}) == "sway"


def test_router_explicit_opie():
    """Explicit opie assignment should route to opie"""
    assert route_task({"agent_assignment": "opie", "task_input": "anything"}) == "opie"


def test_router_explicit_both():
    """Explicit both assignment should route to both"""
    assert route_task({"agent_assignment": "both", "task_input": "anything"}) == "both"


def test_router_smart_sway():
    """Analysis-oriented input should smart-route to sway"""
    result = route_task({"task_input": "analyze the market data and benchmark results"})
    assert result == "sway"


def test_router_smart_opie():
    """Creative input should smart-route to opie"""
    result = route_task({"task_input": "imagine and create a new narrative vision"})
    assert result == "opie"


def test_router_default_sway():
    """Ambiguous input should default to sway"""
    result = route_task({"task_input": "hello world"})
    assert result == "sway"


# ---------------------------------------------------------------------------
# Non-Execution Guarantee Tests
# ---------------------------------------------------------------------------

def test_no_side_effects():
    """process_task must not make any external calls or mutations"""
    opie = OpieAgent()
    task = {
        "task_input": "Test for side effects",
        "security_context": {"user_id": "test"},
    }
    # If this completes without network errors, Opie isn't calling external services
    result = opie.process_task(task)
    assert result["status"] == "ok"


def test_confidence_bounded():
    """Confidence must never exceed 0.99"""
    opie = OpieAgent()
    task = {
        "task_input": "identity expand synthesize create narrative symbol meaning emerge integrate vision",
        "security_context": {"user_id": "test"},
    }
    result = opie.process_task(task)
    assert result["confidence"] <= 0.99


# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_functions = [v for k, v in globals().items() if k.startswith("test_")]
    passed = 0
    failed = 0

    print("=" * 60)
    print("OPIE AGENT TEST SUITE")
    print("=" * 60)

    for test_fn in test_functions:
        try:
            test_fn()
            print(f"  PASS  {test_fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {test_fn.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {test_fn.__name__}: {e}")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")

    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print(f"{failed} TESTS FAILED")

    sys.exit(0 if failed == 0 else 1)
