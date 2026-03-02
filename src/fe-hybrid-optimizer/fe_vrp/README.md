# FE-VRP Optimizer

**Hybrid Forgetting Engine + Calibrated Fleet Pilot** for Vehicle Routing Problems.

A two-layer hybrid control system: a Python engine runs the search loop with strategic forgetting and paradox retention, while a calibrated AI pilot returns strict JSON steering decisions.

## Install

```bash
pip install -r requirements.txt
```

No external dependencies required for stub mode. For LLM mode, install one of:
```bash
pip install anthropic   # for Claude
pip install openai      # for GPT
```

Set your API key as an environment variable (never hardcode):
```bash
export ANTHROPIC_API_KEY=your-key-here
# or
export OPENAI_API_KEY=your-key-here
```

## Quickstart

### Single run (stub pilot, no LLM needed)
```bash
python -m fe_vrp.cli run --n 100 --vehicles 10 --seed 42 --mode stub
```

### Single run (LLM pilot)
```bash
python -m fe_vrp.cli run --n 100 --vehicles 10 --seed 42 --mode llm --llm_provider openai
```

### Baseline comparison
```bash
python -m fe_vrp.cli baseline --n 100 --seed 42
```

### Scaling experiments (baseline vs hybrid at n=50,100,200,400,800)
```bash
python -m fe_vrp.cli scale --seeds 3 --mode stub
```

Outputs `results/scale_results.csv` and `results/scale_summary.json`.

### Run tests
```bash
python -m fe_vrp.tests
```

## Architecture

```
ENGINE (Python search loop)
  ↓ sends iteration packet (JSON)
PILOT (Calibrated AI or stub)
  ↓ returns decision JSON
ENGINE applies decision
```

### Key components

| File | Role |
|------|------|
| `types.py` | Dataclasses: Instance, Candidate, PilotDecision, ParadoxEntry, Pattern |
| `instance.py` | VRP instance generation + loading |
| `evaluate.py` | Fitness calc, geometry metrics, repair |
| `operators.py` | Mutation ops (swap, relocate, reverse, cross_exchange) + pattern injection ops |
| `paradox.py` | Paradox gating (4 gates) + buffer (k=5) + scoring |
| `pattern_mining.py` | Extract cluster/spine/depot-leg patterns from paradox memory |
| `pilot.py` | PilotAdapter (stub + LLM), calibration gate, strict JSON validation |
| `engine.py` | FE search loop integrating all components |
| `baseline.py` | Baseline solver (greedy + mutation + local search, no paradox/pilot) |
| `scale.py` | Scaling harness for n=50..800 |
| `cli.py` | CLI entry points |
| `tests.py` | Unit tests |

### Calibration Protocol (CONEXUS-STEEL-04)

Before LLM steering is allowed, the pilot must return this exact JSON:
```json
{"CALIBRATED": true, "protocol": "CONEXUS-STEEL-04", "pilot_mode": "PARADOX_HOLD"}
```

No extra keys. No deviations. If not received, engine blocks pilot control and falls back to stub.

### Paradox Buffer Rules

- Size ≈ 5, memory-only
- **NEVER used as parents** — only mined for patterns
- Preserve: clusters, short-edge spines, balanced loads
- Discard: collapse solutions, trivial symmetry
- Four gates: bad, geometrically informative, not collapse trap, convertible

### Pattern Injection Ops

Pilot can request: `CLUSTER_LOCK`, `SPINE_SPLIT`, `CAPACITY_REPAIR`, `DEPOT_LEG_MIN`

### Operating Principle

> Hold paradox before optimizing. Preserve structural diversity. Avoid premature convergence. Steer search, don't compute it.

## CLI Reference

```
python -m fe_vrp.cli run [options]
  --n           Number of customers (default: 100)
  --vehicles    Number of vehicles (default: n/10)
  --capacity    Vehicle capacity (auto-computed if omitted)
  --seed        Random seed (default: 42)
  --mode        stub | llm (default: stub)
  --llm_provider openai | anthropic (default: openai)
  --max_gens    Max generations (default: 200)
  --pop_size    Population size (default: 20)

python -m fe_vrp.cli baseline [options]
  (same as run, minus --mode and --llm_provider)

python -m fe_vrp.cli scale [options]
  --sizes       Comma-separated sizes (default: 50,100,200,400,800)
  --seeds       Seeds per size (default: 3)
  --output_dir  Output directory (default: results)
  (plus --mode, --llm_provider, --max_gens, --pop_size)
```
