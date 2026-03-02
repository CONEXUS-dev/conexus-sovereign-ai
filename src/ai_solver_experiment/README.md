# AI Solver Experiment — Controlled ECP Calibration Behavioral Study

## Objective

Measure whether structured AI calibration (ECP protocol) shifts proposal distribution and convergence behavior in an iterative VRP optimization loop.

Not performance alone. **Behavior.**

## Architecture

```
ai_solver_experiment/
    ├── __init__.py              # Package init
    ├── __main__.py              # CLI entry point
    ├── vrp_instance.py          # VRP instance generation (seeded, reproducible)
    ├── evaluator.py             # Deterministic Python evaluator
    ├── baseline.py              # Clarke-Wright savings algorithm
    ├── calibration_protocols.py # ECP as structured prompt injection
    ├── ai_proposal_engine.py    # LLM proposal engine (Anthropic/OpenAI/Gemini)
    ├── iterative_loop.py        # Propose/evaluate/feedback/refine cycle
    ├── metrics.py               # Behavioral metrics (entropy, convergence, escape)
    ├── experiment_runner.py     # Experiment orchestrator + CLI
    ├── results_logger.py        # JSON, CSV, convergence curve output
    └── requirements.txt         # Python dependencies
```

## Three Conditions

| Condition | Description |
|-----------|-------------|
| **A) Baseline** | Clarke-Wright deterministic solver. No AI. |
| **B) Uncalibrated** | AI proposes routes → Python evaluates → feedback loop. No ECP. |
| **C) Calibrated** | Same loop, same evaluator, same constraints. Only difference = ECP calibration injected before solving. |

Everything else identical. That's how you isolate variables.

## What We Measure

### Proposal Distribution
- Route entropy (Shannon entropy of structural hashes)
- Unique proposal ratio
- Average change magnitude between consecutive proposals

### Convergence
- Iterations to plateau
- Improvement slope (linear regression)
- Variance reduction over time

### Escape Behavior
- Stagnation period detection
- Local minima escape count
- Average improvement after escaping stagnation

### Constraint Violations
- Violation frequency across iterations
- Violation trend (improving or worsening)

### Final Performance
- % improvement vs Clarke-Wright baseline
- Best distance achieved
- Feasibility rate

## Setup

```bash
# Install dependencies (only need the provider you'll use)
pip install anthropic        # for Claude
pip install openai           # for GPT-4
pip install google-generativeai  # for Gemini
```

Set your API key:
```bash
# Pick one:
$env:ANTHROPIC_API_KEY = "sk-..."
$env:OPENAI_API_KEY = "sk-..."
$env:GEMINI_API_KEY = "..."
```

## Usage

### Quick Smoke Test
```bash
python -m ai_solver_experiment --sizes 20 --seeds 1 --iterations 5
```

### Medium Run (recommended first)
```bash
python -m ai_solver_experiment --sizes 100 --seeds 3 --iterations 20
```

### Full Experiment
```bash
python -m ai_solver_experiment --sizes 100,200,500 --seeds 5 --iterations 50
```

### Specific Conditions Only
```bash
# Just baseline + calibrated (skip uncalibrated to save API cost)
python -m ai_solver_experiment --sizes 100 --seeds 3 --conditions baseline,calibrated

# Just baseline (no API calls)
python -m ai_solver_experiment --sizes 100,200,500 --seeds 5 --conditions baseline
```

### Use Gemini
```bash
$env:GEMINI_API_KEY = "..."
python -m ai_solver_experiment --provider gemini --sizes 100 --seeds 3
```

### Use OpenAI
```bash
$env:OPENAI_API_KEY = "sk-..."
python -m ai_solver_experiment --provider openai --sizes 100 --seeds 3
```

## Output

Results are saved to `results/ecp_experiment/` (configurable with `--output`):

| File | Contents |
|------|----------|
| `experiment_config.json` | Full experiment configuration |
| `experiment_results.json` | Aggregate results and metrics |
| `experiment_summary.csv` | One row per run, all key metrics |
| `convergence_curves.csv` | Per-iteration fitness for plotting |
| `diversity_metrics.csv` | Per-iteration structural similarity |
| `{condition}_{instance}_s{seed}.json` | Full per-run data |
| `raw_responses/{...}_raw.json` | Complete LLM responses |

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--sizes` | `100,200,500` | Comma-separated customer counts |
| `--seeds` | `5` | Number of random seeds |
| `--iterations` | `50` | Iteration budget per AI run |
| `--provider` | `anthropic` | LLM backend (anthropic/openai/gemini) |
| `--model` | auto | Model override |
| `--output` | `results/ecp_experiment` | Output directory |
| `--pacing` | `1.0` | Seconds between LLM calls |
| `--conditions` | `baseline,uncalibrated,calibrated` | Which conditions to run |
| `--quiet` | off | Suppress verbose output |

## Design Principles

- **No metaphysical framing.** Calibration = structured prompt injection. Period.
- **Reproducibility.** All randomness controlled by seed. Fixed iteration budget.
- **Separation of concerns.** Evaluator knows nothing about AI. AI knows nothing about metrics.
- **Log everything.** Every proposal, every score, every violation, every LLM response.
- **No black boxes.** Every decision is traceable.

## What Success Looks Like

If calibration shifts behavior, it shows up in:
- Proposal entropy (different distribution of solutions)
- Escape behavior (different response to stagnation)
- Convergence slope (different improvement trajectory)
- Iteration efficiency (different path to best solution)

If it doesn't, we learn that too. Either outcome is progress.
