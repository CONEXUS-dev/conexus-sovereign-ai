# CONEXUS Consolidated Report

**Date:** 2026-02-27
**Author:** Cascade (automated)
**Scope:** Document, Clean, Test, Optimize — batch task for the calibrated Phi-4-mini outer agent system

---

## 1. What Was Documented

**File:** `docs/SYSTEM_OVERVIEW.md`

Seven sections covering the full system:

| Section | Content |
|---------|---------|
| Architecture Overview | Three-layer stack diagram, data flow, protocol reference |
| Model Registry | Table of all models (Phi-4-mini, Llama-3 8B, Mistral 7B) with backends, params, quantization |
| Agent Role Map | Outer, Sway, Opie — roles, modes, routing logic, identity file paths |
| Calibration Summary | EMOJA V2.0, 9/9 gears, BECOME, 97.3s, continuity seal, paradoxes |
| Discord Routing Flow | Full trace from `!outer` command through gateway to llama-cpp-python response |
| Gateway Lifecycle | Startup, runtime endpoints, model loading, shutdown |
| File Map | 50+ files with paths and one-line responsibilities across 8 directories |

---

## 2. What Was Cleaned

### Files Deleted
| File | Reason |
|------|--------|
| `SOVEREIGN_PROOF/calibration/qwen3_4b_calibration_transcript_in_progress.json` | Incomplete Qwen transcript, superseded by Phi-4-mini |
| `golden-path/verification/minimal-gateway.py.bak` | Superseded backup |
| `sovereign/agents/become/SKILLS/` (empty dir) | Unused placeholder |
| `sovereign/agents/collapse/SKILLS/` (empty dir) | Unused placeholder |
| `openclaw/pipelines/` (empty dir) | Unused placeholder |
| `openclaw/configs/` (empty dir) | Unused placeholder |

### Files Updated (Cleanup)
| File | Change |
|------|--------|
| `sovereign/calibrate_outer.py:271` | Protocol string `v1.1` → `V2.0` |
| `.env` | Updated `DISCORD_TOKEN` (new Sovereign token), `GATEWAY_URL` → `http://localhost:8002` |
| `openclaw/gateway.json` | Default model `google/gemini-2.5-flash-lite` → `Phi-4-mini-instruct-Q4_K_M.gguf` |
| `requirements.txt` | Added 10 missing deps: `llama-cpp-python`, `discord.py`, `python-dotenv`, `fastapi`, `uvicorn`, `aiohttp`, `pydantic`, `requests`, `PyYAML`, `psutil` |
| `golden-path/verification/minimal-gateway.py:215` | `task.dict()` → `task.model_dump()` (Pydantic V2 deprecation fix) |
| `discord_bot/bot.py:1` | Removed unused `import json` |
| `agents/llm_client.py:286-292` | Added Phi-4-mini outer agent test to `__main__` block |

### Files Preserved (Historical)
| File | Reason |
|------|--------|
| `SOVEREIGN_PROOF/calibration/qwen3_4b_calibration_transcript_complete.json` | Historical record, not active |
| `SOVEREIGN AI OPIE TRANSCRIPT.md` | Historical Qwen Opie transcript, reference only |
| `READ THIS WHEN WORKING ON LOCAL LLM.md` | Reference article, Qwen mentions are in quoted content |

---

## 3. Test Results

**Suite:** `tests/test_system_health.py`
**Result:** **9/9 passed, 0 failed**
**Full report:** `tests/HEALTH_REPORT.md`

