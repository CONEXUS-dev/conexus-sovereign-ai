"""
3D HP Lattice Protein Folding — Core Algorithms  (Version 2)

Refactored from validated study (FE-3D-PF-2025-10-27) to fix three
architectural flaws identified during external audit:

  1. Physics compliance — mutations now use end, crankshaft, and pivot
     moves that preserve covalent bond connectivity (distance-1 between
     consecutive residues). is_valid() enforces both self-avoidance AND
     chain connectivity.

  2. Active paradox buffer — retained states are re-injected into the
     population during the FE repopulation phase, not just logged.

  3. Fair baseline — Monte Carlo uses simulated annealing with
     exponential temperature decay. Invalid moves are handled
     symmetrically (reject & retry) in both algorithms. No free
     random_walk restarts.

Patent Reference: US 63/898,911
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Conformation3D:
    positions: List[Tuple[int, int, int]]
    energy: float
    sequence: str


# ============================================================================
# 3D HP LATTICE MODEL  (Version 2 — physics-compliant)
# ============================================================================

# Six cardinal directions on a 3D cubic lattice
DIRECTIONS_3D = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]

# 90-degree rotation matrices about each axis (24 orientations total, but we
# only need the 9 non-identity 90° rotations for pivot moves).
_ROTATIONS_90 = []
for _axis in range(3):
    for _sign in (1, -1):
        # Build a 90-degree rotation around _axis with direction _sign
        _a1 = (_axis + 1) % 3
        _a2 = (_axis + 2) % 3
        _mat = [0] * 9  # 3x3 flat
        _mat[_axis * 3 + _axis] = 1  # axis component unchanged
        _mat[_a1 * 3 + _a1] = 0
        _mat[_a1 * 3 + _a2] = -_sign
        _mat[_a2 * 3 + _a1] = _sign
        _mat[_a2 * 3 + _a2] = 0
        _ROTATIONS_90.append(tuple(_mat))


def _apply_rotation(mat: tuple, vec: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Apply a 3x3 rotation matrix (flat tuple) to a 3D vector."""
    return (
        mat[0] * vec[0] + mat[1] * vec[1] + mat[2] * vec[2],
        mat[3] * vec[0] + mat[4] * vec[1] + mat[5] * vec[2],
        mat[6] * vec[0] + mat[7] * vec[1] + mat[8] * vec[2],
    )


