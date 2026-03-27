"""
CONEXUS Gemini Demo — Standalone Verification Script

Verifies the integrity of all demo bundle artifacts by checking SHA-256
hashes against the manifest. Produces verification_log.md and
verification_summary.md.

Usage:
    python _verify.py                    (run from verification/ directory)
    python verification/_verify.py       (run from bundle root)
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_bundle_root():
    """Locate the bundle root regardless of where the script is invoked."""
    script_dir = Path(__file__).resolve().parent
    # Script lives in verification/, bundle root is one level up
    bundle_root = script_dir.parent
    if (bundle_root / "run_artifacts").exists() and (bundle_root / "README_verify_demo.md").exists():
        return bundle_root
    # Fallback: maybe invoked from bundle root
    cwd = Path.cwd()
    if (cwd / "run_artifacts").exists():
        return cwd
    print("ERROR: Cannot locate demo bundle root. Run from the bundle directory.")
    sys.exit(1)


def sha256_file(path):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_bundle(bundle_root):
    """Verify all files in the bundle against the manifest."""
    manifest_path = bundle_root / "verification" / "manifest.json"

    if not manifest_path.exists():
        return None, ["manifest.json not found — run packaging first"]

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    files = manifest.get("files", {})
    results = []
    failures = []

    for rel_path, expected_hash in sorted(files.items()):
        full_path = bundle_root / rel_path
        if not full_path.exists():
            results.append((rel_path, "MISSING", expected_hash[:16], "—"))
            failures.append(rel_path)
            continue

        actual_hash = sha256_file(full_path)
        if actual_hash == expected_hash:
            results.append((rel_path, "OK", expected_hash[:16], actual_hash[:16]))
        else:
            results.append((rel_path, "MISMATCH", expected_hash[:16], actual_hash[:16]))
            failures.append(rel_path)

    return results, failures


def verify_invariants(bundle_root):
    """Check the invariant_check.json for all-pass."""
    inv_path = bundle_root / "run_artifacts" / "invariant_check.json"
    if not inv_path.exists():
        return False, "invariant_check.json not found"

    with open(inv_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("status") != "PASSED":
        return False, f"Gate status: {data.get('status')}"

    checks = data.get("checks", [])
    failed = [c for c in checks if not c.get("passed")]
    if failed:
        return False, f"{len(failed)} invariant(s) failed"

    return True, f"All {len(checks)} invariants passed"


def write_log(bundle_root, results, failures, inv_ok, inv_msg):
    """Write verification_log.md."""
    ts = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Verification Log",
        "",
        f"**Timestamp:** {ts}",
        "**Bundle:** gemini_demo_public_v1",
        "",
        "## Hash Verification",
        "",
        "| File | Status | Expected | Actual |",
        "|------|--------|----------|--------|",
    ]

    for rel, status, expected, actual in results:
        lines.append(f"| `{rel}` | {status} | {expected}... | {actual}... |")

    lines.extend([
        "",
        f"**Files checked:** {len(results)}",
        f"**Failures:** {len(failures)}",
        "",
        "## Invariant Verification",
        "",
        f"**Status:** {'PASSED' if inv_ok else 'FAILED'}",
        f"**Detail:** {inv_msg}",
    ])

    log_path = bundle_root / "verification" / "verification_log.md"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return log_path


def write_summary(bundle_root, results, failures, inv_ok):
    """Write verification_summary.md."""
    all_ok = len(failures) == 0 and inv_ok
    verdict = "VERIFIED" if all_ok else "FAILED"

    lines = [
        "# Verification Summary",
        "",
        f"**Result:** {verdict}",
        "",
        f"- Hash checks: {len(results) - len(failures)}/{len(results)} passed",
        f"- Invariant check: {'PASSED' if inv_ok else 'FAILED'}",
        "",
    ]

    if all_ok:
        lines.append("All artifacts match their recorded hashes. All governance invariants confirmed.")
    else:
        lines.append("Verification failed. See verification_log.md for details.")
        if failures:
            lines.append("")
            lines.append("Failed files:")
            for f in failures:
                lines.append(f"- `{f}`")

    summary_path = bundle_root / "verification" / "verification_summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def main():
    bundle_root = find_bundle_root()
    print(f"Bundle root: {bundle_root}")

    # Verify hashes
    results, failures = verify_bundle(bundle_root)
    if results is None:
        print(f"ERROR: {failures[0]}")
        sys.exit(1)

    # Verify invariants
    inv_ok, inv_msg = verify_invariants(bundle_root)

    # Write logs
    log_path = write_log(bundle_root, results, failures, inv_ok, inv_msg)
    summary_path = write_summary(bundle_root, results, failures, inv_ok)

    # Print results
    print()
    for rel, status, expected, actual in results:
        marker = "OK" if status == "OK" else "FAIL"
        print(f"  [{marker}] {rel}")

    print()
    print(f"  Invariants: {inv_msg}")
    print()

    all_ok = len(failures) == 0 and inv_ok
    if all_ok:
        print("  VERIFIED — all hashes match")
    else:
        print(f"  FAILED — {len(failures)} hash failure(s)")

    print(f"\n  Log: {log_path}")
    print(f"  Summary: {summary_path}")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
