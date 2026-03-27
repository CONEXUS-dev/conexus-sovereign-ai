# Phase 1 Preflight Report

**Timestamp:** 2026-03-07T13:49:07Z
**Status:** PASS

## Environment

- **python_version:** 3.14.2 (tags/v3.14.2:df79316, Dec  5 2025, 17:18:21) [MSC v.1944 64 bit (AMD64)]
- **platform:** Windows-11-10.0.26200-SP0
- **machine:** AMD64
- **processor:** Intel64 Family 6 Model 151 Stepping 5, GenuineIntel
- **os:** Windows
- **os_version:** 10.0.26200
- **cwd:** C:\Users\Derek Angell\Desktop\CONEXUS_REPO
- **repo_root:** C:\Users\Derek Angell\Desktop\CONEXUS_REPO
- **gpt4all_device:** cpu (default)
- **gpt4all_ctx:** 4096 (default)
- **gpt4all_model_path:** C:\Users\Derek Angell\.cache\gpt4all (default)

## Baseline Artifacts

| File | Exists | Size |
|---|---|---|
| `SovereignNEXT\pipeline\Sovereign-V5-Anchor.seal.json` | YES | 886 bytes |
| `SovereignNEXT\pipeline\v5_final_state_snapshot.json` | YES | 2,717,532 bytes |
| `SovereignNEXT\pipeline\v5_canonical_report.json` | YES | 5,239 bytes |
| `SovereignNEXT\tests\v3_final_state_snapshot.json` | YES | 454,187 bytes |

## Model Files

| Model | Exists | Size |
|---|---|---|
| `Meta-Llama-3-8B-Instruct.Q4_0.gguf` | YES | 4,661,724,384 bytes |
| `Mistral-7B-Instruct-v0.3.Q4_0.gguf` | YES | 4,113,289,152 bytes |
| `Phi-4-mini-instruct-Q4_K_M.gguf` | YES | 2,491,874,688 bytes |

## Dry-Load Results

| Model | Role | Status | Duration | Response chars |
|---|---|---|---|---|
| `Meta-Llama-3-8B-Instruct.Q4_0.gguf` | collapse | OK | 15.81s | 29 |
| `Mistral-7B-Instruct-v0.3.Q4_0.gguf` | become | OK | 20.92s | 80 |
| `Phi-4-mini-instruct-Q4_K_M.gguf` | outer | OK | 7.27s | 24 |

## Phase 2 Readiness

**YES** — All models loaded and generated successfully. All baseline files present.
