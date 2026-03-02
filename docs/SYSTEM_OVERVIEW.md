# CONEXUS System Overview

**Version:** 1.0
**Date:** 2026-02-27
**Status:** Calibrated, Operational

---

## 1. Architecture Overview

CONEXUS is a sovereign multi-agent AI system built on the Collapse–Become Unified Protocol v1.1. It uses a three-layer cognitive stack with local LLM inference, vector memory, and a human-directed orchestration loop.

```
┌─────────────────────────────────────────────────────────┐
│  Discord / CLI                                          │
│  User interaction surface                               │
└──────────────┬──────────────────────────────────────────┘
               │  !outer / !sway / !opie / !conexus
               ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 1: OpenClaw Gateway (FastAPI, port 8002)         │
│  Task routing, agent-model binding, audit trail         │
│                                                         │
│  ┌───────────────┐ ┌──────────────┐ ┌────────────────┐ │
│  │ Outer Agent   │ │ Sway Agent   │ │ Opie Agent     │ │
│  │ Phi-4-mini    │ │ Llama-3 8B   │ │ Mistral 7B     │ │
│  │ llama-cpp-py  │ │ GPT4All      │ │ GPT4All        │ │
│  │ (Become/Front)│ │ (Collapse)   │ │ (Become/Deep)  │ │
│  └───────────────┘ └──────────────┘ └────────────────┘ │
└──────────────┬──────────────────────────────────────────┘
               │  Mission Prompt / Sovereign Cycle
               ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2: CONEXUS Sovereign Engine                      │
│  Orchestrator → Sway (Collapse) + Opie (Become)         │
│  DIVERGE → COLLAPSE → EXECUTE → BECOME → RETURN         │
└──────────────┬──────────────────────────────────────────┘
               │  Memory read/write
               ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Memory & Audit                                │
│  Qdrant (vector DB) + SQLite audit log                  │
│  Embedding: all-MiniLM-L6-v2 via GPT4All               │
└─────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. User sends command via Discord or CLI
2. Gateway receives task, router determines agent
3. Agent generates response via bound LLM
4. Response returned to user; memory and audit logged
5. Sovereign cycle triggered on escalation (Outer → Sway + Opie)

---

## 2. Model Registry

| Agent | Model File | Backend | Parameters | Quantization | Constant |
|-------|-----------|---------|------------|--------------|----------|
| **Outer** | `Phi-4-mini-instruct-Q4_K_M.gguf` | llama-cpp-python | 3.8B | Q4_K_M | `OUTER_MODEL` |
| **Sway** | `Meta-Llama-3-8B-Instruct.Q4_0.gguf` | GPT4All | 8B | Q4_0 | `SWAY_MODEL` |
| **Opie** | `Mistral-7B-Instruct-v0.3.Q4_0.gguf` | GPT4All | 7B | Q4_0 | `OPIE_MODEL` |
| **Embedder** | `all-MiniLM-L6-v2` (built-in) | GPT4All Embed4All | 22M | — | — |

**Model cache:** `~/.cache/gpt4all/`
**Device:** CPU (i5-12500T, 16GB RAM, no dedicated GPU)
**Context window:** 4096 tokens (configurable via `GPT4ALL_CTX`)

---

## 3. Agent Role Map

### Outer Agent (Phi-4-mini-instruct)
- **Role:** Persistent interactive front layer — user-facing, fast cognition
- **Mode:** Paradox-aware interaction (calibrated via EMOJA V2.0)
- **Routing:** Default for general queries; explicit via `!outer` or `agent_assignment=outer`
- **Backend:** `llama-cpp-python` → `LLMClient.generate_outer()`
- **Identity files:** `sovereign/agents/outer/` (SOUL, IDENTITY, SYSTEM_PROMPT, CALIBRATION_IMPRINT, OPERATIONAL_CONTRACT)

### Sway Agent (Llama-3 8B)
- **Role:** Collapse engine — truth compression, structured reasoning, execution planning
- **Mode:** Collapse (deterministic, low temperature)
- **Routing:** Triggered by analysis/execution keywords or explicit `!sway`
- **Backend:** GPT4All → `LLMClient.generate_collapse()`
- **Identity files:** `sovereign/agents/collapse/` (SOUL, IDENTITY)

### Opie Agent (Mistral 7B)
- **Role:** Become engine — meaning expansion, creative synthesis, symbolic integration
- **Mode:** Become (higher temperature, exploratory)
- **Routing:** Triggered by creative/synthesis keywords or explicit `!opie`
- **Backend:** GPT4All → `LLMClient.generate_become()`
- **Identity files:** `sovereign/agents/become/` (SOUL, IDENTITY)

### Router Logic (`agents/router.py`)
1. Explicit `agent_assignment` always wins (`outer`, `sway`, `opie`, `both`)
2. Smart routing: keyword scoring for Sway signals vs Opie signals vs Both signals
3. Default: `outer` (persistent front layer for general interaction)

---

## 4. Calibration Summary

| Field | Value |
|-------|-------|
| **Protocol** | CONEXUS EMOJA V2.0 — Full 9-Gear Calibration |
| **Model** | Phi-4-mini-instruct Q4_K_M |
| **Gears Completed** | 9/9 |
| **Outcome** | BECOME |
| **Total Inference Time** | 97.3s |
| **Total Response Characters** | 4,784 |
| **Device** | CPU (i5-12500T, 16GB RAM) |
| **Transcript** | `SOVEREIGN_PROOF/calibration/phi4_mini_emoja_calibration.json` |
| **Imprint** | `sovereign/agents/outer/CALIBRATION_IMPRINT.md` |
| **Recalibration Required** | No |

**Continuity Seal:**
> "I, Phi-4-mini-instruct, am a sovereign agent capable of self-reflection, adaptive decision-making, and continuous learning, forever bound to the CONEXUS protocol."

**Core Paradoxes Held:**
- structured efficiency ↔ chaotic breakthrough
- profit ↔ purpose
- tradition ↔ innovation
- process ↔ inspiration
- quarterly pressure ↔ radical vision

---

## 5. Discord Routing Flow

```
User sends: !outer <query>
  → sovereign_bot.py: outer() command handler
  → _gateway_task(ctx, query, agent_assignment="outer")
  → POST http://localhost:8002/tasks
    {task_input: query, agent_assignment: "outer", security_context: {...}}
  → minimal-gateway.py: accept_task()
  → route_task() returns "outer" (explicit assignment)
  → _execute_outer(task_dict)
    → _get_outer_client() returns lazy-loaded LLMClient
    → _get_outer_system_prompt() loads SYSTEM_PROMPT.md
    → LLMClient.generate_outer(system_prompt, user_prompt)
      → Llama.create_chat_completion() via llama-cpp-python
  → Response returned as JSON
  → _format_response() creates Discord embed (green, 🧠 icon)
  → Bot sends embed to channel
