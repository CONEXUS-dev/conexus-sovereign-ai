"""
FE Protein Folding Scaling Study — Experiment Runner

Two-phase orchestrator for Option B full scaling sweep.
  Phase A (Pilot): 200 FE + 200 MC per length → lock E*(L) thresholds
  Phase B (Main):  2000 FE + 2000 MC per length using locked E*(L)

Usage:
  python run_experiment.py --phase A                    # Run all pilot
  python run_experiment.py --phase B                    # Run all main
  python run_experiment.py --phase A --length 20        # Pilot for L=20 only
  python run_experiment.py --phase B --length 20        # Main for L=20 only
  python run_experiment.py --all                        # Full sweep (A then B)

Patent Reference: US 63/898,911
"""

import argparse
import csv
import json
import os
import sys
import time
from hp_lattice_3d import (
    generate_sequence,
    monte_carlo_3d,
    forgetting_engine_3d,
)

# ============================================================================
# LOAD CONFIG
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(SCRIPT_DIR, "config.json")) as f:
    CONFIG = json.load(f)

LENGTHS = CONFIG["lengths"]
PILOT_TRIALS = CONFIG["pilot_trials_per_algorithm"]
MAIN_TRIALS = CONFIG["trials_per_algorithm"]
MC_PARAMS = CONFIG["mc"]
FE_PARAMS = CONFIG["fe"]

RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
INSTANCES_DIR = os.path.join(SCRIPT_DIR, "instances")
LOGS_DIR = os.path.join(SCRIPT_DIR, "logs")

CSV_FIELDS = [
    "length", "algorithm", "trial_id", "seed", "final_energy",
    "success_flag", "convergence_gen", "runtime_ms", "paradox_activity",
]


# ============================================================================
# HELPERS
# ============================================================================

def make_seed(length: int, trial_index: int) -> int:
    """Unique seed per length and trial. No reuse across lengths."""
    return length * 10000 + trial_index


def get_sequence(length: int) -> str:
    """Get or generate the HP sequence for a given length."""
    seq_path = os.path.join(INSTANCES_DIR, f"sequence_L{length}.txt")
    if os.path.exists(seq_path):
        with open(seq_path) as f:
            return f.read().strip()
    seq = generate_sequence(length, seed=1337 + length)
    with open(seq_path, "w") as f:
        f.write(seq)
    return seq


