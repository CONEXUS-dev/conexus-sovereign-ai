"""Artifact integrity verification script — Phase 1 of verification package."""
import json, hashlib, os, datetime

base = os.path.join("artifacts", "three_model_run")
pp = os.path.join("artifacts", "proof_packet_three_model_v1")

manifest_path = os.path.join(base, "meta", "hash_manifest.json")
manifest = json.load(open(manifest_path, encoding="utf-8"))

log_lines = []
log_lines.append("# Artifact Integrity Verification Log")
log_lines.append("")
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_lines.append("**Date:** " + now)
log_lines.append("**Manifest:** artifacts/three_model_run/meta/hash_manifest.json")
log_lines.append("**Total files in manifest:** " + str(len(manifest)))
log_lines.append("")
log_lines.append("## Run Artifacts (three_model_run/)")
log_lines.append("")
log_lines.append("| # | File | Expected (first 16) | Actual (first 16) | Status |")
log_lines.append("|---|------|---------------------|-------------------|--------|")

ok = 0
fail = 0
missing = 0

for i, (rel, expected) in enumerate(sorted(manifest.items()), 1):
    full = os.path.join(base, rel)
    if not os.path.exists(full):
        log_lines.append("| " + str(i) + " | `" + rel + "` | `" + expected[:16] + "...` | — | MISSING |")
        missing += 1
        continue
    actual = hashlib.sha256(open(full, "rb").read()).hexdigest()
    if actual == expected:
        log_lines.append("| " + str(i) + " | `" + rel + "` | `" + expected[:16] + "...` | `" + actual[:16] + "...` | OK |")
        ok += 1
    else:
        log_lines.append("| " + str(i) + " | `" + rel + "` | `" + expected[:16] + "...` | `" + actual[:16] + "...` | MISMATCH |")
        fail += 1

log_lines.append("")
log_lines.append("### Run Artifacts Summary")
log_lines.append("- **Files verified:** " + str(ok))
log_lines.append("- **Mismatches:** " + str(fail))
log_lines.append("- **Missing:** " + str(missing))

run_ok = ok
run_fail = fail
run_missing = missing

# Proof packet manifest
pp_manifest_path = os.path.join(pp, "manifest.json")
pp_manifest = json.load(open(pp_manifest_path, encoding="utf-8"))
pp_files = pp_manifest.get("files", {})

log_lines.append("")
log_lines.append("---")
log_lines.append("")
log_lines.append("## Proof Packet (proof_packet_three_model_v1/)")
log_lines.append("")
log_lines.append("**Manifest:** artifacts/proof_packet_three_model_v1/manifest.json")
log_lines.append("**Total files:** " + str(len(pp_files)))
log_lines.append("")
log_lines.append("| # | File | Expected (first 16) | Actual (first 16) | Status |")
log_lines.append("|---|------|---------------------|-------------------|--------|")

pp_ok = 0
pp_fail = 0
pp_missing = 0

for j, (rel2, exp2) in enumerate(sorted(pp_files.items()), 1):
    full2 = os.path.join(pp, rel2)
    if not os.path.exists(full2):
        log_lines.append("| " + str(j) + " | `" + rel2 + "` | `" + exp2[:16] + "...` | — | MISSING |")
        pp_missing += 1
        continue
    act2 = hashlib.sha256(open(full2, "rb").read()).hexdigest()
    if act2 == exp2:
        log_lines.append("| " + str(j) + " | `" + rel2 + "` | `" + exp2[:16] + "...` | `" + act2[:16] + "...` | OK |")
        pp_ok += 1
    else:
        log_lines.append("| " + str(j) + " | `" + rel2 + "` | `" + exp2[:16] + "...` | `" + act2[:16] + "...` | MISMATCH |")
        pp_fail += 1

log_lines.append("")
log_lines.append("### Proof Packet Summary")
log_lines.append("- **Files verified:** " + str(pp_ok))
log_lines.append("- **Mismatches:** " + str(pp_fail))
log_lines.append("- **Missing:** " + str(pp_missing))

# Duplicate hash check
dupes = {}
for rel, h in manifest.items():
    dupes.setdefault(h, []).append(rel)
real_dupes = {h: files for h, files in dupes.items() if len(files) > 1}
if real_dupes:
    log_lines.append("")
    log_lines.append("---")
    log_lines.append("")
    log_lines.append("## Duplicate Hashes (Expected)")
    for h, files in real_dupes.items():
        log_lines.append("- `" + h[:16] + "...`: " + " = ".join(["`" + f + "`" for f in files]))
    log_lines.append("")
    log_lines.append("Note: `v5_final_state_snapshot.json` = `v5_pass1_state_snapshot.json` is expected when passes=1 (only one pass was executed, so the pass-1 snapshot IS the final snapshot).")

# Final verdict
total_ok = run_ok + pp_ok
total_fail = run_fail + pp_fail
total_missing = run_missing + pp_missing

log_lines.append("")
log_lines.append("---")
log_lines.append("")
log_lines.append("## Final Verdict")
log_lines.append("")
if total_fail == 0 and total_missing == 0:
    log_lines.append("**INTEGRITY: VERIFIED**")
    log_lines.append("")
    log_lines.append("All " + str(total_ok) + " files match their recorded SHA-256 hashes. No missing files. No conflicting hashes.")
    verdict = "VERIFIED"
else:
    log_lines.append("**INTEGRITY: FAILED**")
    log_lines.append("")
    log_lines.append(str(total_fail) + " mismatches, " + str(total_missing) + " missing.")
    verdict = "FAILED"

# Write verification_log.md
with open(os.path.join(pp, "verification_log.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")

# Write verification_summary.md
summary = []
summary.append("# Verification Summary")
summary.append("")
summary.append("**Date:** " + now)
summary.append("**Verdict:** " + verdict)
summary.append("")
summary.append("| Scope | Files | OK | Mismatch | Missing |")
summary.append("|-------|-------|----|----------|---------|")
summary.append("| Run artifacts | " + str(len(manifest)) + " | " + str(run_ok) + " | " + str(run_fail) + " | " + str(run_missing) + " |")
summary.append("| Proof packet | " + str(len(pp_files)) + " | " + str(pp_ok) + " | " + str(pp_fail) + " | " + str(pp_missing) + " |")
summary.append("| **Total** | **" + str(len(manifest) + len(pp_files)) + "** | **" + str(total_ok) + "** | **" + str(total_fail) + "** | **" + str(total_missing) + "** |")
summary.append("")
if verdict == "VERIFIED":
    summary.append("All artifact hashes match. The proof packet is intact and unmodified.")
else:
    summary.append("Integrity check failed. Review verification_log.md for details.")

with open(os.path.join(pp, "verification_summary.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(summary) + "\n")

print("Verdict: " + verdict)
print("Run artifacts: " + str(run_ok) + " OK, " + str(run_fail) + " fail, " + str(run_missing) + " missing")
print("Proof packet: " + str(pp_ok) + " OK, " + str(pp_fail) + " fail, " + str(pp_missing) + " missing")
print("verification_log.md written")
print("verification_summary.md written")
