# CONEXUS Sovereign Pipeline — Gemini Governed Demo

## What This Demo Shows

A one-command, reproducible governed run of the CONEXUS Sovereign pipeline using **Gemini 2.0 Flash** as the cloud LLM backend.

The pipeline's governance operators — Collapse, Become, Paradox-Hold, and Observer — enforce structural invariants on the LLM's output after generation. This demo confirms those invariants hold identically whether the LLM backend is a local model or a cloud API.

The same invariants were previously verified on three local models (LLaMA 8B, Mistral 7B, Phi 4B). Gemini Flash is the fourth model to pass.

---

## Headline Result

| Invariant | Result |
|-----------|--------|
| Open tensions after Collapse | **0** |
| Paradoxes held | **94 / 94** (100%) |
| Paradoxes vetoed | **94 / 94** (100%) |
| Observer attestations | **3** |

**Gemini is the fourth model to pass these governance invariants.**

Four models. Different architectures. Different providers. Same structural outcome. The governance operators are model-agnostic.

---

## What This Demo Does NOT Claim

- This is not a product or hosted service.
- This is not a performance benchmark.
- This does not prove optimality or completeness of the architecture.
- This does not replace or modify the Phase One three-model proof, which is sealed separately.
- LLM output quality is not evaluated — only governance enforcement is tested.

---

## How To Run the Demo

### Prerequisites

- Python 3.10+
- `google-genai` package (`pip install google-genai`)
- A Gemini API key (free tier sufficient)

### Setup

```bash
# Set your Gemini API key (do not commit this)
export GEMINI_API_KEY="your-api-key-here"        # Linux/Mac
$env:GEMINI_API_KEY = "your-api-key-here"         # PowerShell
```

### Run

```bash
python -m SovereignNEXT.pipeline.run_gemini_demo_v1 --passes 1 --seed 42
```

### Expected Runtime

15–25 minutes depending on API latency. The original run completed in 17.5 minutes with 604 Gemini API calls.

### Expected Output

The pipeline will:
1. Load the sealed V5 baseline snapshot (650 claims, 1505 tensions, 84 paradoxes)
2. Run one LLM-driven Become pass via Gemini (claim expansion + tension detection)
3. Run Phase 5 governance operators (Collapse → Become → Paradox-Hold → Observer)
4. Emit timestamped artifacts to `artifacts/gemini_openclaw_demo_v1/runs/`
5. Print invariant confirmation (Gate 3B)

Governance outcomes are deterministic given the same seed. Text content will vary across runs due to LLM non-determinism.

---

## How To Verify

### Verify invariants

```bash
python -c "import json; print(json.dumps(json.load(open('run_artifacts/invariant_check.json')), indent=2))"
```

Expected: all four checks show `"passed": true`.

### Verify artifact integrity

```bash
python verification/_verify.py
```

Expected output: `VERIFIED — all hashes match`.

### Verify manually

Compare SHA-256 hashes in `verification/hashes.sha256` against the actual files:

```bash
# Linux/Mac
sha256sum -c verification/hashes.sha256

# PowerShell
python verification/_verify.py
```

---

## Claim Boundary

This demo extends the governance invariance result to a fourth model (Gemini Flash, cloud API). It confirms that the Sovereign pipeline's structural enforcement is independent of the LLM provider.

This demo does not replace or modify the Phase One three-model proof. That proof is sealed separately and remains unchanged. The Phase One sealed paths were hash-verified before and after this demo was produced.

---

## Bundle Contents

| Path | Purpose |
|------|---------|
| `README_verify_demo.md` | This document |
| `DEMO_SCRIPT_90S.md` | Step-by-step demo recording script |
| `FINAL_GATE_REPORT_DEMO.md` | Audit summary with all gate results |
| `source/run_gemini_demo_v1.py` | Demo runner (inspection copy) |
| `source/gemini_client.py` | Gemini adapter (inspection copy) |
| `source/base.py` | Adapter interface (inspection copy) |
| `run_artifacts/v5_pass1_state_snapshot.json` | Pass 1 state snapshot |
| `run_artifacts/v5_final_state_snapshot.json` | Final state snapshot |
| `run_artifacts/v5_canonical_report.json` | Full operator report |
| `run_artifacts/run_metadata.json` | Run parameters and results |
| `run_artifacts/hash_manifest.json` | SHA-256 hashes of run output |
| `run_artifacts/invariant_check.json` | Gate 3B invariant verification |
| `verification/manifest.json` | Bundle manifest with hashes |
| `verification/hashes.sha256` | Flat hash file |
| `verification/_verify.py` | Standalone verification script |
| `verification/verification_log.md` | Verification execution log |
| `verification/verification_summary.md` | Verification result summary |
