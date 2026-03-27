"""
SovereignNEXT — Phase 5 Step 1: Substrate Unit Tests

Tests proving determinism, hash stability, serialization roundtrip,
mutation replay, and backward compatibility of the paradox substrate.

No LLM calls. No operator logic. Pure Python, pure math.
"""

import sys
import os
import json

# Ensure SovereignNEXT is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from SovereignNEXT.state.emoji_vector import EmojiVector, compute_emoji_metrics
from SovereignNEXT.state.paradox import (
    Paradox, Pole, ParadoxMetrics, ParadoxConstraints,
)
from SovereignNEXT.state.tension import Tension
from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.emoji_mutator import (
    mutate_become, mutate_collapse, mutate_paradox_hold, seed_initial_sequence,
)


# =========================================================================
# Helpers
# =========================================================================

def _make_emoji_vector(ev_id="ev_test_001", seed=42):
    """Create a deterministic EmojiVector for testing."""
    seq = seed_initial_sequence("🧭", "🛡️", seed=seed)
    return EmojiVector(
        sequence=seq,
        pole_a_emoji="🧭",
        pole_b_emoji="🛡️",
        role="paradox_field",
        id=ev_id,
        paradox_id="paradox_test_001",
        related_claims=["claim_0001", "claim_0002"],
        origin="test_fixture",
        last_updated="2026-03-04T00:00:00+00:00",
    )


def _make_paradox(paradox_id="paradox_test_001", with_constraints=False):
    """Create a deterministic Paradox for testing."""
    constraints = ParadoxConstraints(
        collapse_veto=True,
        veto_reason="entropy_above_threshold",
        entropy_threshold=0.70,
        balance_window=(0.35, 0.65),
    ) if with_constraints else ParadoxConstraints()

    return Paradox(
        pole_a=Pole(id="autonomy", emoji="🧭", confidence=0.46),
        pole_b=Pole(id="control", emoji="🛡️", confidence=0.44),
        status="paradox_held",
        id=paradox_id,
        timestamp="2026-03-04T00:00:00+00:00",
        metrics=ParadoxMetrics(
            tension_strength=0.84,
            resolution_pressure=0.31,
            paradox_stability=0.72,
            agent_divergence=0.66,
        ),
        constraints=constraints,
        emoji_vector_id="ev_test_001",
        history=[
            {"event": "created", "operator": "Become", "entropy": 0.62,
             "timestamp": "2026-03-03T05:41:00+00:00"},
        ],
        rubric_scores=[],
        claim_ids=["claim_0001", "claim_0002"],
        mission_ids=["M3"],
    )


def _make_system_state():
    """Create a minimal but complete SystemState for testing."""
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
    tension = Tension(
        pole_a="Autonomy is essential",
        pole_b="Control is essential",
        relation_type="polarity",
        status="open",
        id="tension_0001",
        timestamp="2026-03-04T00:00:00+00:00",
        source_claims=["claim_0001", "claim_0002"],
        emoji_vector_id="ev_test_001",
    )
    ev = _make_emoji_vector()
    paradox = _make_paradox(with_constraints=True)

    state = SystemState(
        claims=[claim_a, claim_b],
        tensions=[tension],
        paradoxes=[paradox],
        emoji_fields=[ev],
        mission_id="M_test",
        iteration=1,
    )
    return state


# =========================================================================
# Test 1: EmojiVector metric determinism
# =========================================================================

def test_emoji_vector_metric_determinism():
    """Same sequence always produces identical metrics."""
    ev = _make_emoji_vector()
    m1 = ev.metrics
    m2 = ev.metrics
    m3 = compute_emoji_metrics(ev.sequence, ev.pole_a_emoji, ev.pole_b_emoji)

    assert m1 == m2, f"Metrics not identical across calls: {m1} vs {m2}"
    assert m1 == m3, f"Property metrics != direct compute: {m1} vs {m3}"
    assert isinstance(m1["entropy"], float)
    assert isinstance(m1["pole_balance"], float)
    assert isinstance(m1["chaos_index"], float)
    assert isinstance(m1["stability_index"], float)
    print("  PASS: EmojiVector metric determinism")


