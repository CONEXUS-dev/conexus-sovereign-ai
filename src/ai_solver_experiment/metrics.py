"""
Metrics Module — Behavioral measurement for the experiment.

Tracks four categories:
  1. Proposal Distribution Metrics (entropy, diversity, change magnitude)
  2. Convergence Metrics (iterations to plateau, improvement slope, variance)
  3. Escape Metrics (local minima escapes, post-stagnation improvement)
  4. Final Performance (% improvement vs baseline, statistical significance)

All metrics are computed from logged iteration data. No AI calls.
"""

import math
from typing import List, Dict, Any, Optional


# ── Proposal Distribution Metrics ────────────────────────────────

def route_structure_hash(routes: List[List[int]]) -> str:
    """
    Hash a route structure into a canonical string for comparison.
    Normalizes route order and direction.
    """
    normalized = []
    for route in routes:
        if not route:
            continue
        # Canonical direction: start with smaller endpoint
        if route[0] > route[-1]:
            route = route[::-1]
        normalized.append(tuple(route))
    normalized.sort()
    return str(normalized)


def route_set_similarity(routes_a: List[List[int]], routes_b: List[List[int]]) -> float:
    """
    Jaccard similarity of edge sets between two solutions.
    Returns 0.0 (completely different) to 1.0 (identical).
    """
    def edge_set(routes):
        edges = set()
        for route in routes:
            if not route:
                continue
            edges.add((-1, route[0]))  # depot -> first
            for i in range(len(route) - 1):
                a, b = route[i], route[i + 1]
                edges.add((min(a, b), max(a, b)))
            edges.add((route[-1], -1))  # last -> depot
        return edges

    ea = edge_set(routes_a)
    eb = edge_set(routes_b)

    if not ea and not eb:
        return 1.0
    intersection = len(ea & eb)
    union = len(ea | eb)
    return intersection / union if union > 0 else 0.0


def proposal_entropy(route_hashes: List[str]) -> float:
    """
    Shannon entropy of proposal distribution.
    Higher = more diverse proposals. Lower = repetitive.
    """
    if not route_hashes:
        return 0.0

    counts = {}
    for h in route_hashes:
        counts[h] = counts.get(h, 0) + 1

    n = len(route_hashes)
    entropy = 0.0
    for count in counts.values():
        p = count / n
        if p > 0:
            entropy -= p * math.log2(p)

    return entropy


def unique_proposal_ratio(route_hashes: List[str]) -> float:
    """Fraction of proposals that are structurally unique."""
    if not route_hashes:
        return 0.0
    return len(set(route_hashes)) / len(route_hashes)


def avg_change_magnitude(similarities: List[float]) -> float:
    """
    Average structural change between consecutive proposals.
    similarities[i] = Jaccard similarity between proposal i and i+1.
    Change magnitude = 1 - similarity.
    """
    if not similarities:
        return 0.0
    return sum(1.0 - s for s in similarities) / len(similarities)


# ── Convergence Metrics ──────────────────────────────────────────

def iterations_to_plateau(
    scores: List[float],
    window: int = 5,
    threshold: float = 0.001,
) -> int:
    """
    Number of iterations until improvement plateaus.
    Plateau = no improvement > threshold over a sliding window.
    """
    if len(scores) < window + 1:
        return len(scores)

    best_so_far = scores[0]
    for i in range(1, len(scores)):
        if scores[i] < best_so_far - threshold:
            best_so_far = scores[i]

        # Check if last `window` iterations had no improvement
        if i >= window:
            window_best = min(scores[i - window : i + 1])
            pre_window_best = min(scores[: i - window + 1])
            if pre_window_best - window_best < threshold:
                return i - window + 1

    return len(scores)


def improvement_slope(scores: List[float]) -> float:
    """
    Linear regression slope of fitness scores over iterations.
    Negative slope = improving. More negative = faster improvement.
    """
    n = len(scores)
    if n < 2:
        return 0.0

    x_mean = (n - 1) / 2.0
    y_mean = sum(scores) / n

    num = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))

    return num / den if den > 0 else 0.0


def variance_reduction(scores: List[float], window: int = 5) -> List[float]:
    """
    Rolling variance of fitness scores.
    Decreasing variance = converging. Increasing = exploring.
    """
    if len(scores) < window:
        return []

    variances = []
    for i in range(len(scores) - window + 1):
        w = scores[i : i + window]
        mean = sum(w) / len(w)
        var = sum((x - mean) ** 2 for x in w) / len(w)
        variances.append(var)

    return variances


# ── Escape Metrics ───────────────────────────────────────────────