def _manhattan(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


class HP3DLattice:
    """3D HP lattice protein folding model with physics-compliant moves."""

    def __init__(self, sequence: str):
        self.sequence = sequence
        self.length = len(sequence)

    # ------------------------------------------------------------------
    # Energy
    # ------------------------------------------------------------------
    def calculate_energy(self, positions: List[Tuple[int, int, int]]) -> float:
        """Calculate H-H contact energy (topological contacts only)."""
        energy = 0
        for i in range(len(positions)):
            if self.sequence[i] == 'P':
                continue
            for j in range(i + 2, len(positions)):
                if self.sequence[j] == 'P':
                    continue
                if _manhattan(positions[i], positions[j]) == 1:
                    energy -= 1
        return energy

    # ------------------------------------------------------------------
    # Validity — self-avoidance AND chain connectivity
    # ------------------------------------------------------------------
    def is_valid(self, positions: List[Tuple[int, int, int]]) -> bool:
        """
        A conformation is valid iff:
          1. No two residues share the same lattice point (self-avoiding).
          2. Every consecutive pair (i, i+1) is exactly distance-1 apart
             (covalent bond integrity).
        """
        if len(positions) != len(set(positions)):
            return False
        for i in range(len(positions) - 1):
            if _manhattan(positions[i], positions[i + 1]) != 1:
                return False
        return True

    # ------------------------------------------------------------------
    # Random walk (used only for initial population seeding)
    # ------------------------------------------------------------------
    def random_walk(self, seed: int) -> Conformation3D:
        """Generate a random valid self-avoiding walk on the 3D lattice."""
        rng = np.random.RandomState(seed)
        positions = [(0, 0, 0)]

        for i in range(1, self.length):
            placed = False
            for _ in range(100):
                d = DIRECTIONS_3D[rng.randint(0, 6)]
                new_pos = (positions[-1][0] + d[0],
                           positions[-1][1] + d[1],
                           positions[-1][2] + d[2])
                if new_pos not in positions:
                    positions.append(new_pos)
                    placed = True
                    break
            if not placed:
                # Dead end — retry with bumped seed
                return self.random_walk(seed + 1)

        energy = self.calculate_energy(positions)
        return Conformation3D(list(positions), energy, self.sequence)

    # ------------------------------------------------------------------
    # Physics-compliant lattice moves
    # ------------------------------------------------------------------
    def _try_end_move(self, positions: list, rng) -> Optional[list]:
        """
        End move: move the first or last residue to a free adjacent site
        of its sole chain neighbor. Preserves connectivity by construction.
        """
        n = len(positions)
        # Choose first (idx=0, anchor=1) or last (idx=n-1, anchor=n-2)
        if rng.random() < 0.5:
            idx, anchor = 0, 1
        else:
            idx, anchor = n - 1, n - 2

        occupied = set(positions)
        anchor_pos = positions[anchor]
        candidates = []
        for d in DIRECTIONS_3D:
            new_pos = (anchor_pos[0] + d[0],
                       anchor_pos[1] + d[1],
                       anchor_pos[2] + d[2])
            if new_pos not in occupied or new_pos == positions[idx]:
                # Must not collide with any OTHER residue
                if new_pos != positions[idx] and new_pos in occupied:
                    continue
                candidates.append(new_pos)

        if not candidates:
            return None

        new_positions = list(positions)
        new_positions[idx] = candidates[rng.randint(0, len(candidates))]
        return new_positions

    def _try_crankshaft_move(self, positions: list, rng) -> Optional[list]:
        """
        Corner / crankshaft move: if residues i-1 and i+1 are distance-2
        apart (forming an L), residue i can flip to the opposite corner.
        """
        n = len(positions)
        if n < 3:
            return None

        # Collect all eligible internal indices
        eligible = []
        for i in range(1, n - 1):
            if _manhattan(positions[i - 1], positions[i + 1]) == 2:
                eligible.append(i)

        if not eligible:
            return None

        idx = eligible[rng.randint(0, len(eligible))]
        p_prev = positions[idx - 1]
        p_next = positions[idx + 1]

        # The new corner position is p_prev + p_next - p_current
        new_pos = (p_prev[0] + p_next[0] - positions[idx][0],
                   p_prev[1] + p_next[1] - positions[idx][1],
                   p_prev[2] + p_next[2] - positions[idx][2])

        occupied = set(positions)
        occupied.discard(positions[idx])
        if new_pos in occupied:
            return None

        new_positions = list(positions)
        new_positions[idx] = new_pos
        return new_positions

    def _try_pivot_move(self, positions: list, rng) -> Optional[list]:
        """
        Pivot move: choose a random internal residue as pivot. Rotate
        either the N-terminal or C-terminal tail by a random 90-degree
        rotation around the pivot point. The pivot itself stays fixed.
        """
        n = len(positions)
        if n < 3:
            return None

        pivot = rng.randint(1, n - 1)  # internal index

        # Rotate the shorter tail for efficiency
        if rng.random() < 0.5:
            # Rotate N-terminal tail (indices 0..pivot-1)
            tail_indices = list(range(0, pivot))
        else:
            # Rotate C-terminal tail (indices pivot+1..n-1)
            tail_indices = list(range(pivot + 1, n))

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
            # Translate to origin, rotate, translate back
            rel = (positions[i][0] - pivot_pos[0],
                   positions[i][1] - pivot_pos[1],
                   positions[i][2] - pivot_pos[2])
            rotated = _apply_rotation(rot, rel)
            new_pos = (rotated[0] + pivot_pos[0],
                       rotated[1] + pivot_pos[1],
                       rotated[2] + pivot_pos[2])
            if new_pos in new_occupied:
                return None  # Collision — reject entire move
            new_occupied.add(new_pos)
            new_positions[i] = new_pos

        return new_positions

    def mutate(self, conf: Conformation3D, rng,
               max_attempts: int = 10) -> Optional[Conformation3D]:
        """
        Attempt a physics-compliant mutation. Tries end, crankshaft, and
        pivot moves in random order. Returns a new Conformation3D on
        success, or None if all attempts fail (reject, no free restart).
        """
        move_funcs = [self._try_end_move, self._try_crankshaft_move,
                      self._try_pivot_move]

        for _ in range(max_attempts):
            rng.shuffle(move_funcs)
            for fn in move_funcs:
                new_pos = fn(list(conf.positions), rng)
                if new_pos is not None and self.is_valid(new_pos):
                    new_energy = self.calculate_energy(new_pos)
                    return Conformation3D(new_pos, new_energy, conf.sequence)
        return None


# ============================================================================
# MONTE CARLO ALGORITHM  (Version 2 — Simulated Annealing, fair baseline)
# ============================================================================

def monte_carlo_3d(sequence: str, max_steps: int, temperature: float,
                   seed: int) -> dict:
    """
    Simulated Annealing Monte Carlo with physics-compliant moves.

    Uses exponential temperature decay from `temperature` down to T_MIN.
    Invalid moves are rejected (no free restarts). Same mutation mechanics
    as the Forgetting Engine for symmetric comparison.
    """
    T_MIN = 0.01

    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)

    current = model.random_walk(seed)
    best = current
    start_time = datetime.now()

    for step in range(max_steps):
        # Exponential cooling schedule
        t = temperature * math.pow(T_MIN / temperature, step / max(max_steps - 1, 1))

        # Attempt a physics-compliant mutation (symmetric with FE)
        candidate = model.mutate(current, rng, max_attempts=5)
        if candidate is None:
            continue  # Reject — no free restart

        delta_e = candidate.energy - current.energy

        # Metropolis criterion with annealing temperature
        if delta_e < 0 or rng.random() < math.exp(-delta_e / max(t, 1e-12)):
            current = candidate
            if current.energy < best.energy:
                best = current

    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

    return {
        "final_energy": best.energy,
        "convergence_generation": max_steps,
        "computation_time_ms": elapsed_ms,
        "paradox_buffer_activity": 0
    }


