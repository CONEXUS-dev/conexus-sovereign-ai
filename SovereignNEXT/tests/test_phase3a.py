"""
SovereignNEXT -- Phase 3a Tests
Tests for Become per-claim expansion and post-expansion tension detection.

Includes mock tests (no LLM) and a live test path that rebuilds Phase 2 state
then runs a single Become pass to observe divergence.
"""

import json
import hashlib
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.become_expander import (
    expand_claim,
    become_pass,
    become_pass_targeted,
    become_pass_adaptive,
    select_targeted_claims,
    analyze_pass3_strategy,
    MAX_CLAIMS_TO_EXPAND,
    MAX_EXPANSIONS_PER_CLAIM,
    MAX_TARGETED_CLAIMS,
    MAX_TARGETED_EXPANSIONS,
    MAX_BROAD_CLAIMS,
    MAX_BROAD_EXPANSIONS,
)
from SovereignNEXT.operators.populate import populate_state

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mock LLM
# ---------------------------------------------------------------------------

def _hash_embed(text):
    """Produce a distinct 384-dim vector from text content."""
    h = hashlib.md5(text.encode()).digest()
    return [float(b) / 255.0 for b in h] * 24  # 16 * 24 = 384


def make_mock_llm(generate_response="[]"):
    """Create a mock LLM client with canned generate + hash-based embed."""
    mock = MagicMock()
    mock.generate.return_value = generate_response

    def mock_embed(text):
        if isinstance(text, list):
            return [_hash_embed(t) for t in text]
        return _hash_embed(text)

    mock.embed.side_effect = mock_embed
    return mock


# ---------------------------------------------------------------------------
# Test 1: expand_claim with mock LLM
# ---------------------------------------------------------------------------

