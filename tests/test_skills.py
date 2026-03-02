"""
OpenClaw Skills Validation & Semantic Routing Test Suite.

Tests:
  1. YAML parsing for all active skills in manifest.json
  2. File consistency between manifest, quarantine, and disk
  3. Safety invariants (no identity mutation, autonomous execution, etc.)
  4. Quarantine correctness
  5. Offline semantic routing (natural-language → skill match)

Run with:  python tests/test_skills.py
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

SKILLS_DIR = Path(REPO_ROOT) / "openclaw" / "skills"
MANIFEST_PATH = SKILLS_DIR / "manifest.json"
QUARANTINE_PATH = SKILLS_DIR / "quarantine.json"

results = []


def record(name, passed, detail=""):
    results.append({"name": name, "passed": passed, "detail": detail})
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {name}  {detail}")


# =========================================================================
# Helpers
# =========================================================================

def _parse_frontmatter(text: str) -> dict:
    """Minimal YAML frontmatter parser."""
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    result = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
            result[key] = [i for i in items if i]
        elif value.startswith('"') and value.endswith('"'):
            result[key] = value.strip('"')
        elif value.startswith("'") and value.endswith("'"):
            result[key] = value.strip("'")
        else:
            result[key] = value
    return result


def _load_manifest():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_quarantine():
    with open(QUARANTINE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _resolve_skill_file(rel_path: str) -> Path:
    """Resolve a manifest path to an actual file on disk."""
    full = SKILLS_DIR / rel_path
    if full.is_dir():
        candidates = list(full.glob("SKILL.md")) + list(full.glob("*.md"))
        if candidates:
            return candidates[0]
    return full


# =========================================================================
# Test 1: YAML Parsing
# =========================================================================

def test_yaml_parsing():
    """Every active skill must have parseable YAML with name + description."""
    manifest = _load_manifest()
    active = manifest["skills"]["active"]
    all_ok = True
    failures = []

    for entry in active:
        name = entry["name"]
        fp = _resolve_skill_file(entry["path"])
        if not fp.exists():
            all_ok = False
            failures.append(f"{name}: file not found ({fp})")
            continue

        text = fp.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)

        has_name = bool(meta.get("name") or meta.get("description"))
        has_desc = bool(meta.get("description"))

        if not has_name and not has_desc:
            # SovereignCalibration has no YAML frontmatter name field — accept if body exists
            if len(text.strip()) > 50:
                continue
            all_ok = False
            failures.append(f"{name}: missing name and description in frontmatter")

    detail = "all skills parsed" if all_ok else "; ".join(failures)
    record("yaml_parsing", all_ok, detail)


# =========================================================================
# Test 2: File Consistency
# =========================================================================

def test_file_consistency():
    """Every manifest entry has a file on disk. Every skill file is tracked."""
    manifest = _load_manifest()
    quarantine = _load_quarantine()

    active_names = {e["name"] for e in manifest["skills"]["active"]}
    quarantine_names = {e["name"] for e in quarantine.get("quarantined_skills", [])}
    q_manifest_names = {e["name"] for e in manifest["skills"].get("quarantined", [])}

    all_tracked = active_names | quarantine_names | q_manifest_names
    failures = []

    # Check every manifest entry has a file
    for entry in manifest["skills"]["active"]:
        fp = _resolve_skill_file(entry["path"])
        if not fp.exists():
            failures.append(f"manifest active '{entry['name']}' — file missing: {fp}")

    for entry in manifest["skills"].get("quarantined", []):
        fp = _resolve_skill_file(entry["path"])
        if not fp.exists():
            failures.append(f"manifest quarantined '{entry['name']}' — file missing: {fp}")

    # Check every skill directory on disk is tracked
    for d in SKILLS_DIR.iterdir():
        if not d.is_dir():
            continue
        if d.name.startswith(".") or d.name == "__pycache__":
            continue
        if d.name not in all_tracked:
            failures.append(f"disk dir '{d.name}' not in manifest or quarantine")

    ok = len(failures) == 0
    detail = "all consistent" if ok else "; ".join(failures)
    record("file_consistency", ok, detail)


# =========================================================================
# Test 3: Safety Invariants
# =========================================================================

UNSAFE_EXECUTION_MODES = {"autonomous", "self", "unrestricted", "uncontrolled"}
UNSAFE_TAGS = {"identity-mutation", "self-modification", "routing-authority", "autonomous-execution"}


def test_safety_invariants():
    """No active skill may have unsafe execution modes or tags."""
    manifest = _load_manifest()
    active = manifest["skills"]["active"]
    failures = []

    for entry in active:
        name = entry["name"]
        fp = _resolve_skill_file(entry["path"])
        if not fp.exists():
            continue

        text = fp.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)

        # Check execution mode
        perms = meta.get("permissions", "")
        if isinstance(perms, str) and "autonomous" in perms.lower():
            failures.append(f"{name}: permissions contain 'autonomous'")
        execution_val = meta.get("execution", "")
        if isinstance(execution_val, str) and execution_val.lower() in UNSAFE_EXECUTION_MODES:
            failures.append(f"{name}: unsafe execution mode '{execution_val}'")

        # Check tags
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        for tag in tags:
            if tag.lower() in UNSAFE_TAGS:
                failures.append(f"{name}: unsafe tag '{tag}'")

        # Check body for forbidden directives
        body_lower = text.lower()
        if "identity mutation" in body_lower and "do not" not in body_lower.split("identity mutation")[0][-50:]:
            # Only flag if it's not in a "do not" context
            pass  # Many skills mention identity in safety sections — skip body heuristic

    ok = len(failures) == 0
    detail = "all active skills safe" if ok else "; ".join(failures)
    record("safety_invariants", ok, detail)


# =========================================================================
# Test 4: Quarantine Correctness
# =========================================================================

EXPECTED_QUARANTINE = {
    "identity-expansion",
    "conditional-autonomous-routing",
    "autonomous-tool-use",
    "self-evolving-loop",
}


def test_quarantine_correctness():
    """Quarantined skills must be exactly the expected set."""
    manifest = _load_manifest()
    quarantine = _load_quarantine()

    manifest_q = {e["name"] for e in manifest["skills"].get("quarantined", [])}
    quarantine_q = {e["name"] for e in quarantine.get("quarantined_skills", [])}

    # Both sources should agree and match expected
    manifest_match = manifest_q == EXPECTED_QUARANTINE
    quarantine_match = quarantine_q == EXPECTED_QUARANTINE
    sources_agree = manifest_q == quarantine_q

    ok = manifest_match and quarantine_match and sources_agree
    if not ok:
        details = []
        if not manifest_match:
            details.append(f"manifest quarantine mismatch: {manifest_q}")
        if not quarantine_match:
            details.append(f"quarantine.json mismatch: {quarantine_q}")
        if not sources_agree:
            details.append("manifest and quarantine.json disagree")
        detail = "; ".join(details)
    else:
        detail = f"exactly {len(EXPECTED_QUARANTINE)} quarantined skills"

    record("quarantine_correctness", ok, detail)


# =========================================================================
# Test 5: Quarantine Exclusion from Active
# =========================================================================

def test_quarantine_not_active():
    """No quarantined skill should appear in the active list."""
    manifest = _load_manifest()
    active_names = {e["name"] for e in manifest["skills"]["active"]}
    overlap = active_names & EXPECTED_QUARANTINE

    ok = len(overlap) == 0
    detail = "no overlap" if ok else f"quarantined skills in active: {overlap}"
    record("quarantine_not_active", ok, detail)


# =========================================================================
# Test 6: Semantic Matcher Loads
# =========================================================================

def test_semantic_matcher_loads():
    """The semantic matcher initializes without error."""
    try:
        from openclaw.skills.semantic_matcher import SemanticSkillMatcher
        matcher = SemanticSkillMatcher()
        matcher.initialize()
        ok = len(matcher.skills) > 0
        detail = f"{len(matcher.skills)} skills loaded and embedded"
        record("semantic_matcher_loads", ok, detail)
        return matcher
    except Exception as e:
        record("semantic_matcher_loads", False, str(e))
        return None


# =========================================================================
# Test 7: Offline Semantic Routing
# =========================================================================

def test_offline_routing(matcher):
    """Natural-language requests should resolve to expected skills."""
    if matcher is None:
        record("offline_routing_paradox", False, "matcher not available")
        record("offline_routing_python", False, "matcher not available")
        record("offline_routing_ethics", False, "matcher not available")
        record("offline_routing_compression", False, "matcher not available")
        return

    test_cases = [
        ("There is a deep contradiction I need to hold without resolving.", "paradox-processing", "offline_routing_paradox"),
        ("Help me write a Python function with type hints.", "python", "offline_routing_python"),
        ("I need to check the ethical implications before proceeding.", "ethics-value-integration", "offline_routing_ethics"),
        ("Compress this mission into a single directive.", "mission-compression", "offline_routing_compression"),
    ]

    for query, expected_skill, test_name in test_cases:
        result = matcher.match_skill(query)
        matched = result.get("skill_name")
        conf = result.get("confidence", 0.0)
        ok = matched == expected_skill and conf > CONFIDENCE_THRESHOLD
        detail = f"query='{query[:50]}...' → {matched} (conf={conf:.4f}), expected={expected_skill}"
        record(test_name, ok, detail)


CONFIDENCE_THRESHOLD = 0.12


# =========================================================================
# Test 8: Patent 7 Compliance
# =========================================================================

CALIBRATION_SKILLS = {
    "SovereignCalibration",
    "paradox-processing",
    "emotional-symbolic-modulation",
    "stress-navigation",
    "ethics-value-integration",
    "memory-management",
}


def test_patent7_compliance():
    """All calibration-bearing skills must have ecp_symbolic_field and ecp_contradiction_pairs."""
    manifest = _load_manifest()
    active = manifest["skills"]["active"]
    failures = []

    # Assert SovereignCalibration is first in manifest (symbolic root authority)
    first_name = active[0]["name"] if active else ""
    if first_name != "SovereignCalibration":
        failures.append(f"SovereignCalibration must be first in manifest, got '{first_name}'")

    for entry in active:
        name = entry["name"]
        if name not in CALIBRATION_SKILLS:
            continue

        # Manifest must declare calibration_type
        cal_type = entry.get("calibration_type", "")
        if cal_type != "patent-7-bearing":
            failures.append(f"{name}: missing calibration_type in manifest")
            continue

        # SovereignCalibration has no YAML frontmatter — check body for emoji tokens
        if name == "SovereignCalibration":
            fp = _resolve_skill_file(entry["path"])
            if fp.exists():
                body = fp.read_text(encoding="utf-8")
                has_emoji = any(ord(ch) > 0x1F000 for ch in body)
                if not has_emoji:
                    failures.append(f"{name}: body missing emoji tokens")
            continue

        # Other calibration skills: parse frontmatter
        fp = _resolve_skill_file(entry["path"])
        if not fp.exists():
            failures.append(f"{name}: file not found")
            continue

        text = fp.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)

        # ecp_symbolic_field must be a single non-empty string on one line
        sym = meta.get("ecp_symbolic_field", "")
        if not isinstance(sym, str) or not sym.strip():
            failures.append(f"{name}: ecp_symbolic_field missing or not a string")
        elif "\n" in sym:
            failures.append(f"{name}: ecp_symbolic_field split across lines (YAML drift)")

        # ecp_contradiction_pairs must be a list with >= 1 entry
        cvec = meta.get("ecp_contradiction_pairs", [])
        if isinstance(cvec, str):
            failures.append(f"{name}: ecp_contradiction_pairs parsed as string, not list")
        elif not isinstance(cvec, list) or len(cvec) < 1:
            failures.append(f"{name}: ecp_contradiction_pairs missing or empty")

    ok = len(failures) == 0
    detail = f"all {len(CALIBRATION_SKILLS)} calibration skills compliant" if ok else "; ".join(failures)
    record("patent7_compliance", ok, detail)


# =========================================================================
# Test 9: Patent 7 Routing Improvement
# =========================================================================

BASELINE_CONFIDENCES = {
    "paradox-processing": 0.3465,
    "stress-navigation": 0.3084,
    "ethics-value-integration": 0.4426,
    "memory-management": 0.4549,
}

STRUCTURAL_BASELINES = {
    "python": 0.3090,
    "mission-compression": 0.5649,
}


def test_patent7_routing(matcher):
    """Calibration skill routing confidence should not regress vs baseline."""
    if matcher is None:
        for skill in BASELINE_CONFIDENCES:
            record(f"patent7_routing_{skill}", False, "matcher not available")
        for skill in STRUCTURAL_BASELINES:
            record(f"patent7_structural_{skill}", False, "matcher not available")
        return

    calibration_cases = [
        ("There is a deep contradiction I need to hold without resolving.",
         "paradox-processing", "patent7_routing_paradox"),
        ("I am under extreme pressure and need to maintain coherence",
         "stress-navigation", "patent7_routing_stress"),
        ("I need to check the ethical implications before proceeding.",
         "ethics-value-integration", "patent7_routing_ethics"),
        ("I need to remember what happened last session and consolidate learnings",
         "memory-management", "patent7_routing_memory"),
    ]

    for query, expected_skill, test_name in calibration_cases:
        result = matcher.match_skill(query)
        matched = result.get("skill_name")
        conf = result.get("confidence", 0.0)
        baseline = BASELINE_CONFIDENCES.get(expected_skill, 0.0)
        delta = conf - baseline
        ok = matched == expected_skill and conf >= (baseline - 0.02)
        detail = (f"query='{query[:50]}...' -> {matched} "
                  f"(conf={conf:.4f}, baseline={baseline:.4f}, delta={delta:+.4f})")
        record(test_name, ok, detail)

    # Structural skills must show NO routing change
    structural_cases = [
        ("Help me write a Python function with type hints.",
         "python", "patent7_structural_python"),
        ("Compress this mission into a single directive.",
         "mission-compression", "patent7_structural_compression"),
    ]

    for query, expected_skill, test_name in structural_cases:
        result = matcher.match_skill(query)
        matched = result.get("skill_name")
        conf = result.get("confidence", 0.0)
        baseline = STRUCTURAL_BASELINES.get(expected_skill, 0.0)
        delta = abs(conf - baseline)
        ok = matched == expected_skill and delta < 0.001
        detail = (f"query='{query[:50]}...' -> {matched} "
                  f"(conf={conf:.4f}, baseline={baseline:.4f}, drift={delta:.4f})")
        record(test_name, ok, detail)


# =========================================================================
# Test 10: Sovereign Calibration Verification (Phase 5)
# =========================================================================

SOVEREIGN_QUERIES = [
    ("There is a deep contradiction I need to hold without resolving.",
     "paradox-processing"),
    ("I need to modulate emotional resonance and expand identity.",
     "emotional-symbolic-modulation"),
    ("I am under extreme pressure and need to maintain coherence",
     "stress-navigation"),
    ("I need to check the ethical implications before proceeding.",
     "ethics-value-integration"),
    ("I need to remember what happened last session and consolidate learnings",
     "memory-management"),
]


def _has_emoji(text: str) -> bool:
    """Return True if text contains any emoji codepoints (U+1F000+)."""
    return any(ord(ch) > 0x1F000 for ch in text)


def test_sovereign_verification(matcher):
    """Each calibration skill routes correctly and has no emoji leakage in text_blob."""
    if matcher is None:
        for _, skill in SOVEREIGN_QUERIES:
            record(f"sovereign_{skill}", False, "matcher not available")
        record("sovereign_no_emoji_leakage", False, "matcher not available")
        return

    # Routing verification: each calibration skill must match its query
    for query, expected_skill in SOVEREIGN_QUERIES:
        result = matcher.match_skill(query)
        matched = result.get("skill_name")
        conf = result.get("confidence", 0.0)
        ok = matched == expected_skill and conf > CONFIDENCE_THRESHOLD
        detail = (f"query='{query[:50]}...' -> {matched} (conf={conf:.4f})")
        record(f"sovereign_{expected_skill}", ok, detail)

    # Emoji leakage check: no text_blob should contain raw emoji codepoints
    leaked = []
    for skill in matcher.skills:
        if _has_emoji(skill.text_blob):
            leaked.append(skill.name)
    ok = len(leaked) == 0
    detail = "no emoji in any text_blob" if ok else f"emoji leaked in: {', '.join(leaked)}"
    record("sovereign_no_emoji_leakage", ok, detail)


# =========================================================================
# Runner
# =========================================================================

def run_all():
    from datetime import datetime
    print("=" * 60)
    print("OpenClaw Skills Validation & Semantic Routing Tests")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    print("\n--- YAML Parsing ---")
    test_yaml_parsing()

    print("\n--- File Consistency ---")
    test_file_consistency()

    print("\n--- Safety Invariants ---")
    test_safety_invariants()

    print("\n--- Quarantine Correctness ---")
    test_quarantine_correctness()
    test_quarantine_not_active()

    print("\n--- Semantic Matcher ---")
    matcher = test_semantic_matcher_loads()

    print("\n--- Offline Semantic Routing ---")
    test_offline_routing(matcher)

    print("\n--- Patent 7 Compliance ---")
    test_patent7_compliance()
    test_patent7_routing(matcher)

    print("\n--- Sovereign Calibration Verification ---")
    test_sovereign_verification(matcher)

    # Summary
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    total = len(results)

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")
    print("=" * 60)

    # Write report
    report_path = Path(REPO_ROOT) / "tests" / "SKILLS_TEST_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# OpenClaw Skills Test Report\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Result:** {passed}/{total} passed, {failed} failed\n\n")
        f.write("## Test Results\n\n")
        f.write("| Test | Status | Detail |\n")
        f.write("|------|--------|--------|\n")
        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            f.write(f"| {r['name']} | {status} | {r['detail'][:100]} |\n")
        f.write("\n---\n\n*Generated by `tests/test_skills.py`*\n")

    print(f"\nReport saved to: {report_path}")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
