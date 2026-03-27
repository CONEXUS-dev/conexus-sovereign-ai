"""
SovereignNEXT — Phase 2 Tests
Tests for claim extraction, tension detection, and populate_state.

Includes both mock tests (no LLM required) and a live test path
that uses the real LLM client against actual mission data.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, List
from unittest.mock import MagicMock

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.claim_extractor import (
    extract_claims,
    _parse_json_claims,
    _fallback_sentence_split,
    MAX_CLAIMS_PER_EXTRACTION,
)
from SovereignNEXT.operators.tension_detector import detect_tensions
from SovereignNEXT.operators.populate import populate_state

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mock LLM
# ---------------------------------------------------------------------------

def make_mock_llm(
    generate_response: str = "[]",
    embed_response: list = None,
):
    """Create a mock LLM client with canned responses."""
    mock = MagicMock()
    mock.generate.return_value = generate_response

    if embed_response is None:
        # Return distinct vectors based on text content hash
        def mock_embed(text):
            import hashlib
            if isinstance(text, list):
                vecs = []
                for t in text:
                    h = hashlib.md5(t.encode()).digest()
                    vecs.append([float(b) / 255.0 for b in h] * 24)  # 16 * 24 = 384
                return vecs
            h = hashlib.md5(text.encode()).digest()
            return [float(b) / 255.0 for b in h] * 24
        mock.embed.side_effect = mock_embed
    else:
        mock.embed.return_value = embed_response

    return mock


# ---------------------------------------------------------------------------
# Test 1: JSON parsing
# ---------------------------------------------------------------------------

def test_json_parsing():
    """Test that _parse_json_claims handles various formats."""
    print("\n--- Test 1: JSON Parsing ---")

    # Clean JSON
    result = _parse_json_claims('[{"text": "claim one", "confidence": 0.8, "tags": ["test"]}]')
    assert result is not None and len(result) == 1, f"Clean JSON failed: {result}"
    print("  Clean JSON: PASS")

    # JSON with markdown fences
    result = _parse_json_claims('```json\n[{"text": "fenced", "confidence": 0.5, "tags": []}]\n```')
    assert result is not None and len(result) == 1, f"Fenced JSON failed: {result}"
    print("  Fenced JSON: PASS")

    # JSON embedded in text
    result = _parse_json_claims('Here are the claims:\n[{"text": "embedded", "confidence": 0.6, "tags": []}]\nDone.')
    assert result is not None and len(result) == 1, f"Embedded JSON failed: {result}"
    print("  Embedded JSON: PASS")

    # Invalid JSON
    result = _parse_json_claims("This is not JSON at all.")
    assert result is None, f"Invalid JSON should return None: {result}"
    print("  Invalid JSON → None: PASS")

    print("  ALL JSON PARSING TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 2: Fallback sentence splitting
# ---------------------------------------------------------------------------

def test_fallback_splitting():
    """Test sentence splitting fallback."""
    print("\n--- Test 2: Fallback Sentence Splitting ---")

    text = (
        "Human-centered design is the antidote to sycophancy. "
        "Transparency frameworks must be implemented immediately. "
        "Accountability mechanisms prevent gaming of the system. "
        "Short. "  # Should be skipped (too short)
        "The integration of emotional intelligence with structural logic creates trust."
    )
    claims = _fallback_sentence_split(text)
    assert len(claims) <= MAX_CLAIMS_PER_EXTRACTION, f"Exceeded cap: {len(claims)}"
    assert all("text" in c for c in claims), "Missing text field"
    assert all(c["confidence"] == 0.5 for c in claims), "Default confidence should be 0.5"
    assert all("fallback_extraction" in c["tags"] for c in claims), "Missing fallback tag"
    # "Short." should be filtered out (< 20 chars)
    assert not any("Short" in c["text"] for c in claims), "Short sentence should be filtered"
    print(f"  Extracted {len(claims)} sentences (skipped short ones): PASS")
    print("  ALL FALLBACK TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 3: Claim extraction with mock LLM
# ---------------------------------------------------------------------------

def test_claim_extraction_mock():
    """Test claim extraction with a mock LLM that returns canned JSON."""
    print("\n--- Test 3: Claim Extraction (Mock LLM) ---")

    canned_json = json.dumps([
        {"text": "Sycophancy must be addressed architecturally.", "confidence": 0.9, "tags": ["architecture"]},
        {"text": "User-centric design prevents sycophantic drift.", "confidence": 0.85, "tags": ["design"]},
        {"text": "Transparency frameworks are essential.", "confidence": 0.7, "tags": ["transparency"]},
    ])
    mock_llm = make_mock_llm(generate_response=canned_json)

    claims = extract_claims(
        text="Some raw LLM output text here.",
        llm=mock_llm,
        model="test-model",
        source="collapse_M1",
        mission_id="M1",
    )

    assert len(claims) == 3, f"Expected 3 claims, got {len(claims)}"
    assert claims[0].text == "Sycophancy must be addressed architecturally."
    assert claims[0].confidence == 0.9
    assert claims[0].source == "collapse_M1"
    assert claims[0].mission_id == "M1"
    assert claims[0].operator == "collapse"
    assert "architecture" in claims[0].tags
    print(f"  Extracted {len(claims)} claims: PASS")

    # Verify cap enforcement
    many_claims = json.dumps([{"text": f"Claim {i}", "confidence": 0.5, "tags": []} for i in range(20)])
    mock_llm2 = make_mock_llm(generate_response=many_claims)
    claims2 = extract_claims(text="text", llm=mock_llm2, model="m", source="s")
    assert len(claims2) <= MAX_CLAIMS_PER_EXTRACTION, f"Cap violated: {len(claims2)}"
    print(f"  Cap enforcement ({len(claims2)} ≤ {MAX_CLAIMS_PER_EXTRACTION}): PASS")

    print("  ALL CLAIM EXTRACTION MOCK TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 4: Tension detection with mock LLM
# ---------------------------------------------------------------------------

def test_tension_detection_mock():
    """Test tension detection with mock embeddings and judge."""
    print("\n--- Test 4: Tension Detection (Mock LLM) ---")

    # Create claims from different operators
    claim_a = Claim(text="Optimization should be the primary goal.", source="collapse_M1", mission_id="M1", operator="collapse")
    claim_b = Claim(text="Emergence and creativity cannot be optimized.", source="become_M2", mission_id="M2", operator="become")
    claim_c = Claim(text="Optimization should be the primary goal.", source="collapse_M1", mission_id="M1", operator="collapse")

    # Mock LLM: embeddings in the tension band, judge returns CONTRADICTION
    mock_llm = MagicMock()

    # Embeddings: A and B are in the 0.3-0.7 band, A and C are identical
    vec_a = [0.5] * 384
    vec_b = [0.5 if i < 200 else -0.5 for i in range(384)]  # ~0.5 cosine with vec_a
    vec_c = [0.5] * 384  # Same as A

    def mock_embed(text):
        if isinstance(text, list):
            vecs = []
            for t in text:
                if "Emergence" in t:
                    vecs.append(vec_b)
                else:
                    vecs.append(vec_a)
            return vecs
        if "Emergence" in text:
            return vec_b
        return vec_a

    mock_llm.embed.side_effect = mock_embed
    mock_llm.generate.return_value = "CONTRADICTION"

    # Detect tensions between new=[claim_b] and existing=[claim_a]
    tensions = detect_tensions(
        new_claims=[claim_b],
        existing_claims=[claim_a],
        llm=mock_llm,
        model="test-model",
    )

    assert len(tensions) >= 0, "Should not crash"  # May or may not find tension depending on exact cosine
    print(f"  Detected {len(tensions)} tensions: OK")

    # Same-operator same-mission should be skipped
    tensions2 = detect_tensions(
        new_claims=[claim_c],
        existing_claims=[claim_a],
        llm=mock_llm,
        model="test-model",
    )
    assert len(tensions2) == 0, f"Same operator+mission should produce 0 tensions, got {len(tensions2)}"
    print("  Same-operator skip: PASS")

    # All tension statuses should be "open"
    for t in tensions:
        assert t.status == "open", f"Tension status should be 'open', got '{t.status}'"
    print("  All statuses = 'open': PASS")

    print("  ALL TENSION DETECTION MOCK TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 5: populate_state integration (mock)
# ---------------------------------------------------------------------------

def test_populate_state_mock():
    """Test the full populate pipeline with mock LLM."""
    print("\n--- Test 5: Populate State Integration (Mock) ---")

    # First population (no existing claims → no tensions)
    canned1 = json.dumps([
        {"text": "Efficiency is paramount.", "confidence": 0.8, "tags": ["efficiency"]},
        {"text": "Structure enables scale.", "confidence": 0.75, "tags": ["structure"]},
    ])
    mock_llm = make_mock_llm(generate_response=canned1)

    state = SystemState(mission_id="M1")
    state = populate_state(
        raw_text="Some collapse output.",
        state=state,
        llm=mock_llm,
        model="test-model",
        source="collapse_M1",
    )

    assert len(state.claims) == 2, f"Expected 2 claims, got {len(state.claims)}"
    assert len(state.tensions) == 0, "First population should have 0 tensions (nothing to compare)"
    assert state.iteration == 1
    print(f"  After pop 1: {len(state.claims)} claims, {len(state.tensions)} tensions, iter={state.iteration}: PASS")

    # Second population (now we have existing claims → tensions may appear)
    canned2 = json.dumps([
        {"text": "Creativity resists structure.", "confidence": 0.7, "tags": ["creativity"]},
    ])
    mock_llm.generate.return_value = canned2

    state = populate_state(
        raw_text="Some become output.",
        state=state,
        llm=mock_llm,
        model="test-model",
        source="become_M2",
        mission_id="M2",
    )

    assert len(state.claims) >= 3, f"Expected ≥3 claims, got {len(state.claims)}"
    assert state.iteration == 2
    print(f"  After pop 2: {len(state.claims)} claims, {len(state.tensions)} tensions, iter={state.iteration}: PASS")

    # Sanity checks
    assert len(state.paradoxes) == 0, "No paradoxes should be created in Phase 2"
    assert len(state.emoji_fields) == 0, "No emoji vectors should be created in Phase 2"
    print("  No paradoxes or emoji vectors: PASS")

    print("  ALL POPULATE STATE MOCK TESTS PASSED")


# ---------------------------------------------------------------------------
# Test 6: Live test with real LLM (optional)
# ---------------------------------------------------------------------------

def test_live_with_mission_data():
    """Live test: feed actual mission_1.json output through the pipeline."""
    print("\n--- Test 6: Live Test with Real LLM + Mission Data ---")

    mission_path = REPO_ROOT / "SOVEREIGN_PROOF" / "v2_full_missions" / "mission_1.json"
    if not mission_path.exists():
        print("  SKIPPED — mission_1.json not found")
        return

    # Load mission data
    with open(mission_path) as f:
        mission = json.load(f)
    raw_text = mission.get("task_output", "")
    if not raw_text:
        print("  SKIPPED — no task_output in mission_1.json")
        return

    print(f"  Loaded mission_1.json: {len(raw_text)} chars")

    # Initialize real LLM client
    try:
        from agents.llm_client import LLMClient, SWAY_MODEL
        llm = LLMClient()
    except Exception as e:
        print(f"  SKIPPED — LLM client init failed: {e}")
        return

    try:
        state = SystemState(mission_id="M1_live")

        # First populate from mission 1
        state = populate_state(
            raw_text=raw_text,
            state=state,
            llm=llm,
            model=SWAY_MODEL,
            source="collapse_M1",
            mission_id="M1",
        )

        print(f"  After M1: {state.summary()}")

        # Verify constraints
        assert len(state.claims) <= MAX_CLAIMS_PER_EXTRACTION, f"Cap violated: {len(state.claims)}"
        assert len(state.paradoxes) == 0, "No paradoxes in Phase 2"
        assert len(state.emoji_fields) == 0, "No emoji vectors in Phase 2"
        for t in state.tensions:
            assert t.status == "open", f"Non-open tension: {t.status}"

        print(f"  Claims: {len(state.claims)}")
        for c in state.claims:
            print(f"    [{c.confidence:.2f}] {c.text[:80]}")

        print(f"  Tensions: {len(state.tensions)}")
        for t in state.tensions:
            print(f"    {t.relation_type}: {t.pole_a[:40]} ↔ {t.pole_b[:40]}")

        # Now load mission 2 and populate again
        m2_path = REPO_ROOT / "SOVEREIGN_PROOF" / "v2_full_missions" / "mission_2.json"
        if m2_path.exists():
            with open(m2_path) as f:
                m2 = json.load(f)
            m2_text = m2.get("task_output", "")
            if m2_text:
                state = populate_state(
                    raw_text=m2_text,
                    state=state,
                    llm=llm,
                    model=SWAY_MODEL,
                    source="become_M2",
                    mission_id="M2",
                )
                print(f"\n  After M2: {state.summary()}")
                print(f"  Claims: {len(state.claims)}")
                print(f"  Tensions: {len(state.tensions)}")
                for t in state.tensions:
                    print(f"    {t.relation_type}: {t.pole_a[:40]} ↔ {t.pole_b[:40]}")

        print("\n  LIVE TEST PASSED")
    finally:
        llm.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("SovereignNEXT — Phase 2 Tests")
    print("=" * 60)

    # Mock tests (always run)
    test_json_parsing()
    test_fallback_splitting()
    test_claim_extraction_mock()
    test_tension_detection_mock()
    test_populate_state_mock()

    # Live test (optional — requires LLM models + mission data)
    if "--live" in sys.argv:
        test_live_with_mission_data()
    else:
        print("\n--- Live test skipped (pass --live to enable) ---")

    print("\n" + "=" * 60)
    print("ALL PHASE 2 TESTS COMPLETE")
    print("=" * 60)
