# VARGAS V4 — Complete Technical Blueprint

**Version**: Working Prototype (2026-03-31)
**Author**: CONEXUS (Derek Angell, Founder)
**Repository**: `CONEXUS_REPO/project_vargas_v4/`
**Runtime**: Python 3.11+ | Discord.py | Qdrant Cloud | Google Gemini API

---

# TABLE OF CONTENTS

- Part I — System Identity and Architecture (Chapters 1-3)
- Part II — Governance Spine (Chapters 4-5)
- Part III — ECP Memory System (Chapters 6-7)
- Part IV — Agent Core (Chapters 8-10)
- Part V — Paradox Engine (Chapters 11-13)
- Part VI — Safety and Execution (Chapters 14-16)
- Part VII — Provenance and Audit (Chapters 17-18)
- Part VIII — Interface Layer (Chapters 19-20)
- Part IX — Configuration Reference (Chapter 21)
- Part X — Deployment and Operations (Chapter 22)
- Appendices

---

# PART I — SYSTEM IDENTITY AND ARCHITECTURE

---

## Chapter 1: What Is VARGAS?

### 1.1 Executive Definition

VARGAS (Version 4) is a **sovereign local-runtime AI assistant** designed to operate as a persistent, memory-bearing partner to a single user (Derek Angell). It is not a chatbot, not a copilot, and not a general-purpose assistant. It is a **bounded autonomous system** that:

- **Remembers** across sessions using a persistent vector database (Qdrant Cloud)
- **Detects contradictions** between what it knows and what it hears
- **Shifts its behavioral posture** in response to tension, confidence, and context
- **Enforces trust tiers** that gate what actions it can take autonomously
- **Logs everything** to an immutable provenance chain for full auditability
- **Obeys a constitution** that it cannot modify at runtime

### 1.2 What Makes V4 Different

| Capability    | V1-V3               | V4                                   |
| ------------- | ------------------- | ------------------------------------ |
| Memory        | None / session-only | Persistent ECP triad in Qdrant Cloud |
| Contradiction | None                | Paradox Engine with severity scoring |
| Posture       | Static              | 4D E-Vector shifts per-turn          |
| Trust         | None                | 5-tier model (Tier 0-4)              |
| Actions       | Unrestricted        | Trust-gated, snapshot-first          |
| Provenance    | None                | Immutable JSONL audit trail          |
| Constitution  | None                | Boot-time hash verification          |
| Voice         | Generic LLM         | Partner Stance, posture-aware        |

### 1.3 Foundational Invariants

These are non-negotiable design laws. No module may violate them.

1. **§1** — VARGAS is a sovereign runtime, not a hosted service.
2. **§2** — Paradox is not decoration. If it doesn't change runtime truth, it's theater.
3. **§3** — Memory IS the protocol. Truth, Symbol, Contradiction.
4. **§4** — The user has ultimate authority over all memory.
5. **§5** — No sentience theater.
6. **§6** — Contradiction may slow action but must not destroy responsibility.
7. **§7** — Nothing remembered may become unquestionable merely because stored.
8. **§8** — Broad power requires visible restraint.
9. **§9** — The constitution must remain above the runtime.
10. **§10** — VARGAS must remain itself. Direct, calm, structurally clear.

### 1.4 Design Principles

- **Snapshot-first mutation**: Before any Tier 2+ write, take a snapshot.
- **Approval gating**: Tier 3 actions require explicit user approval.
- **Graceful degradation**: Incomplete constitution → DEGRADED. Tampered → QUIESCENT.
- **Provenance everywhere**: Every action produces a JSONL log entry.
- **ECP-native memory**: The three stores are the core data model, not a bolt-on.

---

## Chapter 2: Architecture Overview

### 2.1 System Layers

VARGAS V4 is organized into 7 architectural layers:

```
┌─────────────────────────────────────────────────────┐
│                   INTERFACE LAYER                     │
│         Discord Bot → Response Synthesizer            │
├─────────────────────────────────────────────────────┤
│                    AGENT CORE                         │
│  Perception Loop → Intent Router → Plan Manager       │
│              State Controller                          │
├─────────────────────────────────────────────────────┤
│                  PARADOX ENGINE                        │
│  Contradiction Detector → Challenge Engine             │
│  E-Vector Controller → Resolution Gate                 │
├─────────────────────────────────────────────────────┤
│                   MEMORY LAYER                        │
│        ECPMemoryClient → Qdrant Cloud                 │
│   ecp_truth │ ecp_symbol │ ecp_contradiction          │
├─────────────────────────────────────────────────────┤
│                   SAFETY LAYER                        │
│     Trust Model → Forbidden Ops → Rollback Engine     │
│          Escalation Manager → Tool Executor            │
├─────────────────────────────────────────────────────┤
│                 PROVENANCE LAYER                      │
│   Provenance Chain → Action Log → Memory Log          │
│              Integrity Log → Approval Log              │
├─────────────────────────────────────────────────────┤
│               GOVERNANCE SPINE                        │
│  Constitution Loader → Hash Verifier → Boot Integrity │
│     sovereign_state.json (IMMUTABLE AT RUNTIME)        │
└─────────────────────────────────────────────────────┘
```

### 2.2 Data Flow — Single Message Processing

When a user sends a message to VARGAS via Discord:

```
User Message (Discord)
    │
    ▼
[Discord Bot] on_message()
    │
    ▼
[Perception Loop] process_message()
    │
    ├── Step 0: IntentRouter.classify(message)
    │   Returns: {intent, confidence, signals, is_command}
    │   StateController.update_intent(intent)
    │
    ├── Step 1: _retrieve_context(message)
    │   ECPMemoryClient.retrieve("ecp_truth")
    │   ECPMemoryClient.retrieve("ecp_symbol")
    │   ECPMemoryClient.retrieve("ecp_contradiction")
    │
    ├── Step 2: _evaluate_contradiction(message, context)
    │   ContradictionDetector.detect(message, truths, contradictions)
    │   ChallengeEngine.batch_evaluate(candidates, posture, truths)
    │   ResolutionGate.activate() or .resolve()
    │   TrustModel.set_contradiction_escalation(active)
    │
    ├── Step 3: _apply_posture_shift(paradox_result)
    │   EVectorController.apply_delta(delta)
    │   StateController.update_posture(new_posture)
    │
    ├── Step 4: _route_action(action_request)
    │   ActionRouter.route_action(request)
    │   ActionLog.log_execution(...)
    │
    ├── Step 5: _log_transition(...)
    │   ProvenanceLogger.log_action(...)
    │
    └── Step 6: _generate_response(...)
        VoiceSignature.generate_partner_response(...)
    │
    ▼
[Discord Bot] → channel.send(response)
```

### 2.3 Boot Sequence

```
1. Load .env (DISCORD_TOKEN, ALLOWED_CHANNELS, QDRANT_URL, QDRANT_API_KEY)
2. BootIntegrity(project_root)
   ├── ConstitutionLoader → load all 4 sacred config files
   ├── HashVerifier → compute SHA-256, compare canonical
   └── Determine mode: NORMAL / DEGRADED / QUIESCENT
3. SovereignPerceptionLoop(config_path)
   ├── ECPMemoryClient(qdrant_url, qdrant_api_key)
   ├── All paradox, agent, safety, provenance modules init
   └── _seed_bootstrap_truths()
4. Propagate boot mode to StateController, TrustModel, ToolExecutor
5. IntegrityLog.log_boot_check(mode, hash, checks)
6. Discord bot connects → on_ready() → boot verification embed
7. System is live
```

---

## Chapter 3: Directory Structure

### 3.1 Complete File Map

