"""
V1 EXACT REPRODUCTION
Reproduces the original V1 validation study code EXACTLY as found in:
  DOMAIN DATA/protein_folding_3d/protein_folding_3d_forgetting_engine_validation_study.py

Purpose: Confirm we can reproduce 25.8% FE vs 3.9% MC (or close to it)
Then: Systematically isolate which V2 change killed FE's advantage

Sequence: HPHPHPHHPHHHPHPPPHPH (L=20)
MC: 10000 steps, T=1.0 (static), single-point mutation, no connectivity check
FE: pop=50, forget=0.3, gen=100, inert paradox buffer, free random restarts
Threshold: -9.23 (hardcoded)
Seeds: 42..2041 (2000 trials per algorithm)
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
from datetime import datetime
from scipy import stats
import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

@dataclass
class Conformation3D:
    positions: List[Tuple[int, int, int]]
    energy: float
    sequence: str

class HP3DLattice:
    def __init__(self, sequence: str):
        self.sequence = sequence
        self.length = len(sequence)
        self.moves = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]

    def calculate_energy(self, positions):
        energy = 0
        for i in range(len(positions)):
            if self.sequence[i] == 'P':
                continue
            for j in range(i+2, len(positions)):
                if self.sequence[j] == 'P':
                    continue
                dist = sum(abs(positions[i][k] - positions[j][k]) for k in range(3))
                if dist == 1:
                    energy -= 1
        return energy

    def is_valid_v1(self, positions):
        """V1: self-avoidance ONLY (no connectivity check)"""
        return len(positions) == len(set(positions))

    def is_valid_v2(self, positions):
        """V2: self-avoidance + connectivity"""
        if len(positions) != len(set(positions)):
            return False
        for i in range(len(positions) - 1):
            dist = sum(abs(positions[i][k] - positions[i+1][k]) for k in range(3))
            if dist != 1:
                return False
        return True

    def random_walk(self, seed):
        rng = np.random.RandomState(seed)
        positions = [(0, 0, 0)]
        for i in range(1, self.length):
            attempts = 0
            while attempts < 100:
                move = self.moves[rng.randint(0, 6)]
                new_pos = tuple(positions[-1][k] + move[k] for k in range(3))
                if new_pos not in positions:
                    positions.append(new_pos)
                    break
                attempts += 1
            if len(positions) != i + 1:
                return self.random_walk(seed + 1)
        energy = self.calculate_energy(positions)
        return Conformation3D(positions, energy, self.sequence)


# ============================================================================
# V1 EXACT MC (static temperature, no connectivity check)
# ============================================================================
def mc_v1(sequence, max_steps, temperature, seed):
    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)
    current = model.random_walk(seed)
    best = current
    for step in range(max_steps):
        new_positions = list(current.positions)
        idx = rng.randint(1, len(new_positions)-1)
        move = model.moves[rng.randint(0, 6)]
        new_positions[idx] = tuple(new_positions[idx][k] + move[k] for k in range(3))
        if not model.is_valid_v1(new_positions):
            continue
        new_energy = model.calculate_energy(new_positions)
        delta_e = new_energy - current.energy
        if delta_e < 0 or rng.random() < np.exp(-delta_e / temperature):
            current = Conformation3D(new_positions, new_energy, sequence)
            if new_energy < best.energy:
                best = current
    return best.energy

# ============================================================================
# V1 EXACT FE (inert paradox buffer, free random restarts)
# ============================================================================
def fe_v1(sequence, pop_size, forget_rate, max_gen, seed):
    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)
    population = [model.random_walk(seed + i) for i in range(pop_size)]
    paradox_buffer = []
    paradox_count = 0
    best = min(population, key=lambda x: x.energy)

    for gen in range(max_gen):
        population.sort(key=lambda x: x.energy)
        cutoff = int(pop_size * (1 - forget_rate))
        forgotten = population[cutoff:]
        population = population[:cutoff]

        for conf in forgotten:
            if rng.random() < 0.1:
                paradox_buffer.append(conf)
                paradox_count += 1

        while len(population) < pop_size:
            if len(population) > 0:
                parent = population[rng.randint(0, len(population))]
                child_positions = list(parent.positions)
                idx = rng.randint(1, len(child_positions)-1)
                move = model.moves[rng.randint(0, 6)]
                child_positions[idx] = tuple(child_positions[idx][k] + move[k] for k in range(3))
                if model.is_valid_v1(child_positions):
                    child_energy = model.calculate_energy(child_positions)
                    population.append(Conformation3D(child_positions, child_energy, sequence))
                else:
                    # FREE RANDOM RESTART (V1 behavior)
                    population.append(model.random_walk(seed + gen * pop_size + len(population)))
            else:
                population.append(model.random_walk(seed + gen * pop_size + len(population)))

        current_best = min(population, key=lambda x: x.energy)
        if current_best.energy < best.energy:
            best = current_best

    return best.energy, paradox_count

# ============================================================================
# V2-LIKE MC (simulated annealing, V1 mutations but with connectivity check)
# ============================================================================
def mc_v2_sa(sequence, max_steps, seed, T_start=1.0, T_min=0.01):
    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)
    current = model.random_walk(seed)
    best = current
    for step in range(max_steps):
        T = T_start * (T_min / T_start) ** (step / max_steps)
        new_positions = list(current.positions)
        idx = rng.randint(1, len(new_positions)-1)
        move = model.moves[rng.randint(0, 6)]
        new_positions[idx] = tuple(new_positions[idx][k] + move[k] for k in range(3))
        if not model.is_valid_v1(new_positions):  # still V1 physics for isolation
            continue
        new_energy = model.calculate_energy(new_positions)
        delta_e = new_energy - current.energy
        if delta_e < 0 or rng.random() < np.exp(-delta_e / max(T, 1e-10)):
            current = Conformation3D(new_positions, new_energy, sequence)
            if new_energy < best.energy:
                best = current
    return best.energy

# ============================================================================
# HYBRID: V1 FE but NO free random restarts (reject + retry instead)
# ============================================================================
def fe_no_free_restarts(sequence, pop_size, forget_rate, max_gen, seed):
    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)
    population = [model.random_walk(seed + i) for i in range(pop_size)]
    best = min(population, key=lambda x: x.energy)

    for gen in range(max_gen):
        population.sort(key=lambda x: x.energy)
        cutoff = int(pop_size * (1 - forget_rate))
        population = population[:cutoff]

        attempts = 0
        max_attempts = pop_size * 20
        while len(population) < pop_size and attempts < max_attempts:
            attempts += 1
            if len(population) > 0:
                parent = population[rng.randint(0, len(population))]
                child_positions = list(parent.positions)
                idx = rng.randint(1, len(child_positions)-1)
                move = model.moves[rng.randint(0, 6)]
                child_positions[idx] = tuple(child_positions[idx][k] + move[k] for k in range(3))
                if model.is_valid_v1(child_positions):
                    child_energy = model.calculate_energy(child_positions)
                    population.append(Conformation3D(child_positions, child_energy, sequence))
            # NO random_walk fallback — just retry

        # Fill remaining if stuck
        while len(population) < pop_size:
            population.append(model.random_walk(seed + gen * pop_size + len(population)))

        current_best = min(population, key=lambda x: x.energy)
        if current_best.energy < best.energy:
            best = current_best

    return best.energy

# ============================================================================
# MAIN: RUN ALL EXPERIMENTS
# ============================================================================
if __name__ == "__main__":
    SEQ = "HPHPHPHHPHHHPHPPPHPH"
    THRESHOLD = -9.23
    N_TRIALS = 200  # 200 for speed; V1 used 2000
    SEEDS = list(range(42, 42 + N_TRIALS))

    print("=" * 70)
    print("V1 EXACT REPRODUCTION + ISOLATION TESTS")
    print(f"Sequence: {SEQ} (L={len(SEQ)})")
    print(f"Trials: {N_TRIALS} per algorithm")
    print(f"Threshold: {THRESHOLD}")
    print("=" * 70)

    configs = {
        "V1_MC":        ("MC static T=1.0, V1 physics", None),
        "V1_FE":        ("FE inert paradox, free restarts, V1 physics", None),
        "V2_MC_SA":     ("MC with SA (T: 1.0->0.01), V1 physics", None),
        "FE_NO_RESTART":("FE no free restarts, V1 physics", None),
    }

    results = {k: [] for k in configs}

    print("\n[1/4] Running V1 MC (static T=1.0)...")
    t0 = datetime.now()
    for i, seed in enumerate(SEEDS):
        e = mc_v1(SEQ, 10000, 1.0, seed)
        results["V1_MC"].append(e)
        if (i+1) % 50 == 0:
            elapsed = (datetime.now() - t0).total_seconds()
            print(f"  {i+1}/{N_TRIALS} done ({elapsed:.1f}s)")

    print("\n[2/4] Running V1 FE (inert paradox, free restarts)...")
    t0 = datetime.now()
    for i, seed in enumerate(SEEDS):
        e, _ = fe_v1(SEQ, 50, 0.3, 100, seed)
        results["V1_FE"].append(e)
        if (i+1) % 50 == 0:
            elapsed = (datetime.now() - t0).total_seconds()
            print(f"  {i+1}/{N_TRIALS} done ({elapsed:.1f}s)")

    print("\n[3/4] Running V2 MC with SA (T: 1.0->0.01)...")
    t0 = datetime.now()
    for i, seed in enumerate(SEEDS):
        e = mc_v2_sa(SEQ, 10000, seed)
        results["V2_MC_SA"].append(e)
        if (i+1) % 50 == 0:
            elapsed = (datetime.now() - t0).total_seconds()
            print(f"  {i+1}/{N_TRIALS} done ({elapsed:.1f}s)")

    print("\n[4/4] Running FE without free restarts...")
    t0 = datetime.now()
    for i, seed in enumerate(SEEDS):
        e = fe_no_free_restarts(SEQ, 50, 0.3, 100, seed)
        results["FE_NO_RESTART"].append(e)
        if (i+1) % 50 == 0:
            elapsed = (datetime.now() - t0).total_seconds()
            print(f"  {i+1}/{N_TRIALS} done ({elapsed:.1f}s)")

    # ============================================================================
    # ANALYSIS
    # ============================================================================
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    for name, energies in results.items():
        arr = np.array(energies)
        success = np.mean(arr <= THRESHOLD) * 100
        print(f"\n{name}:")
        print(f"  Mean energy: {arr.mean():.3f} ± {arr.std():.3f}")
        print(f"  Min energy:  {arr.min():.1f}")
        print(f"  Success rate (E <= {THRESHOLD}): {success:.1f}%")

    # Key comparisons
    print("\n" + "=" * 70)
    print("KEY COMPARISONS (Mann-Whitney U, one-tailed)")
    print("=" * 70)

    comparisons = [
        ("V1: FE vs MC", "V1_FE", "V1_MC"),
        ("SA effect: V2_MC_SA vs V1_MC", "V2_MC_SA", "V1_MC"),
        ("Restart effect: FE_NO_RESTART vs V1_FE", "FE_NO_RESTART", "V1_FE"),
        ("Fair fight: V1_FE vs V2_MC_SA", "V1_FE", "V2_MC_SA"),
    ]

    for label, a, b in comparisons:
        arr_a = np.array(results[a])
        arr_b = np.array(results[b])
        u, p = stats.mannwhitneyu(arr_a, arr_b, alternative='less')
        d = (arr_a.mean() - arr_b.mean()) / np.sqrt((arr_a.std()**2 + arr_b.std()**2) / 2)
        succ_a = np.mean(arr_a <= THRESHOLD) * 100
        succ_b = np.mean(arr_b <= THRESHOLD) * 100
        print(f"\n{label}:")
        print(f"  {a}: {arr_a.mean():.3f} (success {succ_a:.1f}%)")
        print(f"  {b}: {arr_b.mean():.3f} (success {succ_b:.1f}%)")
        print(f"  Cohen's d: {d:.3f}")
        print(f"  p-value: {p:.6f}")

    # Save results
    outpath = os.path.join(SCRIPT_DIR, "results", "v1_reproduction_results.csv")
    os.makedirs(os.path.join(SCRIPT_DIR, "results"), exist_ok=True)
    with open(outpath, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["trial", "V1_MC", "V1_FE", "V2_MC_SA", "FE_NO_RESTART"])
        for i in range(N_TRIALS):
            w.writerow([i, results["V1_MC"][i], results["V1_FE"][i],
                        results["V2_MC_SA"][i], results["FE_NO_RESTART"][i]])
    print(f"\nResults saved to {outpath}")