# =========================================================================
# Test 2: EmojiVector serialization roundtrip
# =========================================================================

def test_emoji_vector_roundtrip():
    """to_dict() -> from_dict() -> to_dict() produces identical output."""
    ev = _make_emoji_vector()
    d1 = ev.to_dict()
    ev2 = EmojiVector.from_dict(d1)
    d2 = ev2.to_dict()

    assert d1 == d2, f"Roundtrip mismatch:\n  d1={json.dumps(d1, indent=2)}\n  d2={json.dumps(d2, indent=2)}"
    print("  PASS: EmojiVector serialization roundtrip")


# =========================================================================
# Test 3: EmojiVector content hash stability
# =========================================================================

def test_emoji_vector_hash_stability():
    """Same vector always produces the same hash."""
    ev = _make_emoji_vector()
    h1 = ev.content_hash()
    h2 = ev.content_hash()
    assert h1 == h2, f"Hash not stable: {h1} vs {h2}"
    assert len(h1) == 64, f"Not a SHA-256 hex digest: length={len(h1)}"

    # Different vector produces different hash
    ev3 = _make_emoji_vector(ev_id="ev_test_002")
    h3 = ev3.content_hash()
    assert h1 != h3, "Different vectors should have different hashes"
    print("  PASS: EmojiVector content hash stability")


# =========================================================================
# Test 4: Paradox with constraints roundtrip
# =========================================================================

def test_paradox_constraints_roundtrip():
    """Serialize/deserialize preserves all fields including constraints."""
    p = _make_paradox(with_constraints=True)
    d1 = p.to_dict()
    p2 = Paradox.from_dict(d1)
    d2 = p2.to_dict()

    assert d1 == d2, f"Paradox roundtrip mismatch:\n  d1={json.dumps(d1, indent=2)}\n  d2={json.dumps(d2, indent=2)}"

    # Verify constraints are present and correct
    assert p2.constraints.collapse_veto is True
    assert p2.constraints.veto_reason == "entropy_above_threshold"
    assert p2.constraints.entropy_threshold == 0.70
    assert p2.constraints.balance_window == (0.35, 0.65)
    print("  PASS: Paradox with constraints roundtrip")


# =========================================================================
# Test 5: Paradox content hash stability
# =========================================================================

def test_paradox_hash_stability():
    """Same paradox always produces the same hash."""
    p = _make_paradox(with_constraints=True)
    h1 = p.content_hash()
    h2 = p.content_hash()
    assert h1 == h2, f"Hash not stable: {h1} vs {h2}"
    assert len(h1) == 64

    # Different paradox produces different hash
    p3 = _make_paradox(paradox_id="paradox_test_002", with_constraints=True)
    h3 = p3.content_hash()
    assert h1 != h3, "Different paradoxes should have different hashes"
    print("  PASS: Paradox content hash stability")


# =========================================================================
# Test 6: Mutation determinism
# =========================================================================

def test_mutation_determinism():
    """mutate_become(seed=N) produces identical results on repeated calls."""
    for mutate_fn, name in [
        (mutate_become, "become"),
        (mutate_collapse, "collapse"),
        (mutate_paradox_hold, "paradox_hold"),
    ]:
        ev_a = _make_emoji_vector(ev_id="ev_mut_a")
        ev_b = _make_emoji_vector(ev_id="ev_mut_b")

        mutate_fn(ev_a, seed=999)
        mutate_fn(ev_b, seed=999)

        assert ev_a.sequence == ev_b.sequence, (
            f"Mutation {name} not deterministic:\n  a={ev_a.sequence}\n  b={ev_b.sequence}"
        )
        assert ev_a.metrics == ev_b.metrics, (
            f"Mutation {name} metrics differ after identical mutation"
        )

    print("  PASS: Mutation determinism (become, collapse, paradox_hold)")


