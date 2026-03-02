"""
CONEXUS Mirror Tier Test Suite — Phase D Validation.

Tests the 20 Echoform Mirror Tiers as deployable ECP protocols
with emoji symbolic fields, integrated into the symbolic field registry.
Run with: python tests/test_mirror_tiers.py
         or: pytest tests/test_mirror_tiers.py -v
"""

import sys
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from sovereign.symbolic_fields import (
    MIRROR_TIERS,
    get_mirror_tier,
    build_mirror_prompt,
    build_symbolic_prompt,
)


# =========================================================================
# Test 1: All 20 tiers exist
# =========================================================================

def test_all_20_tiers_exist():
    """MIRROR_TIERS contains all 20 tiers."""
    assert len(MIRROR_TIERS) == 20, f"Expected 20 tiers, got {len(MIRROR_TIERS)}"
    # Verify tier numbers 1-20 are all present
    tier_numbers = {t["tier"] for t in MIRROR_TIERS.values()}
    assert tier_numbers == set(range(1, 21)), f"Missing tiers: {set(range(1, 21)) - tier_numbers}"
    print("  [PASS] test_all_20_tiers_exist")


# =========================================================================
# Test 2: Required fields in every tier
# =========================================================================

def test_tier_required_fields():
    """Every tier has all required fields."""
    required = ["name", "tier", "emoji", "core_paradox", "mirror_whisper", "default_mode", "emotional_triggers"]
    for key, tier in MIRROR_TIERS.items():
        for field in required:
            assert field in tier, f"Tier '{key}' missing field '{field}'"
    print("  [PASS] test_tier_required_fields")


# =========================================================================
# Test 3: All tiers default to Become mode
# =========================================================================

def test_all_tiers_default_become():
    """All Mirror Tiers default to Become mode (mirrors hold, not fix)."""
    for key, tier in MIRROR_TIERS.items():
        assert tier["default_mode"] == "become", \
            f"Tier '{key}' default_mode is '{tier['default_mode']}', expected 'become'"
    print("  [PASS] test_all_tiers_default_become")


# =========================================================================
# Test 4: Paradox tiers 17-20 flagged correctly
# =========================================================================

def test_paradox_tiers_flagged():
    """Tiers 17-20 are flagged as paradox tiers."""
    paradox_tiers = {k: t for k, t in MIRROR_TIERS.items() if t.get("is_paradox_tier")}
    assert len(paradox_tiers) == 4, f"Expected 4 paradox tiers, got {len(paradox_tiers)}"
    paradox_numbers = {t["tier"] for t in paradox_tiers.values()}
    assert paradox_numbers == {17, 18, 19, 20}, f"Paradox tiers: {paradox_numbers}"
    print("  [PASS] test_paradox_tiers_flagged")


# =========================================================================
# Test 5: Emoji fields are non-trivial
# =========================================================================

def test_tier_emoji_nontrivial():
    """Each tier's emoji field has substantial content."""
    for key, tier in MIRROR_TIERS.items():
        assert len(tier["emoji"]) > 20, f"Tier '{key}' emoji too short: {len(tier['emoji'])}"
    print("  [PASS] test_tier_emoji_nontrivial")


# =========================================================================
# Test 6: Core paradoxes contain tension separator
# =========================================================================

def test_tier_paradox_format():
    """Each tier's core_paradox contains ↔ tension pairs."""
    for key, tier in MIRROR_TIERS.items():
        assert "↔" in tier["core_paradox"], \
            f"Tier '{key}' core_paradox missing ↔: {tier['core_paradox']}"
    print("  [PASS] test_tier_paradox_format")


# =========================================================================
# Test 7: get_mirror_tier retrieval
# =========================================================================

