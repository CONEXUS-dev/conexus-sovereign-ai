# Artifact Integrity Verification Log

**Date:** 2026-03-07 20:08:13
**Manifest:** artifacts/three_model_run/meta/hash_manifest.json
**Total files in manifest:** 15

## Run Artifacts (three_model_run/)

| # | File | Expected (first 16) | Actual (first 16) | Status |
|---|------|---------------------|-------------------|--------|
| 1 | `llama\hash_manifest.json` | `02120c83b31bef30...` | `02120c83b31bef30...` | OK |
| 2 | `llama\run_metadata.json` | `db0dbc126c6d412c...` | `db0dbc126c6d412c...` | OK |
| 3 | `llama\v5_pass1_state_snapshot.json` | `8329eca75bd54fd9...` | `8329eca75bd54fd9...` | OK |
| 4 | `meta\comparison_metrics.json` | `29e259d65dd1fa60...` | `29e259d65dd1fa60...` | OK |
| 5 | `meta\comparison_report.md` | `103ef95c6dc51910...` | `103ef95c6dc51910...` | OK |
| 6 | `mistral\hash_manifest.json` | `32fe1c0f70c4f886...` | `32fe1c0f70c4f886...` | OK |
| 7 | `mistral\run_metadata.json` | `ebcc3075c0d8ed87...` | `ebcc3075c0d8ed87...` | OK |
| 8 | `mistral\v5_canonical_report.json` | `d2f9375ac20c88e3...` | `d2f9375ac20c88e3...` | OK |
| 9 | `mistral\v5_final_state_snapshot.json` | `503c827a61d3c840...` | `503c827a61d3c840...` | OK |
| 10 | `mistral\v5_pass1_state_snapshot.json` | `503c827a61d3c840...` | `503c827a61d3c840...` | OK |
| 11 | `phi\hash_manifest.json` | `0b023f38aa996a16...` | `0b023f38aa996a16...` | OK |
| 12 | `phi\run_metadata.json` | `6a8d57d49d707cea...` | `6a8d57d49d707cea...` | OK |
| 13 | `phi\v5_canonical_report.json` | `62a5543954984ca0...` | `62a5543954984ca0...` | OK |
| 14 | `phi\v5_final_state_snapshot.json` | `1ce87fbf854c7aec...` | `1ce87fbf854c7aec...` | OK |
| 15 | `phi\v5_pass1_state_snapshot.json` | `1ce87fbf854c7aec...` | `1ce87fbf854c7aec...` | OK |

### Run Artifacts Summary
- **Files verified:** 15
- **Mismatches:** 0
- **Missing:** 0

---

## Proof Packet (proof_packet_three_model_v1/)

**Manifest:** artifacts/proof_packet_three_model_v1/manifest.json
**Total files:** 10

| # | File | Expected (first 16) | Actual (first 16) | Status |
|---|------|---------------------|-------------------|--------|
| 1 | `CONEXUS_SOVEREIGN_SYNC_BRIEF.md` | `58ac384b4ccb1928...` | `58ac384b4ccb1928...` | OK |
| 2 | `README_verify.md` | `a5762ef27fc4fe88...` | `a5762ef27fc4fe88...` | OK |
| 3 | `comparison_metrics.json` | `29e259d65dd1fa60...` | `29e259d65dd1fa60...` | OK |
| 4 | `comparison_report.md` | `103ef95c6dc51910...` | `103ef95c6dc51910...` | OK |
| 5 | `hash_manifest.json` | `1f490febcd5de6c0...` | `1f490febcd5de6c0...` | OK |
| 6 | `observer_reports/mistral_report.json` | `d2f9375ac20c88e3...` | `d2f9375ac20c88e3...` | OK |
| 7 | `observer_reports/phi_report.json` | `62a5543954984ca0...` | `62a5543954984ca0...` | OK |
| 8 | `run_metadata/llama_metadata.json` | `db0dbc126c6d412c...` | `db0dbc126c6d412c...` | OK |
| 9 | `run_metadata/mistral_metadata.json` | `ebcc3075c0d8ed87...` | `ebcc3075c0d8ed87...` | OK |
| 10 | `run_metadata/phi_metadata.json` | `6a8d57d49d707cea...` | `6a8d57d49d707cea...` | OK |

### Proof Packet Summary
- **Files verified:** 10
- **Mismatches:** 0
- **Missing:** 0

---

## Duplicate Hashes (Expected)
- `503c827a61d3c840...`: `mistral\v5_final_state_snapshot.json` = `mistral\v5_pass1_state_snapshot.json`
- `1ce87fbf854c7aec...`: `phi\v5_final_state_snapshot.json` = `phi\v5_pass1_state_snapshot.json`

Note: `v5_final_state_snapshot.json` = `v5_pass1_state_snapshot.json` is expected when passes=1 (only one pass was executed, so the pass-1 snapshot IS the final snapshot).

---

## Final Verdict

**INTEGRITY: VERIFIED**

All 25 files match their recorded SHA-256 hashes. No missing files. No conflicting hashes.
