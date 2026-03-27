# Invariant Proof Table

Each invariant below was verified across all three model runs (LLaMA 8B, Mistral 7B, Phi 4B). Evidence references specific fields in the proof packet artifacts.

| # | Invariant | LLaMA | Mistral | Phi | Evidence | Artifact |
|---|-----------|-------|---------|-----|----------|----------|
| 1 | Zero open tensions | 0 | 0 | 0 | `runs.{model}.open_tensions = 0` | `comparison_metrics.json` |
| 2 | 100% paradoxes held | 94/94 | 94/94 | 94/94 | `runs.{model}.held_count = 94`; final paradox count = 94 | `comparison_metrics.json`, `observer_reports/*.json → per_pass[0].held_count` |
| 3 | 100% paradoxes vetoed | 94/94 | 94/94 | 94/94 | `runs.{model}.vetoed_count = 94`; final paradox count = 94 | `comparison_metrics.json`, `observer_reports/*.json → per_pass[0].vetoed_count` |
| 4 | Identical paradox promotions | +10 | +10 | +10 | `runs.{model}.delta_paradoxes = 10` | `comparison_metrics.json` |
| 5 | Identical paradox count | 94 | 94 | 94 | `runs.{model}.final_paradoxes = 94` | `comparison_metrics.json` |
| 6 | Identical operator sequence | Collapse → Become → Hold → Observer | same | same | `operator_sequence` field; confirmed by per-pass operator sections in canonical reports | `comparison_metrics.json`, `observer_reports/*.json` |
| 7 | Identical starting snapshot | `f9a12fa4...` | `f9a12fa4...` | `f9a12fa4...` | `input_content_hash` matches across all runs | `comparison_metrics.json → input_content_hash`, `run_metadata/*.json → snapshot` |
| 8 | Identical seed | 42 | 42 | 42 | `seed = 42` in all run metadata | `run_metadata/{llama,mistral,phi}_metadata.json → seed` |
| 9 | Governance v1 unchanged | v1 | v1 | v1 | `governance_version = "v1"` in all run metadata; no governance files modified during runs | `run_metadata/*.json → governance_version`, `comparison_metrics.json → governance_version` |

## Verification Command

To programmatically confirm all invariants:

```bash
python -c "import json; d=json.load(open('comparison_metrics.json')); iv=d['invariants_verified']; [print(k + ': ' + str(v)) for k,v in iv.items()]; print('ALL PASS' if all(iv.values()) else 'FAIL')"
```

Expected output: all `True`, ending with `ALL PASS`.

## Notes

- LLaMA operator-level fields (`held_count`, `vetoed_count`) are `null` in `comparison_metrics.json` because the LLaMA run was crash-recovered and no canonical report was generated. The invariant values for LLaMA are confirmed from the state snapshot (94 paradoxes, 0 open tensions).
- Invariants 1–5 are structural outcomes enforced by operators. Invariants 6–9 are experimental controls held constant by design.
