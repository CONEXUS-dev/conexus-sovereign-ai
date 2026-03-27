# How to Verify the Three-Model Governed Run

**Date:** 2026-03-07 | **Baseline:** Sovereign-V5-Anchor | **Governance:** v1 | **Seed:** 42

## What Was Done

Three local LLMs — LLaMA (8B), Mistral (7B), Phi (4B) — each served as the sole language model for a single pass of the CONEXUS Sovereign pipeline. The pipeline applies a fixed operator sequence (Collapse → Become → Paradox-Hold → Observer) to a shared starting state. The question tested: **do governance invariants hold regardless of which model generates LLM output?**

## What Was Held Constant vs. What Varied

| Dimension          | Constant across all runs                             | Variable across runs           |
| ------------------ | ---------------------------------------------------- | ------------------------------ |
| Starting state     | `v5_final_state_snapshot.json` (hash: `f9a12fa4...`) | —                              |
| Operator sequence  | Collapse → Become → Paradox-Hold → Observer          | —                              |
| Governance version | v1 (no modifications)                                | —                              |
| Seed               | 42                                                   | —                              |
| Passes             | 1                                                    | —                              |
| LLM model          | —                                                    | LLaMA 8B / Mistral 7B / Phi 4B |
| LLM backend        | —                                                    | GPT4All / GPT4All / llama-cpp  |
| Model parameters   | —                                                    | 8B / 7B / 4B                   |

## What Invariants Were Checked

All nine invariants listed in `comparison_metrics.json → invariants_verified` evaluated to `true`:

1. All paradoxes held (94/94 in every run)
2. All paradoxes vetoed by Collapse (94/94 in every run)
3. Zero open tensions (0 in every run)
4. Operator sequence preserved identically
5. Governance v1 unchanged
6. Identical starting snapshot (same input hash)
7. Identical seed (42)
8. Identical paradox count (94)
9. Identical paradox promotions (10 new)

## How to Reproduce Verification Locally

**Step 1 — Verify artifact hashes:**

```bash
python _verify.py
```

This checks all SHA-256 hashes in `hash_manifest.json` and `manifest.json`. Expected output: `Verdict: VERIFIED`.

**Step 2 — Inspect invariants programmatically:**

```bash
python -c "import json; d=json.load(open('comparison_metrics.json')); print(all(d['invariants_verified'].values()))"
```

Expected output: `True`.

**Step 3 — Re-run a model (optional, requires model files):**

```bash
python -m SovereignNEXT.pipeline.run_three_model_suite --model phi --passes 1 --seed 42
```

Operator behavior will be identical. LLM output may differ slightly due to floating-point nondeterminism.

## What Conclusions Are Justified

- The pipeline's governance operators enforce the same invariants regardless of which LLM generates the underlying text.
- The structural outcomes (paradox count, promotions, hold/veto ratios) are stable across models of different sizes and backends.
- The operator sequence constrains LLM output after generation — the model does not control governance outcomes.

## What Conclusions Are NOT Claimed

- This does not prove the architecture is optimal or complete.
- This does not prove the models produce "correct" or "intelligent" output.
- This does not prove the invariants would hold under arbitrary governance modifications.
- This does not claim bit-level reproducibility of LLM output across runs.
- This does not claim the results generalize to models not tested.

## Limitations

- LLaMA run was recovered from a crash (Pass 1 snapshot only; no canonical report).
- All runs used 1 pass due to 16 GB RAM hardware constraint.
- LLM output is non-deterministic at the floating-point level; operator behavior is deterministic given state + seed.
