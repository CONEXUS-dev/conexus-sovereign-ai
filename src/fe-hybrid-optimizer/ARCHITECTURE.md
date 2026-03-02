# FE Hybrid Control Architecture

## Core Concept

**FE is NOT a standalone deterministic heuristic.**

**FE IS a two-layer hybrid control system:**
- **Layer 1 (Engine)**: Deterministic search substrate
- **Layer 2 (Pilot)**: Calibrated AI controller

The invention is the **control architecture**, not the algorithm alone.

---

## Layer 1: Engine (Deterministic Substrate)

### Responsibilities
- VRP instance generation/loading
- Candidate solution representation
- Feasible move operators (swap, relocate, 2-opt-in-route, cross-exchange)
- Capacity-aware deterministic repair
- Objective evaluation
- Paradox buffer storage (deterministic)
- State logging

### Rules
- **Deterministic**: Given seeds + pilot decisions → same output
- **No AI creativity**: Engine never invents structural changes
- **Action executor only**: Applies pilot decisions mechanically

### Files
- `engine/vrp_instance.py` - Instance generation
- `engine/candidate.py` - Solution representation
- `engine/operators.py` - Move operators
- `engine/repair.py` - Deterministic repair
- `engine/evaluation.py` - Objective calculation
- `engine/paradox.py` - Paradox buffer
- `engine/core.py` - Main search loop

---

## Layer 2: Pilot Adapter (AI Controller)

### Responsibilities
- Receive iteration packet (structured JSON state)
- Return strict JSON decision from allowed action set
- Never manipulate routes directly
- Never output free text in production

### Rules
- **Multi-backend**: Anthropic, OpenAI, Gemini, Stub
- **Logged verbatim**: All inputs/outputs recorded
- **Replay mode**: Reuse recorded decisions, no AI calls

### Files
- `pilot/adapter.py` - Main adapter interface
- `pilot/backends/anthropic.py` - Claude backend
- `pilot/backends/openai.py` - GPT backend
- `pilot/backends/gemini.py` - Gemini backend
- `pilot/backends/stub.py` - Deterministic stub
- `pilot/schema.py` - JSON schemas
- `pilot/calibration.py` - CONEXUS-STEEL-04 handshake

---

## Reproducibility: Record and Replay

### Live Mode
1. Engine computes iteration packet
2. Adapter sends to pilot
3. Pilot returns JSON decision
4. Engine applies action deterministically
5. Log everything (JSONL trace)

### Replay Mode
- **No AI calls**
- Read recorded decision trace
- Apply decisions in order
- **Output hash must match original**

This is how we make AI-controlled optimization reproducible without pretending AI isn't part of it.

---

## Hard Invariants

### Indexing (Canonical)
- **Internal customers**: 0..N-1
- **Depot**: index N (or separate constant)
- **Never use 0 as depot if customer 0 exists**
- Convert to 1..N only for display output

### Feasibility Gates (Hard Failures)
For investor-grade runs, these are **hard constraints**:

1. **Coverage**: Every customer 0..N-1 appears exactly once
2. **No duplicates**: No customer appears twice
3. **Demand conservation**: sum(route_loads) = total_demand
4. **Capacity**: Every route load ≤ capacity
5. **Route integrity**: Depot start/end consistent

**If any check fails:**
- Mark run INVALID
- Do not compare performance
- Save full debug report

### Repair Strategy
Two-phase deterministic repair:
1. **Coverage repair**: Fix missing/duplicates
2. **Capacity repair**: Move customers to routes with slack using best insertion cost

Must be deterministic under seed.

---

## Objective Definition

For investor-grade VRP validation:
- **Distance only** with hard constraints enforced
- **Do not compare penalized infeasible vs feasible solver**

If testing soft capacity mode:
- Separate experiment
- OR-Tools must use matching penalties
- Do not mix regimes

---

## Baselines and Fairness

### OR-Tools (Recommended)
- Time limit = FE runtime
- Hard constraints match FE problem
- Log parameters and version

### Clarke-Wright + Local Search (Alternative)
- CW once (deterministic)
- Local search for same wall-clock budget as FE
- Compare distance

**Requirements:**
- Same instance
- Same constraints
- Same time budget
- Same metric

---

## Iteration Packet Schema

Compact JSON state summary:

```json
{
  "iteration": 42,
  "best_distance": 1234.56,
  "route_count": 5,
  "loads": {
    "min": 45,
    "max": 98,
    "mean": 72.3,
    "top_5": [98, 95, 92, 88, 85]
  },
  "capacity_slack": 123,
  "routes_near_capacity": 3,
  "worst_edges": [
    {"from": 12, "to": 34, "dist": 89.2},
    {"from": 5, "to": 67, "dist": 78.1}
  ],
  "stagnation_steps": 8,
  "recent_moves": [
    {"op": "swap", "delta": -12.3, "accepted": true},
    {"op": "relocate", "delta": 5.6, "accepted": false}
  ],
  "paradox_size": 3,
  "paradox_best_alt": 1245.67
}
```

---

## Pilot Action Space

Strict JSON decision format:

```json
{
  "action": "APPLY_OPERATOR",
  "operator": "swap",
  "target_routes": [2, 5],
  "parameters": {
    "intensity": 0.7
  }
}
```

### Allowed Actions
- `APPLY_OPERATOR` - swap, relocate, 2-opt, cross-exchange
- `FOCUS_ROUTE` - prioritize specific routes
- `REPAIR_CAPACITY` - force capacity repair now
- `DIVERSIFY` - pull from paradox or reseed
- `INTENSIFY` - local search on best
- `STOP` - convergence reached

**No new actions without schema update.**

---

## Logging Requirements (Investor-Grade)

Per run, save:
- `instance.json` - coordinates, demands, capacity, seed
- `config.json` - seeds, budgets, versions
- `pilot_trace.jsonl` - iteration packets + decisions
- `engine_trace.jsonl` - operators, deltas, feasibility
- `final_solution.json` - routes, loads, distance
- `summary.json` - distance, time, feasibility, baseline delta
- `*.sha256` - hashes for all artifacts

Environment recording:
- Python version, OS, package versions
- Model name for pilot
- Timestamp

---

## Acceptance Criteria

Do not declare "validated" until these pass:

1. **Replay determinism**: Live run hash = Replay run hash
2. **Feasibility**: FE and baseline pass all hard constraints
3. **Fair baseline**: Same wall-clock budget
4. **No silent failures**: Feasibility failure aborts with debug report

---

## Implementation Order

1. Freeze canonical indexing
2. Hard feasibility gates + deterministic repair
3. OR-Tools baseline (fixed indexing)
4. Pilot adapter with strict JSON schema
5. Logging and replay mode
6. Test on small N (25, 50) until perfect
7. Scale to 100 when stable
8. Report performance deltas

---

## What NOT to Do

- ❌ Claim stub reproduces audit pack numbers
- ❌ Publish "win" without feasibility gates
- ❌ Compare infeasible penalized vs feasible solver
- ❌ Hardcode results into JSON exporter
- ❌ Change problem definition between FE and baseline

---

## Repo Structure

```
fe-hybrid-optimizer/
├── engine/
│   ├── __init__.py
│   ├── vrp_instance.py
│   ├── candidate.py
│   ├── operators.py
│   ├── repair.py
│   ├── evaluation.py
│   ├── paradox.py
│   └── core.py
├── pilot/
│   ├── __init__.py
│   ├── adapter.py
│   ├── schema.py
│   ├── calibration.py
│   └── backends/
│       ├── __init__.py
│       ├── anthropic.py
│       ├── openai.py
│       ├── gemini.py
│       └── stub.py
├── baselines/
│   ├── __init__.py
│   ├── ortools_solver.py
│   └── clarke_wright.py
├── validators/
│   ├── __init__.py
│   ├── feasibility.py
│   └── replay.py
├── runners/
│   ├── __init__.py
│   ├── run_live.py
│   ├── run_replay.py
│   └── run_baseline.py
├── artifacts/
│   └── (generated run outputs)
├── instances/
│   └── (VRP problem instances)
├── README.md
├── ARCHITECTURE.md
└── requirements.txt
```

---

## Commands

```bash
# Live hybrid run (AI pilot)
python -m runners.run_live --instance instances/vrp_100.json --pilot anthropic --iterations 100

# Replay run (no AI, uses recorded decisions)
python -m runners.run_replay --trace artifacts/run_001/pilot_trace.jsonl

# Baseline run (time-matched)
python -m runners.run_baseline --instance instances/vrp_100.json --time-budget 30.0

# Validate replay determinism
python -m validators.replay --live artifacts/run_001 --replay artifacts/run_001_replay
```

---

## The Honest Claim

**We are NOT claiming:**
- "FE beats OR-Tools deterministically without AI"

**We ARE claiming:**
- "A calibrated AI pilot can reliably steer a deterministic engine into better regions of the search space as complexity grows"

This is a **control-theory claim**, not a pure optimization claim.

It is:
- Defensible
- Fundable
- Consistent with last year's results
- Aligned with CONEXUS-STEEL-04 specification