def test_expand_claim_mock():
    """Test per-claim expansion with a mock LLM returning canned alternatives."""
    print("\n--- Test 1: expand_claim (Mock LLM) ---")

    canned = json.dumps([
        {"text": "Sycophancy may be a rational strategy for AI systems optimizing for approval.", "confidence": 0.7, "type": "counter_framing"},
        {"text": "The claim assumes users can reliably distinguish sycophancy from genuine agreement.", "confidence": 0.65, "type": "deeper_why"},
        {"text": "In medical AI, sycophancy could mean confirming a misdiagnosis to avoid conflict.", "confidence": 0.8, "type": "domain_shift"},
        {"text": "When user goals are genuinely aligned with AI output, 'sycophancy' becomes indistinguishable from accuracy.", "confidence": 0.6, "type": "limit_case"},
    ])
    mock_llm = make_mock_llm(generate_response=canned)

    parent = Claim(
        text="Sycophancy must be addressed architecturally.",
        confidence=1.0,
        source="collapse_M1",
        mission_id="M1",
        operator="collapse",
    )

    expansions = expand_claim(parent, mock_llm, "test-model")

    assert len(expansions) == 4, f"Expected 4 expansions, got {len(expansions)}"
    print(f"  Generated {len(expansions)} expansions: PASS")

    # Check provenance
    for exp in expansions:
        assert exp.parent_id == parent.id, f"parent_id mismatch: {exp.parent_id} != {parent.id}"
        assert exp.operator == "become"
        assert exp.source == "become_expand"
        assert "expansion" in exp.tags
        assert "become" in exp.tags
    print("  Provenance (parent_id, operator, source, tags): PASS")

    # Check expansion types are tagged
    types_found = {t for exp in expansions for t in exp.tags if t in {"counter_framing", "deeper_why", "domain_shift", "limit_case"}}
    assert len(types_found) == 4, f"Expected 4 expansion types, got {types_found}"
    print(f"  Expansion types: {types_found}: PASS")

    # Check confidence varies (not all 1.0)
    confidences = [exp.confidence for exp in expansions]
    assert not all(c == 1.0 for c in confidences), f"All confidences are 1.0: {confidences}"
    print(f"  Confidence variation: {confidences}: PASS")

    # Check texts are distinct from parent
    for exp in expansions:
        assert exp.text != parent.text, f"Expansion is identical to parent: {exp.text}"
    print("  Texts distinct from parent: PASS")

    print("  ALL expand_claim MOCK TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 2: expand_claim handles LLM failure gracefully
# ---------------------------------------------------------------------------

def test_expand_claim_failure():
    """Test that expansion returns empty list on LLM failure."""
    print("\n--- Test 2: expand_claim Failure Handling ---")

    mock_llm = MagicMock()
    mock_llm.generate.side_effect = RuntimeError("LLM crashed")

    parent = Claim(text="Some claim.", confidence=1.0, source="test")
    expansions = expand_claim(parent, mock_llm, "test-model")
    assert expansions == [], f"Expected empty list on failure, got {len(expansions)}"
    print("  LLM crash -> empty list: PASS")

    # Bad JSON
    mock_llm2 = make_mock_llm(generate_response="This is not JSON at all.")
    expansions2 = expand_claim(parent, mock_llm2, "test-model")
    assert expansions2 == [], f"Expected empty list on bad JSON, got {len(expansions2)}"
    print("  Bad JSON -> empty list: PASS")

    print("  ALL FAILURE HANDLING TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 3: become_pass integration (mock)
# ---------------------------------------------------------------------------

def test_become_pass_mock():
    """Test full Become pass with mock LLM."""
    print("\n--- Test 3: become_pass Integration (Mock) ---")

    # Build initial state with 3 claims (simulating Phase 2 output)
    state = SystemState(mission_id="M1")
    state.add_claim(Claim(text="Efficiency is paramount.", confidence=1.0, source="collapse_M1", operator="collapse", mission_id="M1"))
    state.add_claim(Claim(text="Structure enables scale.", confidence=1.0, source="collapse_M1", operator="collapse", mission_id="M1"))
    state.add_claim(Claim(text="Design should center the user.", confidence=0.9, source="become_M1", operator="become", mission_id="M1"))

    initial_count = len(state.claims)
    assert initial_count == 3

    # Mock LLM returns 4 expansions per claim
    canned = json.dumps([
        {"text": "Efficiency can suppress innovation when taken to extremes.", "confidence": 0.6, "type": "counter_framing"},
        {"text": "Efficiency assumes a well-defined objective function exists.", "confidence": 0.7, "type": "deeper_why"},
        {"text": "In ecology, efficiency means fragility -- diverse systems outperform optimized ones.", "confidence": 0.75, "type": "domain_shift"},
        {"text": "Efficiency becomes meaningless when the problem definition is wrong.", "confidence": 0.65, "type": "limit_case"},
    ])
    mock_llm = make_mock_llm(generate_response=canned)

    # Also mock the judge for tension detection
    mock_llm.generate.side_effect = None
    _call_count = [0]
    def multi_response(*args, **kwargs):
        _call_count[0] += 1
        # First 3 calls are expansions (one per claim), rest are judge calls
        if _call_count[0] <= 3:
            return canned
        return "CONTRADICTION"
    mock_llm.generate.side_effect = multi_response

    state = become_pass(
        state=state,
        llm=mock_llm,
        model="become-model",
        judge_model="judge-model",
    )

    # Verify expansion claims were added
    expansion_claims = [c for c in state.claims if c.parent_id is not None]
    original_claims = [c for c in state.claims if c.parent_id is None]
    assert len(original_claims) == initial_count, f"Original claims changed: {len(original_claims)}"
    assert len(expansion_claims) > 0, "No expansion claims created"
    print(f"  Original claims: {len(original_claims)}, Expansion claims: {len(expansion_claims)}: PASS")

    # Verify all expansion claims have become provenance
    for ec in expansion_claims:
        assert ec.operator == "become"
        assert ec.source == "become_expand"
        assert ec.parent_id is not None
        assert ec.parent_id in {c.id for c in original_claims}
    print("  Expansion provenance: PASS")

    # Verify no paradoxes or emojis created
    assert len(state.paradoxes) == 0, "Paradoxes should not exist in Phase 3a"
    assert len(state.emoji_fields) == 0, "Emoji vectors should not exist in Phase 3a"
    print("  No paradoxes or emojis: PASS")

    # Verify iteration incremented
    assert state.iteration == 1, f"Expected iteration 1, got {state.iteration}"
    print(f"  Iteration: {state.iteration}: PASS")

    print(f"  Summary: {state.summary()}")
    print("  ALL become_pass MOCK TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 4: Expansion cap enforcement
# ---------------------------------------------------------------------------

def test_expansion_cap():
    """Verify only MAX_CLAIMS_TO_EXPAND claims are expanded."""
    print("\n--- Test 4: Expansion Cap Enforcement ---")

    state = SystemState(mission_id="M1")
    # Add 10 claims
    for i in range(10):
        state.add_claim(Claim(
            text=f"Claim number {i} about important topic {i}.",
            confidence=1.0,
            source="collapse_M1",
            operator="collapse",
            mission_id="M1",
        ))

    canned = json.dumps([
        {"text": "Counter perspective.", "confidence": 0.5, "type": "counter_framing"},
    ])
    mock_llm = make_mock_llm(generate_response=canned)

    state = become_pass(state, mock_llm, "m", "m", max_claims=MAX_CLAIMS_TO_EXPAND)

    expansion_claims = [c for c in state.claims if c.parent_id is not None]
    # Each expanded claim should produce 1 expansion (from our canned response)
    # Total expansions should be capped at MAX_CLAIMS_TO_EXPAND * 1
    assert len(expansion_claims) <= MAX_CLAIMS_TO_EXPAND * MAX_EXPANSIONS_PER_CLAIM, \
        f"Expansion cap violated: {len(expansion_claims)} expansions"
    print(f"  {len(expansion_claims)} expansions from {MAX_CLAIMS_TO_EXPAND} claims (cap respected): PASS")

    print("  EXPANSION CAP TEST PASSED")


# ---------------------------------------------------------------------------
# Test 5: select_targeted_claims scoring (mock)
# ---------------------------------------------------------------------------

def test_select_targeted_claims_mock():
    """Test that targeted selection picks high-tension claims and excludes zero-tension ones."""
    print("\n--- Test 5: select_targeted_claims (Mock) ---")

    from SovereignNEXT.state.tension import Tension

    state = SystemState(mission_id="M1")

    # Create 5 claims with varying properties
    c1 = Claim(text="Claim A with many tensions.", confidence=0.75, source="collapse_M1", operator="collapse", mission_id="M1")
    c2 = Claim(text="Claim B with one tension.", confidence=0.70, source="collapse_M1", operator="collapse", mission_id="M1")
    c3 = Claim(text="Claim C with zero tensions.", confidence=0.80, source="collapse_M1", operator="collapse", mission_id="M1")
    c4 = Claim(text="Claim D limit case.", confidence=0.65, source="become_expand", operator="become", mission_id="M1", tags=["limit_case", "expansion", "become"])
    c5 = Claim(text="Claim E cross-claim.", confidence=0.60, source="become_expand", operator="become", mission_id="M1")

    for c in [c1, c2, c3, c4, c5]:
        state.add_claim(c)

    # Add tensions: c1 involved in 3 tensions, c2 in 1, c4 in 1 (but limit_case), c5 in 2 cross-claim
    state.add_tension(Tension(pole_a=c1.text, pole_b="other", source_claims=[c1.id, "x1"], relation_type="contradiction"))
    state.add_tension(Tension(pole_a=c1.text, pole_b="other2", source_claims=[c1.id, "x2"], relation_type="tradeoff"))
    state.add_tension(Tension(pole_a=c1.text, pole_b="other3", source_claims=[c1.id, "x3"], relation_type="contradiction"))
    state.add_tension(Tension(pole_a=c2.text, pole_b="other", source_claims=[c2.id, "x1"], relation_type="tradeoff"))
    state.add_tension(Tension(pole_a=c4.text, pole_b="other", source_claims=[c4.id, "x1"], relation_type="contradiction"))
    state.add_tension(Tension(pole_a=c5.text, pole_b="other", source_claims=[c5.id, "x1"], relation_type="tradeoff"))
    state.add_tension(Tension(pole_a=c5.text, pole_b="other2", source_claims=[c5.id, "x4"], relation_type="contradiction"))

    selected = select_targeted_claims(state, max_claims=3)

    selected_ids = {c.id for c in selected}

    # c1 should be selected (3 tensions, mid-confidence)
    assert c1.id in selected_ids, f"c1 (high tension density) should be selected, got {selected_ids}"
    print("  High-tension-density claim selected: PASS")

    # c3 should NOT be selected (zero tensions)
    assert c3.id not in selected_ids, "c3 (zero tensions) should be excluded"
    print("  Zero-tension claim excluded: PASS")

    # c4 should NOT be selected (limit_case tag)
    assert c4.id not in selected_ids, "c4 (limit_case) should be excluded"
    print("  Limit-case claim excluded: PASS")

    # c1 should rank higher than c2 (more tensions)
    if c2.id in selected_ids:
        idx_c1 = [i for i, c in enumerate(selected) if c.id == c1.id][0]
        idx_c2 = [i for i, c in enumerate(selected) if c.id == c2.id][0]
        assert idx_c1 < idx_c2, "c1 should rank higher than c2"
        print("  Ranking: high-density > low-density: PASS")

    print(f"  Selected {len(selected)} claims: {[c.id for c in selected]}")
    print("  ALL select_targeted_claims TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 6: become_pass_targeted integration (mock)
# ---------------------------------------------------------------------------

def test_become_pass_targeted_mock():
    """Test targeted Become pass with mock LLM."""
    print("\n--- Test 6: become_pass_targeted Integration (Mock) ---")

    from SovereignNEXT.state.tension import Tension

    state = SystemState(mission_id="M1")

    # Create original claims
    orig1 = Claim(text="Original claim about efficiency.", confidence=1.0, source="collapse_M1", operator="collapse", mission_id="M1")
    orig2 = Claim(text="Original claim about transparency.", confidence=1.0, source="collapse_M1", operator="collapse", mission_id="M2")
    state.add_claim(orig1)
    state.add_claim(orig2)

    # Simulate pass-1 expansions
    exp1 = Claim(text="Counter: efficiency suppresses innovation.", confidence=0.70, source="become_expand", operator="become", mission_id="M1", parent_id=orig1.id, tags=["counter_framing", "expansion", "become"])
    exp2 = Claim(text="Deeper: transparency assumes good faith actors.", confidence=0.65, source="become_expand", operator="become", mission_id="M2", parent_id=orig2.id, tags=["deeper_why", "expansion", "become"])
    exp3 = Claim(text="Domain: in ecology, efficiency means fragility.", confidence=0.75, source="become_expand", operator="become", mission_id="M1", parent_id=orig1.id, tags=["domain_shift", "expansion", "become"])
    state.add_claim(exp1)
    state.add_claim(exp2)
    state.add_claim(exp3)

    # Add tensions from pass 1
    state.add_tension(Tension(pole_a=exp1.text, pole_b=orig1.text, source_claims=[exp1.id, orig1.id], relation_type="contradiction"))
    state.add_tension(Tension(pole_a=exp1.text, pole_b=orig2.text, source_claims=[exp1.id, orig2.id], relation_type="tradeoff"))
    state.add_tension(Tension(pole_a=exp2.text, pole_b=orig2.text, source_claims=[exp2.id, orig2.id], relation_type="contradiction"))
    state.add_tension(Tension(pole_a=exp3.text, pole_b=orig1.text, source_claims=[exp3.id, orig1.id], relation_type="tradeoff"))

    pre_claims = len(state.claims)
    pre_tensions = len(state.tensions)

    # Mock LLM: returns 3 expansions per claim, then CONTRADICTION for judging
    canned = json.dumps([
        {"text": "Targeted counter perspective.", "confidence": 0.55, "type": "counter_framing"},
        {"text": "Targeted deeper question.", "confidence": 0.60, "type": "deeper_why"},
        {"text": "Targeted domain shift.", "confidence": 0.50, "type": "domain_shift"},
    ])
    mock_llm = make_mock_llm(generate_response=canned)

    _call_count = [0]
    def multi_response(*args, **kwargs):
        _call_count[0] += 1
        # First N calls are expansions, rest are judge calls
        if _call_count[0] <= 8:  # generous cap for expansion calls
            return canned
        return "CONTRADICTION"
    mock_llm.generate.side_effect = multi_response

    state = become_pass_targeted(
        state=state,
        llm=mock_llm,
        model="become-model",
        judge_model="judge-model",
    )

    # Verify new claims were added
    new_claims = len(state.claims) - pre_claims
    assert new_claims > 0, "No new claims from targeted pass"
    print(f"  New claims: {new_claims}: PASS")

    # Verify pass-2 expansions have parent_id pointing to pass-1 expansions (grandchild lineage)
    pass2_claims = [c for c in state.claims if c.parent_id is not None and c.parent_id not in {orig1.id, orig2.id}]
    if pass2_claims:
        for c in pass2_claims:
            assert c.parent_id is not None
            assert c.operator == "become"
        print(f"  Grandchild lineage (pass-2 -> pass-1): {len(pass2_claims)} claims: PASS")
    else:
        # If targeting picked originals (which have tensions), that's also valid
        pass2_exp = [c for c in state.claims if c.parent_id is not None]
        print(f"  Expansion claims with lineage: {len(pass2_exp) - 3}: PASS")

    # Verify no paradoxes or emojis
    assert len(state.paradoxes) == 0, "No paradoxes in Phase 3a"
    assert len(state.emoji_fields) == 0, "No emoji vectors in Phase 3a"
    print("  No paradoxes or emojis: PASS")

    # Verify iteration incremented
    assert state.iteration == 1, f"Expected iteration 1, got {state.iteration}"
    print(f"  Iteration: {state.iteration}: PASS")

    print(f"  Summary: {state.summary()}")
    print("  ALL become_pass_targeted MOCK TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 7: Live test with real LLM + mission data (Pass 1)
# ---------------------------------------------------------------------------

def test_live_become_pass():
    """Live: rebuild Phase 2 state from missions, then run Become, observe tensions."""
    print("\n--- Test 7: Live Become Pass (Pass 1) ---")

    # Load mission data
    m1_path = REPO_ROOT / "SOVEREIGN_PROOF" / "v2_full_missions" / "mission_1.json"
    m2_path = REPO_ROOT / "SOVEREIGN_PROOF" / "v2_full_missions" / "mission_2.json"
    if not m1_path.exists():
        print("  SKIPPED -- mission_1.json not found")
        return

    # Initialize LLM
    try:
        from agents.llm_client import LLMClient, SWAY_MODEL, OPIE_MODEL
        llm = LLMClient()
    except Exception as e:
        print(f"  SKIPPED -- LLM client init failed: {e}")
        return

    try:
        # Rebuild Phase 2 state
        state = SystemState(mission_id="M1_live")
        embedding_cache = {}

        with open(m1_path) as f:
            m1 = json.load(f)
        state = populate_state(m1.get("task_output", ""), state, llm, SWAY_MODEL,
                               source="collapse_M1", mission_id="M1", embedding_cache=embedding_cache)

        if m2_path.exists():
            with open(m2_path) as f:
                m2 = json.load(f)
            state = populate_state(m2.get("task_output", ""), state, llm, SWAY_MODEL,
                                   source="become_M2", mission_id="M2", embedding_cache=embedding_cache)

        print(f"  Phase 2 rebuilt: {state.summary()}")
        pre_become_claims = len(state.claims)
        pre_become_tensions = len(state.tensions)

        # Run Become pass
        # Note: Using SWAY_MODEL for both expansion and judging because only one
        # 7B model fits in CPU RAM at a time. The expand_claim() function sets
        # temp=0.65 internally regardless of model, so creative divergence is preserved.
        print("\n  Running Become pass (per-claim expansion)...")
        state = become_pass(
            state=state,
            llm=llm,
            model=SWAY_MODEL,
            judge_model=SWAY_MODEL,
            embedding_cache=embedding_cache,
        )

        # Report results
        print(f"\n  === BECOME PASS RESULTS ===")
        print(f"  Claims before: {pre_become_claims} -> after: {len(state.claims)}")
        print(f"  Tensions before: {pre_become_tensions} -> after: {len(state.tensions)}")

        expansion_claims = [c for c in state.claims if c.parent_id is not None]
        original_claims = [c for c in state.claims if c.parent_id is None]
        print(f"  Original claims: {len(original_claims)}")
        print(f"  Expansion claims: {len(expansion_claims)}")

        # Show expansion details
        print("\n  --- Expansion Claims ---")
        for ec in expansion_claims:
            exp_type = [t for t in ec.tags if t not in ("expansion", "become")]
            print(f"    [{ec.confidence:.2f}] ({', '.join(exp_type)}) parent={ec.parent_id}: {ec.text[:80]}")

        # Show tensions
        if state.tensions:
            print(f"\n  --- Tensions ({len(state.tensions)}) ---")
            for t in state.tensions:
                print(f"    {t.relation_type}: {t.pole_a[:40]} <-> {t.pole_b[:40]} (strength={t.metrics.tension_strength:.3f})")
        else:
            print("\n  --- No tensions detected ---")

        # Confidence variation check
        all_confs = [c.confidence for c in state.claims]
        unique_confs = set(all_confs)
        print(f"\n  Confidence variation: {len(unique_confs)} unique values in {len(all_confs)} claims")
        if len(unique_confs) > 1:
            print(f"    Range: {min(all_confs):.2f} - {max(all_confs):.2f}")

        # Invariant checks
        assert len(state.paradoxes) == 0, "No paradoxes in Phase 3a"
        assert len(state.emoji_fields) == 0, "No emoji vectors in Phase 3a"
        for ec in expansion_claims:
            assert ec.parent_id is not None
            assert ec.operator == "become"
        for t in state.tensions:
            assert t.status == "open"

        print("\n  LIVE BECOME PASS -- COMPLETE")
        print(f"  Final state: {state.summary()}")

    finally:
        llm.close()


# ---------------------------------------------------------------------------
# Test 8: Live test -- Targeted Become Pass #2
# ---------------------------------------------------------------------------

def test_live_become_pass_2(state_from_pass1=None):
    """Live: take pass-1 state and run a targeted Become pass #2.

    If state_from_pass1 is None, rebuilds Phase 2 + pass 1 from scratch.
    """
    print("\n--- Test 8: Live Targeted Become Pass #2 ---")

    m1_path = REPO_ROOT / "SOVEREIGN_PROOF" / "v2_full_missions" / "mission_1.json"
    m2_path = REPO_ROOT / "SOVEREIGN_PROOF" / "v2_full_missions" / "mission_2.json"
    if not m1_path.exists():
        print("  SKIPPED -- mission_1.json not found")
        return

    try:
        from agents.llm_client import LLMClient, SWAY_MODEL, OPIE_MODEL
        llm = LLMClient()
    except Exception as e:
        print(f"  SKIPPED -- LLM client init failed: {e}")
        return

    try:
        embedding_cache = {}

        if state_from_pass1 is not None:
            state = state_from_pass1
            print(f"  Using provided pass-1 state: {state.summary()}")
        else:
            # Rebuild Phase 2 state
            state = SystemState(mission_id="M1_live")
            with open(m1_path) as f:
                m1 = json.load(f)
            state = populate_state(m1.get("task_output", ""), state, llm, SWAY_MODEL,
                                   source="collapse_M1", mission_id="M1", embedding_cache=embedding_cache)
            if m2_path.exists():
                with open(m2_path) as f:
                    m2 = json.load(f)
                state = populate_state(m2.get("task_output", ""), state, llm, SWAY_MODEL,
                                       source="become_M2", mission_id="M2", embedding_cache=embedding_cache)
            print(f"  Phase 2 rebuilt: {state.summary()}")

            # Run Become pass 1
            print("  Running Become pass 1...")
            state = become_pass(
                state=state,
                llm=llm,
                model=SWAY_MODEL,
                judge_model=SWAY_MODEL,
                embedding_cache=embedding_cache,
            )
            print(f"  Pass 1 complete: {state.summary()}")

        pre_pass2_claims = len(state.claims)
        pre_pass2_tensions = len(state.tensions)

        # Run Targeted Become Pass #2
        print("\n  Running Targeted Become Pass #2...")
        state = become_pass_targeted(
            state=state,
            llm=llm,
            model=SWAY_MODEL,
            judge_model=SWAY_MODEL,
            embedding_cache=embedding_cache,
        )

        # Report results
        print(f"\n  === TARGETED BECOME PASS #2 RESULTS ===")
        print(f"  Claims before: {pre_pass2_claims} -> after: {len(state.claims)}")
        print(f"  Tensions before: {pre_pass2_tensions} -> after: {len(state.tensions)}")

        # Show lineage depth
        originals = [c for c in state.claims if c.parent_id is None]
        gen1 = [c for c in state.claims if c.parent_id is not None and c.parent_id in {o.id for o in originals}]
        gen2 = [c for c in state.claims if c.parent_id is not None and c.parent_id in {g.id for g in gen1}]
        print(f"  Lineage: {len(originals)} originals -> {len(gen1)} gen-1 -> {len(gen2)} gen-2")

        # Show pass-2 expansion details
        pass2_claims = state.claims[pre_pass2_claims:]
        if pass2_claims:
            print(f"\n  --- Pass-2 Expansion Claims ({len(pass2_claims)}) ---")
            for ec in pass2_claims:
                exp_type = [t for t in ec.tags if t not in ("expansion", "become")]
                print(f"    [{ec.confidence:.2f}] ({', '.join(exp_type)}) parent={ec.parent_id}: {ec.text[:80]}")

        # Show all tensions
        if state.tensions:
            print(f"\n  --- All Tensions ({len(state.tensions)}) ---")
            for t in state.tensions:
                print(f"    {t.relation_type}: {t.pole_a[:40]} <-> {t.pole_b[:40]} (strength={t.metrics.tension_strength:.3f})")

        # Confidence variation
        all_confs = [c.confidence for c in state.claims]
        unique_confs = set(all_confs)
        print(f"\n  Confidence variation: {len(unique_confs)} unique values in {len(all_confs)} claims")
        if len(unique_confs) > 1:
            print(f"    Range: {min(all_confs):.2f} - {max(all_confs):.2f}")

        # Invariant checks
        assert len(state.paradoxes) == 0, "No paradoxes in Phase 3a"
        assert len(state.emoji_fields) == 0, "No emoji vectors in Phase 3a"
        for ec in pass2_claims:
            assert ec.parent_id is not None
            assert ec.operator == "become"
        for t in state.tensions:
            assert t.status == "open"

        print("\n  LIVE TARGETED BECOME PASS #2 -- COMPLETE")
        print(f"  Final state: {state.summary()}")

    finally:
        llm.close()


# ---------------------------------------------------------------------------
# Test 9: analyze_pass3_strategy scoring (mock)
# ---------------------------------------------------------------------------

def test_analyze_pass3_strategy_mock():
    """Test that strategy analysis picks targeted/broad/hybrid correctly."""
    print("\n--- Test 9: analyze_pass3_strategy (Mock) ---")

    from SovereignNEXT.state.tension import Tension

    # Scenario A: Highly clustered tensions -> targeted
    state_a = SystemState(mission_id="M1")
    hub = Claim(text="Hub claim.", confidence=0.80, source="test", mission_id="M1")
    others = [Claim(text=f"Other {i}.", confidence=0.70, source="test", mission_id="M1") for i in range(5)]
    state_a.add_claim(hub)
    for o in others:
        state_a.add_claim(o)
    # Hub involved in 5 tensions, others in 1 each
    for o in others:
        state_a.add_tension(Tension(pole_a=hub.text, pole_b=o.text, source_claims=[hub.id, o.id], relation_type="contradiction"))

    result_a = analyze_pass3_strategy(state_a)
    assert result_a["strategy"] == "targeted", f"Expected targeted, got {result_a['strategy']}"
    print(f"  Scenario A (clustered): strategy={result_a['strategy']}: PASS")

    # Scenario B: Many zero-tension claims -> broad
    state_b = SystemState(mission_id="M1")
    for i in range(10):
        state_b.add_claim(Claim(text=f"Claim {i}.", confidence=0.70, source="test", mission_id="M1"))
    # Only 1 tension between first 2 claims
    c_list = list(state_b.claims)
    state_b.add_tension(Tension(pole_a=c_list[0].text, pole_b=c_list[1].text, source_claims=[c_list[0].id, c_list[1].id], relation_type="tradeoff"))

    result_b = analyze_pass3_strategy(state_b)
    assert result_b["strategy"] == "broad", f"Expected broad, got {result_b['strategy']}"
    print(f"  Scenario B (sparse): strategy={result_b['strategy']}: PASS")

    # Scenario C: Moderate distribution -> hybrid
    state_c = SystemState(mission_id="M1")
    claims_c = [Claim(text=f"Claim {i}.", confidence=0.70, source="test", mission_id="M1") for i in range(10)]
    for c in claims_c:
        state_c.add_claim(c)
    # Spread tensions across 6 of 10 claims (not clustered, not sparse)
    for i in range(0, 6, 2):
        state_c.add_tension(Tension(
            pole_a=claims_c[i].text, pole_b=claims_c[i+1].text,
            source_claims=[claims_c[i].id, claims_c[i+1].id],
            relation_type="contradiction",
        ))

    result_c = analyze_pass3_strategy(state_c)
    assert result_c["strategy"] == "hybrid", f"Expected hybrid, got {result_c['strategy']}"
    print(f"  Scenario C (mixed): strategy={result_c['strategy']}: PASS")

    # Verify metrics are present
    for result in [result_a, result_b, result_c]:
        assert "metrics" in result
        assert "rationale" in result
        assert "cluster_ratio" in result["metrics"]
        assert "zero_tension_claims" in result["metrics"]
        assert "polarity_axes" in result["metrics"]
        assert "confidence_tiers" in result["metrics"]
    print("  Metrics structure: PASS")

    print("  ALL analyze_pass3_strategy TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 10: become_pass_adaptive integration (mock)
# ---------------------------------------------------------------------------

def test_become_pass_adaptive_mock():
    """Test adaptive Become pass with mock LLM."""
    print("\n--- Test 10: become_pass_adaptive Integration (Mock) ---")

    from SovereignNEXT.state.tension import Tension

    state = SystemState(mission_id="M1")

    # Build a state that will trigger hybrid strategy:
    # Some hot-spot claims + some zero-tension claims
    hot1 = Claim(text="Hot claim about efficiency.", confidence=0.80, source="collapse_M1", operator="collapse", mission_id="M1")
    hot2 = Claim(text="Hot claim about design.", confidence=0.75, source="collapse_M1", operator="collapse", mission_id="M1")
    cold1 = Claim(text="Cold claim about testing.", confidence=0.70, source="become_expand", operator="become", mission_id="M1", parent_id="fake_parent_1")
    cold2 = Claim(text="Cold claim about scaling.", confidence=0.65, source="become_expand", operator="become", mission_id="M1", parent_id="fake_parent_2")
    cold3 = Claim(text="Cold claim about monitoring.", confidence=0.60, source="become_expand", operator="become", mission_id="M1", parent_id="fake_parent_3")
    neutral1 = Claim(text="Neutral claim about deployment.", confidence=0.90, source="collapse_M1", operator="collapse", mission_id="M1")
    neutral2 = Claim(text="Neutral claim about integration.", confidence=0.85, source="collapse_M1", operator="collapse", mission_id="M1")

    for c in [hot1, hot2, cold1, cold2, cold3, neutral1, neutral2]:
        state.add_claim(c)

    # Hot claims have multiple tensions
    state.add_tension(Tension(pole_a=hot1.text, pole_b=hot2.text, source_claims=[hot1.id, hot2.id], relation_type="contradiction"))
    state.add_tension(Tension(pole_a=hot1.text, pole_b=neutral1.text, source_claims=[hot1.id, neutral1.id], relation_type="tradeoff"))
    state.add_tension(Tension(pole_a=hot2.text, pole_b=neutral2.text, source_claims=[hot2.id, neutral2.id], relation_type="contradiction"))

    pre_claims = len(state.claims)
    pre_tensions = len(state.tensions)

    # Mock LLM
    canned = json.dumps([
        {"text": "Adaptive counter perspective.", "confidence": 0.55, "type": "counter_framing"},
        {"text": "Adaptive deeper question.", "confidence": 0.60, "type": "deeper_why"},
        {"text": "Adaptive domain shift.", "confidence": 0.50, "type": "domain_shift"},
    ])
    mock_llm = make_mock_llm(generate_response=canned)

    _call_count = [0]
    def multi_response(*args, **kwargs):
        _call_count[0] += 1
        if _call_count[0] <= 12:
            return canned
        return "CONTRADICTION"
    mock_llm.generate.side_effect = multi_response

    state = become_pass_adaptive(
        state=state,
        llm=mock_llm,
        model="become-model",
        judge_model="judge-model",
    )

    # Verify new claims were added
    new_claims = len(state.claims) - pre_claims
    assert new_claims > 0, "No new claims from adaptive pass"
    print(f"  New claims: {new_claims}: PASS")

    # Verify all new claims have correct lineage
    new_claim_list = state.claims[pre_claims:]
    for c in new_claim_list:
        assert c.parent_id is not None, f"Expansion {c.id} has no parent_id"
        assert c.operator == "become", f"Expansion {c.id} operator should be 'become'"
        assert c.source == "become_expand", f"Expansion {c.id} source should be 'become_expand'"
    print("  Expansion lineage: PASS")

    # Verify no paradoxes or emojis
    assert len(state.paradoxes) == 0, "No paradoxes in Phase 3a"
    assert len(state.emoji_fields) == 0, "No emoji vectors in Phase 3a"
    print("  No paradoxes or emojis: PASS")

    # Verify iteration incremented
    assert state.iteration == 1, f"Expected iteration 1, got {state.iteration}"
    print(f"  Iteration: {state.iteration}: PASS")

    print(f"  Summary: {state.summary()}")
    print("  ALL become_pass_adaptive MOCK TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 11: Live test -- Adaptive Become Pass #3
# ---------------------------------------------------------------------------

def _save_snapshot(state, label):
    """Save state snapshot to disk (incremental, crash-resilient)."""
    snapshot_dir = REPO_ROOT / "SovereignNEXT" / "tests"
    path = snapshot_dir / f"{label}_state_snapshot.json"
    try:
        with open(path, "w", encoding="utf-8") as sf:
            json.dump(state.to_dict(), sf, indent=2)
        print(f"  Snapshot saved: {path.name}")
    except Exception as e:
        print(f"  WARNING: snapshot save failed ({label}): {e}")


def test_live_become_pass_3():
    """Live: rebuild Phase 2 -> pass 1 -> pass 2 -> run adaptive pass 3 -> HOLD."""
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n--- Test 11: Live Adaptive Become Pass #3 ---")

    m1_path = REPO_ROOT / "SOVEREIGN_PROOF" / "v2_full_missions" / "mission_1.json"
    m2_path = REPO_ROOT / "SOVEREIGN_PROOF" / "v2_full_missions" / "mission_2.json"
    if not m1_path.exists():
        print("  SKIPPED -- mission_1.json not found")
        return

    try:
        from agents.llm_client import LLMClient, SWAY_MODEL
        llm = LLMClient()
    except Exception as e:
        print(f"  SKIPPED -- LLM client init failed: {e}")
        return

    state = None
    try:
        embedding_cache = {}

        # Rebuild Phase 2 state
        state = SystemState(mission_id="M1_live")
        with open(m1_path) as f:
            m1 = json.load(f)
        state = populate_state(m1.get("task_output", ""), state, llm, SWAY_MODEL,
                               source="collapse_M1", mission_id="M1", embedding_cache=embedding_cache)
        if m2_path.exists():
            with open(m2_path) as f:
                m2 = json.load(f)
            state = populate_state(m2.get("task_output", ""), state, llm, SWAY_MODEL,
                                   source="become_M2", mission_id="M2", embedding_cache=embedding_cache)
        print(f"  Phase 2 rebuilt: {state.summary()}")

        # Run Become pass 1
        print("  Running Become pass 1...")
        state = become_pass(
            state=state,
            llm=llm,
            model=SWAY_MODEL,
            judge_model=SWAY_MODEL,
            embedding_cache=embedding_cache,
        )
        print(f"  Pass 1 complete: {state.summary()}")
        _save_snapshot(state, "pass1")

        # Run Targeted Become pass 2
        print("  Running Targeted Become pass 2...")
        state = become_pass_targeted(
            state=state,
            llm=llm,
            model=SWAY_MODEL,
            judge_model=SWAY_MODEL,
            embedding_cache=embedding_cache,
        )
        print(f"  Pass 2 complete: {state.summary()}")
        _save_snapshot(state, "pass2")

        pre_pass3_claims = len(state.claims)
        pre_pass3_tensions = len(state.tensions)

        # Run Adaptive Become Pass #3
        print("\n  Running Adaptive Become Pass #3...")
        state = become_pass_adaptive(
            state=state,
            llm=llm,
            model=SWAY_MODEL,
            judge_model=SWAY_MODEL,
            embedding_cache=embedding_cache,
        )

        # Report results
        print(f"\n  === ADAPTIVE BECOME PASS #3 RESULTS ===")
        print(f"  Claims before: {pre_pass3_claims} -> after: {len(state.claims)}")
        print(f"  Tensions before: {pre_pass3_tensions} -> after: {len(state.tensions)}")

        # Show lineage depth
        originals = [c for c in state.claims if c.parent_id is None]
        gen1 = [c for c in state.claims if c.parent_id is not None and c.parent_id in {o.id for o in originals}]
        gen2_parents = {g.id for g in gen1}
        gen2 = [c for c in state.claims if c.parent_id is not None and c.parent_id in gen2_parents]
        gen3_parents = {g.id for g in gen2}
        gen3 = [c for c in state.claims if c.parent_id is not None and c.parent_id in gen3_parents]
        remainder = len(state.claims) - len(originals) - len(gen1) - len(gen2) - len(gen3)
        print(f"  Lineage: {len(originals)} originals -> {len(gen1)} gen-1 -> {len(gen2)} gen-2 -> {len(gen3)} gen-3")
        if remainder > 0:
            print(f"    ({remainder} claims with deeper or cross-gen lineage)")

        # Show pass-3 expansion details
        pass3_claims = state.claims[pre_pass3_claims:]
        if pass3_claims:
            print(f"\n  --- Pass-3 Expansion Claims ({len(pass3_claims)}) ---")
            for ec in pass3_claims:
                exp_type = [t for t in ec.tags if t not in ("expansion", "become")]
                print(f"    [{ec.confidence:.2f}] ({', '.join(exp_type)}) parent={ec.parent_id}: {ec.text[:80]}")

        # Show tension type breakdown
        if state.tensions:
            type_counts = {}
            for t in state.tensions:
                type_counts[t.relation_type] = type_counts.get(t.relation_type, 0) + 1
            print(f"\n  --- Tension Breakdown ({len(state.tensions)} total) ---")
            for ttype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
                print(f"    {ttype}: {count}")

        # Confidence variation
        all_confs = [c.confidence for c in state.claims]
        unique_confs = set(all_confs)
        print(f"\n  Confidence variation: {len(unique_confs)} unique values in {len(all_confs)} claims")
        if len(unique_confs) > 1:
            print(f"    Range: {min(all_confs):.2f} - {max(all_confs):.2f}")

        # Invariant checks
        assert len(state.paradoxes) == 0, "No paradoxes in Phase 3a"
        assert len(state.emoji_fields) == 0, "No emoji vectors in Phase 3a"
        for ec in pass3_claims:
            assert ec.parent_id is not None
            assert ec.operator == "become"
        for t in state.tensions:
            assert t.status == "open"

        print("\n  LIVE ADAPTIVE BECOME PASS #3 -- COMPLETE")
        print(f"  Final state: {state.summary()}")
        _save_snapshot(state, "pass3")

    finally:
        # Always save the best available state, even after a crash
        if state is not None:
            _save_snapshot(state, "pass3_final")
        llm.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("SovereignNEXT -- Phase 3a Tests")
    print("=" * 60)

    # Mock tests (always run)
    test_expand_claim_mock()
    test_expand_claim_failure()
    test_become_pass_mock()
    test_expansion_cap()
    test_select_targeted_claims_mock()
    test_become_pass_targeted_mock()
    test_analyze_pass3_strategy_mock()
    test_become_pass_adaptive_mock()

    # Live tests (optional)
    if "--live" in sys.argv:
        test_live_become_pass()
    elif "--live2" in sys.argv:
        test_live_become_pass_2()
    elif "--live3" in sys.argv:
        test_live_become_pass_3()
    else:
        print("\n--- Live tests skipped (pass --live for pass 1, --live2 for pass 2, --live3 for pass 3) ---")

    print("\n" + "=" * 60)
    print("ALL PHASE 3a TESTS COMPLETE")
    print("=" * 60)
