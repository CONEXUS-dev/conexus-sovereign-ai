"""
Paradox buffer: gating, scoring, update, novelty.

Rules (from MASTER KEY):
- Size ≈ 5, memory-only, NEVER used as parents.
- Mined for patterns only.
- Preserve: clusters, short-edge spines, balanced loads.
- Discard: collapse solutions, trivial symmetry.

Paradox gates (from spec):
1. "bad" — worse than median fitness OR overload above floor.
2. "geometrically informative" — at least 2 geometry signals fire.
3. "NOT collapse trap" — max_customers_per_vehicle <= 14 AND
   min_customers_per_vehicle >= 3.
4. "convertible" — at least one cluster/spine subset of size 4–8.
"""

import statistics
from typing import List, Optional
from .types import Instance, Candidate, ParadoxEntry


# ── paradox gates ────────────────────────────────────────────────

def is_bad(cand: Candidate, median_fitness: float, overload_floor: int = 0) -> bool:
    """Gate 1: candidate is worse than median or has overload."""
    return cand.fitness > median_fitness or cand.overload > overload_floor


def is_geometrically_informative(cand: Candidate) -> bool:
    """Gate 2: at least 2 geometry signals are interesting."""
    m = cand.metrics
    signals = 0
    if m.get("spine_score", 0) > 0.25:
        signals += 1
    if m.get("compactness", 1.0) < 0.8:
        signals += 1
    if m.get("depot_leg_sum", 0) < m.get("distance_total", 1e9) * 0.4:
        signals += 1
    if m.get("turning_sum", 0) < 500:
        signals += 1
    return signals >= 2


def is_not_collapse_trap(cand: Candidate) -> bool:
    """Gate 3: not a degenerate solution."""
    m = cand.metrics
    return (m.get("max_customers_per_vehicle", 999) <= 14 and
            m.get("min_customers_per_vehicle", 0) >= 3)


def is_convertible(inst: Instance, cand: Candidate) -> bool:
    """Gate 4: has at least one cluster/spine subset of size 4–8."""
    for route in cand.routes:
        if 4 <= len(route) <= 8:
            return True
    # also check if any sub-segment of a larger route qualifies
    for route in cand.routes:
        if len(route) > 8:
            # sliding window
            for start in range(len(route) - 3):
                end = min(start + 8, len(route))
                seg = route[start:end]
                if 4 <= len(seg) <= 8:
                    return True
    return False


def passes_all_gates(inst: Instance, cand: Candidate,
                     median_fitness: float, overload_floor: int = 0) -> bool:
    """True if candidate passes all four paradox gates."""
    return (is_bad(cand, median_fitness, overload_floor) and
            is_geometrically_informative(cand) and
            is_not_collapse_trap(cand) and
            is_convertible(inst, cand))


# ── scoring ──────────────────────────────────────────────────────

def paradox_score(cand: Candidate, buffer: List[ParadoxEntry]) -> float:
    """Score a candidate for paradox buffer admission.
    Prefer: high spine_score, low compactness, low depot legs, novelty."""
    m = cand.metrics
    spine = m.get("spine_score", 0)
    compact = m.get("compactness", 1.0)
    depot = m.get("depot_leg_sum", 0)
    dist = m.get("distance_total", 1e9)

    # novelty: average Hamming distance to existing buffer entries
    novelty = 0.0
    if buffer:
        for entry in buffer:
            hamming = sum(1 for a, b in zip(cand.assign, entry.candidate.assign) if a != b)
            novelty += hamming
        novelty /= len(buffer)
    else:
        novelty = len(cand.assign)  # max novelty if buffer empty

    score = (spine * 100
             + (1.0 - compact) * 50
             + (1.0 - depot / max(dist, 1)) * 30
             + novelty * 0.5)
    return score


# ── buffer management ────────────────────────────────────────────

class ParadoxBuffer:
    """Memory-only paradox buffer. Size ≈ k. Never used as parents."""

    def __init__(self, k: int = 5):
        self.k = k
        self.entries: List[ParadoxEntry] = []

    def try_add(self, inst: Instance, cand: Candidate,
                median_fitness: float, overload_floor: int = 0) -> bool:
        """Attempt to add candidate. Returns True if added."""
        if not passes_all_gates(inst, cand, median_fitness, overload_floor):
            return False

        score = paradox_score(cand, self.entries)
        entry = ParadoxEntry(candidate=cand, score=score)

        if len(self.entries) < self.k:
            self.entries.append(entry)
            self.entries.sort(key=lambda e: e.score, reverse=True)
            return True

        # replace worst if new score is better
        if score > self.entries[-1].score:
            self.entries[-1] = entry
            self.entries.sort(key=lambda e: e.score, reverse=True)
            return True

        return False

    def age_all(self):
        for e in self.entries:
            e.age += 1

    @property
    def size(self) -> int:
        return len(self.entries)

    def get_candidates(self) -> List[Candidate]:
        """Return candidates (read-only, for pattern mining)."""
        return [e.candidate for e in self.entries]

    def summary(self) -> dict:
        return {
            "size": self.size,
            "scores": [round(e.score, 2) for e in self.entries],
            "ages": [e.age for e in self.entries],
        }