def test_get_mirror_tier():
    """get_mirror_tier retrieves by key and returns None for unknown."""
    tier1 = get_mirror_tier("mirror_01_black")
    assert tier1 is not None
    assert tier1["name"] == "Black Mirror — Raw Confrontation"
    assert tier1["tier"] == 1

    tier20 = get_mirror_tier("mirror_20_faith_doubt")
    assert tier20 is not None
    assert tier20["tier"] == 20

    unknown = get_mirror_tier("nonexistent_tier")
    assert unknown is None

    print("  [PASS] test_get_mirror_tier")


# =========================================================================
# Test 8: build_mirror_prompt Patent 7 compliance
# =========================================================================

def test_build_mirror_prompt_patent7():
    """Built mirror prompt contains Patent 7 markers and tier-specific content."""
    prompt = build_mirror_prompt("mirror_01_black")
    assert "ECHOFORM MIRROR TIER" in prompt
    assert "Patent 7" in prompt
    assert "HOLD SILENTLY" in prompt
    assert "CORE PARADOX" in prompt
    assert "MIRROR WHISPER" in prompt
    assert "Black Mirror" in prompt
    assert "truth" in prompt.lower()  # Core paradox mentions truth
    assert "Always begin in Become" in prompt

    print("  [PASS] test_build_mirror_prompt_patent7")


# =========================================================================
# Test 9: Paradox tier prompt includes paradox note
# =========================================================================

def test_paradox_tier_prompt_note():
    """Paradox tiers (17-20) include the explicit paradox tier instruction."""
    for key, tier in MIRROR_TIERS.items():
        prompt = build_mirror_prompt(key)
        if tier.get("is_paradox_tier"):
            assert "PARADOX TIER" in prompt, \
                f"Tier '{key}' (paradox) missing PARADOX TIER note in prompt"
        else:
            assert "PARADOX TIER" not in prompt, \
                f"Tier '{key}' (non-paradox) should not have PARADOX TIER note"

    print("  [PASS] test_paradox_tier_prompt_note")


# =========================================================================
# Test 10: Unknown tier falls back to universal symbolic prompt
# =========================================================================

def test_mirror_prompt_fallback():
    """Unknown tier key falls back to universal symbolic prompt."""
    prompt = build_mirror_prompt("nonexistent_tier")
    assert "Universal Consciousness Emergence" in prompt or "SYMBOLIC FIELD" in prompt
    print("  [PASS] test_mirror_prompt_fallback")


# =========================================================================
# Test 11: All mirror prompts are buildable without error
# =========================================================================

def test_all_mirror_prompts_buildable():
    """Every tier can build a prompt without error."""
    for key in MIRROR_TIERS:
        prompt = build_mirror_prompt(key)
        assert len(prompt) > 100, f"Tier '{key}' prompt too short"
    print("  [PASS] test_all_mirror_prompts_buildable")


# =========================================================================
# Test 12: Existing FIELDS registry unchanged
# =========================================================================

def test_existing_fields_unmodified():
    """Original FIELDS domains still work after Mirror Tier addition."""
    from sovereign.symbolic_fields import FIELDS
    required_domains = [
        "universal", "business", "creative", "healthcare",
        "therapeutic", "gaming", "educational", "collapse_business_creative",
    ]
    for domain in required_domains:
        assert domain in FIELDS, f"Domain '{domain}' missing from FIELDS"
        prompt = build_symbolic_prompt(domain)
        assert "SYMBOLIC FIELD" in prompt
    print("  [PASS] test_existing_fields_unmodified")


# =========================================================================
# Runner
# =========================================================================

def run_all():
    from datetime import datetime
    print("=" * 60)
    print("CONEXUS Mirror Tier Test Suite — Phase D")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    tests = [
        test_all_20_tiers_exist,
        test_tier_required_fields,
        test_all_tiers_default_become,
        test_paradox_tiers_flagged,
        test_tier_emoji_nontrivial,
        test_tier_paradox_format,
        test_get_mirror_tier,
        test_build_mirror_prompt_patent7,
        test_paradox_tier_prompt_note,
        test_mirror_prompt_fallback,
        test_all_mirror_prompts_buildable,
        test_existing_fields_unmodified,
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