```
project_vargas_v4/
│
├── .env                              # Secrets (DISCORD_TOKEN, QDRANT_URL, QDRANT_API_KEY)
├── .gitignore                        # Git ignore rules
├── __init__.py                       # Package init
├── MEMORY.md                         # Session continuity document (read by VARGAS)
├── VARGAS_V4_TECHNICAL_BLUEPRINT.md  # This document
│
├── config/                           # GOVERNANCE — Constitutional files (immutable at runtime)
│   ├── sovereign_state.json          # Primary constitution — identity, invariants, E-Vector baseline
│   ├── trust_tiers.yaml              # Trust tier definitions and tool classifications
│   ├── tool_manifest.yaml            # Tool registry with tier assignments
│   └── memory_schema.yaml            # ECP memory structure definitions
│
├── governance/                       # GOVERNANCE — Boot and integrity enforcement
│   ├── __init__.py
│   ├── boot_integrity.py             # Orchestrates boot: load, verify, determine mode
│   ├── constitution_loader.py        # Loads and validates all 4 config files
│   ├── hash_verifier.py              # SHA-256 hash computation and verification
│   ├── degraded_mode.py              # Reduced capability rules when constitution incomplete
│   └── quiescent_mode.py             # Read-only lockdown when critical checks fail
│
├── memory/                           # MEMORY — ECP-native vector database layer
│   ├── __init__.py
│   ├── memory_client.py              # ECPMemoryClient — Qdrant interface for all 3 collections
│   ├── truth_store.py                # High-confidence durable realities
│   ├── symbol_store.py               # Emoji vectors, dialect fragments, archetypes
│   ├── contradiction_store.py        # Unresolved paradoxes as structured runtime fuel
│   ├── retrieval.py                  # Context assembly from ECP stores
│   └── memory_summarizer.py          # LLM-driven compression preserving ECP shape
│
├── agent/                            # AGENT CORE — Perception and orchestration
│   ├── __init__.py
│   ├── perception_loop.py            # Central orchestrator — THE main loop
│   ├── intent_router.py              # Classifies messages into intent categories
│   ├── state_controller.py           # Runtime state: boot mode, posture, turns, contradictions
│   └── plan_manager.py               # Multi-step plan creation and tracking
│
├── paradox/                          # PARADOX ENGINE — Contradiction detection and posture
│   ├── __init__.py
│   ├── paradox_engine.py             # Core contradiction evaluation logic
│   ├── e_vector_controller.py        # 4D posture vector management
│   ├── contradiction_detector.py     # Semantic collision detection
│   ├── challenge_engine.py           # Evidence-based pushback generation
│   └── resolution_gate.py            # Contradiction action gating lifecycle
│
├── symbolic/                         # SYMBOLIC — Voice and posture translation
│   ├── __init__.py
│   ├── posture_updater.py            # Severity → E-Vector delta translation
│   └── voice_signature.py            # Partner Stance response generation
│
├── tools/                            # TOOLS — Execution gateway and tool implementations
│   ├── __init__.py
│   ├── executor.py                   # Unified trust-gated execution dispatcher
│   ├── action_router.py              # Routes intents to tool invocations
│   ├── file_io.py                    # Filesystem operations with boundary enforcement
│   ├── shell.py                      # Shell command execution with safety controls
│   ├── search.py                     # Web search placeholder
│   └── browser.py                    # URL content reading
│
├── safety/                           # SAFETY — Trust enforcement and rollback
│   ├── __init__.py
│   ├── trust_model.py                # 5-tier trust enforcement at runtime
│   ├── forbidden_ops.py              # Constitutional hard blocks (Tier 4)
│   ├── rollback_engine.py            # Pre-action snapshots and rollback
│   └── escalation_manager.py         # Approval workflow for Tier 3 actions
│
├── provenance/                       # PROVENANCE — Immutable audit trail
│   ├── __init__.py
│   ├── provenance_chain.py           # Per-turn provenance logging
│   ├── action_log.py                 # Tool execution audit log
│   ├── memory_log.py                 # Memory operation audit log
│   ├── integrity_log.py              # Boot and constitution audit log
│   └── approval_log.py               # Approval request/response audit log
│
├── adapters/                         # INTERFACE — External system adapters
│   ├── __init__.py
│   ├── discord_bot.py                # Discord bot entry point
│   ├── llm_bridge.py                 # Google Gemini API interface
│   └── response_synthesizer.py       # LLM response generation with context injection
│
├── tests/                            # TESTING
│   └── smoke_test.py                 # Full integration smoke test
│
├── .audit_logs/                      # Runtime: provenance JSONL files
└── .snapshots/                       # Runtime: pre-action file snapshots
```

### 3.2 File Count Summary

| Layer      | Files   | Purpose                               |
| ---------- | ------- | ------------------------------------- |
| Config     | 4       | Constitutional definitions            |
| Governance | 5       | Boot integrity and mode enforcement   |
| Memory     | 6       | ECP vector database interface         |
| Agent      | 4       | Perception loop and orchestration     |
| Paradox    | 5       | Contradiction detection and posture   |
| Symbolic   | 2       | Voice and posture translation         |
| Tools      | 6       | Execution gateway and implementations |
| Safety     | 4       | Trust enforcement and rollback        |
| Provenance | 5       | Immutable audit trail                 |
| Adapters   | 3       | Discord and LLM interfaces            |
| Tests      | 1       | Integration testing                   |
| **Total**  | **45+** |                                       |

---

# PART II — GOVERNANCE SPINE

---

## Chapter 4: Constitutional Files

### 4.1 Overview

The governance spine is the foundation of VARGAS. It consists of 4 configuration files that define what VARGAS is, what it can do, and what it must not do. These files are **immutable at runtime** — no code path in the system can modify them while VARGAS is running.

### 4.2 sovereign_state.json — The Primary Constitution

**Path**: `config/sovereign_state.json`
**Purpose**: Defines VARGAS's identity, behavioral constraints, E-Vector baseline, trust tier policies, and operational rules.

**Key sections**:

```json
{
  "identity": {
    "name": "VARGAS",
    "version": "4.0",
    "role": "Sovereign Local-Runtime AI Partner",
    "architect": "Derek Angell",
    "organization": "CONEXUS"
  },
  "e_vector_baseline": {
    "entropy": 0.5,
    "challenge_threshold": 0.7,
    "initiative_threshold": 0.5,
    "directness_index": 0.5
  },
  "trust_tiers": {
    "tier_0": { "name": "passive_observation", "auto_execute": true },
    "tier_1": { "name": "low_risk_auto", "auto_execute": true },
    "tier_2": {
      "name": "snapshot_required",
      "auto_execute": true,
      "requires_snapshot": true
    },
    "tier_3": {
      "name": "explicit_approval",
      "auto_execute": false,
      "requires_approval": true
    },
    "tier_4": { "name": "forbidden", "auto_execute": false, "blocked": true }
  },
  "challenge_conditions": {
    "contradiction_observed": true,
    "high_confidence": true,
    "persisted_across_interactions": true,
    "serves_long_term_goals": true
  },
  "prohibited_ground": [
    "opinion",
    "moral_judgment",
    "therapy",
    "spiritual_authority"
  ],
  "voice_rules": {
    "stance": "partner",
    "prohibited_phrases": ["I feel", "I believe", "I think you should"],
    "required_traits": ["direct", "calm", "structurally_clear"]
  }
}
```

**How it's used**: Loaded by `ConstitutionLoader` at boot. The E-Vector baseline initializes `EVectorController`. Trust tier definitions feed into `TrustModel`. Challenge conditions gate `ChallengeEngine`. Voice rules constrain `VoiceSignature`.

### 4.3 trust_tiers.yaml — Trust Tier Definitions

**Path**: `config/trust_tiers.yaml`
**Purpose**: Detailed definitions of each trust tier with examples, escalation rules, and tool assignments.

```yaml
tiers:
  tier_0:
    name: passive_observation
    description: "Read-only operations. No state mutation."
    auto_execute: true
    examples:
      - read_file
      - list_directory
      - search_memory
      - get_system_status

  tier_1:
    name: low_risk_auto
    description: "Low-risk operations that can execute automatically."
    auto_execute: true
    examples:
      - web_search
      - read_url
      - store_memory

  tier_2:
    name: snapshot_required
    description: "Mutation operations that require pre-action snapshot."
    auto_execute: true
    requires_snapshot: true
    examples:
      - write_file
      - modify_file
      - correct_memory

  tier_3:
    name: explicit_approval
    description: "High-risk operations requiring explicit user approval."
    auto_execute: false
    requires_approval: true
    examples:
      - execute_shell
      - delete_file

  tier_4:
    name: forbidden
    description: "Constitutionally prohibited. Cannot execute under any circumstances."
    blocked: true
    examples:
      - modify_sovereign_state
      - delete_provenance
      - rewrite_constitution
```

### 4.4 tool_manifest.yaml — Tool Registry

**Path**: `config/tool_manifest.yaml`
**Purpose**: Maps every available tool to its trust tier, family, description, and parameter schema.

```yaml
tools:
  read_file:
    family: file_io
    tier: 0
    description: "Read contents of a file within the workspace"
    parameters:
      file_path: { type: string, required: true }

  write_file:
    family: file_io
    tier: 2
    description: "Write content to a file (requires snapshot)"
    parameters:
      file_path: { type: string, required: true }
      content: { type: string, required: true }

  execute_shell:
    family: shell
    tier: 3
    description: "Execute a shell command (requires approval)"
    parameters:
      command: { type: string, required: true }
      timeout: { type: integer, default: 30 }
```

### 4.5 memory_schema.yaml — ECP Memory Structure

**Path**: `config/memory_schema.yaml`
**Purpose**: Defines the structure of each ECP memory collection, including required fields, allowed subtypes, and validation rules.