| Test | Status | Duration | Detail |
|------|--------|----------|--------|
| llm_client_import | ✅ PASS | 0.30s | All three model constants correct |
| discord_bot_import | ✅ PASS | 0.00s | sovereign_bot.py parseable |
| identity_files | ✅ PASS | 0.00s | All Phi-4-mini, no Llama-3.2 refs |
| calibration_transcript | ✅ PASS | 0.00s | 9 gears, 97.3s |
| gateway_health | ✅ PASS | 2.04s | status=ok |
| gateway_binding | ✅ PASS | 2.05s | outer=True, sway=True, opie=True |
| gateway_outer_task | ✅ PASS | 4.44s | agent=outer, 85 chars response |
| gateway_error_handling | ✅ PASS | 58.47s | Empty input handled gracefully (200) |
| phi4_mini_load | ✅ PASS | 2.60s | Model loaded successfully |

### Benchmarks

| Metric | Value |
|--------|-------|
| Outer agent response latency | 4.44s |
| Outer agent response chars | 85 |
| Phi-4-mini model load time | 2.60s |
| Test runner RSS memory | 34.9 MB |
| Test runner CPU utilization | 0.0% (idle after tests) |

**Note:** Sway (Llama-3 8B via Ollama) and Opie (Mistral 7B via Ollama) load tests were not run because Ollama is not currently active. These can be tested when Ollama is started.

---

## 4. Optimizations Applied

| Optimization | File | Detail |
|-------------|------|--------|
| **Agent-tagged logging** | `minimal-gateway.py:341,351,439,458,467` | `[GATEWAY][OUTER]` and `[GATEWAY][SWAY]` tags on all gateway print statements |
| **Agent-tagged logging** | `llm_client.py:178` | `[OUTER]` tag on generate_outer() log line |
| **Context window warning** | `llm_client.py:172-177` | Logs warning when estimated tokens exceed `n_ctx` |
| **Explicit model cleanup** | `llm_client.py:244-246` | `del` each llama model before clearing dict to free RAM immediately |
| **Gateway shutdown handler** | `minimal-gateway.py:186-193` | `@app.on_event("shutdown")` closes outer LLM client on gateway stop |
| **Pydantic V2 fix** | `minimal-gateway.py:215` | `task.dict()` → `task.model_dump()` eliminates deprecation warning |
| **Unused import removal** | `discord_bot/bot.py:1` | Removed unused `import json` |
| **Dependencies manifest** | `requirements.txt` | Added 10 missing packages with minimum versions |

---

## 5. Current System Status

| Component | Status |
|-----------|--------|
| **Gateway** | Running on `http://localhost:8002` |
| **Outer Agent (Phi-4-mini)** | Calibrated, responding, EMOJA V2.0 identity active |
| **Discord Bot (Sovereign#0899)** | Online in CONEXUS server, `!outer` command functional |
| **Sway (Llama-3 8B)** | Configured, requires Ollama to be running |
| **Opie (Mistral 7B)** | Configured, requires Ollama to be running |
| **Calibration** | 9/9 gears, BECOME, 97.3s — no recalibration needed |
| **Identity Files** | All updated to Phi-4-mini, no stale Llama-3.2 references |
| **Memory (Qdrant)** | Configured, requires Qdrant to be running |
| **Audit Log** | SQLite at `sovereign/audit.db`, operational |
| **Tests** | 9/9 passing |

### Files Modified in This Session

| File | Action |
|------|--------|
| `docs/SYSTEM_OVERVIEW.md` | Created (documentation) |
| `tests/test_system_health.py` | Created (test suite) |
| `tests/HEALTH_REPORT.md` | Created (test results) |
| `CONSOLIDATED_REPORT.md` | Created (this report) |
| `sovereign/calibrate_outer.py` | Fixed protocol version string |
| `.env` | Updated token and gateway URL |
| `openclaw/gateway.json` | Updated default model |
| `requirements.txt` | Added missing dependencies |
| `golden-path/verification/minimal-gateway.py` | Pydantic fix, logging tags, shutdown handler |
| `agents/llm_client.py` | Outer test in __main__, context window warning, explicit cleanup |
| `discord_bot/bot.py` | Removed unused import |

---

*Calibration, identity, system prompts, and routing logic were NOT modified.*
*Holding state.*
