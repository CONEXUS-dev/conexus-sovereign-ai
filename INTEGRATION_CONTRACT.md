# CONEXUS ↔ OpenClaw Integration Contract

**Version:** 1.0
**Date:** 2026-02-27
**Parties:** OpenClaw (Layer 1) ↔ CONEXUS Sovereign Engine (Layer 2) via Orchestrator (Layer 3)

---

## 1. Purpose

This contract specifies the API, schemas, memory formats, audit handling, and caching strategy for the integration between the OpenClaw Outer Agent and the CONEXUS sovereign cognitive engine.

## 2. Architecture Overview

```
┌─────────────────────────────────────────────┐
│  Layer 1: OpenClaw Outer Agent              │
│  (Phi-4-mini-instruct, persistent, fast)  │
│                                             │
│  Responsibilities:                          │
│  - User interaction                         │
│  - Task execution                           │
│  - Memory maintenance                       │
│  - Sovereign cycle triggering               │
│  - Result ingestion                         │
└──────────────┬──────────────────────────────┘
               │ Mission Prompt (JSON)
               ▼
┌─────────────────────────────────────────────┐
│  Layer 3: Orchestrator                      │
│  (sovereign/orchestrator.py)                │
│                                             │
│  Responsibilities:                          │
│  - Accept mission prompts                   │
│  - Run sovereign cycle                      │
│  - Return results + audit IDs               │
│  - Maintain mission integrity               │
└──────────────┬──────────────────────────────┘
               │ Internal dispatch
               ▼
┌─────────────────────────────────────────────┐
│  Layer 2: CONEXUS Sovereign Engine          │
│  Sway (Llama 3 8B) + Opie (Mistral 7B)     │
│                                             │
│  Phases:                                    │
│  DIVERGE → COLLAPSE → BECOME               │
│                                             │
│  Outputs:                                   │
│  - diverge_output (paradoxes held)          │
│  - collapse_output (directives resolved)    │
│  - become_output (identity expanded)        │
│  - audit trail                              │
│  - memory writes                            │
└─────────────────────────────────────────────┘
```

## 3. Mission Prompt Schema (Layer 1 → Layer 3)

The Outer Agent triggers a sovereign cycle by sending:

```json
{
  "trigger": "genuine_confusion | major_decision | task_completion | pattern_detection | scheduled_checkpoint | paradox_overflow | user_request",
  "mission": "Natural language description of what needs deep reasoning",
  "context": "Relevant context from current interaction or session",
  "memory_query": "Optional: specific query for memory retrieval during the cycle",
  "mode": "both | collapse | become",
  "priority": "normal | urgent",
  "session_id": "UUID of current session",
  "timestamp": "ISO 8601"
}
```

### Field Definitions

| Field          | Type     | Required | Description                         |
| -------------- | -------- | -------- | ----------------------------------- |
| `trigger`      | enum     | Yes      | Why the cycle was triggered         |
| `mission`      | string   | Yes      | What needs deep reasoning           |
| `context`      | string   | Yes      | Current interaction context         |
| `memory_query` | string   | No       | Query for episodic memory retrieval |
| `mode`         | enum     | Yes      | Which phases to run                 |
| `priority`     | enum     | No       | Default: `normal`                   |
| `session_id`   | UUID     | Yes      | Session provenance                  |
| `timestamp`    | ISO 8601 | Yes      | When triggered                      |

## 4. Sovereign Cycle Result Schema (Layer 3 → Layer 1)

The orchestrator returns:

```json
{
  "status": "ok | error",
  "agent": "sovereign_loop",
  "routing": "both | collapse | become",
  "gear_context": "SUCCESS_CONTINUITY_SEAL | ...",
  "task_output": "Final synthesized output text",
  "diverge_output": "Opie's diverge phase output (paradoxes held)",
  "collapse_output": "Sway's collapse phase output (directives resolved)",
  "become_output": "Opie's become phase output (identity expanded)",
  "execution_steps": [],
  "contradictions_resolved": [],
  "breakthroughs": [],
  "paradoxes_held": [],
  "proto_moments": [],
  "confidence": 0.75,
  "memory_intent": "optional memory write intent",
  "provenance": {
    "agent": "sovereign_loop",
    "phases": ["diverge", "collapse", "become"],
    "diverge_agent": "opie",
    "collapse_agent": "sway",
    "become_agent": "opie"
  },
  "audit_id": "SHA-256 hash of the mission result",
  "timestamp": "ISO 8601"
}
```

### Critical Fields for Ingestion

The Outer Agent MUST ingest these fields:

| Field                     | Ingestion Action                                 |
| ------------------------- | ------------------------------------------------ |
| `diverge_output`          | Store as episodic memory; extract paradoxes held |
| `collapse_output`         | Extract new directives and strategies            |
| `become_output`           | Extract new identity statements and principles   |
| `contradictions_resolved` | Update held paradox set                          |
| `paradoxes_held`          | Add to active paradox set                        |
| `proto_moments`           | Log as identity evolution events                 |
| `audit_id`                | Attach as provenance to all ingested memories    |