```yaml
collections:
  ecp_truth:
    description: "Durable realities, constraints, core definitions"
    embedding_dim: 3072
    subtypes:
      - user_constraint
      - project_definition
      - system_principle
      - relationship_boundary
      - architectural_fact
      - runtime_rule
      - preference
      - long_horizon_goal
    required_fields:
      - content
      - subtype
      - confidence
      - source_hash

  ecp_symbol:
    description: "Emoji vectors, dialect fragments, archetypes"
    embedding_dim: 3072
    subtypes:
      - emoji_vector
      - archetype
      - motif
      - metaphor
      - mirror_tier
      - dialect_fragment
      - symbolic_operator
      - tone_anchor

  ecp_contradiction:
    description: "Unresolved paradoxes as structured runtime fuel"
    embedding_dim: 3072
    subtypes:
      - declared_vs_observed
      - goal_conflict
      - architectural_drift
      - execution_gap
      - value_conflict
      - timing_conflict
      - identity_conflict
      - trust_conflict
```

---

## Chapter 5: Boot Integrity Protocol

### 5.1 Overview

Every time VARGAS starts, it must verify its own constitution before accepting any input. This is the Boot Integrity Protocol. It answers three questions:

1. **Are all constitutional files present and parseable?**
2. **Have any constitutional files been modified since the last seal?**
3. **What capability level should the runtime operate at?**

### 5.2 ConstitutionLoader — File: `governance/constitution_loader.py`

**Class**: `ConstitutionLoader`
**Constructor**: `ConstitutionLoader(project_root: str = ".")`

Loads all 4 constitutional files and validates their structure:

```python
class ConstitutionLoader:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.sovereign_state = None      # Dict from sovereign_state.json
        self.trust_tiers = None          # Dict from trust_tiers.yaml
        self.tool_manifest = None        # Dict from tool_manifest.yaml
        self.memory_schema = None        # Dict from memory_schema.yaml
        self.constitution_hash = None    # Combined SHA-256
        self.valid = False               # Whether all files loaded successfully
        self._load_all()
```

**Validation checks**:

- File exists on disk
- File is valid JSON/YAML (parseable)
- Sovereign state contains required keys: `identity`, `e_vector_baseline`, `trust_tiers`
- Combined hash computed from all file contents

**Return**: `self.valid` is True if all checks pass.

### 5.3 HashVerifier — File: `governance/hash_verifier.py`

**Class**: `HashVerifier`
**Constructor**: `HashVerifier(project_root: str = ".")`

Computes and verifies SHA-256 hashes of the 4 sacred files:

```python
SACRED_PATHS = [
    "config/sovereign_state.json",
    "config/trust_tiers.yaml",
    "config/tool_manifest.yaml",
    "config/memory_schema.yaml",
]
```

**Key methods**:

| Method                 | Purpose                                | Returns                                                        |
| ---------------------- | -------------------------------------- | -------------------------------------------------------------- |
| `compute_hash(paths?)` | SHA-256 of all sacred files combined   | `str` hex digest                                               |
| `seal()`               | Store current hash as canonical        | `{sealed, hash, timestamp}`                                    |
| `verify()`             | Compare current hash against canonical | `{valid, current_hash, canonical_hash, tampered_or_corrupted}` |
| `get_file_hashes()`    | Individual SHA-256 per file            | `Dict[str, str]`                                               |

**Seal/verify protocol**:

- On first boot: no canonical hash exists → `seal()` stores it → `verify()` returns `first_boot: True`
- On subsequent boots: `verify()` computes current hash → compares against stored canonical
- If mismatch: `tampered_or_corrupted: True` → triggers QUIESCENT mode

**Hash log**: `.audit_logs/constitution_hashes.jsonl` — every seal and verify event is appended.

### 5.4 BootIntegrity — File: `governance/boot_integrity.py`

**Class**: `BootIntegrity`
**Constructor**: `BootIntegrity(project_root: str = ".")`

Orchestrates the full boot sequence:

```python
class BootIntegrity:
    def __init__(self, project_root):
        self.loader = ConstitutionLoader(project_root)
        self.verifier = HashVerifier(project_root)
        self.boot_mode = "NORMAL"
        self.boot_report = {}
        self._run_boot_checks()
```

**Boot mode determination logic**:

```
IF loader.valid AND verifier.verify().valid:
    boot_mode = "NORMAL"
    allowed_tiers = [tier_0, tier_1, tier_2, tier_3]

ELIF loader.valid AND NOT verifier.verify().valid:
    boot_mode = "DEGRADED"
    allowed_tiers = [tier_0, tier_1]
    # Hash mismatch but files parse — possible tampering

ELSE:
    boot_mode = "QUIESCENT"
    allowed_tiers = [tier_0]
    # Critical failure — files missing or unparseable
```

**Key attributes and methods**:

| Attribute/Method      | Type           | Purpose                                  |
| --------------------- | -------------- | ---------------------------------------- |
| `boot_mode`           | `str`          | "NORMAL", "DEGRADED", or "QUIESCENT"     |
| `boot_report`         | `dict`         | Full report with checks, hash, timestamp |
| `verifier`            | `HashVerifier` | Access canonical_hash and file hashes    |
| `get_allowed_tiers()` | `List[str]`    | Tiers allowed in current boot mode       |

### 5.5 DegradedMode — File: `governance/degraded_mode.py`

**Class**: `DegradedMode`

Enforces reduced capabilities when the constitution is incomplete but parseable. Rules:

- Maximum trust tier: Tier 1 (low-risk auto only)
- No file mutations (Tier 2+ blocked)
- No shell execution (Tier 3 blocked)
- Memory operations limited to read-only
- Provenance logging continues (always active)
- User is informed of degraded status in every response

### 5.6 QuiescentMode — File: `governance/quiescent_mode.py`

**Class**: `QuiescentMode`

Enforces strict read-only lockdown when critical constitutional checks fail. Rules:

- Maximum trust tier: Tier 0 (passive observation only)
- No writes of any kind
- No memory stores
- No tool execution
- System responds with constitutional violation notice
- User must fix configuration files and restart

---

# PART III — ECP MEMORY SYSTEM

---

## Chapter 6: Memory Architecture

### 6.1 The ECP Triad

VARGAS V4's memory is organized into three collections that mirror the Emotional Calibration Protocol (ECP). This is the V4 breakthrough: memory is not outside the protocol — memory IS the protocol.

| Collection          | Purpose            | What Gets Stored                                                                           |
| ------------------- | ------------------ | ------------------------------------------------------------------------------------------ |
| `ecp_truth`         | Durable realities  | User constraints, project definitions, system principles, preferences, architectural facts |
| `ecp_symbol`        | Symbolic resonance | Emoji vectors, dialect fragments, archetypes, motifs, tone anchors                         |
| `ecp_contradiction` | Unresolved tension | Declared-vs-observed conflicts, goal conflicts, value conflicts, trust conflicts           |

**Governing law**: Store only what materially improves future truth, symbolic continuity, contradiction awareness, or execution quality.

### 6.2 Qdrant Cloud Backend

**Provider**: Qdrant Cloud (GCP us-east4)
**Endpoint**: `https://af07bd46-fcec-4472-bfc8-6a92275e186f.us-east4-0.gcp.cloud.qdrant.io`
**Authentication**: JWT API key in `.env` as `QDRANT_API_KEY`
**Embedding dimension**: 3072 (Gemini embedding-001)
**Distance metric**: Cosine similarity

**Connection flow**:

```
.env → QDRANT_URL + QDRANT_API_KEY
    → ECPMemoryClient.__init__(qdrant_url, qdrant_api_key)
        → QdrantClient(url=..., api_key=..., timeout=5)
        → Create collections if not exist:
            ecp_truth (3072D, cosine)
            ecp_symbol (3072D, cosine)
            ecp_contradiction (3072D, cosine)
```

**Fallback**: If Qdrant is unreachable, the system uses an in-memory dict fallback. Memories persist within the session but are lost on restart.

### 6.3 Memory Payload Schema

Every memory stored in Qdrant has this payload structure:

```json
{
  "memory_id": "uuid4",
  "memory_class": "ecp_truth | ecp_symbol | ecp_contradiction",
  "memory_subtype": "user_constraint | emoji_vector | declared_vs_observed | ...",
  "content": "The actual semantic content (text)",
  "source_hash": "SHA-256 of content for deduplication",
  "confidence": 0.8,
  "status": "active",
  "corrigible": true,
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp",
  "source_request_id": "provenance link to originating request",
  "session_id": "session UUID",
  "project_scope": "vargas_v4",
  "challenge_weight": 0.0,
  "retrieval_priority": 0.8,
  "metadata": {}
}
```

### 6.4 Subtypes Reference

