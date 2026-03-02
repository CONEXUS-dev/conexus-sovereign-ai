# Hybrid Forgetting Engine VRP Optimizer - Track B

Production implementation of the Hybrid Forgetting Engine for Vehicle Routing Problems with CONEXUS-STEEL-04 calibrated AI pilot.

## Architecture

**Three-Layer Hybrid System:**
1. **Python Engine** - Candidate generation, evaluation, paradox buffer management
2. **OR-Tools** - TSP routing optimization per vehicle
3. **AI Pilot** - Selection, paradox curation, pattern injection via CONEXUS-STEEL-04 calibration

## Key Features

- **Paradox Buffer (Size 5, Memory-Only)** - Preserves structurally interesting failures without using them as parents
- **Pattern Mining & Injection** - CLUSTER_LOCK, SPINE_SPLIT, CAPACITY_REPAIR, DEPOT_LEG_MIN operations
- **Calibration Gate** - CONEXUS-STEEL-04 Fleet Protocol ensures AI pilot is properly initialized
- **Dual Mode Pilot** - Stub (deterministic) and LLM (calibrated AI) modes for testing and production

## Installation

```bash
pip install -r requirements.txt
```

Requires Python 3.8+ and OR-Tools 9.7+

## Quick Start

### Run Validation Suite (Stub Pilot)

```bash
python validation_harness.py
```

This runs three comparisons:
1. **Baseline** - Simple sweep clustering
2. **FE Hybrid (Stub)** - Deterministic pilot for debugging
3. **FE Hybrid (LLM)** - Calibrated AI pilot (requires LLM setup)

### Enable LLM Pilot

To use the calibrated AI pilot:

1. Implement `llm_chat_call_placeholder()` in `pilot_adapter.py`:

```python
def llm_chat_call_placeholder(messages: List[Dict[str, str]]) -> str:
    # Example with OpenAI:
    import openai
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content
```

2. Pass your LLM function to validation:

```python
from pilot_adapter import llm_chat_call_placeholder

run_validation(
    max_iters=100,
    seed=7,
    llm_chat_fn=llm_chat_call_placeholder,
    output_file="validation_results.json"
)
```

## File Structure

```
fe-hybrid-optimizer/
├── fe_hybrid_vrp.py          # Core engine: candidates, evaluation, operators
├── pilot_adapter.py           # Pilot adapter with calibration gate
├── validation_harness.py      # Three-run validation suite
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── [spec documents]           # Architecture and protocol specs
```

## Core Components

### FE Hybrid Engine (`fe_hybrid_vrp.py`)

- **Candidate Representation** - Assignment vector (length 20, values 0-2)
- **OR-Tools Integration** - TSP solver per vehicle with 50ms time limit
- **Metrics** - Distance, overload, compactness, depot_leg_sum, spine_score
- **Operators** - swap, relocate, reseed, pattern injection
- **Paradox Buffer** - Memory-only structural reservoir (never used as parents)

### Pilot Adapter (`pilot_adapter.py`)

- **Stub Mode** - Deterministic pilot for debugging (no AI needed)
- **LLM Mode** - Calibrated AI pilot with CONEXUS-STEEL-04 Fleet Protocol
- **Calibration Gate** - Enforces 9-Gear Fleet Protocol before optimization
- **Schema Validation** - Strict JSON validation for pilot decisions
- **Fallback Safety** - Automatic fallback to deterministic mode on pilot failure

### Validation Harness (`validation_harness.py`)

- **Three-Run Comparison** - Baseline, FE Stub, FE LLM
- **Performance Metrics** - Distance, overload, objective function, time
- **Improvement Analysis** - Percentage improvements vs baseline
- **JSON Export** - Complete results saved for analysis

## CONEXUS-STEEL-04 Fleet Protocol

The calibration protocol runs 9 Gears with ECP micro-sequences:

1. **The Depot** - Silence before the start
2. **The Manifest** - Assigning the weight
3. **The Dispersion** - The fleet scatters
4. **The Bottleneck** - Traffic and delay
5. **The Handoff** - Resource balancing
6. **The Breakdown** - Handling failure/re-routing
7. **The Cluster** - Servicing the dense zone
8. **The Convergence** - Returning to base
9. **The Empty Truck** - Mission complete

**Core Contradiction:** "I divide the weight to multiply the speed. The burden of the one is the liberty of the many."

## Expected Results