def load_thresholds() -> dict:
    """Load locked E*(L) thresholds from Phase A results."""
    path = os.path.join(RESULTS_DIR, "pilot_thresholds.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def save_thresholds(thresholds: dict):
    """Save locked E*(L) thresholds."""
    path = os.path.join(RESULTS_DIR, "pilot_thresholds.json")
    with open(path, "w") as f:
        json.dump(thresholds, f, indent=2)


def csv_path(phase: str, length: int) -> str:
    return os.path.join(RESULTS_DIR, f"phase_{phase}_L{length}.csv")


def run_trial(algorithm: str, sequence: str, seed: int) -> dict:
    """Run a single trial. Returns result dict."""
    if algorithm == "MC":
        return monte_carlo_3d(
            sequence,
            max_steps=MC_PARAMS["max_steps"],
            temperature=MC_PARAMS["temperature"],
            seed=seed,
        )
    else:
        return forgetting_engine_3d(
            sequence,
            pop_size=FE_PARAMS["pop_size"],
            forget_rate=FE_PARAMS["forget_rate"],
            max_gen=FE_PARAMS["max_gen"],
            seed=seed,
        )


# ============================================================================
# PHASE A — PILOT
# ============================================================================

def run_phase_a(lengths: list):
    """Run pilot trials to establish E*(L) thresholds."""
    print("=" * 70)
    print("PHASE A — PILOT (establishing thresholds)")
    print("=" * 70)

    thresholds = load_thresholds()

    for L in lengths:
        if str(L) in thresholds:
            print(f"\n  L={L}: threshold already locked at E*={thresholds[str(L)]}")
            continue

        sequence = get_sequence(L)
        print(f"\n  L={L} | sequence={sequence[:30]}{'...' if len(sequence) > 30 else ''}")
        print(f"  Running {PILOT_TRIALS} MC + {PILOT_TRIALS} FE trials...")

        out_path = csv_path("A", L)
        best_energy = 0.0
        t0 = time.time()

        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()

            for algo in ["MC", "FE"]:
                for i in range(PILOT_TRIALS):
                    seed = make_seed(L, i) if algo == "MC" else make_seed(L, PILOT_TRIALS + i)
                    result = run_trial(algo, sequence, seed)
                    energy = result["final_energy"]
                    if energy < best_energy:
                        best_energy = energy

                    writer.writerow({
                        "length": L,
                        "algorithm": algo,
                        "trial_id": i,
                        "seed": seed,
                        "final_energy": energy,
                        "success_flag": "",  # determined after threshold lock
                        "convergence_gen": result["convergence_generation"],
                        "runtime_ms": round(result["computation_time_ms"], 2),
                        "paradox_activity": result["paradox_buffer_activity"],
                    })

                    if (i + 1) % 50 == 0:
                        print(f"    {algo} {i+1}/{PILOT_TRIALS} done")

        elapsed = time.time() - t0
        thresholds[str(L)] = best_energy
        save_thresholds(thresholds)
        print(f"  L={L} LOCKED: E*={best_energy} ({elapsed:.1f}s)")

    print("\n" + "=" * 70)
    print("PHASE A COMPLETE — Thresholds locked:")
    for L in lengths:
        print(f"  L={L}: E*={thresholds.get(str(L), '???')}")
    print("=" * 70)


# ============================================================================
# PHASE B — MAIN
# ============================================================================

def run_phase_b(lengths: list):
    """Run main trials using locked E*(L) thresholds."""
    thresholds = load_thresholds()

    missing = [L for L in lengths if str(L) not in thresholds]
    if missing:
        print(f"ERROR: No thresholds for lengths {missing}. Run Phase A first.")
        sys.exit(1)

    print("=" * 70)
    print("PHASE B — MAIN (using locked thresholds)")
    print("=" * 70)

    for L in lengths:
        e_star = thresholds[str(L)]
        sequence = get_sequence(L)
        print(f"\n  L={L} | E*={e_star} | sequence={sequence[:30]}{'...' if len(sequence) > 30 else ''}")
        print(f"  Running {MAIN_TRIALS} MC + {MAIN_TRIALS} FE trials...")

        out_path = csv_path("B", L)
        t0 = time.time()

        with open(out_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()

            for algo in ["MC", "FE"]:
                for i in range(MAIN_TRIALS):
                    # Offset seeds from pilot range
                    seed = make_seed(L, 5000 + i) if algo == "MC" else make_seed(L, 5000 + MAIN_TRIALS + i)
                    result = run_trial(algo, sequence, seed)
                    energy = result["final_energy"]

                    writer.writerow({
                        "length": L,
                        "algorithm": algo,
                        "trial_id": i,
                        "seed": seed,
                        "final_energy": energy,
                        "success_flag": 1 if energy <= e_star else 0,
                        "convergence_gen": result["convergence_generation"],
                        "runtime_ms": round(result["computation_time_ms"], 2),
                        "paradox_activity": result["paradox_buffer_activity"],
                    })

                    if (i + 1) % 250 == 0:
                        elapsed_so_far = time.time() - t0
                        total_done = (MAIN_TRIALS if algo == "FE" else 0) + i + 1
                        total_all = MAIN_TRIALS * 2
                        rate = total_done / elapsed_so_far if elapsed_so_far > 0 else 0
                        eta = (total_all - total_done) / rate if rate > 0 else 0
                        print(f"    {algo} {i+1}/{MAIN_TRIALS} done "
                              f"({elapsed_so_far:.0f}s elapsed, ~{eta:.0f}s remaining)")

        elapsed = time.time() - t0
        print(f"  L={L} COMPLETE ({elapsed:.1f}s)")

    print("\n" + "=" * 70)
    print("PHASE B COMPLETE")
    print("=" * 70)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="FE Protein Folding Scaling Study — Experiment Runner"
    )
    parser.add_argument("--phase", choices=["A", "B"], help="Run Phase A (pilot) or Phase B (main)")
    parser.add_argument("--length", type=int, help="Run only this length (default: all)")
    parser.add_argument("--all", action="store_true", help="Run full sweep (Phase A then B)")

    args = parser.parse_args()

    lengths = [args.length] if args.length else LENGTHS

    # Validate length
    if args.length and args.length not in LENGTHS:
        print(f"ERROR: Length {args.length} not in config. Valid: {LENGTHS}")
        sys.exit(1)

    if args.all:
        run_phase_a(lengths)
        run_phase_b(lengths)
    elif args.phase == "A":
        run_phase_a(lengths)
    elif args.phase == "B":
        run_phase_b(lengths)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