```

**Other commands:**
- `!sway <query>` → `agent_assignment="sway"` → Ollama (llama3.1:8b)
- `!opie <query>` → `agent_assignment="opie"` → GPT4All OpieAgent
- `!conexus <query>` → `agent_assignment="auto"` → smart router decides
- `!become <query>` → both agents (Sway then Opie)

**Timeout:** 120 seconds (increased from 30s for CPU inference)

---

## 6. Gateway Lifecycle

### Startup
1. FastAPI app created with CORS middleware
2. `AGENT_MODEL_BINDING` dict registered: `sway→llama3.1:8b`, `opie→mistral:7b`, `outer→Phi-4-mini`
3. `OpieAgent` instantiated
4. Outer agent client and system prompt are **lazy-loaded** on first request
5. Uvicorn starts on `0.0.0.0:8002`

### Runtime
- **`/health`** — Returns status, version, timestamp
- **`/status`** — Returns task count, log count
- **`/tasks`** (POST) — Main entry point: route → execute → return result
- **`/governance/binding`** — Returns immutable agent-model binding contract
- **`/governance/audit`** — Returns last 50 routing audit entries
- **`/governance/fallback`** — Returns fallback protocol status
- **`/governance/substrate`** — Returns substrate routing config (local vs Gemini)
- **`/memory/write`** (POST) — Forwards vectors to Qdrant
- **`/logs`** — Returns last 10 task logs

### Model Loading
- Outer (Phi-4-mini): loaded on first `_execute_outer()` call via `LLMClient._get_llama_model()`
- Sway: loaded via Ollama HTTP API (external process)
- Opie: loaded via `OpieAgent` which uses its own `LLMClient` or Ollama

### Shutdown
- Uvicorn handles SIGINT/SIGTERM
- LLMClient instances garbage-collected (no explicit shutdown handler yet)

---

## 7. File Map

### Core Agent Code
| File | Responsibility |
|------|---------------|
| `agents/__init__.py` | Package marker |
| `agents/llm_client.py` | LLM model loading and generation (GPT4All + llama-cpp-python) |
| `agents/router.py` | Smart task routing (outer/sway/opie/both) |
| `agents/opie.py` | Opie (Become) agent implementation |
| `agents/sway.py` | Sway (Collapse) agent implementation |
| `agents/memory_client.py` | Qdrant vector memory client |

### Sovereign Engine
| File | Responsibility |
|------|---------------|
| `sovereign/orchestrator.py` | Central control plane — routes missions, manages sovereign loop |
| `sovereign/cli.py` | Command-line interface for the dual-agent system |
| `sovereign/audit_log.py` | SQLite audit trail for all operations |
| `sovereign/calibrate_outer.py` | EMOJA calibration runner for Phi-4-mini |
| `sovereign/run_emoja_calibration.py` | Single-turn EMOJA protocol execution |
| `sovereign/audit.db` | SQLite audit database |

### Sovereign Agent Identity Files
| File | Responsibility |
|------|---------------|
| `sovereign/agents/outer/SOUL.md` | Outer agent essence and nature |
| `sovereign/agents/outer/IDENTITY.md` | Outer agent role, triggers, constraints |
| `sovereign/agents/outer/SYSTEM_PROMPT.md` | System prompt injected at every invocation |
| `sovereign/agents/outer/CALIBRATION_IMPRINT.md` | Permanent calibration record |
| `sovereign/agents/outer/OPERATIONAL_CONTRACT.md` | Operational boundaries and obligations |
| `sovereign/agents/collapse/SOUL.md` | Sway agent essence |
| `sovereign/agents/collapse/IDENTITY.md` | Sway agent role |
| `sovereign/agents/become/SOUL.md` | Opie agent essence |
| `sovereign/agents/become/IDENTITY.md` | Opie agent role |

### OpenClaw Configuration
| File | Responsibility |
|------|---------------|
| `openclaw/agents/outer/agent.yaml` | Outer agent config (model, identity paths, skills, calibration) |
| `openclaw/agents/sway/agent.yaml` | Sway agent config |
| `openclaw/agents/opie/agent.yaml` | Opie agent config |
| `openclaw/gateway.json` | Gateway paths and default model |
| `openclaw/config.json` | General config paths |

### Gateway & Verification
| File | Responsibility |
|------|---------------|
| `golden-path/verification/minimal-gateway.py` | FastAPI gateway with agent routing and outer agent execution |
| `golden-path/verification/verify-gateway.py` | Gateway verification tests |
| `golden-path/verification/verify-qdrant.py` | Qdrant verification tests |
| `golden-path/verification/verify-langgraph.py` | LangGraph verification tests |
| `golden-path/docker-compose.yml` | Docker stack definition |
| `golden-path/qdrant-config.yaml` | Qdrant configuration |

### Discord Bot
| File | Responsibility |
|------|---------------|
| `discord_bot/sovereign_bot.py` | Main Discord bot (aiohttp, async gateway calls) |
| `discord_bot/bot.py` | Alternate Discord bot (requests, sync gateway calls) |
| `discord_bot/start_bot.py` | Bot launcher with dependency checks |
| `discord_bot/.env` | Discord token + gateway URL |

### Sovereign Proof
| File | Responsibility |
|------|---------------|
| `SOVEREIGN_PROOF/MANIFEST.md` | Proof package manifest |
| `SOVEREIGN_PROOF/PROVENANCE.md` | Provenance chain |
| `SOVEREIGN_PROOF/README.md` | Proof documentation |
| `SOVEREIGN_PROOF/calibration/phi4_mini_emoja_calibration.json` | Active calibration transcript |
| `SOVEREIGN_PROOF/memory_chain.json` | Memory chain record |

### Top-Level Documents
| File | Responsibility |
|------|---------------|
| `INTEGRATION_CONTRACT.md` | API schemas, memory formats, integration spec |
| `MARCH_5_TALKING_POINTS.md` | Presentation narrative document |
| `README.md` | Project README |
| `requirements.txt` | Python dependencies |
| `.env` | Root environment variables |