# =========================================================================
# Test 7: Mutation replay from history
# =========================================================================

def test_mutation_replay():
    """Given a known seed sequence, can reconstruct the exact emoji vector state."""
    # Step 1: Create initial vector
    initial_seq = seed_initial_sequence("🧭", "🛡️", seed=42)

    # Step 2: Apply a sequence of mutations with known seeds
    mutation_log = [
        ("become", 100),
        ("collapse", 200),
        ("paradox_hold", 300),
        ("become", 400),
    ]

    # Forward pass: build the vector
    ev_forward = EmojiVector(
        sequence=list(initial_seq),
        pole_a_emoji="🧭",
        pole_b_emoji="🛡️",
        id="ev_replay_fwd",
        last_updated="2026-03-04T00:00:00+00:00",
    )
    for op, seed in mutation_log:
        if op == "become":
            mutate_become(ev_forward, seed=seed)
        elif op == "collapse":
            mutate_collapse(ev_forward, seed=seed)
        elif op == "paradox_hold":
            mutate_paradox_hold(ev_forward, seed=seed)

    forward_hash = ev_forward.content_hash()
    forward_seq = list(ev_forward.sequence)

    # Replay pass: start from the same initial and apply the same log
    ev_replay = EmojiVector(
        sequence=list(initial_seq),
        pole_a_emoji="🧭",
        pole_b_emoji="🛡️",
        id="ev_replay_fwd",
        last_updated="2026-03-04T00:00:00+00:00",
    )
    for op, seed in mutation_log:
        if op == "become":
            mutate_become(ev_replay, seed=seed)
        elif op == "collapse":
            mutate_collapse(ev_replay, seed=seed)
        elif op == "paradox_hold":
            mutate_paradox_hold(ev_replay, seed=seed)

    replay_hash = ev_replay.content_hash()

    assert forward_seq == ev_replay.sequence, "Replay sequence doesn't match forward pass"
    assert forward_hash == replay_hash, "Replay hash doesn't match forward pass"
    print("  PASS: Mutation replay from history")


# =========================================================================
# Test 8: SystemState roundtrip
# =========================================================================

def test_system_state_roundtrip():
    """Full state serialize -> deserialize -> content_hash matches."""
    state = _make_system_state()
    d1 = state.to_dict()
    h1 = state.content_hash()

    state2 = SystemState.from_dict(d1)
    d2 = state2.to_dict()
    h2 = state2.content_hash()

    assert d1 == d2, "SystemState roundtrip dict mismatch"
    assert h1 == h2, f"SystemState hash mismatch: {h1} vs {h2}"

    # Triple roundtrip for paranoia
    state3 = SystemState.from_dict(d2)
    h3 = state3.content_hash()
    assert h1 == h3, "Triple roundtrip hash mismatch"
    print("  PASS: SystemState roundtrip (hash stable across serialize/deserialize)")


# =========================================================================
# Test 9: Pole confidence preservation
# =========================================================================

def test_pole_confidence_preservation():
    """Confidence survives serialization roundtrip."""
    pole = Pole(id="autonomy", emoji="🧭", confidence=0.46)
    d = pole.to_dict()
    pole2 = Pole.from_dict(d)

    assert pole2.confidence == 0.46, f"Confidence lost: {pole2.confidence}"
    assert pole2.id == "autonomy"
    assert pole2.emoji == "🧭"

    # Default confidence when missing from dict
    pole_legacy = Pole.from_dict({"id": "legacy", "emoji": "🧭"})
    assert pole_legacy.confidence == 0.5, "Default confidence should be 0.5"

    print("  PASS: Pole confidence preservation")


# =========================================================================
# Test 10: Constraints veto gate encoding
# =========================================================================

