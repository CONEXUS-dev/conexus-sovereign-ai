# VARGAS V3 — Comprehensive Guide

**Version:** 3.0  
**Build Date:** 2026-03-27  
**Test Status:** 141/141 V2 passed + 64/64 V3 passed = 205 total, zero regressions  
**Author:** Derek Angell + Cascade

---

## Table of Contents

- [VARGAS V3 — Comprehensive Guide](#vargas-v3--comprehensive-guide)
  - [Table of Contents](#table-of-contents)
  - [1. What Changed: V2 → V3](#1-what-changed-v2--v3)
    - [Summary of all V3 additions:](#summary-of-all-v3-additions)
  - [2. Architecture Overview](#2-architecture-overview)
  - [3. Model Configuration](#3-model-configuration)
  - [4. Phase 0: Qdrant Prerequisites](#4-phase-0-qdrant-prerequisites)
  - [5. Phase 1: Quick Wins](#5-phase-1-quick-wins)
    - [1A: Screenshot Upload](#1a-screenshot-upload)
    - [1B: Blanket Approval](#1b-blanket-approval)
    - [1C: DM Support](#1c-dm-support)
    - [1D: Audit Log Viewer](#1d-audit-log-viewer)
  - [6. Phase 2: Reliability](#6-phase-2-reliability)
    - [2A: Context Window Management](#2a-context-window-management)
    - [2B: Native Function Calling](#2b-native-function-calling)
    - [2C: Intent Classifier Upgrade](#2c-intent-classifier-upgrade)
    - [2D: Multi-Model Fallback](#2d-multi-model-fallback)
    - [2E: Memory Summarization](#2e-memory-summarization)
  - [7. Phase 3: New Capabilities](#7-phase-3-new-capabilities)
    - [3A: Voice Input](#3a-voice-input)
    - [3B: Streaming Responses](#3b-streaming-responses)
    - [3C: Persistent Browser](#3c-persistent-browser)
  - [8. Phase 4: Sovereign Integration](#8-phase-4-sovereign-integration)
    - [4A: Governance Bridge (`adapters/sovereign_bridge.py`)](#4a-governance-bridge-adapterssovereign_bridgepy)
    - [4B: Ambient Observer](#4b-ambient-observer)
  - [9. Phase 5: Cloud Deploy](#9-phase-5-cloud-deploy)
    - [Dockerfile](#dockerfile)
    - [render.yaml](#renderyaml)
    - [Qdrant Cloud](#qdrant-cloud)
  - [10. Intent Classification (V3 Additions)](#10-intent-classification-v3-additions)
  - [11. File Map (V3 New/Modified)](#11-file-map-v3-newmodified)
    - [New Files](#new-files)
    - [Modified Files](#modified-files)
  - [12. Configuration Reference](#12-configuration-reference)
  - [13. Environment Variables](#13-environment-variables)
  - [14. How to Test](#14-how-to-test)
  - [15. What V3 CAN Do](#15-what-v3-can-do)
  - [16. What V3 CANNOT Do Yet](#16-what-v3-cannot-do-yet)

---

## 1. What Changed: V2 → V3

**V1** was the mind: conversation, memory, web search, URL reading, OpenClaw skills, attunement.

**V2** was the body: browser automation, shell execution, file I/O, multi-step task planning.

**V3** is the nervous system: model optimization, context window management, multi-model fallback, native function calling, voice input, streaming, Sovereign governance awareness, memory compression, and cloud deploy readiness.

V3 is purely additive. Nothing from V1 or V2 was removed or degraded.

### Summary of all V3 additions:

| Phase | Task | Description |
|-------|------|-------------|
| 0 | Qdrant prereqs | Local runtime, health check, dev script |
| 1A | Screenshot upload | Attach screenshots from browser tool to Discord |
| 1B | Blanket approval | Natural language approval for tool actions |
| 1C | DM support | Use author ID as channel ID for DMs |
| 1D | Audit log viewer | Read and summarize log files on request |
| 2A | Context window | Token estimation + auto-trimming at 900K tokens |
| 2B | Native function calling | Gemini tool use API with tool declarations |
| 2C | Intent upgrade | LLM fallback for ambiguous intents |
| 2D | Multi-model fallback | Primary → fallback on API errors |
| 2E | Memory summarization | Compress old memories via LLM |
| 3A | Voice input | Whisper transcription of Discord audio messages |
| 3B | Streaming responses | `generate_stream()` for progressive output |
| 3C | Persistent browser | Session state tracking, auto-reconnect |
| 4A | Governance bridge | Read-only SovereignNEXT state access |
| 4B | Ambient observer | Sovereign health injected into every prompt |
| 5A | Cloud deploy | Dockerfile + render.yaml for Render |
| 5B | Discord tests | 64 V3-specific integration tests |

---

## 2. Architecture Overview

```
Discord Message
    │
    ▼
┌─────────────────────────────────────────────────┐
│  on_message (discord/bot.py)                    │
│  ├─ Downloads images, PDFs, text files          │
│  ├─ V3: Transcribes voice messages (Whisper)    │
│  ├─ V3: Supports DM channels                   │
│  ├─ V3: Blanket approval commands               │
│  ├─ V3: Attaches screenshots to replies         │
│  └─ Calls vargas.respond()                      │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  VargasAgent.respond() (vargas_agent.py)        │
│  ├─ 1. Classify intent (patterns + LLM fallback)│
│  ├─ 2. Handle memory / plans / tool contexts     │
│  ├─ 3. V3: Inject Sovereign health context      │
│  ├─ 4. V3: Context window management (trim)     │
│  ├─ 5. V3: Function calling OR standard gen     │
│  ├─ 6. Post-response memory + attunement        │
│  └─ 7. V3: Periodic memory summarization        │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  GeminiLLMClient (gemini_client.py)             │
│  ├─ Primary: gemini-3.1-pro-preview (1M ctx)   │
│  ├─ Fallback: gemini-2.5-pro (stable)          │
│  ├─ V3: generate_with_tools() — function calling│
│  ├─ V3: generate_stream() — streaming output    │
│  └─ V3: _call_with_retry_raw() — raw responses │
└──────────────┬──────────────────────────────────┘
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
   Sovereign  Qdrant  Tools
   Bridge     Memory  (Browser/Shell/File/Search)
```

---

## 3. Model Configuration

| Role | Model | Purpose |
|------|-------|---------|
| **Primary** | `gemini-3.1-pro-preview` | Highest-capability: 1M tokens, thinking, function calling |
| **Fallback** | `gemini-2.5-pro` | Stable deep reasoning, used on primary failure |
| **Lightweight** | `gemini-2.5-flash` | Intent classification fallback only |
| **Embedding** | `gemini-embedding-001` | Memory vector embeddings (3072-dim) |

Config-driven via `config/vargas_config.json`. The agent logs active model at startup:
```
[VARGAS] Model config — primary=gemini-3.1-pro-preview, fallback=gemini-2.5-pro, embedding=gemini-embedding-001
```

---

## 4. Phase 0: Qdrant Prerequisites

- Local Qdrant via Docker: `docker run -p 6333:6333 qdrant/qdrant`
- Health check in memory client: `VargasMemoryClient.health_check()`
- Dev script: `start_dev.ps1` spins up Qdrant + Discord bot

---

## 5. Phase 1: Quick Wins

### 1A: Screenshot Upload
When the agent loop takes browser screenshots, the Discord bot attaches them as files to the reply message.

### 1B: Blanket Approval
Users can type "blanket approve", "approve all", "yes to all" to auto-approve pending tool actions.

### 1C: DM Support
Discord DMs use `message.author.id` as the channel ID for conversation history and context.

### 1D: Audit Log Viewer
15 intent patterns detect audit log requests. Reads `tool_use.log`, `memory_writes.log`, `intent_log.log`, `attunement.log` and formats recent entries.

---

## 6. Phase 2: Reliability

### 2A: Context Window Management
- `_estimate_tokens()`: ~4 chars/token rough estimator
- Auto-trims conversation history and memory context if prompt exceeds 900K tokens
- Oldest messages trimmed first, memory truncated as last resort

### 2B: Native Function Calling
- `generate_with_tools()` on GeminiLLMClient sends tool declarations to Gemini
- Tool schemas built from available tools: web_search, url_read, browser, file, shell
- Gated behind `use_function_calling: true` in config (default: false)
- Function calls are executed via ToolExecutor, results injected, then regenerated

### 2C: Intent Classifier Upgrade
- LLM fallback for messages >15 chars that match no pattern
- Uses lightweight model for cost efficiency
- JSON-parsed response validated against VALID_INTENTS

### 2D: Multi-Model Fallback
- GeminiLLMClient accepts `fallback_model` parameter
- On primary model API failure, automatically retries with fallback
- Logged: `[GEMINI] primary model failed, trying fallback`

### 2E: Memory Summarization
- `summarize_collection()`: compresses old memories above threshold into LLM-generated summary
- `run_summarization_pass()`: runs across all 3 collections
- Triggered every 25 interactions (configurable via `max_memories_per_class`)
- Preserves 10 most recent entries, deletes compressed originals

---

## 7. Phase 3: New Capabilities

### 3A: Voice Input
- Detects audio attachments: `.ogg`, `.mp3`, `.wav`, `.m4a`, `.webm`, `.opus`
- Transcribes via OpenAI Whisper (`whisper-1` model)
- Requires `OPENAI_API_KEY` environment variable
- Transcribed text injected as `[VOICE MESSAGE — transcribed]: ...`

### 3B: Streaming Responses
- `generate_stream()` on GeminiLLMClient yields text chunks
- Uses `generate_content_stream` from google-genai SDK
- Ready for progressive Discord message editing (bot integration pending)

### 3C: Persistent Browser
- Session state tracked: `session_active`, `last_url`
- `ensure_session()` checks if browser is alive
- Session preserved across actions via `--session vargas` flag
- `close()` resets session state

---

## 8. Phase 4: Sovereign Integration

### 4A: Governance Bridge (`adapters/sovereign_bridge.py`)
- Read-only bridge to SovereignNEXT
- Loads sealed V5 baseline snapshot
- Runs Sovereign Observer for full reports
- Surfaces: health summary, seal metadata, state summary, governance contracts
- `format_for_prompt()` produces lightweight context string

### 4B: Ambient Observer
- Every response includes Sovereign health context in system prompt
- `sovereign_state` intent (20+ patterns) triggers full governance context injection
- Observer report includes: anomaly flags, attestations, veto summary, belief stratification

---

## 9. Phase 5: Cloud Deploy

### Dockerfile
- Python 3.12-slim base
- Installs requirements, copies project, runs Discord bot
- `PYTHONPATH=/app` for import resolution

### render.yaml
- Worker service (no web port needed for Discord bot)
- Environment variables: GEMINI_API_KEY, DISCORD_BOT_TOKEN, OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY

### Qdrant Cloud
- Config supports `qdrant_url` and `qdrant_api_key` for cloud Qdrant
- Falls back to localhost if not set

---

## 10. Intent Classification (V3 Additions)

| Intent | Patterns | Example |
|--------|----------|---------|
| `audit_log` | 15 patterns | "show me the audit logs", "what have you done" |
| `sovereign_state` | 20+ patterns | "sovereign health", "governance report", "anomaly flags" |
| LLM fallback | messages >15 chars, no pattern match | Uses lightweight model for disambiguation |

---

## 11. File Map (V3 New/Modified)

### New Files
- `adapters/sovereign_bridge.py` — Sovereign governance bridge
- `Dockerfile` — Container build for cloud deploy
- `render.yaml` — Render.com service config
- `test_vargas_v3.py` — 64 V3-specific tests

### Modified Files
- `config/vargas_config.json` — Added fallback_model, lightweight_model
- `adapters/cloud_llm/gemini_client.py` — fallback_model, generate_with_tools, generate_stream, _call_with_retry_raw
- `agent/vargas_agent.py` — Config-driven model init, sovereign bridge, function calling, memory summarization, context window
- `agent/intent_classifier.py` — sovereign_state intent, LLM fallback
- `discord/bot.py` — Voice transcription, DM support, blanket approval, screenshot attachment
- `memory/memory_client.py` — summarize_collection, run_summarization_pass
- `tools/browser.py` — Persistent session tracking
- `requirements.txt` — Added openai>=1.0.0
- `.env.example` — Added OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY

---

## 12. Configuration Reference

`config/vargas_config.json`:

```json
{
  "model": "gemini-3.1-pro-preview",
  "embedding_model": "gemini-embedding-001",
  "fallback_model": "gemini-2.5-pro",
  "lightweight_model": "gemini-2.5-flash",
  "temperature": 0.7,
  "max_tokens": 4096,
  "use_function_calling": false,
  "qdrant_url": "http://localhost:6333",
  "qdrant_api_key": null,
  "memory": {
    "max_memories_per_class": 100
  }
}
```

---

## 13. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `DISCORD_TOKEN` | Yes | Discord bot token |
| `GOOGLE_CSE_API_KEY` | For web search | Google Custom Search API key |
| `GOOGLE_CSE_ID` | For web search | Google Custom Search Engine ID |
| `OPENAI_API_KEY` | For voice | OpenAI API key (Whisper transcription) |
| `QDRANT_HOST` | No (default: localhost) | Qdrant host |
| `QDRANT_PORT` | No (default: 6333) | Qdrant port |
| `QDRANT_URL` | For cloud | Qdrant Cloud URL (overrides host/port) |
| `QDRANT_API_KEY` | For cloud | Qdrant Cloud API key |

---

## 14. How to Test

```powershell
# Run all V2 tests (141 tests)
python test_vargas_v2.py

# Run all V3 tests (64 tests)
python test_vargas_v3.py

# Both should report 0 failures
```

---

## 15. What V3 CAN Do

Everything V2 can do, plus:
- Use the highest-capability Gemini model with automatic fallback
- Manage context window to avoid exceeding 1M token limit
- Transcribe Discord voice messages via Whisper
- Compress old memories to keep collections lean
- Use native Gemini function calling (when enabled)
- Read SovereignNEXT governance state and surface reports
- Maintain persistent browser sessions across actions
- Stream LLM responses chunk-by-chunk
- Deploy to Render with Docker
- Classify ambiguous intents via LLM when patterns fail

---

## 16. What V3 CANNOT Do Yet

- **Streaming Discord edits**: `generate_stream()` exists but bot doesn't progressively edit messages yet
- **Multi-turn function calling**: Only single-round tool use currently
- **Voice output**: No TTS — only transcription input
- **Live Sovereign mutation**: Bridge is read-only by design
- **Cloud deploy**: Config ready but not yet deployed to Render
- **Memory stress test**: Summarization implemented but not stress-tested at scale