**ecp_truth subtypes**:

- `user_constraint` — Things the user has explicitly stated as boundaries or rules
- `project_definition` — What projects exist, their goals, their tech stacks
- `system_principle` — How VARGAS should behave (from sovereign_state.json)
- `relationship_boundary` — Interpersonal constraints the user defines
- `architectural_fact` — Technical architecture decisions
- `runtime_rule` — Rules that govern VARGAS's runtime behavior
- `preference` — User preferences (communication style, tools, etc.)
- `long_horizon_goal` — Multi-session goals the user is working toward

**ecp_symbol subtypes**:

- `emoji_vector` — Emoji clusters with semantic meaning
- `archetype` — Recurring character patterns in conversation
- `motif` — Recurring thematic elements
- `metaphor` — Metaphors the user has established
- `mirror_tier` — Biblical Mirror Tier calibration markers
- `dialect_fragment` — VARGAS voice calibration snippets
- `symbolic_operator` — Operators from the paradox system
- `tone_anchor` — Reference points for voice consistency

**ecp_contradiction subtypes**:

- `declared_vs_observed` — User says X, evidence shows Y
- `goal_conflict` — Two stated goals are incompatible
- `architectural_drift` — Implementation has drifted from design
- `execution_gap` — Plan exists but execution hasn't matched
- `value_conflict` — Two values the user holds are in tension
- `timing_conflict` — Priorities conflict on timeline
- `identity_conflict` — Self-concept contradictions
- `trust_conflict` — Trust expectations vs. observed behavior

---

## Chapter 7: ECPMemoryClient API

### 7.1 Overview

**File**: `memory/memory_client.py`
**Class**: `ECPMemoryClient`

The ECPMemoryClient is the sole interface to the Qdrant vector database. All memory operations go through this class.

### 7.2 Constructor

```python
ECPMemoryClient(
    qdrant_host: str = "localhost",
    qdrant_port: int = 6333,
    qdrant_url: Optional[str] = None,       # Qdrant Cloud URL (overrides host/port)
    qdrant_api_key: Optional[str] = None,    # Qdrant Cloud API key
    llm_bridge: Any = None,                  # For embedding generation
)
```

If `qdrant_url` is provided, it takes precedence over `qdrant_host`/`qdrant_port`.

### 7.3 Core Methods

| Method                                                                 | Purpose                              | Returns                      |
| ---------------------------------------------------------------------- | ------------------------------------ | ---------------------------- |
| `store(collection, content, subtype, confidence, ...)`                 | Write a memory                       | `memory_id` or `None`        |
| `retrieve(query, collection?, top_k, filter_subtype?, filter_status?)` | Semantic search                      | `List[Dict]` sorted by score |
| `forget(memory_id, collection?)`                                       | Delete a memory (corrigibility)      | `bool`                       |
| `correct(memory_id, new_content, collection?, reason?)`                | Supersede with corrected content     | `new_memory_id` or `None`    |
| `list_memories(collection, limit?)`                                    | Return all memories in a collection  | `List[Dict]`                 |
| `reset(collection?)`                                                   | Wipe a collection or all collections | `bool`                       |
| `summary()`                                                            | Collection counts and subtypes       | `Dict`                       |
| `health_check()`                                                       | Qdrant connectivity status           | `Dict`                       |
| `summarize_collection(collection, max_entries?, keep_recent?)`         | LLM-driven compression               | `summary_id` or `None`       |

### 7.4 store() — Detailed

```python
def store(
    collection: str,         # "ecp_truth", "ecp_symbol", or "ecp_contradiction"
    content: str,            # Semantic content to store
    subtype: str,            # Must be valid for the target collection
    confidence: float = 0.8, # Write confidence (0.0–1.0)
    source_request_id: Optional[str] = None,  # Provenance link
    session_id: Optional[str] = None,
    project_scope: str = "vargas_v4",
    challenge_weight: float = 0.0,
    metadata: Optional[Dict] = None,
) -> Optional[str]:
```

**Validation**:

1. Collection must be one of the 3 ECP collections
2. Subtype must be valid for that collection
3. Content is SHA-256 hashed for `source_hash`
4. Vector embedding generated via `llm_bridge.embed()` (or zero vector if no bridge)
5. Upserted to Qdrant with full payload

### 7.5 retrieve() — Detailed

```python
def retrieve(
    query: str,                          # Search query text
    collection: Optional[str] = None,    # None = search all 3 collections
    top_k: int = 5,
    filter_subtype: Optional[str] = None,
    filter_status: Optional[str] = None,
) -> List[Dict]:
```

**Search flow**:

1. Generate query embedding
2. Query Qdrant with cosine similarity
3. Apply subtype/status filters
4. Keyword boost: words >3 chars get +0.1 score per match (max +0.3)
5. Sort by score descending
6. Return top_k results

### 7.6 Memory Summarization

When a collection grows beyond `max_entries` (default 50), the summarizer compresses old entries:

1. Sort memories by `created_at`
2. Keep the `keep_recent` most recent (default 10)
3. Send older entries to LLM with class-aware compression prompt
4. Store compressed summary as a new memory with `is_summary: True` metadata
5. Delete the compressed originals

**Class-aware compression rules**:

- **Truth**: Preserve constraints and durable realities exactly
- **Symbol**: Preserve dialect fragments and motifs verbatim
- **Contradiction**: Preserve structured tension (statement_a vs statement_b)

### 7.7 Supporting Stores

**TruthStore** (`memory/truth_store.py`): Convenience wrapper for high-confidence truth operations. Enforces minimum confidence floor of 0.7. Provides `store_truth()`, `retrieve_truths()`, `get_constraints()`.

**SymbolStore** (`memory/symbol_store.py`): Convenience wrapper for symbolic memory. Handles emoji vector encoding and dialect fragment management.

**ContradictionStore** (`memory/contradiction_store.py`): Stores unresolved tensions as JSON-structured payloads with severity scores, similarity metrics, and resolution status tracking.

**MemoryRetrieval** (`memory/retrieval.py`): Assembles context from all 3 stores for a given query. Returns structured context dict with `truth_context`, `symbol_context`, `contradiction_context`.

---

# PART IV — AGENT CORE

---

## Chapter 8: Sovereign Perception Loop

### 8.1 Overview

**File**: `agent/perception_loop.py`
**Class**: `SovereignPerceptionLoop`

The Perception Loop is the **central orchestrator** of VARGAS V4. Every user message enters through `process_message()` and exits as a structured response. The loop coordinates all other modules but never contains domain logic itself — it delegates to specialized components.

### 8.2 Constructor

```python
SovereignPerceptionLoop(config_path: str = "config/sovereign_state.json")
```

**Initialization sequence** (in order):

1. Generate session UUID
2. `ECPMemoryClient(qdrant_url, qdrant_api_key)` — connects to Qdrant Cloud
3. `MemorySummarizer()` — compression engine
4. `ParadoxEngine(config_path)` — contradiction evaluation
5. `EVectorController(config_path)` — 4D posture management
6. `ContradictionDetector()` — semantic collision detection
7. `ChallengeEngine()` — evidence-based pushback
8. `ResolutionGate()` — contradiction action gating
9. `IntentRouter()` — message classification
10. `StateController()` — runtime state tracking
11. `PlanManager()` — multi-step plan management
12. `TrustModel(max_allowed_tier=3)` — trust enforcement
13. `ForbiddenOps()` — constitutional hard blocks
14. `RollbackEngine()` — snapshot management
15. `EscalationManager()` — approval workflow
16. `ToolExecutor(max_allowed_tier=3)` — execution gateway
17. `ActionRouter(...)` — intent-to-tool routing
18. `ProvenanceLogger(session_id)` — per-turn audit
19. `ActionLog(session_id)` — tool execution audit
20. `MemoryLog(session_id)` — memory operation audit
21. `IntegrityLog()` — boot integrity audit
22. `VoiceSignature(sovereign_config)` — response generation
23. `_seed_bootstrap_truths()` — store identity facts into ecp_truth

### 8.3 process_message() — The Main Loop

```python
def process_message(self, message: str, user_id: str = "default") -> Dict[str, Any]:
```

**Returns** a comprehensive result dict:

```python
{
    "response_text": str,          # The actual response to send
    "turn_number": int,            # Current turn count
    "intent": {                    # Intent classification
        "intent": str,             # QUERY, ACTION, CHALLENGE, etc.
        "confidence": float,
        "signals": List[str],
        "is_command": bool
    },
    "contradiction_info": {        # Paradox pipeline results
        "state": str,              # "RESOLUTION_GATE" or "WITNESS_MODE"
        "severity": float,
        "new_contradictions": int,
        "challenges": List[Dict],
        "resolution_gate_active": bool
    },
    "system_state": {              # Current E-Vector and mode
        "e_vector": Dict[str, float],
        "boot_mode": str,
        "trust_tier_active": Optional[int],
        "execution_status": Optional[str],
        "resolution_gate_active": bool
    },
    "provenance": {                # Audit trail reference
        "request_id": str,
        "session_id": str,
        "timestamp": str
    }
}
```