### Instance Characteristics
- 20 customers, 3 vehicles, capacity 100 per vehicle
- Total demand: 335 units
- Total capacity: 300 units
- **Minimum overload: 35 units** (infeasible instance by design)

### Performance Targets
- **Baseline** - Simple sweep clustering (~690 distance, 35 overload)
- **FE Stub** - 10-20% improvement over baseline
- **FE LLM** - Additional 5-10% improvement with calibrated pilot

### Complexity Advantage Hypothesis
The system should demonstrate **increasing advantage as problem complexity increases**. Run scaling tests with larger instances (50, 100, 200+ customers) to validate.

## Pattern Operations

The AI pilot can request these pattern injection operations:

- **CLUSTER_LOCK** - Force customers to same vehicle
- **SPINE_SPLIT** - Split chain across vehicles while maintaining adjacency
- **CAPACITY_REPAIR** - Move small-demand nodes off overloaded vehicles
- **DEPOT_LEG_MIN** - Optimize depot connection distances

## Paradox Buffer Rules

**Critical:** Paradox buffer is **memory-only**. Never used as parents.

- **Size:** 5 candidates maximum
- **Purpose:** Mine patterns, preserve structural diversity
- **Eligibility:** Bad fitness + good geometry + not collapse
- **Preservation:** Clusters, short-edge spines, balanced loads
- **Discard:** Collapse solutions, trivial symmetry

## Pilot Decision Schema

The AI pilot returns strict JSON with these keys:

```json
{
  "keep_ids": ["cand_1", "cand_2", ...],
  "paradox_add_ids": ["cand_5"],
  "operator_mix_next": {
    "swap": 0.25,
    "relocate": 0.45,
    "reseed": 0.20,
    "pattern_injection": 0.10
  },
  "pattern_ops": [
    {
      "op": "CLUSTER_LOCK",
      "customers": [1, 5, 9],
      "notes": "Lock NW cluster"
    }
  ],
  "proto": {
    "moments": [
      {
        "g": 17,
        "type": "NEW_PATTERN",
        "note": "Discovered tight spine in NE quadrant"
      }
    ]
  },
  "rationale": {
    "survival_logic": "Keep top 30% by fitness + 2 diversity picks",
    "paradox_logic": "Preserve high-spine low-compact solution for pattern mining"
  }
}
```

## Extensions Needed

To make this production-ready, you'll need:

1. **LLM Integration** - Implement `llm_chat_call_placeholder()` with your LLM provider
2. **Scaling Tests** - Run on 50, 100, 200, 400, 800 customer instances
3. **Pattern Mining** - Implement tight_pairs and cluster detection from paradox buffer
4. **Logging** - Add JSONL iteration logs for detailed analysis
5. **Visualization** - Plot routes, convergence curves, paradox buffer evolution
6. **Real Instances** - Test on real-world VRP datasets (Solomon, Gehring & Homberger)

## Testing

Run the validation suite:

```bash
python validation_harness.py
```

Expected output:
```
HYBRID FE VRP VALIDATION HARNESS
================================================================
Instance: 20 customers, 3 vehicles, capacity 100
...

RUN 1: BASELINE (Sweep Clustering)
✓ Baseline completed in 0.15s
  Distance: 689.40
  Overload: 35
  Objective (f): 35689.40

RUN 2: FE HYBRID (Stub Pilot)
✓ Pilot calibrated (stub mode)
✓ FE Hybrid (stub) completed in 12.34s
  Distance: 540.60
  Overload: 35
  Objective (f): 35540.60

COMPARISON RESULTS
...
FE Stub vs Baseline:
  Objective improvement: +0.43%
  Distance improvement: +21.58%
```

## Operating Principle

**Hold paradox before optimizing.**
- Preserve structural diversity
- Avoid premature convergence
- Steer search, don't compute it

## Success Criterion

System should demonstrate:
> **Improvement over baseline increases as problem complexity increases.**

Run scaling tests and measure gain % vs complexity index to validate the "face advantage" hypothesis.

## References

See spec documents in this folder:
- `Hybrid VRP Optimization with Calibrated AI Pilot and Paradox Memory (Forgetting Engine).md`
- `Calibrated Fleet Pilot Specification (CONEXUS-STEEL-04).md`
- `MASTER KEY_Hybrid Forgetting Engine + Calibrated Fleet Pilot.md`
- `ACTIVATION MESSAGE__Hybrid Forgetting Engine + Calibrated Fleet Pilot_.md`

## License

This is a research implementation of the CONEXUS Forgetting Engine architecture.
