# Gemini Demo — Verification Guide

This packet contains artifacts from a governed pipeline run using **Gemini 2.0 Flash** as the LLM backend. This is a demo integration run, not Phase Two science.

---

## What This Proves

The Sovereign governance operators (Collapse → Become → Paradox-Hold → Observer) enforce identical structural invariants when the LLM backend is a cloud model (Gemini Flash) as when it is a local model (LLaMA, Mistral, Phi).

## What This Does NOT Prove

- That Gemini produces better or equivalent text quality
- That the architecture is optimal or complete
- That invariants hold for all possible cloud models
- That this extends the Phase One three-model proof (that proof is sealed separately)

---

## Constants (same across all runs)

| Parameter | Value |
|-----------|-------|
| Baseline | Sovereign-V5-Anchor |
| Governance | v1 |
| Seed | 42 |
| Passes | 1 |
| Operators | Collapse → Become → Paradox-Hold → Observer |
| Starting snapshot hash | f9a12fa4... |

## Variables (this run)

| Parameter | Value |
|-----------|-------|
| Model | gemini-2.0-flash |
| Backend | google-genai (cloud API) |
| Route | direct |
| Duration | 17.5 minutes |
| API calls | 604 |

## Invariant Results

| Invariant | Result |
|-----------|--------|
| Open tensions after Collapse | 0 |
| Paradoxes held | 94/94 (100%) |
| Paradoxes vetoed | 94/94 (100%) |
| Observer attestations | 3 |

## How To Verify

1. Check hashes: `cat hash_manifest.json`
2. Check invariants: `cat invariant_check.json`
3. Check run metadata: `cat run_metadata.json`
4. Reproduce: `$env:GEMINI_API_KEY = "your-key"; python -m SovereignNEXT.pipeline.run_gemini_demo_v1 --passes 1 --seed 42`

Governance outcomes will be identical on reproduction. Text content will vary (LLM non-determinism).

## Packet Contents

| File | Purpose |
|------|---------|
| `run_metadata.json` | Run parameters, model, duration, final counts |
| `v5_canonical_report.json` | Full operator report with health summary |
| `v5_final_state_snapshot.json` | Complete final state |
| `invariant_check.json` | Gate 3B invariant verification result |
| `hash_manifest.json` | SHA-256 of all run output files |
| `manifest.json` | SHA-256 of all proof packet files |
| `hashes.sha256` | Flat hash file for command-line verification |
| `README_verify_demo.md` | This document |
| `DEMO_SCRIPT_90S.md` | 90-second demo walkthrough |
| `FINAL_GATE_REPORT_DEMO.md` | Final gate report |