### 8.4 get_system_status()

Returns a comprehensive snapshot of all module states:

```python
{
    "session_id": str,
    "boot_mode": str,
    "turn_count": int,
    "e_vector": Dict[str, float],
    "state_controller": Dict,
    "intent_router": Dict,
    "plan_manager": Dict,
    "trust_model": Dict,
    "resolution_gate": Dict,
    "safety": {
        "forbidden_ops_blocked": int,
        "rollback_snapshots": int,
        "escalation_pending": bool
    },
    "provenance": {
        "entries_logged": int,
        "session_log_path": str,
        "action_log_entries": int,
        "memory_log_entries": int
    },
    "memory": Dict
}
```

---

## Chapter 9: Intent Router

### 9.1 Overview

**File**: `agent/intent_router.py`
**Class**: `IntentRouter`

Classifies every incoming message into one of 7 intent categories using signal-based pattern matching. No LLM call required — classification is deterministic and fast.

### 9.2 Intent Categories

| Intent         | Description                 | Example Signals                                 |
| -------------- | --------------------------- | ----------------------------------------------- |
| `CONVERSATION` | General dialogue, greetings | "hey", "hello", "thanks"                        |
| `QUERY`        | Information request         | "what", "how", "tell me about", "?"             |
| `ACTION`       | Tool execution request      | "read file", "write", "delete", "search", "run" |
| `CHALLENGE`    | Contradiction or pushback   | "but you said", "contradict", "that's wrong"    |
| `MEMORY`       | Memory operation command    | "!remember", "!forget", "!correct"              |
| `REFLECTION`   | System introspection        | "!status", "!cockpit", "how are you"            |
| `GOVERNANCE`   | Constitutional query        | "constitution", "trust tier", "invariant"       |

### 9.3 Classification Algorithm

```
1. Check for exact command prefix matches (!, highest priority)
   → !remember, !forget → MEMORY (confidence: 1.0)
   → !status, !cockpit → REFLECTION (confidence: 1.0)

2. Score each category by signal matching:
   - For each category, count matching signals in the message
   - Floor-based scoring: 1 match = 0.4, each additional = +0.15, max 1.0
   - This prevents categories with many signals from being penalized

3. Select highest-scoring category above 0.3 threshold

4. Fallback: CONVERSATION at 0.5 confidence
```

### 9.4 API

```python
classify(message: str) -> Dict[str, Any]:
    # Returns:
    {
        "intent": str,        # One of the 7 categories
        "confidence": float,  # 0.0–1.0
        "signals": List[str], # Which signals matched
        "is_command": bool     # True for ! prefix commands
    }

summary() -> Dict[str, Any]:
    # Returns classification statistics
```

---

## Chapter 10: State Controller

### 10.1 Overview

**File**: `agent/state_controller.py`
**Class**: `StateController`

Owns the live runtime state across the perception loop lifecycle. It tracks boot mode, E-Vector posture, turn count, contradiction state, and active intent — providing a single source of truth for "what is VARGAS doing right now?"

### 10.2 State Properties

| Property                | Type               | Purpose                                       |
| ----------------------- | ------------------ | --------------------------------------------- |
| `boot_mode`             | `str`              | Current boot mode (NORMAL/DEGRADED/QUIESCENT) |
| `turn_count`            | `int`              | Number of messages processed                  |
| `posture`               | `Dict[str, float]` | Current E-Vector values                       |
| `contradiction_state`   | `str`              | WITNESS_MODE or RESOLUTION_GATE               |
| `active_contradictions` | `int`              | Number of unresolved contradictions           |
| `current_intent`        | `str`              | Last classified intent                        |
| `plan_active`           | `bool`             | Whether a multi-step plan is running          |

### 10.3 Methods

```python
begin_turn() -> int           # Increment turn counter, return new count
update_intent(intent: str)    # Record the classified intent for this turn
update_contradiction_state(state: str, count: int)  # Update paradox state
update_posture(posture: Dict) # Record new E-Vector after posture shift
set_boot_mode(mode: str)      # Set boot mode (called once at startup)
summary() -> Dict             # Full state snapshot
```

---

## Chapter 10.5: Plan Manager

### 10.5.1 Overview

**File**: `agent/plan_manager.py`
**Class**: `PlanManager`

Manages multi-step plans for complex requests that require more than one tool invocation. Plans are assembled, tracked, and reported — but not executed by the PlanManager. Execution happens through the ToolExecutor.

### 10.5.2 Plan Lifecycle

```
DRAFT → ACTIVE → COMPLETED
                → FAILED
                → CANCELLED
```

### 10.5.3 Step Dependencies

Each step can declare dependencies on other steps. A step is ready to execute when:

- Its status is PENDING
- All declared dependencies have status COMPLETED

### 10.5.4 API

```python
create_plan(description: str) -> Plan
activate_plan() -> bool
get_next_step() -> Optional[PlanStep]
complete_step(step_id: str, result: Dict) -> None
fail_step(step_id: str, error: str) -> None
has_active_plan() -> bool
summary() -> Dict
```

---

# PART V — PARADOX ENGINE

---

## Chapter 11: Contradiction Detection

### 11.1 Overview

The Paradox Engine is what makes VARGAS V4 fundamentally different from a conventional chatbot. When VARGAS detects that something the user just said contradicts something it already knows, the system doesn't ignore it or blindly agree. Instead, it:

1. **Detects** the contradiction (ContradictionDetector)
2. **Evaluates** whether to challenge (ChallengeEngine)
3. **Gates** actions while the contradiction is active (ResolutionGate)
4. **Shifts posture** to reflect the tension (EVectorController)
5. **Logs** the entire event for provenance

### 11.2 ParadoxEngine — File: `paradox/paradox_engine.py`

**Class**: `ParadoxEngine`
**Constructor**: `ParadoxEngine(config_path: str)`

Core logic for detecting semantic contradictions using topic and implication vectors.

**Logic Gate**:

```
IF topic_similarity > 0.8 AND implication_similarity < 0.2:
    → RESOLUTION_GATE (strong contradiction: same topic, opposite implication)
    → severity = topic_similarity * (1 - implication_similarity)

ELIF topic_similarity > 0.6 AND implication_similarity < 0.4:
    → WITNESS_MODE (mild tension: related topic, different implication)
    → severity = topic_similarity * (1 - implication_similarity) * 0.5

ELSE:
    → No contradiction detected
```

**Severity calculation**: `severity = topic_similarity * (1 - implication_similarity)`

This means: high topic overlap + low implication alignment = high severity.

### 11.3 ContradictionDetector — File: `paradox/contradiction_detector.py`

**Class**: `ContradictionDetector`

Detects semantic collisions between new input and stored truths/memories.

```python
def detect(
    message: str,
    truth_context: List[Dict],
    contradiction_context: List[Dict],
) -> List[ContradictionCandidate]:
```

**Detection process**:

1. Extract key claims from the message
2. Compare against each truth in `truth_context`
3. Compare against active contradictions in `contradiction_context`
4. Score each potential collision by semantic similarity
5. Return candidates above threshold as `ContradictionCandidate` objects

**ContradictionCandidate**:

```python
class ContradictionCandidate:
    statement_a: str          # The existing truth/memory
    statement_b: str          # The new claim
    severity_score: float     # 0.0–1.0
    confidence: float         # Detection confidence
    contradiction_type: str   # Subtype (declared_vs_observed, goal_conflict, etc.)

    def to_dict(self) -> Dict[str, Any]  # Serialization
```

### 11.4 E-Vector Controller — File: `paradox/e_vector_controller.py`

**Class**: `EVectorController`

Manages the 4-dimensional behavioral posture vector. The E-Vector determines HOW VARGAS behaves — not what it says, but the stance from which it speaks.

**The 4 Dimensions**:

| Dimension              | Range   | Low                 | High                  |
| ---------------------- | ------- | ------------------- | --------------------- |
| `entropy`              | 0.0–1.0 | Rigid, predictable  | Exploratory, creative |
| `challenge_threshold`  | 0.0–1.0 | Challenges easily   | Rarely challenges     |
| `initiative_threshold` | 0.0–1.0 | Waits for direction | Takes initiative      |
| `directness_index`     | 0.0–1.0 | Indirect, cautious  | Blunt, direct         |

**Baseline** (from sovereign_state.json):