def detect_stagnation_periods(
    scores: List[float],
    threshold: float = 0.001,
    min_length: int = 3,
) -> List[Dict[str, Any]]:
    """
    Detect periods of stagnation (no improvement for min_length iterations).
    Returns list of {start, end, length, escaped, escape_delta}.
    """
    if not scores:
        return []

    periods = []
    best = scores[0]
    stag_start = None
    stag_best = best

    for i in range(1, len(scores)):
        improved = scores[i] < best - threshold

        if improved:
            if stag_start is not None and (i - stag_start) >= min_length:
                periods.append({
                    "start": stag_start,
                    "end": i - 1,
                    "length": i - stag_start,
                    "escaped": True,
                    "escape_delta": stag_best - scores[i],
                })
            stag_start = None
            best = scores[i]
            stag_best = best
        else:
            if stag_start is None:
                stag_start = i
                stag_best = best

    # Handle trailing stagnation
    if stag_start is not None and (len(scores) - stag_start) >= min_length:
        periods.append({
            "start": stag_start,
            "end": len(scores) - 1,
            "length": len(scores) - stag_start,
            "escaped": False,
            "escape_delta": 0.0,
        })

    return periods


def escape_count(stagnation_periods: List[Dict[str, Any]]) -> int:
    """Number of successful escapes from stagnation."""
    return sum(1 for p in stagnation_periods if p["escaped"])


def avg_escape_delta(stagnation_periods: List[Dict[str, Any]]) -> float:
    """Average improvement magnitude when escaping stagnation."""
    escapes = [p["escape_delta"] for p in stagnation_periods if p["escaped"]]
    return sum(escapes) / len(escapes) if escapes else 0.0


# ── Constraint Violation Tracking ────────────────────────────────

def violation_frequency(eval_results: List[Dict[str, Any]]) -> float:
    """Fraction of iterations with constraint violations."""
    if not eval_results:
        return 0.0
    violations = sum(1 for r in eval_results if not r.get("feasible", True))
    return violations / len(eval_results)


def violation_trend(eval_results: List[Dict[str, Any]]) -> List[int]:
    """Binary series: 1 = violation, 0 = feasible, per iteration."""
    return [0 if r.get("feasible", True) else 1 for r in eval_results]


# ── Final Performance ────────────────────────────────────────────

def pct_improvement(baseline_score: float, final_score: float) -> float:
    """Percentage improvement over baseline. Positive = better."""
    if baseline_score == 0:
        return 0.0
    return (baseline_score - final_score) / baseline_score * 100.0


# ── Aggregate Summary ────────────────────────────────────────────

def compute_run_metrics(
    iteration_log: List[Dict[str, Any]],
    baseline_distance: float,
) -> Dict[str, Any]:
    """
    Compute all metrics for a single run from its iteration log.

    Each entry in iteration_log should have:
        - iteration: int
        - routes: list of routes
        - eval: evaluation dict from evaluator
        - fitness: float (distance + penalty)
    """
    if not iteration_log:
        return {"error": "empty log"}

    # Extract series
    scores = [entry["fitness"] for entry in iteration_log]
    eval_results = [entry["eval"] for entry in iteration_log]

    # Route hashes and similarities
    route_hashes = []
    similarities = []
    for i, entry in enumerate(iteration_log):
        h = route_structure_hash(entry.get("routes", []))
        route_hashes.append(h)
        if i > 0:
            prev_routes = iteration_log[i - 1].get("routes", [])
            curr_routes = entry.get("routes", [])
            similarities.append(route_set_similarity(prev_routes, curr_routes))

    # Stagnation analysis
    stag_periods = detect_stagnation_periods(scores)

    # Best score
    best_score = min(scores)
    best_iter = scores.index(best_score)
    best_eval = eval_results[best_iter]

    return {
        # Proposal distribution
        "proposal_entropy": proposal_entropy(route_hashes),
        "unique_proposal_ratio": unique_proposal_ratio(route_hashes),
        "avg_change_magnitude": avg_change_magnitude(similarities),

        # Convergence
        "iterations_to_plateau": iterations_to_plateau(scores),
        "improvement_slope": improvement_slope(scores),
        "variance_reduction": variance_reduction(scores),

        # Escape
        "stagnation_periods": stag_periods,
        "escape_count": escape_count(stag_periods),
        "avg_escape_delta": avg_escape_delta(stag_periods),

        # Violations
        "violation_frequency": violation_frequency(eval_results),
        "violation_trend": violation_trend(eval_results),

        # Final performance
        "best_fitness": best_score,
        "best_distance": best_eval.get("distance", best_score),
        "best_feasible": best_eval.get("feasible", False),
        "best_iteration": best_iter,
        "pct_vs_baseline": pct_improvement(baseline_distance, best_score),
        "total_iterations": len(scores),

        # Raw series for plotting
        "fitness_series": scores,
    }
