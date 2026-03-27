# Final Gate Report — Three-Model Governed Run

**Date:** 2026-03-07
**Baseline:** Sovereign-V5-Anchor
**Governance:** v1 | Seed 42 | 1 pass | Operator sequence: Collapse → Become → Paradox-Hold → Observer

---

## What Was Produced

| Document | Purpose |
|----------|---------|
| `README_verify.md` | One-page external verification guide |
| `structural_overview.md` | Visual/ASCII explanation of pipeline architecture and operator dominance |
| `interpretation_notes.md` | Metric-by-metric interpretation of the three-model comparison |
| `invariants_table.md` | Single table mapping each invariant to its evidence and artifact |
| `reviewer_faq.md` | Defensive FAQ answering 8 anticipated skeptical questions |
| `verification_log.md` | Full SHA-256 hash verification log for all run and packet artifacts |
| `verification_summary.md` | One-page integrity verification summary |
| `comparison_report.md` | Tabulated meta-comparison across all three models |
| `comparison_metrics.json` | Structured metrics and invariant verification flags |
| `manifest.json` | SHA-256 manifest of all 18 files in this packet |
| `hashes.sha256` | Flat hash file for command-line verification |
| `_verify.py` | Standalone verification script (run to confirm all hashes) |

Supporting artifacts (copied unchanged from source):
- `run_metadata/llama_metadata.json`
- `run_metadata/mistral_metadata.json`
- `run_metadata/phi_metadata.json`
- `observer_reports/mistral_report.json`
- `observer_reports/phi_report.json`
- `hash_manifest.json` (cross-references all run artifacts)
- `CONEXUS_SOVEREIGN_SYNC_BRIEF.md` (system brief)

---

## What Was Verified

1. **Artifact integrity:** 25 files checked against SHA-256 manifests. 0 mismatches. 0 missing. (`verification_log.md`)
2. **Original artifact preservation:** All 8 copied artifacts match their source files byte-for-byte. No modifications.
3. **Governance invariants:** All 9 invariants evaluated to `true` across all three model runs. (`invariants_table.md`, `comparison_metrics.json`)

---

## What Claims Are Justified

These conclusions are supported by the artifacts in this packet:

1. The pipeline's governance operators enforce identical structural invariants (zero open tensions, 100% paradox held, 100% paradox vetoed) regardless of which LLM generates the underlying text.
2. Three models of different sizes (4B, 7B, 8B), architectures (Phi, Mistral, LLaMA), and backends (llama-cpp, GPT4All) all produced governed output satisfying the same 9 invariants.
3. Model-dependent quantities (claim count, tension count, text content) vary as expected. Model-independent quantities (paradox count, promotions, hold/veto ratios, open tension count) do not vary.
4. The operator sequence constrains LLM output after generation. The LLM does not control governance outcomes.
5. All artifacts are hashable, auditable, and independently verifiable.

---

## What Claims Are Explicitly NOT Made

1. This does not prove the architecture is optimal, complete, or final.
2. This does not prove the models produce correct, meaningful, or intelligent output.
3. This does not prove the invariants hold for models not tested.
4. This does not prove the invariants hold under modified governance versions.
5. This does not claim bit-level reproducibility of LLM output.
6. This does not claim the pipeline produces useful results — only that it produces governed results.
7. This does not claim the Observer's anomaly classification is optimal or complete.

---

## Packet Integrity

- **Files in packet:** 18 (+ `_verify.py` utility)
- **Manifest:** `manifest.json` (SHA-256 of all 18 files)
- **Flat hashes:** `hashes.sha256`
- **Verification:** Run `python _verify.py` from the packet directory

---

The three-model governed proof is complete and externally verifiable.