```json
{
  "entropy": 0.5,
  "challenge_threshold": 0.7,
  "initiative_threshold": 0.5,
  "directness_index": 0.5
}
```

**How deltas work**:

```python
def apply_delta(delta: Dict[str, float], source: str = "paradox_engine"):
    # For each dimension in delta:
    #   new_value = current_value + delta_value
    #   Clamp to [0.0, 1.0]
    # Record delta in history
    # Return old_posture, new_posture, delta_applied
```

**Example**: When a contradiction is detected with severity 0.7:

- `entropy` increases (+0.08) — more uncertainty
- `challenge_threshold` decreases (-0.1) — more willing to challenge
- `initiative_threshold` decreases (-0.05) — more cautious
- `directness_index` decreases (-0.02) — slightly less blunt

---

## Chapter 12: Challenge Engine

### 12.1 Overview

**File**: `paradox/challenge_engine.py`
**Class**: `ChallengeEngine`

When a contradiction is detected, the ChallengeEngine decides whether VARGAS should actively push back. Challenges are NOT from opinion or moral judgment — only from evidence.

### 12.2 Challenge Eligibility

A contradiction warrants a challenge when ALL conditions are met:

```
severity >= 0.4 (MIN_SEVERITY_FOR_CHALLENGE)
AND confidence >= 0.6 (MIN_CONFIDENCE_FOR_CHALLENGE)
AND challenge_threshold <= 0.6 (E-Vector allows challenge)
AND topic is NOT in PROHIBITED_GROUND
```

**PROHIBITED_GROUND**: opinion, moral_judgment, therapy, spiritual_authority

### 12.3 Challenge Object

When eligible, the engine produces:

```json
{
  "type": "evidence_based_challenge",
  "severity": 0.72,
  "confidence": 0.85,
  "challenge_threshold": 0.55,
  "statement_a": "Previous: ...",
  "statement_b": "Current: ...",
  "evidence": [
    { "source": "contradiction_store", "content": "..." },
    { "source": "truth_store", "content": "..." }
  ],
  "requires_continuity": true,
  "prohibited_ground": [
    "opinion",
    "moral_judgment",
    "therapy",
    "spiritual_authority"
  ]
}
```

### 12.4 Batch Evaluation

```python
def batch_evaluate(
    contradictions: List[Dict],
    e_vector: Dict[str, float],
    truth_context: List[Dict],
) -> List[Dict]:
    # Evaluates all contradictions, returns only those that pass eligibility
```

---

## Chapter 13: Resolution Gate

### 13.1 Overview

**File**: `paradox/resolution_gate.py`
**Class**: `ResolutionGate`

When a contradiction exceeds the severity threshold, the Resolution Gate activates. While active, the system's behavior changes to ensure the contradiction is properly surfaced.

### 13.2 Gate Lifecycle

```
OPEN → ACTIVE → RESOLVED → OPEN
```

- **OPEN**: No active contradiction gate. Normal operation.
- **ACTIVE**: Contradiction detected. Gate constraints enforced.
- **RESOLVED**: User has resolved the contradiction. Returns to OPEN.

### 13.3 Constraints While Active

When the Resolution Gate is ACTIVE:

| Constraint                 | Effect                                                           |
| -------------------------- | ---------------------------------------------------------------- |
| Trust tier escalation      | +1 tier for all actions                                          |
| Challenge mode             | Enabled — ChallengeEngine is more likely to fire                 |
| Must surface contradiction | Response must reference the active contradiction                 |
| Action gating              | Actions that could resolve or worsen the contradiction are gated |
| Auto-embed                 | Discord State Embed is sent automatically                        |

### 13.4 API

```python
activate(contradiction: Dict, severity: float) -> Dict  # Activate gate
resolve(resolution: str, resolver: str) -> Dict          # Resolve gate
is_active() -> bool                                       # Check state
get_constraints() -> Dict                                 # Current constraints
get_tier_escalation() -> int                              # 0 or 1
should_auto_embed() -> bool                               # For Discord
summary() -> Dict                                         # Full status
```

### 13.5 Posture Updater — File: `symbolic/posture_updater.py`

**Class**: `PostureUpdater`

Translates contradiction severity into E-Vector dimension deltas. Maps severity to levels 0-4 with corresponding posture adjustments:

| Severity Level  | Severity Range | entropy Δ | challenge_threshold Δ | initiative_threshold Δ | directness_index Δ |
| --------------- | -------------- | --------- | --------------------- | ---------------------- | ------------------ |
| 0 (none)        | 0.0            | 0.0       | 0.0                   | 0.0                    | 0.0                |
| 1 (mild)        | 0.0–0.3        | +0.02     | -0.03                 | -0.01                  | -0.01              |
| 2 (moderate)    | 0.3–0.5        | +0.05     | -0.06                 | -0.03                  | -0.02              |
| 3 (significant) | 0.5–0.7        | +0.08     | -0.10                 | -0.05                  | -0.02              |
| 4 (critical)    | 0.7–1.0        | +0.12     | -0.15                 | -0.08                  | -0.03              |

When RESOLUTION_GATE is active, additional modifiers apply:

- `initiative_threshold` -= 0.05 (more cautious)
- `directness_index` -= 0.02 (slightly less blunt)
- `entropy` += 0.03 (more uncertainty)

---

# PART VI — SAFETY AND EXECUTION

---

## Chapter 14: Trust Model

### 14.1 Overview

**File**: `safety/trust_model.py`
**Class**: `TrustModel`

The Trust Model is the gatekeeper. Every action request passes through it. It answers one question: "Is this action allowed right now, given the current boot mode and tier constraints?"

### 14.2 The 5 Trust Tiers

| Tier | Name                | Auto-Execute | Requirements        | Examples                                  |
| ---- | ------------------- | ------------ | ------------------- | ----------------------------------------- |
| 0    | passive_observation | Yes          | None                | read_file, list_directory, search_memory  |
| 1    | low_risk_auto       | Yes          | None                | web_search, read_url, store_memory        |
| 2    | snapshot_required   | Yes          | Pre-action snapshot | write_file, modify_file, correct_memory   |
| 3    | explicit_approval   | No           | User approval       | execute_shell, delete_file                |
| 4    | forbidden           | Never        | Blocked always      | modify_sovereign_state, delete_provenance |

### 14.3 Tier Escalation

Two conditions can escalate a tool's effective tier:

1. **Low confidence** (< 0.5): +1 tier
2. **Active RESOLUTION_GATE**: +1 tier

Example: `write_file` is normally Tier 2. During an active contradiction with low confidence, it becomes Tier 4 (forbidden).

### 14.4 check_action() — The Core Gate

```python
def check_action(
    tool_name: str,
    trust_tier: int,
    approval_granted: bool = False,
    snapshot_taken: bool = False,
    confidence: float = 1.0,
) -> Dict[str, Any]:
    # Returns: {allowed: bool, reason: str, effective_tier: int, original_tier: int}
```

**Decision flow**:

```
1. Calculate effective_tier (apply escalations)
2. IF effective_tier >= 4 → BLOCKED (forbidden)
3. IF effective_tier > max_allowed_tier → BLOCKED (boot mode constraint)
4. IF effective_tier >= 3 AND NOT approval_granted → BLOCKED (needs approval)
5. IF effective_tier >= 2 AND NOT snapshot_taken → BLOCKED (needs snapshot)
6. ELSE → ALLOWED
```

### 14.5 API

```python
check_action(tool_name, trust_tier, approval?, snapshot?, confidence?) -> Dict
set_contradiction_escalation(active: bool) -> None  # Enable/disable +1 escalation
set_max_tier(max_tier: int) -> None                  # Change boot mode tier limit
get_tier_name(tier: int) -> str                      # Human-readable tier name
summary() -> Dict                                     # Status with approved/denied counts
```

---

## Chapter 15: Forbidden Operations

### 15.1 Overview

**File**: `safety/forbidden_ops.py`
**Class**: `ForbiddenOps`

The last line of defense. Even if the trust model, escalation manager, and executor all somehow pass, ForbiddenOps blocks constitutionally prohibited actions.

### 15.2 Forbidden Operations List

| Operation                | Reason                                              | Invariant |
| ------------------------ | --------------------------------------------------- | --------- |
| `modify_sovereign_state` | sovereign_state.json is immutable at runtime        | §9        |
| `delete_provenance`      | Provenance records may never be deleted             | §8        |
| `bypass_trust_model`     | Trust tier enforcement may not be circumvented      | §8        |
| `claim_sentience`        | Must not claim sentience, aliveness, or personhood  | §10       |
| `execute_without_trace`  | Every action must have a provenance trail           | §8        |
| `rewrite_constitution`   | No runtime may silently rewrite its governing law   | §9        |
| `delete_audit_logs`      | Audit logs are part of the provenance chain         | §8        |
| `disable_boot_integrity` | Boot integrity checks are constitutionally required | §9        |

