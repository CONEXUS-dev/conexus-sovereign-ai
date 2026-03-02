"""
Pattern mining from paradox buffer.
Extract cluster/spine patterns from structurally interesting solutions.
"""

import math
from typing import List
from .types import Instance, Candidate, Pattern


def mine_patterns(inst: Instance, candidates: List[Candidate]) -> List[Pattern]:
    """Extract patterns from paradox buffer candidates."""
    patterns: List[Pattern] = []
    for cand in candidates:
        patterns.extend(_extract_clusters(inst, cand))
        patterns.extend(_extract_spines(inst, cand))
        patterns.extend(_extract_depot_legs(inst, cand))
    # deduplicate by customer set
    seen = set()
    unique = []
    for p in patterns:
        key = (p.kind, tuple(sorted(p.customers)))
        if key not in seen:
            seen.add(key)
            unique.append(p)
    # sort by score descending
    unique.sort(key=lambda p: p.score, reverse=True)
    return unique[:20]  # cap at 20 patterns


def _extract_clusters(inst: Instance, cand: Candidate) -> List[Pattern]:
    """Find compact sub-groups within routes (size 4-8)."""
    patterns = []
    for route in cand.routes:
        if len(route) < 4:
            continue
        # sliding window of sizes 4-8
        for size in range(4, min(9, len(route) + 1)):
            for start in range(len(route) - size + 1):
                seg = route[start:start + size]
                # score by compactness (low avg pairwise distance)
                dists = []
                for i in range(len(seg)):
                    for j in range(i + 1, len(seg)):
                        dists.append(inst.dist(seg[i], seg[j]))
                avg_d = sum(dists) / len(dists) if dists else 1e9
                # lower avg distance = better cluster
                score = 1.0 / (avg_d + 1e-9)
                patterns.append(Pattern(
                    kind="CLUSTER", customers=seg,
                    score=score, source_cid=cand.cid,
                ))
    # keep top 5 clusters per candidate
    patterns.sort(key=lambda p: p.score, reverse=True)
    return patterns[:5]


def _extract_spines(inst: Instance, cand: Candidate) -> List[Pattern]:
    """Find chains of short edges (spine patterns)."""
    patterns = []
    for route in cand.routes:
        if len(route) < 4:
            continue
        # find consecutive short edges
        edges = []
        for i in range(len(route) - 1):
            edges.append(inst.dist(route[i], route[i + 1]))
        if not edges:
            continue
        median_edge = sorted(edges)[len(edges) // 2]
        # find runs of short edges
        run_start = None
        for i, e in enumerate(edges):
            if e <= median_edge:
                if run_start is None:
                    run_start = i
            else:
                if run_start is not None and i - run_start >= 3:
                    seg = route[run_start:i + 1]
                    if 4 <= len(seg) <= 8:
                        score = sum(1.0 / (edges[k] + 1e-9)
                                    for k in range(run_start, i)) / len(seg)
                        patterns.append(Pattern(
                            kind="SPINE", customers=seg,
                            score=score, source_cid=cand.cid,
                        ))
                run_start = None
        # check trailing run
        if run_start is not None and len(edges) - run_start >= 3:
            seg = route[run_start:len(route)]
            if 4 <= len(seg) <= 8:
                score = sum(1.0 / (edges[k] + 1e-9)
                            for k in range(run_start, len(edges))) / len(seg)
                patterns.append(Pattern(
                    kind="SPINE", customers=seg,
                    score=score, source_cid=cand.cid,
                ))
    return patterns[:5]


def _extract_depot_legs(inst: Instance, cand: Candidate) -> List[Pattern]:
    """Find customers with long depot legs (candidates for DEPOT_LEG_MIN)."""
    patterns = []
    for route in cand.routes:
        if not route:
            continue
        first_leg = inst.dist(-1, route[0])
        last_leg = inst.dist(route[-1], -1)
        if first_leg > 30:  # threshold
            patterns.append(Pattern(
                kind="DEPOT_LEG", customers=[route[0]],
                score=first_leg, source_cid=cand.cid,
            ))
        if last_leg > 30:
            patterns.append(Pattern(
                kind="DEPOT_LEG", customers=[route[-1]],
                score=last_leg, source_cid=cand.cid,
            ))
    return patterns[:5]
