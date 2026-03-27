# Three-Model Governed Run — Phase 2 Design Document

**Date:** 2026-03-07
**Author:** Opie (Cascade)
**Status:** Implementation complete

## Strategy

**Option A: Three isolated runs.** Each run binds ALL LLM calls to a single model. Produces three independent final states for comparison. Zero operator or governance changes.

## Starting Snapshot

**`SovereignNEXT/pipeline/v5_final_state_snapshot.json`** (Sovereign-V5-Anchor sealed baseline)

Per Pylo's correction: using the sealed V5 baseline (not V3) strengthens the claim "this is the baseline" and avoids semantic ambiguity.

## Implementation

### Changes to existing code

**File:** `SovereignNEXT/pipeline/run_sovereign_pipeline_v5.py`

Two new parameters added to `run_canonical_pipeline()`:
- `model_override: str = None` — model name string for all LLM calls (default: `SWAY_MODEL`)
- `output_dir: str = None` — artifact output directory (default: `OUTPUT_DIR`)

Binding point (was line 448, now uses `active_model`):
```python
active_model = model_override or SWAY_MODEL
new_claims, new_tensions, new_promos = _run_llm_pass(
    state, llm, active_model, pass_num, embedding_cache,
)
```

`_save_report()` also accepts `output_dir` param and uses it instead of hardcoded `OUTPUT_DIR`.

All snapshot saves now pass `output_dir=active_output_dir`.

**No operator logic changes. No governance changes. No observer changes.**

### New file

**File:** `SovereignNEXT/pipeline/run_three_model_suite.py` (~390 lines)

- CLI: `--model {llama,mistral,phi}` or `--all`
- Model registry maps keys to GGUF filenames, labels, backends
- For LLaMA/Mistral: calls `run_canonical_pipeline()` with `model_override`
- For Phi: uses `_PatchedLLMClient` subclass that routes `generate()` → `generate_outer()` via llama-cpp
- Phi adapter is LOCAL to `_run_with_phi_adapter()` and restored in `finally` block — no global LLMClient mutation
- Output: `artifacts/three_model_run/<model_name>/`
- Saves `run_metadata.json` and `hash_manifest.json` per run

## Exact Command Lines

```bash
# Run A — LLaMA
python -m SovereignNEXT.pipeline.run_three_model_suite --model llama --passes 3 --seed 42

# Run B — Mistral
python -m SovereignNEXT.pipeline.run_three_model_suite --model mistral --passes 3 --seed 42

# Run C — Phi
python -m SovereignNEXT.pipeline.run_three_model_suite --model phi --passes 3 --seed 42

# All three sequentially
python -m SovereignNEXT.pipeline.run_three_model_suite --all --passes 3 --seed 42
```

All commands use default snapshot (`v5_final_state_snapshot.json`).

## Exact Output Paths

```
artifacts/three_model_run/
├── llama/
│   ├── run_metadata.json
│   ├── hash_manifest.json
│   ├── v5_canonical_report.json
│   ├── v5_pass1_state_snapshot.json
│   ├── v5_pass2_state_snapshot.json
│   ├── v5_pass3_state_snapshot.json
│   └── v5_final_state_snapshot.json
├── mistral/
│   └── [same artifact set]
└── phi/
    └── [same artifact set]
```

## Phi Routing Verification

- `PhiLLMAdapter` and `_PatchedLLMClient` both route `generate()` → `generate_outer()`
- `generate_outer()` uses llama-cpp-python backend (not GPT4All)
- Adapter is scoped to function, restored in `finally` block
- Preflight test confirmed Phi loads and generates via `generate_outer()` (7.27s, 24 chars)

## Test Verification

14/14 sovereign observer unit tests pass after pipeline changes.
Syntax verification: both files parse cleanly via `ast.parse()`.
CLI `--help` verified.