def test_constraints_veto_gate():
    """Verify constraints field correctly encodes and reconstructs veto conditions."""
    # Active veto
    c_active = ParadoxConstraints(
        collapse_veto=True,
        veto_reason="entropy_above_threshold",
        entropy_threshold=0.70,
        balance_window=(0.35, 0.65),
    )
    d = c_active.to_dict()
    c_rt = ParadoxConstraints.from_dict(d)

    assert c_rt.collapse_veto is True
    assert c_rt.veto_reason == "entropy_above_threshold"
    assert c_rt.entropy_threshold == 0.70
    assert c_rt.balance_window == (0.35, 0.65)
    assert isinstance(c_rt.balance_window, tuple), "balance_window must be tuple after roundtrip"

    # Default (no veto)
    c_default = ParadoxConstraints()
    assert c_default.collapse_veto is False
    assert c_default.veto_reason == ""

    # From empty dict (backward compat with Phase 4 snapshots)
    c_legacy = ParadoxConstraints.from_dict({})
    assert c_legacy.collapse_veto is False
    assert c_legacy.entropy_threshold == 0.70
    assert c_legacy.balance_window == (0.35, 0.65)

    print("  PASS: Constraints veto gate encoding")


# =========================================================================
# Test 11: Phase 4 snapshot backward compatibility
# =========================================================================

def test_phase4_snapshot_backward_compat():
    """Phase 4 snapshots (without constraints or pole confidence) load correctly."""
    # Simulate a Phase 4 paradox dict (no constraints, no pole confidence)
    phase4_paradox_dict = {
        "id": "paradox_0001",
        "poles": {
            "a": {"id": "autonomy", "emoji": "🧭"},
            "b": {"id": "control", "emoji": "🛡️"},
        },
        "status": "open",
        "metrics": {"tension_strength": 0.5},
        "emoji_vector_id": "ev_0001",
        "history": [],
        "rubric_scores": [],
        "links": {
            "claims": ["claim_0001"],
            "missions": ["M1"],
            "memory_hash": None,
            "related_paradoxes": [],
        },
        "timestamp": "2026-03-03T00:00:00+00:00",
    }

    p = Paradox.from_dict(phase4_paradox_dict)

    # Constraints should default safely
    assert p.constraints.collapse_veto is False
    assert p.constraints.entropy_threshold == 0.70
    assert p.constraints.balance_window == (0.35, 0.65)

    # Pole confidence should default to 0.5
    assert p.pole_a.confidence == 0.5
    assert p.pole_b.confidence == 0.5

    # Core fields preserved
    assert p.id == "paradox_0001"
    assert p.status == "open"
    assert p.emoji_vector_id == "ev_0001"

    # Roundtrip still works (now includes defaults)
    d = p.to_dict()
    p2 = Paradox.from_dict(d)
    assert p.content_hash() == p2.content_hash()

    print("  PASS: Phase 4 snapshot backward compatibility")


# =========================================================================
# Runner
# =========================================================================

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("PHASE 5 STEP 1 — SUBSTRATE UNIT TESTS")
    print("=" * 60 + "\n")

    tests = [
        test_emoji_vector_metric_determinism,
        test_emoji_vector_roundtrip,
        test_emoji_vector_hash_stability,
        test_paradox_constraints_roundtrip,
        test_paradox_hash_stability,
        test_mutation_determinism,
        test_mutation_replay,
        test_system_state_roundtrip,
        test_pole_confidence_preservation,
        test_constraints_veto_gate,
        test_phase4_snapshot_backward_compat,
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
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'=' * 60}")

    if failed > 0:
        print("\nSTATUS: FAIL — substrate not ready")
        sys.exit(1)
    else:
        print("\nSTATUS: PASS — substrate is deterministic, hash-stable, and reversible")
        sys.exit(0)


if __name__ == "__main__":
    main()
