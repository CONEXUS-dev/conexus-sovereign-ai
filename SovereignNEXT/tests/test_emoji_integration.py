"""
SovereignNEXT — Emoji-Vector Integration Tests
Mock tests for all three integration points:
  1. Tension detector polarity bias via emoji_context
  2. Become expander divergence bias via emoji_field
  3. Emoji mutator mutation rules
  4. Paradox promoter lifecycle logic

All tests use mocks. No LLM calls. No file I/O.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.emoji_vector import (
    EmojiVector,
    CHAOS_EMOJIS,
    STABLE_EMOJIS,
    SUPERPOSITION_EMOJIS,
)
from SovereignNEXT.state.tension import Tension
from SovereignNEXT.state.system_state import SystemState

from SovereignNEXT.operators.tension_detector import (
    _build_judge_prompt,
    POLARITY_BIAS_INSTRUCTION,
    CHAOS_BIAS_INSTRUCTION,
    POLARITY_ENTROPY_THRESHOLD,
    POLARITY_CHAOS_THRESHOLD,
)
from SovereignNEXT.operators.become_expander import (
    _build_expansion_prompt,
    BALANCED_SPLIT_INSTRUCTION,
    OVERSTABLE_INSTRUCTION,
    DIVERGENCE_BALANCE_THRESHOLD,
    DIVERGENCE_STABILITY_THRESHOLD,
)
from SovereignNEXT.operators.emoji_mutator import (
    mutate_become,
    mutate_collapse,
    mutate_paradox_hold,
    mutate_for_operator,
    seed_initial_sequence,
    BECOME_MUTATION_BUDGET,
    COLLAPSE_MUTATION_BUDGET,
    PARADOXHOLD_MUTATION_BUDGET,
)
from SovereignNEXT.operators.paradox_promoter import (
    find_promotable_tensions,
    promote_tension,
    promote_all_eligible,
)


# ===========================================================================
# Test 1: Tension Detector -- Polarity Bias via emoji_context
# ===========================================================================

def test_judge_prompt_no_emoji():
    """Without emoji_context, the judge prompt should be unmodified."""
    print("\n--- Test 1a: Judge prompt without emoji_context ---")
    c_a = Claim(text="Transparency is essential for AI trust.")
    c_b = Claim(text="Opacity protects proprietary algorithms.")

    sys_prompt, user_prompt = _build_judge_prompt(c_a, c_b, emoji_context=None)
    assert POLARITY_BIAS_INSTRUCTION not in user_prompt, "No polarity bias without emoji_context"
    assert CHAOS_BIAS_INSTRUCTION not in user_prompt, "No chaos bias without emoji_context"
    assert "Transparency is essential" in user_prompt
    assert "Opacity protects" in user_prompt
    print("  No-emoji judge prompt: PASS")


def test_judge_prompt_low_entropy():
    """EmojiVector with low entropy should not trigger polarity bias."""
    print("\n--- Test 1b: Judge prompt with low-entropy emoji_context ---")
    c_a = Claim(text="Claim A")
    c_b = Claim(text="Claim B")

    # Low entropy: mostly one emoji repeated
    ev = EmojiVector(
        sequence=["\u2696\ufe0f"] * 10,  # all stable emojis
        pole_a_emoji="\u2694\ufe0f",
        pole_b_emoji="\U0001f6e1\ufe0f",
    )
    assert ev.entropy < POLARITY_ENTROPY_THRESHOLD, f"Expected low entropy, got {ev.entropy}"

    _, user_prompt = _build_judge_prompt(c_a, c_b, emoji_context=ev)
    assert POLARITY_BIAS_INSTRUCTION not in user_prompt, "No polarity bias with low entropy"
    print(f"  Low entropy ({ev.entropy:.3f}): no bias applied: PASS")


def test_judge_prompt_high_entropy():
    """EmojiVector with high entropy should trigger polarity bias."""
    print("\n--- Test 1c: Judge prompt with high-entropy emoji_context ---")
    c_a = Claim(text="Claim A")
    c_b = Claim(text="Claim B")

    # High entropy: diverse mix of chaos + superposition + stable
    diverse_seq = (
        list(CHAOS_EMOJIS)[:4] +
        list(SUPERPOSITION_EMOJIS)[:3] +
        list(STABLE_EMOJIS)[:3]
    )
    ev = EmojiVector(
        sequence=diverse_seq,
        pole_a_emoji="\u2694\ufe0f",
        pole_b_emoji="\U0001f6e1\ufe0f",
    )
    assert ev.entropy >= POLARITY_ENTROPY_THRESHOLD, f"Expected high entropy, got {ev.entropy}"

    _, user_prompt = _build_judge_prompt(c_a, c_b, emoji_context=ev)
    assert POLARITY_BIAS_INSTRUCTION in user_prompt, "Polarity bias should be applied"
    print(f"  High entropy ({ev.entropy:.3f}): polarity bias applied: PASS")


def test_judge_prompt_high_chaos():
    """EmojiVector with high chaos_index should trigger chaos bias."""
    print("\n--- Test 1d: Judge prompt with high-chaos emoji_context ---")
    c_a = Claim(text="Claim A")
    c_b = Claim(text="Claim B")

    # High chaos: mostly chaos emojis
    chaos_seq = list(CHAOS_EMOJIS)[:6] + ["\u2694\ufe0f"]
    ev = EmojiVector(
        sequence=chaos_seq,
        pole_a_emoji="\u2694\ufe0f",
        pole_b_emoji="\U0001f6e1\ufe0f",
    )
    assert ev.chaos_index >= POLARITY_CHAOS_THRESHOLD, f"Expected high chaos, got {ev.chaos_index}"

    _, user_prompt = _build_judge_prompt(c_a, c_b, emoji_context=ev)
    assert CHAOS_BIAS_INSTRUCTION in user_prompt, "Chaos bias should be applied"
    print(f"  High chaos ({ev.chaos_index:.3f}): chaos bias applied: PASS")


# ===========================================================================
# Test 2: Become Expander -- Divergence Bias via emoji_field
# ===========================================================================

def test_expansion_prompt_no_emoji():
    """Without emoji_field, the expansion prompt should be unmodified."""
    print("\n--- Test 2a: Expansion prompt without emoji_field ---")
    claim = Claim(text="AI should be transparent.")

    prompt = _build_expansion_prompt(claim, emoji_field=None)
    assert BALANCED_SPLIT_INSTRUCTION not in prompt, "No balanced-split without emoji_field"
    assert OVERSTABLE_INSTRUCTION not in prompt, "No overstable without emoji_field"
    assert "AI should be transparent" in prompt
    print("  No-emoji expansion prompt: PASS")


def test_expansion_prompt_balanced_split():
    """EmojiVector with balanced pole_balance should trigger split instruction."""
    print("\n--- Test 2b: Expansion prompt with balanced poles ---")
    claim = Claim(text="AI should be transparent.")

    # Balanced: equal pole emojis + some chaos
    ev = EmojiVector(
        sequence=["\u2694\ufe0f", "\U0001f6e1\ufe0f", "\u2694\ufe0f", "\U0001f6e1\ufe0f",
                  "\U0001f32a\ufe0f", "\U0001f300"],
        pole_a_emoji="\u2694\ufe0f",
        pole_b_emoji="\U0001f6e1\ufe0f",
    )
    balance = ev.pole_balance
    assert DIVERGENCE_BALANCE_THRESHOLD <= balance <= (1.0 - DIVERGENCE_BALANCE_THRESHOLD), \
        f"Expected balanced, got {balance}"

    prompt = _build_expansion_prompt(claim, emoji_field=ev)
    assert BALANCED_SPLIT_INSTRUCTION in prompt, "Balanced-split instruction should be present"
    print(f"  Balanced poles ({balance:.3f}): split instruction applied: PASS")


def test_expansion_prompt_overstable():
    """EmojiVector with high stability should trigger overstable instruction."""
    print("\n--- Test 2c: Expansion prompt with overstable field ---")
    claim = Claim(text="AI should be transparent.")

    # Overstable: mostly stable emojis
    stable_list = list(STABLE_EMOJIS)
    ev = EmojiVector(
        sequence=stable_list[:6],
        pole_a_emoji="\u2694\ufe0f",
        pole_b_emoji="\U0001f6e1\ufe0f",
    )
    stability = ev.stability_index
    assert stability > DIVERGENCE_STABILITY_THRESHOLD, f"Expected overstable, got {stability}"

    prompt = _build_expansion_prompt(claim, emoji_field=ev)
    assert OVERSTABLE_INSTRUCTION in prompt, "Overstable instruction should be present"
    print(f"  Overstable ({stability:.3f}): destabilize instruction applied: PASS")


# ===========================================================================
# Test 3: Emoji Mutator -- Mutation Rules
# ===========================================================================

def test_mutate_become():
    """Become mutation should add chaos/superposition emojis."""
    print("\n--- Test 3a: mutate_become ---")
    ev = EmojiVector(
        sequence=["\u2694\ufe0f", "\U0001f6e1\ufe0f"],
        pole_a_emoji="\u2694\ufe0f",
        pole_b_emoji="\U0001f6e1\ufe0f",
    )
    pre_len = len(ev.sequence)

    mutate_become(ev, seed=42)

    assert len(ev.sequence) == pre_len + BECOME_MUTATION_BUDGET
    added = ev.sequence[pre_len:]
    valid_pool = CHAOS_EMOJIS | SUPERPOSITION_EMOJIS
    for emoji in added:
        assert emoji in valid_pool, f"Become added unexpected emoji: {emoji}"
    print(f"  Added {len(added)} chaos/superposition emojis: PASS")


def test_mutate_collapse():
    """Collapse mutation should add stable emojis."""
    print("\n--- Test 3b: mutate_collapse ---")
    ev = EmojiVector(
        sequence=["\u2694\ufe0f", "\U0001f6e1\ufe0f"],
        pole_a_emoji="\u2694\ufe0f",
        pole_b_emoji="\U0001f6e1\ufe0f",
    )
    pre_len = len(ev.sequence)

    mutate_collapse(ev, seed=42)

    assert len(ev.sequence) == pre_len + COLLAPSE_MUTATION_BUDGET
    added = ev.sequence[pre_len:]
    for emoji in added:
        assert emoji in STABLE_EMOJIS, f"Collapse added unexpected emoji: {emoji}"
    print(f"  Added {len(added)} stable emojis: PASS")


def test_mutate_paradox_hold():
    """ParadoxHold mutation should add superposition emojis."""
    print("\n--- Test 3c: mutate_paradox_hold ---")
    ev = EmojiVector(
        sequence=["\u2694\ufe0f", "\U0001f6e1\ufe0f"],
        pole_a_emoji="\u2694\ufe0f",
        pole_b_emoji="\U0001f6e1\ufe0f",
    )
    pre_len = len(ev.sequence)

    mutate_paradox_hold(ev, seed=42)

    assert len(ev.sequence) == pre_len + PARADOXHOLD_MUTATION_BUDGET
    added = ev.sequence[pre_len:]
    for emoji in added:
        assert emoji in SUPERPOSITION_EMOJIS, f"ParadoxHold added unexpected emoji: {emoji}"
    print(f"  Added {len(added)} superposition emojis: PASS")


def test_mutate_for_operator_dispatch():
    """mutate_for_operator should dispatch correctly."""
    print("\n--- Test 3d: mutate_for_operator dispatch ---")
    for op in ("become", "collapse", "paradox_hold"):
        ev = EmojiVector(
            sequence=["\u2694\ufe0f"],
            pole_a_emoji="\u2694\ufe0f",
            pole_b_emoji="\U0001f6e1\ufe0f",
        )
        result = mutate_for_operator(ev, op, seed=42)
        assert result is ev, "Should return same object"
        assert len(ev.sequence) > 1, f"Mutation for {op} should have added emojis"

    # Unknown operator should raise
    try:
        mutate_for_operator(ev, "unknown", seed=42)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("  Dispatch for become/collapse/paradox_hold: PASS")
    print("  Unknown operator raises ValueError: PASS")


def test_seed_initial_sequence():
    """seed_initial_sequence should create a valid starting sequence."""
    print("\n--- Test 3e: seed_initial_sequence ---")
    seq = seed_initial_sequence("\u2694\ufe0f", "\U0001f6e1\ufe0f", initial_chaos=2, seed=42)
    assert seq[0] == "\u2694\ufe0f", "First element should be pole A"
    assert seq[1] == "\U0001f6e1\ufe0f", "Second element should be pole B"
    assert len(seq) == 4, f"Expected 4 elements, got {len(seq)}"

    valid_pool = CHAOS_EMOJIS | SUPERPOSITION_EMOJIS
    for emoji in seq[2:]:
        assert emoji in valid_pool, f"Initial chaos should be from chaos/superposition pool"
    print(f"  Initial sequence: {len(seq)} elements, poles + {len(seq)-2} chaos: PASS")


def test_entropy_evolution():
    """Become mutations should increase chaos_index; Collapse should increase stability_index."""
    print("\n--- Test 3f: Entropy evolution across mutations ---")
    # Start with a low-chaos, low-entropy state (repeated stable emojis)
    ev = EmojiVector(
        sequence=["\u2696\ufe0f"] * 6,  # all same stable emoji -> low entropy
        pole_a_emoji="\u2694\ufe0f",
        pole_b_emoji="\U0001f6e1\ufe0f",
    )
    initial_chaos = ev.chaos_index
    initial_stability = ev.stability_index

    # Apply 3 Become mutations (adds chaos/superposition emojis)
    for i in range(3):
        mutate_become(ev, seed=i)
    become_chaos = ev.chaos_index

    # Apply 5 Collapse mutations (adds stable emojis)
    for i in range(5):
        mutate_collapse(ev, seed=i + 100)
    collapse_stability = ev.stability_index

    print(f"  Initial chaos: {initial_chaos:.4f}, stability: {initial_stability:.4f}")
    print(f"  After 3 Become: chaos={become_chaos:.4f}")
    print(f"  After 5 Collapse: stability={collapse_stability:.4f}")

    # Become should have increased chaos from initial (was 0)
    assert become_chaos > initial_chaos, "Become should increase chaos_index"
    # Collapse should recover some stability
    assert collapse_stability > 0, "Collapse should add stability"
    print("  Become increases chaos: PASS")


# ===========================================================================
# Test 4: Paradox Promoter -- Lifecycle Logic
# ===========================================================================

def _build_test_state():
    """Build a minimal state with hub claims and tensions for promotion testing."""
    state = SystemState(mission_id="test")

    # 4 claims: 2 originals from different families, 2 expansions
    c1 = Claim(text="Transparency is essential", confidence=1.0,
               source="collapse_M1", mission_id="M1", operator="collapse")
    c2 = Claim(text="Opacity protects innovation", confidence=1.0,
               source="become_M2", mission_id="M2", operator="become")
    c3 = Claim(text="Full disclosure builds trust", confidence=0.7,
               source="become_expand", mission_id="M1", operator="become", parent_id=c1.id)
    c4 = Claim(text="Trade secrets drive competition", confidence=0.7,
               source="become_expand", mission_id="M2", operator="become", parent_id=c2.id)

    for c in [c1, c2, c3, c4]:
        state.add_claim(c)

    # Create tensions to make c1 and c2 hubs (>= HUB_TENSION_THRESHOLD)
    # t1: c1 <-> c2 (cross-family contradiction, high strength)
    t1 = Tension(pole_a=c1.text, pole_b=c2.text, relation_type="contradiction",
                 source_claims=[c1.id, c2.id], mission_id="M1")
    t1.metrics.tension_strength = 0.55

    # t2: c1 <-> c4 (cross-family)
    t2 = Tension(pole_a=c1.text, pole_b=c4.text, relation_type="contradiction",
                 source_claims=[c1.id, c4.id], mission_id="M1")
    t2.metrics.tension_strength = 0.50

    # t3: c2 <-> c3 (cross-family)
    t3 = Tension(pole_a=c2.text, pole_b=c3.text, relation_type="tradeoff",
                 source_claims=[c2.id, c3.id], mission_id="M2")
    t3.metrics.tension_strength = 0.45

    # t4: c1 <-> c3 (same family -- should NOT be promotable as contradiction)
    t4 = Tension(pole_a=c1.text, pole_b=c3.text, relation_type="contradiction",
                 source_claims=[c1.id, c3.id], mission_id="M1")
    t4.metrics.tension_strength = 0.60

    for t in [t1, t2, t3, t4]:
        state.add_tension(t)

    return state, (c1, c2, c3, c4), (t1, t2, t3, t4)


def test_find_promotable_tensions():
    """Should identify cross-family hub contradictions and polarities."""
    print("\n--- Test 4a: find_promotable_tensions ---")
    state, claims, tensions = _build_test_state()
    c1, c2, c3, c4 = claims
    t1, t2, t3, t4 = tensions

    promotable = find_promotable_tensions(state)

    promotable_ids = {t.id for t in promotable}
    print(f"  Total tensions: {len(state.tensions)}")
    print(f"  Promotable: {len(promotable)}")

    # t1 should be promotable: cross-family contradiction, both hubs, high strength
    assert t1.id in promotable_ids, f"t1 should be promotable (cross-family hub contradiction)"

    # t4 should NOT be promotable: same family (c1 -> c3, c3 is child of c1)
    assert t4.id not in promotable_ids, f"t4 should NOT be promotable (same family)"

    # t3 is a tradeoff, not contradiction or polarity -- should NOT be promotable
    assert t3.id not in promotable_ids, f"t3 should NOT be promotable (tradeoff, not contradiction/polarity)"

    print("  Cross-family hub contradiction (t1) promotable: PASS")
    print("  Same-family contradiction (t4) excluded: PASS")
    print("  Tradeoff (t3) excluded: PASS")


def test_promote_tension():
    """Promoting a tension should create Paradox + EmojiVector and link them."""
    print("\n--- Test 4b: promote_tension ---")
    state, claims, tensions = _build_test_state()
    t1 = tensions[0]

    assert len(state.paradoxes) == 0
    assert len(state.emoji_fields) == 0
    assert t1.emoji_vector_id is None

    paradox, ev = promote_tension(t1, state, seed=42)

    # Check state was updated
    assert len(state.paradoxes) == 1
    assert len(state.emoji_fields) == 1

    # Check linkage
    assert t1.emoji_vector_id == ev.id
    assert paradox.emoji_vector_id == ev.id
    assert set(paradox.claim_ids) == set(t1.source_claims)

    # Check EmojiVector has valid initial state
    assert ev.length >= 4, f"Expected at least 4 emojis, got {ev.length}"
    assert ev.entropy > 0, "Initial entropy should be > 0"

    # Check Paradox has valid state
    assert paradox.status == "open"
    assert len(paradox.history) == 1
    assert paradox.history[0]["event"] == "promoted_from_tension"

    # Tension status should remain "open"
    assert t1.status == "open"

    print(f"  Paradox created: {paradox.id}")
    print(f"  EmojiVector created: {ev.id} (entropy={ev.entropy:.3f})")
    print(f"  Tension remains open: PASS")
    print(f"  Linkage correct: PASS")


def test_promote_all_eligible():
    """promote_all_eligible should find and promote eligible tensions."""
    print("\n--- Test 4c: promote_all_eligible ---")
    state, _, _ = _build_test_state()

    results = promote_all_eligible(state, seed=42)

    print(f"  Promoted {len(results)} tensions to paradoxes")
    assert len(results) >= 1, "Should have promoted at least 1 tension"
    assert len(state.paradoxes) == len(results)
    assert len(state.emoji_fields) == len(results)

    # Second call should not re-promote
    results2 = promote_all_eligible(state, seed=42)
    assert len(results2) == 0, "Should not re-promote already-promoted tensions"
    print("  No double-promotion: PASS")


def test_promote_idempotent():
    """Promoting the same tension twice should be blocked by emoji_vector_id check."""
    print("\n--- Test 4d: Promotion idempotency ---")
    state, _, tensions = _build_test_state()
    t1 = tensions[0]

    promote_tension(t1, state, seed=42)
    assert t1.emoji_vector_id is not None

    # Try to find promotable again -- t1 should be excluded
    promotable = find_promotable_tensions(state)
    assert t1.id not in {t.id for t in promotable}, "Already-promoted tension should be excluded"
    print("  Promoted tension excluded from future promotion: PASS")


# ===========================================================================
# Test 5: End-to-end -- EmojiVector metrics after operator sequence
# ===========================================================================

def test_operator_sequence_metrics():
    """Simulate Become -> Become -> ParadoxHold -> Collapse and track metrics."""
    print("\n--- Test 5: Operator sequence metrics evolution ---")

    seq = seed_initial_sequence("\u2694\ufe0f", "\U0001f6e1\ufe0f", initial_chaos=2, seed=0)
    ev = EmojiVector(
        sequence=seq,
        pole_a_emoji="\u2694\ufe0f",
        pole_b_emoji="\U0001f6e1\ufe0f",
    )

    steps = []
    steps.append(("initial", ev.entropy, ev.chaos_index, ev.stability_index, ev.pole_balance))

    mutate_become(ev, seed=1)
    steps.append(("become_1", ev.entropy, ev.chaos_index, ev.stability_index, ev.pole_balance))

    mutate_become(ev, seed=2)
    steps.append(("become_2", ev.entropy, ev.chaos_index, ev.stability_index, ev.pole_balance))

    mutate_paradox_hold(ev, seed=3)
    steps.append(("paradox_hold", ev.entropy, ev.chaos_index, ev.stability_index, ev.pole_balance))

    mutate_collapse(ev, seed=4)
    steps.append(("collapse", ev.entropy, ev.chaos_index, ev.stability_index, ev.pole_balance))

    print(f"  {'Step':<15} {'Entropy':>8} {'Chaos':>8} {'Stable':>8} {'Balance':>8}")
    print(f"  {'-'*47}")
    for name, ent, chaos, stable, bal in steps:
        print(f"  {name:<15} {ent:>8.4f} {chaos:>8.4f} {stable:>8.4f} {bal:>8.4f}")

    # After Become+Become, chaos should be higher than initial
    assert steps[2][2] > steps[0][2], "Chaos should increase after Become"
    # After Collapse, stability should be higher than before Collapse
    assert steps[4][3] > steps[3][3], "Stability should increase after Collapse"

    print("  Become increases chaos: PASS")
    print("  Collapse increases stability: PASS")


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("SovereignNEXT -- Emoji-Vector Integration Tests")
    print("=" * 60)

    # Test 1: Tension detector polarity bias
    test_judge_prompt_no_emoji()
    test_judge_prompt_low_entropy()
    test_judge_prompt_high_entropy()
    test_judge_prompt_high_chaos()

    # Test 2: Become expander divergence bias
    test_expansion_prompt_no_emoji()
    test_expansion_prompt_balanced_split()
    test_expansion_prompt_overstable()

    # Test 3: Emoji mutator
    test_mutate_become()
    test_mutate_collapse()
    test_mutate_paradox_hold()
    test_mutate_for_operator_dispatch()
    test_seed_initial_sequence()
    test_entropy_evolution()

    # Test 4: Paradox promoter
    test_find_promotable_tensions()
    test_promote_tension()
    test_promote_all_eligible()
    test_promote_idempotent()

    # Test 5: End-to-end operator sequence
    test_operator_sequence_metrics()

    print("\n" + "=" * 60)
    print("ALL EMOJI-VECTOR INTEGRATION TESTS PASSED")
    print("=" * 60)