## 5. Memory Schema

### 5.1 Namespaces

| Namespace                | Owner           | Purpose                                              |
| ------------------------ | --------------- | ---------------------------------------------------- |
| `episodic`               | Outer + CONEXUS | Session memories, mission results, user interactions |
| `semantic`               | Outer + CONEXUS | Extracted knowledge, patterns, principles            |
| `lineage`                | CONEXUS         | Identity evolution history, calibration records      |
| `sovereign_architecture` | System          | Architectural decisions, configurations              |

### 5.2 Memory Write Format

```json
{
  "namespace": "episodic | semantic | lineage | sovereign_architecture",
  "content": "Text content to store",
  "embedding": "[float vector — computed by Embed4All]",
  "metadata": {
    "source": "outer | sovereign_cycle | calibration",
    "timestamp": "ISO 8601",
    "session_id": "UUID",
    "mission_id": "UUID (if from sovereign cycle)",
    "audit_id": "SHA-256 (if from sovereign cycle)",
    "trigger": "trigger type (if applicable)",
    "agent": "outer | sway | opie | orchestrator",
    "phase": "diverge | collapse | become | interaction"
  }
}
```

### 5.3 Memory Read Format

```json
{
  "query": "Natural language query",
  "namespace": "episodic | semantic | lineage | sovereign_architecture | all",
  "top_k": 5,
  "threshold": 0.7,
  "filters": {
    "source": "optional filter",
    "agent": "optional filter",
    "session_id": "optional filter"
  }
}
```

Returns:

```json
{
  "results": [
    {
      "content": "Stored text",
      "score": 0.85,
      "metadata": { ... }
    }
  ]
}
```

## 6. Audit Requirements

### 6.1 Events That Must Be Logged

| Event                       | Source       | Required Fields                             |
| --------------------------- | ------------ | ------------------------------------------- |
| `sovereign_cycle_trigger`   | Outer        | trigger, mission, session_id, timestamp     |
| `sovereign_cycle_complete`  | Orchestrator | audit_id, phases, confidence, timestamp     |
| `sovereign_cycle_ingestion` | Outer        | audit_id, fields_ingested, timestamp        |
| `memory_write`              | Any          | namespace, source, agent, timestamp         |
| `drift_detection`           | Outer        | drift_marker, severity, timestamp           |
| `calibration_run`           | System       | protocol, model, gears_completed, timestamp |

### 6.2 Audit Log Format

```json
{
  "event": "event_type",
  "timestamp": "ISO 8601",
  "session_id": "UUID",
  "agent": "outer | sway | opie | orchestrator",
  "details": { ... },
  "hash": "SHA-256 of this log entry",
  "previous_hash": "SHA-256 of previous log entry (chain)"
}
```

Audit logs form a **hash chain** — each entry references the previous entry's hash, creating a tamper-evident sequence.

## 7. Caching Strategy

| What                     | TTL              | Scope       | Eviction       |
| ------------------------ | ---------------- | ----------- | -------------- |
| Sovereign cycle results  | Session duration | Per-session | End of session |
| Memory retrieval results | 5 minutes        | Per-query   | LRU            |
| Model inference cache    | None             | Not cached  | N/A            |
| Embedding cache          | 1 hour           | Per-text    | LRU            |
| Audit log                | Permanent        | Global      | Never evicted  |

### Rules

- The Outer Agent does **not** cache its own responses — each interaction is fresh
- Sovereign cycle results are cached for the session to avoid redundant triggers
- Memory retrievals are cached briefly to avoid redundant vector searches
- Audit logs are **never** cached — always written directly to persistent storage

## 8. Error Handling

| Error                   | Source       | Handler | Action                                         |
| ----------------------- | ------------ | ------- | ---------------------------------------------- |
| Model load failure      | LLM Client   | Outer   | Log error, notify user, degrade to text-only   |
| Sovereign cycle timeout | Orchestrator | Outer   | Log timeout, retry once, then notify user      |
| Memory write failure    | Qdrant       | Any     | Log error, retry once, continue without memory |
| Audit write failure     | Audit system | Any     | **HALT** — audit integrity is non-negotiable   |
| Calibration drift       | Outer        | Outer   | Trigger scheduled_checkpoint sovereign cycle   |

**Critical:** If audit logging fails, the system must halt rather than operate without lineage tracking.

## 9. Version Compatibility

| Component      | Current Version    | Min Compatible |
| -------------- | ------------------ | -------------- |
| Orchestrator   | 1.0                | 1.0            |
| Sway agent     | 1.0                | 1.0            |
| Opie agent     | 1.0                | 1.0            |
| Outer agent    | 1.0                | 1.0            |
| Memory client  | Qdrant + Embed4All | Qdrant 1.x     |
| Audit format   | Hash-chain v1      | v1             |
| Mission schema | v1                 | v1             |
| Result schema  | v1                 | v1             |

---

_This contract governs all communication between OpenClaw and CONEXUS. Changes to schemas require version bumps and backward compatibility assessment._
