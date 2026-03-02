"""
ISOLATION TEST: Which V2 change killed FE's advantage?

From v1_exact_reproduction.py we learned:
  - V1 FE = 67% success, V1 MC = 0% success (massive FE advantage)
  - Adding SA to MC: no effect (0% -> 0%)
  - Removing free restarts from FE: no effect (67% -> 68%)
  - So the culprit is NOT SA and NOT restart removal

This script tests the remaining V2 changes in isolation:
  A) V1 mutations + V2 connectivity check (is_valid with connectivity)
  B) V2 physics-compliant mutations + V1 validity (self-avoidance only)
  C) Different sequence (V2 uses seed-generated, V1 uses hardcoded)
  D) Different threshold (V2 uses pilot-derived, V1 uses hardcoded -9.23)

The goal: find the ONE change that breaks FE dominance.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime
from scipy import stats
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

@dataclass
class Conformation3D:
    positions: List[Tuple[int, int, int]]
    energy: float
    sequence: str

DIRECTIONS_3D = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]

_ROTATIONS_90 = []
for _axis in range(3):
    for _sign in (1, -1):
        _a1 = (_axis + 1) % 3
        _a2 = (_axis + 2) % 3
        _mat = [0] * 9
        _mat[_axis * 3 + _axis] = 1
        _mat[_a1 * 3 + _a1] = 0
        _mat[_a1 * 3 + _a2] = -_sign
        _mat[_a2 * 3 + _a1] = _sign
        _mat[_a2 * 3 + _a2] = 0
        _ROTATIONS_90.append(tuple(_mat))

def _apply_rotation(mat, vec):
    return (
        mat[0]*vec[0] + mat[1]*vec[1] + mat[2]*vec[2],
        mat[3]*vec[0] + mat[4]*vec[1] + mat[5]*vec[2],
        mat[6]*vec[0] + mat[7]*vec[1] + mat[8]*vec[2],
    )

def _manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])

class HP3DLattice:
    def __init__(self, sequence):
        self.sequence = sequence
        self.length = len(sequence)

    def calculate_energy(self, positions):
        energy = 0
        for i in range(len(positions)):
            if self.sequence[i] == 'P':
                continue
            for j in range(i+2, len(positions)):
                if self.sequence[j] == 'P':
                    continue
                if _manhattan(positions[i], positions[j]) == 1:
                    energy -= 1
        return energy

    def is_valid_v1(self, positions):
        return len(positions) == len(set(positions))

    def is_valid_v2(self, positions):
        if len(positions) != len(set(positions)):
            return False
        for i in range(len(positions) - 1):
            if _manhattan(positions[i], positions[i+1]) != 1:
                return False
        return True

    def random_walk(self, seed):
        rng = np.random.RandomState(seed)
        positions = [(0, 0, 0)]
        for i in range(1, self.length):
            placed = False
            for _ in range(100):
                d = DIRECTIONS_3D[rng.randint(0, 6)]
                new_pos = (positions[-1][0]+d[0], positions[-1][1]+d[1], positions[-1][2]+d[2])
                if new_pos not in positions:
                    positions.append(new_pos)
                    placed = True
                    break
            if not placed:
                return self.random_walk(seed + 1)
        energy = self.calculate_energy(positions)
        return Conformation3D(list(positions), energy, self.sequence)

    # V2 physics-compliant moves
    def _try_end_move(self, positions, rng):
        n = len(positions)
        if rng.random() < 0.5:
            idx, anchor = 0, 1
        else:
            idx, anchor = n-1, n-2
        occupied = set(positions)
        anchor_pos = positions[anchor]
        candidates = []
        for d in DIRECTIONS_3D:
            new_pos = (anchor_pos[0]+d[0], anchor_pos[1]+d[1], anchor_pos[2]+d[2])
            if new_pos not in occupied or new_pos == positions[idx]:
                if new_pos != positions[idx] and new_pos in occupied:
                    continue
                candidates.append(new_pos)
        if not candidates:
            return None
        new_positions = list(positions)
        new_positions[idx] = candidates[rng.randint(0, len(candidates))]
        return new_positions

    def _try_crankshaft_move(self, positions, rng):
        n = len(positions)
        if n < 3:
            return None
        eligible = []
        for i in range(1, n-1):
            if _manhattan(positions[i-1], positions[i+1]) == 2:
                eligible.append(i)
        if not eligible:
            return None
        idx = eligible[rng.randint(0, len(eligible))]
        new_pos = (positions[idx-1][0]+positions[idx+1][0]-positions[idx][0],
                   positions[idx-1][1]+positions[idx+1][1]-positions[idx][1],
                   positions[idx-1][2]+positions[idx+1][2]-positions[idx][2])
        occupied = set(positions)
        occupied.discard(positions[idx])
        if new_pos in occupied:
            return None
        new_positions = list(positions)
        new_positions[idx] = new_pos
        return new_positions

    def _try_pivot_move(self, positions, rng):
        n = len(positions)
        if n < 3:
            return None
        pivot = rng.randint(1, n-1)
        if rng.random() < 0.5:
            tail_indices = list(range(0, pivot))
        else:
            tail_indices = list(range(pivot+1, n))
        if not tail_indices:
            return None
        rot = _ROTATIONS_90[rng.randint(0, len(_ROTATIONS_90))]
        pivot_pos = positions[pivot]
        new_positions = list(positions)
        new_occupied = set()
        for i in range(n):
            if i not in tail_indices:
                new_occupied.add(positions[i])
        for i in tail_indices:
            rel = (positions[i][0]-pivot_pos[0], positions[i][1]-pivot_pos[1], positions[i][2]-pivot_pos[2])
            rotated = _apply_rotation(rot, rel)
            new_pos = (rotated[0]+pivot_pos[0], rotated[1]+pivot_pos[1], rotated[2]+pivot_pos[2])
            if new_pos in new_occupied:
                return None
            new_occupied.add(new_pos)
            new_positions[i] = new_pos
        return new_positions

    def mutate_v2(self, conf, rng, max_attempts=10):
        move_funcs = [self._try_end_move, self._try_crankshaft_move, self._try_pivot_move]
        for _ in range(max_attempts):
            rng.shuffle(move_funcs)
            for fn in move_funcs:
                new_pos = fn(list(conf.positions), rng)
                if new_pos is not None and self.is_valid_v2(new_pos):
                    new_energy = self.calculate_energy(new_pos)
                    return Conformation3D(new_pos, new_energy, conf.sequence)
        return None


# ============================================================================
# TEST A: V1 mutations + V2 connectivity check
# (Does adding connectivity check to is_valid break things?)
# ============================================================================
def mc_v1mut_v2valid(sequence, max_steps, temperature, seed):
    """V1 single-point mutations but validated with connectivity check"""
    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)
    current = model.random_walk(seed)
    best = current
    for step in range(max_steps):
        new_positions = list(current.positions)
        idx = rng.randint(1, len(new_positions)-1)
        move = DIRECTIONS_3D[rng.randint(0, 6)]
        new_positions[idx] = tuple(new_positions[idx][k] + move[k] for k in range(3))
        if not model.is_valid_v2(new_positions):  # V2 connectivity check
            continue
        new_energy = model.calculate_energy(new_positions)
        delta_e = new_energy - current.energy
        if delta_e < 0 or rng.random() < np.exp(-delta_e / temperature):
            current = Conformation3D(new_positions, new_energy, sequence)
            if new_energy < best.energy:
                best = current
    return best.energy

def fe_v1mut_v2valid(sequence, pop_size, forget_rate, max_gen, seed):
    """V1 FE logic but mutations validated with connectivity check"""
    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)
    population = [model.random_walk(seed + i) for i in range(pop_size)]
    best = min(population, key=lambda x: x.energy)
    for gen in range(max_gen):
        population.sort(key=lambda x: x.energy)
        cutoff = int(pop_size * (1 - forget_rate))
        population = population[:cutoff]
        while len(population) < pop_size:
            if len(population) > 0:
                parent = population[rng.randint(0, len(population))]
                child_positions = list(parent.positions)
                idx = rng.randint(1, len(child_positions)-1)
                move = DIRECTIONS_3D[rng.randint(0, 6)]
                child_positions[idx] = tuple(child_positions[idx][k] + move[k] for k in range(3))
                if model.is_valid_v2(child_positions):  # V2 connectivity check
                    child_energy = model.calculate_energy(child_positions)
                    population.append(Conformation3D(child_positions, child_energy, sequence))
                else:
                    population.append(model.random_walk(seed + gen * pop_size + len(population)))
            else:
                population.append(model.random_walk(seed + gen * pop_size + len(population)))
        current_best = min(population, key=lambda x: x.energy)
        if current_best.energy < best.energy:
            best = current_best
    return best.energy


# ============================================================================
# TEST B: V2 physics-compliant mutations + V1 validity
# (Does switching to end/crankshaft/pivot break things?)
# ============================================================================
def mc_v2mut(sequence, max_steps, temperature, seed):
    """V2 physics-compliant mutations, static temperature"""
    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)
    current = model.random_walk(seed)
    best = current
    for step in range(max_steps):
        candidate = model.mutate_v2(current, rng, max_attempts=5)
        if candidate is None:
            continue
        delta_e = candidate.energy - current.energy
        if delta_e < 0 or rng.random() < np.exp(-delta_e / temperature):
            current = candidate
            if current.energy < best.energy:
                best = current
    return best.energy

def fe_v2mut(sequence, pop_size, forget_rate, max_gen, seed):
    """V2 physics-compliant mutations in FE, with free restarts on failure"""
    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)
    population = [model.random_walk(seed + i) for i in range(pop_size)]
    best = min(population, key=lambda x: x.energy)
    for gen in range(max_gen):
        population.sort(key=lambda x: x.energy)
        cutoff = int(pop_size * (1 - forget_rate))
        population = population[:cutoff]
        stall = 0
        while len(population) < pop_size:
            if len(population) > 0 and stall < pop_size * 5:
                parent = population[rng.randint(0, len(population))]
                child = model.mutate_v2(parent, rng, max_attempts=5)
                if child is not None:
                    population.append(child)
                    stall = 0
                else:
                    stall += 1
            else:
                population.append(model.random_walk(seed + gen * pop_size + len(population)))
                stall = 0
        current_best = min(population, key=lambda x: x.energy)
        if current_best.energy < best.energy:
            best = current_best
    return best.energy


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    SEQ = "HPHPHPHHPHHHPHPPPHPH"
    THRESHOLD = -9.23
    N = 200
    SEEDS = list(range(42, 42 + N))

    # Also test V2's generated sequence for L=20
    rng_seq = np.random.RandomState(1337 + 20)
    SEQ_V2 = ''.join(rng_seq.choice(['H', 'P'], p=[0.5, 0.5]) for _ in range(20))

    print("=" * 70)
    print("ISOLATION TEST: Which V2 change killed FE's advantage?")
    print(f"V1 Sequence: {SEQ}")
    print(f"V2 Sequence: {SEQ_V2}")
    print(f"Trials: {N}, Threshold: {THRESHOLD}")
    print("=" * 70)

    experiments = {}

    # Baseline: V1 exact (from previous run, but re-run smaller for reference)
    print("\n[1/6] V1 MC baseline (V1 mutations, V1 validity)...")
    t0 = datetime.now()
    mc_v1_results = []
    for i, seed in enumerate(SEEDS):
        model = HP3DLattice(SEQ)
        rng = np.random.RandomState(seed)
        current = model.random_walk(seed)
        best = current
        for step in range(10000):
            new_positions = list(current.positions)
            idx = rng.randint(1, len(new_positions)-1)
            move = DIRECTIONS_3D[rng.randint(0, 6)]
            new_positions[idx] = tuple(new_positions[idx][k] + move[k] for k in range(3))
            if not model.is_valid_v1(new_positions):
                continue
            new_energy = model.calculate_energy(new_positions)
            delta_e = new_energy - current.energy
            if delta_e < 0 or rng.random() < np.exp(-delta_e / 1.0):
                current = Conformation3D(new_positions, new_energy, SEQ)
                if new_energy < best.energy:
                    best = current
        mc_v1_results.append(best.energy)
        if (i+1) % 100 == 0:
            print(f"  {i+1}/{N} ({(datetime.now()-t0).total_seconds():.1f}s)")
    experiments["V1_MC"] = mc_v1_results

    print("\n[2/6] V1 FE baseline (V1 mutations, V1 validity)...")
    t0 = datetime.now()
    fe_v1_results = []
    for i, seed in enumerate(SEEDS):
        model = HP3DLattice(SEQ)
        rng = np.random.RandomState(seed)
        population = [model.random_walk(seed + j) for j in range(50)]
        best = min(population, key=lambda x: x.energy)
        for gen in range(100):
            population.sort(key=lambda x: x.energy)
            cutoff = int(50 * 0.7)
            population = population[:cutoff]
            while len(population) < 50:
                parent = population[rng.randint(0, len(population))]
                child_pos = list(parent.positions)
                idx = rng.randint(1, len(child_pos)-1)
                move = DIRECTIONS_3D[rng.randint(0, 6)]
                child_pos[idx] = tuple(child_pos[idx][k] + move[k] for k in range(3))
                if model.is_valid_v1(child_pos):
                    child_e = model.calculate_energy(child_pos)
                    population.append(Conformation3D(child_pos, child_e, SEQ))
                else:
                    population.append(model.random_walk(seed + gen * 50 + len(population)))
            cb = min(population, key=lambda x: x.energy)
            if cb.energy < best.energy:
                best = cb
        fe_v1_results.append(best.energy)
        if (i+1) % 100 == 0:
            print(f"  {i+1}/{N} ({(datetime.now()-t0).total_seconds():.1f}s)")
    experiments["V1_FE"] = fe_v1_results

    # TEST A: V1 mutations + V2 connectivity check
    print("\n[3/6] TEST A: V1 mutations + V2 connectivity check (MC)...")
    t0 = datetime.now()
    results_a_mc = []
    for i, seed in enumerate(SEEDS):
        e = mc_v1mut_v2valid(SEQ, 10000, 1.0, seed)
        results_a_mc.append(e)
        if (i+1) % 100 == 0:
            print(f"  {i+1}/{N} ({(datetime.now()-t0).total_seconds():.1f}s)")
    experiments["A_MC_v1mut_v2valid"] = results_a_mc

    print("\n[4/6] TEST A: V1 mutations + V2 connectivity check (FE)...")
    t0 = datetime.now()
    results_a_fe = []
    for i, seed in enumerate(SEEDS):
        e = fe_v1mut_v2valid(SEQ, 50, 0.3, 100, seed)
        results_a_fe.append(e)
        if (i+1) % 100 == 0:
            print(f"  {i+1}/{N} ({(datetime.now()-t0).total_seconds():.1f}s)")
    experiments["A_FE_v1mut_v2valid"] = results_a_fe

    # TEST B: V2 physics-compliant mutations (the suspected culprit)
    print("\n[5/6] TEST B: V2 physics-compliant mutations (MC, static T)...")
    t0 = datetime.now()
    results_b_mc = []
    for i, seed in enumerate(SEEDS):
        e = mc_v2mut(SEQ, 10000, 1.0, seed)
        results_b_mc.append(e)
        if (i+1) % 100 == 0:
            print(f"  {i+1}/{N} ({(datetime.now()-t0).total_seconds():.1f}s)")
    experiments["B_MC_v2mut"] = results_b_mc

    print("\n[6/6] TEST B: V2 physics-compliant mutations (FE, free restarts)...")
    t0 = datetime.now()
    results_b_fe = []
    for i, seed in enumerate(SEEDS):
        e = fe_v2mut(SEQ, 50, 0.3, 100, seed)
        results_b_fe.append(e)
        if (i+1) % 100 == 0:
            print(f"  {i+1}/{N} ({(datetime.now()-t0).total_seconds():.1f}s)")
    experiments["B_FE_v2mut"] = results_b_fe

    # ============================================================================
    # ANALYSIS
    # ============================================================================
    print("\n" + "=" * 70)
    print("ISOLATION TEST RESULTS")
    print("=" * 70)

    for name, energies in experiments.items():
        arr = np.array(energies)
        success = np.mean(arr <= THRESHOLD) * 100
        print(f"\n{name}:")
        print(f"  Mean energy: {arr.mean():.3f} ± {arr.std():.3f}")
        print(f"  Min: {arr.min():.1f}, Max: {arr.max():.1f}")
        print(f"  Success rate (E <= {THRESHOLD}): {success:.1f}%")

    print("\n" + "=" * 70)
    print("DIAGNOSIS: FE-MC GAP BY CONDITION")
    print("=" * 70)

    pairs = [
        ("BASELINE (V1)", "V1_FE", "V1_MC"),
        ("TEST A: + V2 connectivity check", "A_FE_v1mut_v2valid", "A_MC_v1mut_v2valid"),
        ("TEST B: + V2 physics mutations", "B_FE_v2mut", "B_MC_v2mut"),
    ]

    for label, fe_key, mc_key in pairs:
        fe = np.array(experiments[fe_key])
        mc = np.array(experiments[mc_key])
        fe_succ = np.mean(fe <= THRESHOLD) * 100
        mc_succ = np.mean(mc <= THRESHOLD) * 100
        gap = fe.mean() - mc.mean()
        d = gap / np.sqrt((fe.std()**2 + mc.std()**2) / 2)
        u, p = stats.mannwhitneyu(fe, mc, alternative='less')
        print(f"\n{label}:")
        print(f"  FE: {fe.mean():.3f} (success {fe_succ:.1f}%)")
        print(f"  MC: {mc.mean():.3f} (success {mc_succ:.1f}%)")
        print(f"  Gap (FE - MC): {gap:.3f}")
        print(f"  Cohen's d: {d:.3f}")
        print(f"  p-value: {p:.6f}")
        if fe_succ > mc_succ:
            print(f"  >>> FE WINS by {fe_succ - mc_succ:.1f} percentage points")
        elif mc_succ > fe_succ:
            print(f"  >>> MC WINS by {mc_succ - fe_succ:.1f} percentage points")
        else:
            print(f"  >>> TIE")