# ============================================================================
# FORGETTING ENGINE ALGORITHM  (Version 2 — active paradox buffer)
# ============================================================================

# Fraction of new children sourced from paradox buffer each generation
_PARADOX_REINJECTION_RATE = 0.15  # 15%

def forgetting_engine_3d(sequence: str, pop_size: int, forget_rate: float,
                         max_gen: int, seed: int) -> dict:
    """
    Forgetting Engine with active paradox retention and reinjection.

    Key differences from Version 1:
      - Mutations use physics-compliant moves (end, crankshaft, pivot).
      - Invalid moves are rejected (no free random_walk restarts).
      - Paradox buffer is actively reinjected: 15% of each new generation
        is produced by mutating states pulled from the buffer.
    """
    model = HP3DLattice(sequence)
    rng = np.random.RandomState(seed)

    population = [model.random_walk(seed + i) for i in range(pop_size)]
    paradox_buffer: List[Conformation3D] = []
    paradox_retained_count = 0
    paradox_reinjected_count = 0

    start_time = datetime.now()
    best = min(population, key=lambda x: x.energy)

    for gen in range(max_gen):
        population.sort(key=lambda x: x.energy)

        # Strategic forgetting
        cutoff = int(pop_size * (1 - forget_rate))
        forgotten = population[cutoff:]
        population = population[:cutoff]

        # Paradox retention: save 10% of forgotten states into buffer
        for conf in forgotten:
            if rng.random() < 0.1:
                paradox_buffer.append(conf)
                paradox_retained_count += 1

        # Cap buffer to prevent unbounded growth
        max_buffer = pop_size * 5
        if len(paradox_buffer) > max_buffer:
            paradox_buffer = paradox_buffer[-max_buffer:]

        # ---- Repopulation ----
        slots_needed = pop_size - len(population)

        # How many slots come from paradox reinjection?
        paradox_slots = 0
        if paradox_buffer:
            paradox_slots = max(1, int(slots_needed * _PARADOX_REINJECTION_RATE))
            paradox_slots = min(paradox_slots, slots_needed)

        elite_slots = slots_needed - paradox_slots

        # Fill elite-derived slots (mutate from surviving elite)
        filled = 0
        stall = 0
        while filled < elite_slots and stall < elite_slots * 5:
            if not population:
                break
            parent = population[rng.randint(0, len(population))]
            child = model.mutate(parent, rng, max_attempts=5)
            if child is not None:
                population.append(child)
                filled += 1
                stall = 0
            else:
                stall += 1

        # Fill paradox-derived slots (mutate from buffer entries)
        filled_p = 0
        stall_p = 0
        while filled_p < paradox_slots and stall_p < paradox_slots * 5:
            buf_parent = paradox_buffer[rng.randint(0, len(paradox_buffer))]
            child = model.mutate(buf_parent, rng, max_attempts=5)
            if child is not None:
                population.append(child)
                filled_p += 1
                paradox_reinjected_count += 1
                stall_p = 0
            else:
                stall_p += 1

        # Track best
        if population:
            current_best = min(population, key=lambda x: x.energy)
            if current_best.energy < best.energy:
                best = current_best

    elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

    return {
        "final_energy": best.energy,
        "convergence_generation": max_gen,
        "computation_time_ms": elapsed_ms,
        "paradox_buffer_activity": paradox_retained_count
    }


# ============================================================================
# SEQUENCE GENERATOR (new for scaling study)
# ============================================================================

def generate_sequence(length: int, seed: int) -> str:
    """
    Generate a random HP sequence of given length with fixed seed.

    Uses ~50% H ratio to ensure meaningful folding landscape.
    One sequence per length, same for all trials at that length.
    """
    rng = np.random.RandomState(seed)
    return ''.join(rng.choice(['H', 'P'], p=[0.5, 0.5]) for _ in range(length))