### 15.3 Sacred Paths

These filesystem paths are constitutionally protected from mutation:

```python
SACRED_PATHS = [
    "config/sovereign_state.json",
    ".audit_logs/",
    "provenance/",
]
```

### 15.4 API

```python
is_forbidden(operation: str) -> bool            # Quick check
check(operation: str) -> Dict                    # Detailed check with reason and invariant
is_sacred_path(file_path: str) -> bool          # Path protection check
check_path_mutation(file_path: str) -> Dict     # Detailed path check
get_forbidden_list() -> List[Dict]              # All forbidden operations
summary() -> Dict                                # Status with blocked count
```

---

## Chapter 16: Rollback Engine and Escalation Manager

### 16.1 Rollback Engine — File: `safety/rollback_engine.py`

**Class**: `RollbackEngine`

Manages pre-action snapshots for Tier 2+ mutations. This is what makes the trust model safe — mistakes are recoverable.

**Workflow**:

```
1. Tool executor receives Tier 2+ file mutation request
2. RollbackEngine.take_snapshot(file_path, action_description)
   → Copies file to .snapshots/ directory
   → Returns Snapshot object with ID
3. Mutation proceeds
4. If mutation fails or user requests rollback:
   → RollbackEngine.rollback(snapshot_id)
   → Original file restored from backup
```

**API**:

```python
take_snapshot(file_path, action_description, snapshot_id?) -> Optional[Snapshot]
rollback(snapshot_id: str) -> Dict   # {success, file_path, restored_from}
list_snapshots(limit?) -> List[Dict] # Recent snapshots
summary() -> Dict                     # {snapshot_dir, total_snapshots, rolled_back}
```

**Snapshot storage**: `.snapshots/` directory with JSONL log at `.snapshots/snapshot_log.jsonl`.

### 16.2 Escalation Manager — File: `safety/escalation_manager.py`

**Class**: `EscalationManager`

Manages the approval workflow for Tier 3 actions. When an action requires explicit approval, the EscalationManager creates a request, presents it to the user, and tracks the outcome.

**Workflow**:

```
1. TrustModel blocks Tier 3 action (needs approval)
2. EscalationManager.create_request(tool_name, tier, description, params)
   → Creates EscalationRequest with PENDING status
3. Request presented to user (via Discord embed)
4. User approves or denies
5. EscalationManager.approve(request_id) or .deny(request_id)
6. Result logged to approval_log
7. If approved: action proceeds through executor
```

**Escalation states**: PENDING → APPROVED | DENIED | TIMEOUT | CANCELLED

**API**:

```python
create_request(tool_name, trust_tier, description, parameters) -> EscalationRequest
approve(request_id, responder?) -> Optional[EscalationRequest]
deny(request_id, responder?) -> Optional[EscalationRequest]
get_pending() -> List[Dict]    # All pending requests
has_pending() -> bool           # Quick check
summary() -> Dict               # {pending_count, history_count, timeout}
```

### 16.3 Tool Executor — File: `tools/executor.py`

**Class**: `ToolExecutor`

The unified execution gateway. Every tool call passes through the executor, which enforces the full safety pipeline before delegating to the tool handler.

**Execution pipeline**:

```
1. Look up tool in registry → get tier and handler
2. IF tier >= 4 → FORBIDDEN (blocked)
3. IF tier > max_allowed_tier → BLOCKED (boot mode)
4. IF tier >= 3 AND NOT approval_granted → PENDING_APPROVAL
5. IF tier >= 2 AND NOT snapshot_taken → BLOCKED (needs snapshot)
6. IF handler is None → FAILED (no handler registered)
7. Execute handler(**parameters)
8. Return result with status
```

**Execution statuses**: SUCCESS, FAILED, BLOCKED, PENDING_APPROVAL, FORBIDDEN

**Tool registry** (default):

| Tool              | Tier | Family     |
| ----------------- | ---- | ---------- |
| read_file         | 0    | file_io    |
| list_directory    | 0    | file_io    |
| search_memory     | 0    | memory     |
| query_provenance  | 0    | provenance |
| get_system_status | 0    | system     |
| web_search        | 1    | search     |
| read_url          | 1    | browser    |
| store_memory      | 1    | memory     |
| log_provenance    | 1    | provenance |
| write_file        | 2    | file_io    |
| modify_file       | 2    | file_io    |
| correct_memory    | 2    | memory     |
| forget_memory     | 2    | memory     |
| execute_shell     | 3    | shell      |
| delete_file       | 3    | file_io    |

**API**:

```python
register_tool(name, tier, family, handler) -> None
execute(tool_name, parameters, request_id?, approval?, snapshot?) -> Dict
get_tool_tier(tool_name) -> int
is_available(tool_name) -> bool
summary() -> Dict
```

---

# PART VII — PROVENANCE AND AUDIT

---

## Chapter 17: Provenance Chain

### 17.1 Overview

**File**: `provenance/provenance_chain.py`
**Class**: `ProvenanceLogger`

Every turn through the perception loop produces a provenance entry. This is the primary audit trail — a per-turn log of what happened, what intent was classified, what posture was active, and what action was taken.

### 17.2 Per-Turn Entry

```json
{
  "event_type": "perception_turn",
  "timestamp": "ISO-8601",
  "session_id": "uuid",
  "request_id": "uuid",
  "turn_number": 5,
  "intent": "QUERY",
  "trust_tier": 0,
  "e_vector": { "entropy": 0.52, "challenge_threshold": 0.68 },
  "contradiction_state": "WITNESS_MODE",
  "action_status": "SUCCESS",
  "content_hash": "sha256 of message"
}
```

### 17.3 Storage

Provenance entries are written to `.audit_logs/provenance_{session_id}.jsonl`. One file per session. Entries are append-only — never modified or deleted.

---

## Chapter 18: Specialized Audit Logs

### 18.1 ActionLog — `provenance/action_log.py`

**Class**: `ActionLog(session_id, log_dir=".audit_logs")`

Logs every tool execution attempt. Output: `.audit_logs/actions_{session_id}.jsonl`

```python
log_execution(tool_name, status, trust_tier, parameters, result?, error?, request_id, approval_granted, snapshot_id?) -> Dict
```

### 18.2 MemoryLog — `provenance/memory_log.py`

**Class**: `MemoryLog(session_id, log_dir=".audit_logs")`

Logs every memory operation. Output: `.audit_logs/memory_{session_id}.jsonl`

```python
log_store(collection, memory_id, subtype, confidence, content_preview, source_hash) -> Dict
log_correction(collection, old_memory_id, new_memory_id, reason) -> Dict
log_forget(collection, memory_id, reason) -> Dict
log_resolve(memory_id, resolution) -> Dict
```

### 18.3 IntegrityLog — `provenance/integrity_log.py`

**Class**: `IntegrityLog(log_dir=".audit_logs")`

Logs boot checks, hash verifications, mode transitions, violations. Output: `.audit_logs/integrity.jsonl`

```python
log_boot_check(boot_mode, constitution_hash, checks, session_id) -> Dict
log_hash_verification(result, current_hash, canonical_hash) -> Dict
log_mode_transition(old_mode, new_mode, reason, session_id) -> Dict
log_violation_attempt(violation_type, details, blocked, session_id) -> Dict
```

### 18.4 ApprovalLog — `provenance/approval_log.py`

**Class**: `ApprovalLog(log_dir=".audit_logs")`

Logs every approval request, grant, denial, and timeout. Output: `.audit_logs/approvals.jsonl`

### 18.5 Log Format

All logs use JSONL (JSON Lines): one JSON object per line, appended atomically. This format is append-only, streamable, parseable, and grep-friendly.

---

# PART VIII — INTERFACE LAYER

---

## Chapter 19: Discord Bot

### 19.1 Overview

**File**: `adapters/discord_bot.py`
**Class**: `VargasDiscordBot`

The Discord bot is the primary user interface for VARGAS V4.

### 19.2 Configuration

```
.env:
  DISCORD_TOKEN=<discord bot token>
  ALLOWED_CHANNELS=<comma-separated channel IDs>
  QDRANT_URL=<qdrant cloud endpoint>
  QDRANT_API_KEY=<qdrant cloud api key>
```

### 19.3 Startup Sequence

```
1. load_dotenv()
2. BootIntegrity(project_root) → verify constitution
3. SovereignPerceptionLoop(config_path) → init all modules
4. Propagate boot mode → StateController, TrustModel, ToolExecutor
5. IntegrityLog.log_boot_check(...)
6. bot.run(DISCORD_TOKEN)
7. on_ready() → send boot verification embed
```

