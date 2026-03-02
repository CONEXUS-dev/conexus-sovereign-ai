# CONEXUS Sovereign AI — Proof Package

## What This Is

This package contains irrefutable, artifact-based evidence that the CONEXUS Collapse-Become dual-agent sovereign AI system is **real and operational**.

Five missions were processed by two specialized AI agents — **Sway** (Collapse/compression) and **Opie** (Become/expansion) — running entirely on local hardware with no cloud dependencies. Every mission includes full provenance: cryptographic hashes, timestamps, agent identity, confidence scores, and a complete audit trail.

> **Terminology note:** This document uses "sovereign cycle" to describe the DIVERGE → COLLAPSE → BECOME sequence. The on-disk filenames retain the original `sovereign_loop` label for artifact integrity.

## What You're Looking At

| Mission | Mode                     | Agent(s)    | What It Proves                                                     |
| ------- | ------------------------ | ----------- | ------------------------------------------------------------------ |
| **1**   | Sovereign Cycle          | Sway → Opie | Full Collapse-Become cycle on core IP (FE investor pitch + vision) |
| **2**   | Collapse Only            | Sway        | Structured execution plan for hostile reviewer (CAE protocol)      |
| **3**   | Become Only              | Opie        | Paradox-holding creative synthesis (math + consciousness)          |
| **4**   | Collapse Only            | Sway        | Architecture audit with severity ranking and hardening plan        |
| **5**   | Sovereign Cycle + Memory | Sway → Opie | Investor narrative informed by memories from Missions 1-4          |

## Key Claims Proven

1. **Two agents with genuinely different cognitive modes.** Collapse missions (2, 4) produce structured execution plans with numbered steps, dependencies, and risk rankings. Become missions (3) produce paradox-holding synthesis with symbolic integration. The outputs are verifiably different.
2. **A sovereign cycle that hands off between agents.** Missions 1 and 5 show three distinct phases (DIVERGE → COLLAPSE → BECOME) with separate `diverge_output`, `collapse_output`, and `become_output` fields proving sequential agent processing.
3. **Full audit trail with cryptographic hashes.** Every mission has a SHA-256 input hash and output hash recorded in SQLite. These are independently verifiable.
4. **Vector memory that closes the cycle.** Missions 1-4 wrote to Qdrant vector memory. Mission 5 retrieved relevant memories and used them as context — the sovereign cycle feeds itself.
5. **100% local execution.** No cloud API, no internet required for inference. Two LLMs (Llama 3 8B, Mistral 7B) and one embedding model run in-process via GPT4All on CPU.

## Architecture

```
  Derek (Principal Orchestrator)
         │
         ▼
  ┌─────────────────┐
  │  Orchestrator    │──── Audit Log (SQLite)
  │  (Router)        │──── Vector Memory (Qdrant)
  └────────┬────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
  ┌──────┐   ┌──────┐
  │ Sway │   │ Opie │
  │(Llama│   │(Mist-│
  │  3)  │   │ ral) │
  └──────┘   └──────┘
  COLLAPSE    BECOME
  compress    expand
  execute     synthesize
  resolve     hold paradox
```

## Architecture Notes

The sovereign cycle currently executes as a **three-phase sequential pipeline** (DIVERGE → COLLAPSE → BECOME) within a single invocation. Opie's diverge output feeds Sway's collapse phase, whose output feeds Opie's become phase. There is no intra-invocation feedback loop — the cycle does not re-enter DIVERGE based on BECOME output within the same call.

Paradox is preserved **structurally**: Opie holds tensions; Sway resolves them into directives. Both outputs are retained in the final result and written to vector memory. The system holds paradox _across agents_, not within one.

## Next Research Milestones

- **Feedback dynamics:** Enable conditional re-entry from BECOME → DIVERGE within a single sovereign cycle when the become phase detects that critical paradoxes were flattened during collapse.
- **Contextual contradiction resolution:** Replace Sway's static pole_a priority with gear-context-weighted resolution (e.g., VISION_HOLD gears weight emergence higher than PERFORMANCE_STRESS gears).
- **Adaptive confidence scoring:** Derive confidence from output quality metrics rather than heuristic baselines.

## How to Verify

```bash
# Check system health
python -m sovereign.cli --health

# View audit trail
python -m sovereign.cli --audit

# Run a new mission (collapse mode)
python -m sovereign.cli --mode collapse "Break down X into 3 steps"

# Run a new mission (become mode)
python -m sovereign.cli --mode become "Explore the meaning of Y"

# Run a sovereign loop
python -m sovereign.cli --mode both "Analyze and expand Z"
```

## Package Contents

```
SOVEREIGN_PROOF/
├── README.md                          # This file
├── PROVENANCE.md                      # Cryptographic provenance + memory chain
├── MANIFEST.md                        # Complete file manifest with SHA-256 hashes
├── memory_chain.json                  # Full memory retrieval metadata
├── missions/
│   ├── mission_1_sovereign_loop.json  # FE investor pitch + vision (both)
│   ├── mission_2_collapse.json        # CAE experimental protocol (collapse)
│   ├── mission_3_become.json          # Paradox-holding exploration (become)
│   ├── mission_4_collapse.json        # Architecture audit (collapse)
│   └── mission_5_sovereign_loop.json  # Investor narrative + memory (both)
├── audit/
│   ├── audit_log.json                 # Full structured audit trail
│   ├── audit_log.csv                  # Flat audit table
│   └── audit_summary.md               # Human-readable audit table
└── source/
    ├── llm_client.py                  # GPT4All abstraction layer
    ├── sway.py                        # Collapse agent (Sway)
    ├── opie.py                        # Become agent (Opie)
    ├── router.py                      # Task routing logic
    ├── memory_client.py               # Qdrant memory client
    ├── orchestrator.py                # Central control plane
    ├── audit_log.py                   # SQLite audit trail
    └── cli.py                         # Command-line interface
```

## Technical Stack

| Component      | Technology                       |
| -------------- | -------------------------------- |
| LLM Runtime    | GPT4All (Python SDK, in-process) |
| Collapse Model | Meta-Llama-3-8B-Instruct Q4_0    |
| Become Model   | Mistral-7B-Instruct-v0.3 Q4_0    |
| Embeddings     | all-MiniLM-L6-v2 (384-dim)       |
| Vector Memory  | Qdrant (localhost:6333)          |
| Audit Trail    | SQLite                           |
| Orchestration  | Python (custom)                  |
| Device         | CPU                              |

---

_Built by Derek Angell. CONEXUS Collapse-Become Unified Protocol v1.1._

_Patent reference: US 63/898,911_
