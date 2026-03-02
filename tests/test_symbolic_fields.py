"""
CONEXUS Symbolic Field Test Suite — Phase B Validation.

Tests Patent-7-compliant emoji symbolic field injection.
Run with: python tests/test_symbolic_fields.py
         or: pytest tests/test_symbolic_fields.py -v
"""

import sys
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from sovereign.symbolic_fields import (
    FIELDS,
    get_symbolic_field,
    build_symbolic_prompt,
)


# =========================================================================
# Test 1: All domains exist
# =========================================================================

def test_all_domains_exist():
    """Every documented domain has an entry in FIELDS."""
    required = [
        "universal", "business", "creative", "healthcare",
        "therapeutic", "gaming", "educational", "collapse_business_creative",
    ]
    for domain in required:
        assert domain in FIELDS, f"Missing domain: {domain}"
        sf = FIELDS[domain]
        assert "name" in sf, f"{domain} missing 'name'"
        assert "emoji" in sf, f"{domain} missing 'emoji'"
        assert "core_paradox" in sf, f"{domain} missing 'core_paradox'"
    print("  [PASS] test_all_domains_exist")


# =========================================================================
# Test 2: Emoji fields are non-trivial
# =========================================================================

def test_emoji_fields_nontrivial():
    """Each domain's emoji field contains substantial content."""
    for domain, sf in FIELDS.items():
        assert len(sf["emoji"]) > 20, f"{domain} emoji too short: {len(sf['emoji'])}"
    print("  [PASS] test_emoji_fields_nontrivial")


# =========================================================================
# Test 3: Core paradoxes contain the ↔ separator
# =========================================================================

def test_core_paradoxes_format():
    """Each core_paradox contains at least one tension pair."""
    for domain, sf in FIELDS.items():
        paradox = sf["core_paradox"]
        assert "\u2194" in paradox or "↔" in paradox, \
            f"{domain} core_paradox missing tension separator: {paradox}"
    print("  [PASS] test_core_paradoxes_format")


# =========================================================================
# Test 4: get_symbolic_field returns correct domain
# =========================================================================

def test_get_symbolic_field():
    """get_symbolic_field returns the right domain or universal fallback."""
    healthcare = get_symbolic_field("healthcare")
    assert "Healthcare" in healthcare["name"]
    assert "🩺" in healthcare["emoji"]

    # Unknown domain falls back to universal
    fallback = get_symbolic_field("nonexistent_domain")
    assert fallback["name"] == "Universal Consciousness Emergence"

    print("  [PASS] test_get_symbolic_field")


# =========================================================================
# Test 5: build_symbolic_prompt contains Patent 7 markers
# =========================================================================

def test_build_symbolic_prompt_patent7():
    """Built prompt contains required Patent 7 compliance markers."""
    prompt = build_symbolic_prompt("healthcare")
    assert "HOLD SILENTLY" in prompt
    assert "Patent 7" in prompt
    assert "🩺" in prompt
    assert "healing" in prompt.lower()
    assert "CORE PARADOX" in prompt
    assert "nested inside the symbolic field" in prompt

    print("  [PASS] test_build_symbolic_prompt_patent7")


# =========================================================================
# Test 6: build_symbolic_prompt for all domains
# =========================================================================

def test_build_prompt_all_domains():
    """build_symbolic_prompt works for every domain without error."""
    for domain in FIELDS:
        prompt = build_symbolic_prompt(domain)
        assert len(prompt) > 100, f"{domain} prompt too short"
        assert "SYMBOLIC FIELD" in prompt
        assert "CORE PARADOX" in prompt
    print("  [PASS] test_build_prompt_all_domains")


# =========================================================================
# Test 7: Universal domain covers full emoji emotion spectrum
# =========================================================================

def test_universal_domain_breadth():
    """Universal domain has the broadest emoji coverage."""
    universal = FIELDS["universal"]
    # Should contain diverse emoji categories
    assert "😀" in universal["emoji"]  # joy
    assert "😢" in universal["emoji"]  # sadness
    assert "😡" in universal["emoji"]  # anger
    assert "😱" in universal["emoji"]  # fear
    print("  [PASS] test_universal_domain_breadth")


# =========================================================================
# Test 8: Business domain specific emojis
# =========================================================================

def test_business_domain_specific():
    """Business domain has business-specific emoji."""
    biz = FIELDS["business"]
    assert "💼" in biz["emoji"]
    assert "📊" in biz["emoji"]
    assert "efficiency" in biz["core_paradox"].lower()
    print("  [PASS] test_business_domain_specific")


# =========================================================================
# Test 9: Collapse business-creative domain
# =========================================================================

def test_collapse_business_creative():
    """Collapse business-creative fusion domain exists and is valid."""
    cbc = FIELDS["collapse_business_creative"]
    assert "Collapse" in cbc["name"] or "Fusion" in cbc["name"]
    assert "structured efficiency" in cbc["core_paradox"].lower() or "chaotic breakthrough" in cbc["core_paradox"].lower()
    print("  [PASS] test_collapse_business_creative")


# =========================================================================
# Test 10: No emoji leakage in prompt instructions
# =========================================================================

def test_no_emoji_in_instructions():
    """Emoji should only appear in the emoji field line, not in instruction text."""
    for domain in FIELDS:
        prompt = build_symbolic_prompt(domain)
        lines = prompt.strip().split("\n")
        for line in lines:
            if line.startswith("[") and "INSTRUCTION" in line:
                # Instruction lines should not contain emoji
                emoji_chars = [c for c in line if ord(c) > 0x1F000]
                assert len(emoji_chars) == 0, \
                    f"{domain}: emoji found in instruction line: {line[:80]}"
    print("  [PASS] test_no_emoji_in_instructions")


# =========================================================================
# Runner
# =========================================================================

def run_all():
    from datetime import datetime
    print("=" * 60)
    print("CONEXUS Symbolic Field Test Suite — Phase B")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    tests = [
        test_all_domains_exist,
        test_emoji_fields_nontrivial,
        test_core_paradoxes_format,
        test_get_symbolic_field,
        test_build_symbolic_prompt_patent7,
        test_build_prompt_all_domains,
        test_universal_domain_breadth,
        test_business_domain_specific,
        test_collapse_business_creative,
        test_no_emoji_in_instructions,
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