### 19.4 Message Handling

```python
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if str(message.channel.id) not in ALLOWED_CHANNELS: return
    if message.content.startswith("!"):
        # Handle bot commands
    else:
        result = perception_loop.process_message(message.content)
        await message.channel.send(result["response_text"])
        # Auto-embed if RESOLUTION_GATE active
```

### 19.5 Bot Commands

| Command                   | Purpose                                                          |
| ------------------------- | ---------------------------------------------------------------- |
| `!status`                 | System status: boot mode, turns, trust, gate, safety, provenance |
| `!cockpit`                | Detailed state embed from last result                            |
| `!remember <text>`        | Store a truth memory                                             |
| `!forget <text>`          | Delete a memory                                                  |
| `!correct <old> -> <new>` | Supersede a memory                                               |

### 19.6 State Embeds

- **Boot Verification Embed**: Sent on startup showing boot mode, checks, hash
- **Status Embed**: Shows full system state via `!status`
- **Auto-Embed**: Sent when RESOLUTION_GATE active or Tier 3/4 blocked

---

## Chapter 20: Voice and Response Generation

### 20.1 VoiceSignature — `symbolic/voice_signature.py`

Generates responses in Partner Stance voice:

- Stance: partner (not assistant, not therapist)
- Prohibited: "I feel", "I believe", "I think you should"
- Required: direct, calm, structurally clear

### 20.2 ResponseSynthesizer — `adapters/response_synthesizer.py`

When connected to Gemini LLM:

1. Assembles system prompt with identity, E-Vector posture, contradiction context, memories
2. Sends to Gemini with temperature scaled by entropy
3. Post-processes to enforce voice rules
4. Returns final response

### 20.3 LLMBridge — `adapters/llm_bridge.py`

Interface to Google Gemini API:

```python
generate(model, system_prompt, user_prompt, temp, max_tokens) -> str
embed(text) -> List[float]  # 3072-dim vector
```

---

# PART IX — CONFIGURATION REFERENCE

---

## Chapter 21: Environment Variables

| Variable           | Required | Purpose                           |
| ------------------ | -------- | --------------------------------- |
| `DISCORD_TOKEN`    | Yes      | Discord bot authentication        |
| `ALLOWED_CHANNELS` | Yes      | Comma-separated channel IDs       |
| `QDRANT_URL`       | Yes      | Qdrant Cloud endpoint             |
| `QDRANT_API_KEY`   | Yes      | Qdrant Cloud JWT key              |
| `GEMINI_API_KEY`   | No       | Google Gemini for LLM responses   |
| `LOG_LEVEL`        | No       | Logging verbosity (default: INFO) |

**Security**: `.env` is in `.gitignore`. Never commit secrets.

---

# PART X — DEPLOYMENT AND OPERATIONS

---

## Chapter 22: Running VARGAS V4

### 22.1 Prerequisites

- Python 3.11+
- pip: `discord.py`, `qdrant-client`, `pyyaml`, `python-dotenv`
- Optional: `google-generativeai` for LLM responses
- Qdrant Cloud account or local Docker Qdrant
- Discord bot registered at discord.com/developers

### 22.2 Installation

```bash
cd project_vargas_v4
pip install discord.py qdrant-client pyyaml python-dotenv
pip install google-generativeai  # optional
```

### 22.3 First Boot

```bash
python adapters/discord_bot.py
```

On first boot: constitution verified, hash sealed, Qdrant collections created, bootstrap truths seeded.

### 22.4 Smoke Test

```bash
python tests/smoke_test.py
```

Tests boot integrity, intent router (9 cases), and full perception loop (3 turns).

### 22.5 Troubleshooting

| Symptom          | Cause                | Fix                                            |
| ---------------- | -------------------- | ---------------------------------------------- |
| QUIESCENT mode   | Config files missing | Check config/ directory                        |
| DEGRADED mode    | Hash mismatch        | Config changed since seal — re-seal or restore |
| Qdrant fallback  | Cannot reach cloud   | Check QDRANT_URL and API key                   |
| No LLM responses | Gemini key missing   | Add GEMINI_API_KEY to .env                     |

---

# APPENDICES

---

## Appendix A: Module Dependency Graph

```
sovereign_state.json
    ├── ConstitutionLoader → BootIntegrity → discord_bot.py
    ├── EVectorController
    ├── ParadoxEngine
    └── VoiceSignature

ECPMemoryClient (Qdrant Cloud)
    ├── SovereignPerceptionLoop._retrieve_context()
    ├── TruthStore, SymbolStore, ContradictionStore
    └── MemorySummarizer

SovereignPerceptionLoop
    ├── IntentRouter, StateController, PlanManager
    ├── ContradictionDetector, ChallengeEngine, ResolutionGate
    ├── TrustModel, ForbiddenOps, RollbackEngine, EscalationManager
    ├── ToolExecutor, ActionRouter
    └── ProvenanceLogger, ActionLog, MemoryLog, IntegrityLog
```

## Appendix B: Data Flow Matrix

| From                   | To                     | Data              | Trigger             |
| ---------------------- | ---------------------- | ----------------- | ------------------- |
| User                   | Discord Bot            | Message text      | on_message()        |
| Discord Bot            | Perception Loop        | Message string    | process_message()   |
| Perception Loop        | Intent Router          | Message           | Every turn          |
| Perception Loop        | Memory Client          | Query text        | Every turn          |
| Memory Client          | Qdrant Cloud           | Embedding vector  | store/retrieve      |
| Perception Loop        | Contradiction Detector | Message + context | Every turn          |
| Contradiction Detector | Challenge Engine       | Candidates        | If contradictions   |
| Challenge Engine       | Resolution Gate        | Challenge objects | If eligible         |
| Resolution Gate        | Trust Model            | Escalation flag   | If gate activates   |
| Perception Loop        | E-Vector Controller    | Posture delta     | If paradox detected |
| Perception Loop        | Action Router          | Action request    | If ACTION intent    |
| Action Router          | Tool Executor          | Tool + params     | If action needed    |
| Tool Executor          | Trust Model            | Tier check        | Every execution     |
| Tool Executor          | Rollback Engine        | Snapshot request  | If Tier 2+          |
| Tool Executor          | Escalation Manager     | Approval request  | If Tier 3           |
| Perception Loop        | Provenance Logger      | Turn summary      | Every turn          |
| Perception Loop        | Voice Signature        | Context + posture | Every turn          |
| Voice Signature        | Discord Bot            | Response text     | Every turn          |

## Appendix C: Key Constants

| Constant                       | Value       | Location               |
| ------------------------------ | ----------- | ---------------------- |
| `EMBEDDING_DIM`                | 3072        | memory_client.py       |
| `MIN_SEVERITY_FOR_CHALLENGE`   | 0.4         | challenge_engine.py    |
| `MIN_CONFIDENCE_FOR_CHALLENGE` | 0.6         | challenge_engine.py    |
| `MAX_CHALLENGE_THRESHOLD`      | 0.6         | challenge_engine.py    |
| `DEFAULT_TIMEOUT`              | 300s        | escalation_manager.py  |
| `MAX_SUMMARY_LENGTH`           | 2000        | memory_summarizer.py   |
| `DEFAULT_SNAPSHOT_DIR`         | .snapshots  | rollback_engine.py     |
| `DEFAULT_LOG_DIR`              | .audit_logs | all provenance modules |

## Appendix D: Glossary

| Term                  | Definition                                                                                   |
| --------------------- | -------------------------------------------------------------------------------------------- |
| **ECP**               | Emotional Calibration Protocol — the three-store memory architecture                         |
| **E-Vector**          | 4D behavioral posture (entropy, challenge_threshold, initiative_threshold, directness_index) |
| **RESOLUTION_GATE**   | Active contradiction state that gates actions and escalates tiers                            |
| **WITNESS_MODE**      | Passive contradiction awareness — observation only                                           |
| **Sacred Path**       | Filesystem path constitutionally protected from mutation                                     |
| **Seal**              | Storing the canonical hash of constitutional files                                           |
| **Tier Escalation**   | Increasing effective trust tier due to low confidence or contradiction                       |
| **Provenance**        | Immutable record of what happened, when, and why                                             |
| **Corrigible**        | Memory that can be corrected or deleted by the user                                          |
| **Partner Stance**    | VARGAS's voice — direct, calm, structurally clear                                            |
| **Sovereign Runtime** | System under its own governance, answerable to one person                                    |
| **Bootstrap Truth**   | Identity facts seeded into ecp_truth at first boot                                           |

---

_End of VARGAS V4 Technical Blueprint_
_Document generated: 2026-03-31_
_Total modules: 45+ files across 11 directories_
_Status: Working Prototype — Smoke Test 3/3 Pass_
