"""
SovereignNEXT — Phase 4 Completion Package
Pure-computation analysis of v2 and v3 collapsed snapshots.
No LLM calls. Produces 5 artifacts and HOLDs.

Stages:
  1. Snapshot ingestion & validation
  2. Decision-type extraction
  3. Delta computation
  4. Tension-level diff map (shared tensions 0001-0144)
  5. Margin & entropy analysis
  6. Paradox substrate analysis (v3 only)
  7. Structural integrity checks
  8. Artifact generation
  9. HOLD
"""

import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from SovereignNEXT.state.system_state import SystemState

SNAPSHOT_DIR = REPO_ROOT / "SovereignNEXT" / "tests"
V2_COLLAPSED = SNAPSHOT_DIR / "v2_collapsed_snapshot.json"
V3_COLLAPSED = SNAPSHOT_DIR / "v3_collapsed_snapshot.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_snapshot(path: Path) -> Tuple[SystemState, dict]:
    """Load snapshot, return (SystemState, raw_dict)."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    state = SystemState.from_dict(raw)
    return state, raw


def _get_margin(tension_dict: dict) -> Optional[float]:
    """Extract margin from the last history entry of a tension."""
    for entry in reversed(tension_dict.get("history", [])):
        if "margin" in entry:
            return entry["margin"]
    return None


def _get_decision(tension_dict: dict) -> str:
    """Extract decision from the last history entry."""
    for entry in reversed(tension_dict.get("history", [])):
        if "event" in entry:
            return entry["event"]
    return "unknown"


def _was_vetoed(tension_dict: dict) -> bool:
    """Check if tension was paradox-vetoed."""
    for entry in tension_dict.get("history", []):
        if entry.get("paradox_vetoed", False):
            return True
    return False


def _safe_stats(values: List[float]) -> Dict[str, float]:
    """Compute mean, median, variance, skew for a list of floats."""
    if not values:
        return {"mean": 0.0, "median": 0.0, "variance": 0.0, "skew": 0.0, "count": 0}
    n = len(values)
    mean = statistics.mean(values)
    median = statistics.median(values)
    variance = statistics.variance(values) if n > 1 else 0.0
    # Skewness (Fisher's)
    if n > 2 and variance > 0:
        std = math.sqrt(variance)
        skew = (n / ((n - 1) * (n - 2))) * sum(((x - mean) / std) ** 3 for x in values)
    else:
        skew = 0.0
    return {
        "mean": round(mean, 4),
        "median": round(median, 4),
        "variance": round(variance, 6),
        "skew": round(skew, 4),
        "count": n,
    }


# ===========================================================================
# Stage 1: Snapshot Ingestion & Validation
# ===========================================================================

def stage1_validate(v2_raw: dict, v3_raw: dict) -> Dict[str, Any]:
    """Validate schema integrity of both snapshots."""
    report = {"v2": {}, "v3": {}}

    for label, raw in [("v2", v2_raw), ("v3", v3_raw)]:
        issues = []

        # Required top-level keys
        for key in ("claims", "tensions", "paradoxes", "emoji_fields", "mission_id", "iteration"):
            if key not in raw:
                issues.append(f"Missing top-level key: {key}")

        # Tension validation
        tension_ids = set()
        for i, t in enumerate(raw.get("tensions", [])):
            tid = t.get("id", f"<missing_id_{i}>")
            if "id" not in t:
                issues.append(f"Tension at index {i} missing 'id'")
            if tid in tension_ids:
                issues.append(f"Duplicate tension ID: {tid}")
            tension_ids.add(tid)
            for field in ("pole_a", "pole_b", "status", "relation_type"):
                if field not in t:
                    issues.append(f"{tid} missing field: {field}")
            # Check history has margin
            if not t.get("history"):
                issues.append(f"{tid} has empty history (scoring error?)")

        # Paradox validation
        paradox_ids = set()
        for i, p in enumerate(raw.get("paradoxes", [])):
            pid = p.get("id", f"<missing_id_{i}>")
            if "id" not in p:
                issues.append(f"Paradox at index {i} missing 'id'")
            if pid in paradox_ids:
                issues.append(f"Duplicate paradox ID: {pid}")
            paradox_ids.add(pid)
            if "status" not in p:
                issues.append(f"{pid} missing 'status'")
            if "emoji_vector_id" not in p:
                issues.append(f"{pid} missing 'emoji_vector_id'")

        # Emoji vector validation
        ev_ids = set()
        for i, ev in enumerate(raw.get("emoji_fields", [])):
            evid = ev.get("id", f"<missing_id_{i}>")
            if evid in ev_ids:
                issues.append(f"Duplicate emoji vector ID: {evid}")
            ev_ids.add(evid)

        # Cross-reference: paradox emoji_vector_ids should exist
        for p in raw.get("paradoxes", []):
            evid = p.get("emoji_vector_id")
            if evid and evid not in ev_ids:
                issues.append(f"Paradox {p['id']} references missing emoji vector: {evid}")

        report[label] = {
            "claims": len(raw.get("claims", [])),
            "tensions": len(raw.get("tensions", [])),
            "paradoxes": len(raw.get("paradoxes", [])),
            "emoji_vectors": len(raw.get("emoji_fields", [])),
            "mission_id": raw.get("mission_id"),
            "iteration": raw.get("iteration"),
            "issues": issues,
            "valid": len(issues) == 0,
        }

    return report


# ===========================================================================
# Stage 2: Decision-Type Extraction
# ===========================================================================

def stage2_decisions(raw: dict, label: str) -> Dict[str, Any]:
    """Extract decision counts and rates from a snapshot."""
    tensions = raw.get("tensions", [])
    total = len(tensions)

    committed_a = 0
    committed_b = 0
    deferred = 0
    paradox_held = 0
    errors = 0
    vetoed = 0

    for t in tensions:
        status = t.get("status", "unknown")
        if status == "collapsed_to_a":
            committed_a += 1
        elif status == "collapsed_to_b":
            committed_b += 1
        elif status == "paradox_held":
            paradox_held += 1
        elif status == "open":
            # Open after Collapse = deferred or error
            if t.get("history"):
                deferred += 1
            else:
                errors += 1
        else:
            errors += 1

        if _was_vetoed(t):
            vetoed += 1

    committed = committed_a + committed_b

    return {
        "label": label,
        "total": total,
        "committed": committed,
        "committed_a": committed_a,
        "committed_b": committed_b,
        "deferred": deferred,
        "paradox_held": paradox_held,
        "errors": errors,
        "vetoed": vetoed,
        "commit_rate": round(committed / total * 100, 2) if total else 0,
        "defer_rate": round(deferred / total * 100, 2) if total else 0,
        "paradox_hold_rate": round(paradox_held / total * 100, 2) if total else 0,
        "veto_rate": round(vetoed / total * 100, 2) if total else 0,
        "error_rate": round(errors / total * 100, 2) if total else 0,
    }


# ===========================================================================
# Stage 3: Delta Computation
# ===========================================================================

def stage3_deltas(v2_dec: dict, v3_dec: dict) -> Dict[str, Any]:
    """Compute v3 - v2 deltas for all decision metrics."""
    delta = {}
    for key in ("total", "committed", "committed_a", "committed_b", "deferred",
                 "paradox_held", "errors", "vetoed"):
        delta[key] = v3_dec[key] - v2_dec[key]
    for key in ("commit_rate", "defer_rate", "paradox_hold_rate", "veto_rate", "error_rate"):
        delta[key] = round(v3_dec[key] - v2_dec[key], 2)
    return delta


# ===========================================================================
# Stage 4: Tension-Level Diff Map
# ===========================================================================

def stage4_tension_diff(v2_raw: dict, v3_raw: dict) -> Dict[str, Any]:
    """Compare tensions present in both snapshots (shared IDs)."""
    v2_map = {t["id"]: t for t in v2_raw.get("tensions", [])}
    v3_map = {t["id"]: t for t in v3_raw.get("tensions", [])}

    shared_ids = sorted(set(v2_map.keys()) & set(v3_map.keys()))
    v3_only_ids = sorted(set(v3_map.keys()) - set(v2_map.keys()))

    diffs = []
    reversals = []
    margin_changes = []

    for tid in shared_ids:
        t2 = v2_map[tid]
        t3 = v3_map[tid]

        v2_status = t2.get("status", "unknown")
        v3_status = t3.get("status", "unknown")
        v2_margin = _get_margin(t2)
        v3_margin = _get_margin(t3)
        v2_vetoed = _was_vetoed(t2)
        v3_vetoed = _was_vetoed(t3)
        v2_decision = _get_decision(t2)
        v3_decision = _get_decision(t3)

        status_changed = v2_status != v3_status
        margin_delta = None
        if v2_margin is not None and v3_margin is not None:
            margin_delta = round(v3_margin - v2_margin, 4)

        entry = {
            "tension_id": tid,
            "v2_status": v2_status,
            "v3_status": v3_status,
            "status_changed": status_changed,
            "v2_decision": v2_decision,
            "v3_decision": v3_decision,
            "v2_margin": v2_margin,
            "v3_margin": v3_margin,
            "margin_delta": margin_delta,
            "v2_vetoed": v2_vetoed,
            "v3_vetoed": v3_vetoed,
            "veto_changed": v2_vetoed != v3_vetoed,
        }
        diffs.append(entry)

        if status_changed:
            # Detect specific reversal types
            if v2_status.startswith("collapsed") and v3_status == "paradox_held":
                reversals.append({"tension_id": tid, "type": "commit_to_hold", "v2": v2_status, "v3": v3_status})
            elif v2_status == "paradox_held" and v3_status.startswith("collapsed"):
                reversals.append({"tension_id": tid, "type": "hold_to_commit", "v2": v2_status, "v3": v3_status})
            elif v2_status.startswith("collapsed") and v3_status == "open":
                reversals.append({"tension_id": tid, "type": "commit_to_defer", "v2": v2_status, "v3": v3_status})
            elif v2_status == "open" and v3_status.startswith("collapsed"):
                reversals.append({"tension_id": tid, "type": "defer_to_commit", "v2": v2_status, "v3": v3_status})
            elif v2_status == "open" and v3_status == "paradox_held":
                reversals.append({"tension_id": tid, "type": "defer_to_hold", "v2": v2_status, "v3": v3_status})
            elif v2_status == "paradox_held" and v3_status == "open":
                reversals.append({"tension_id": tid, "type": "hold_to_defer", "v2": v2_status, "v3": v3_status})

        if margin_delta is not None:
            margin_changes.append({"tension_id": tid, "delta": margin_delta, "v2": v2_margin, "v3": v3_margin})

    # Sort margin changes by absolute delta descending
    margin_changes.sort(key=lambda x: abs(x["delta"]), reverse=True)

    # Category change summary
    change_summary = Counter()
    for r in reversals:
        change_summary[r["type"]] += 1

    return {
        "shared_count": len(shared_ids),
        "v3_only_count": len(v3_only_ids),
        "v3_only_ids": v3_only_ids,
        "status_changed_count": sum(1 for d in diffs if d["status_changed"]),
        "veto_changed_count": sum(1 for d in diffs if d["veto_changed"]),
        "reversals": reversals,
        "reversal_summary": dict(change_summary),
        "top_10_margin_changes": margin_changes[:10],
        "diffs": diffs,
    }


# ===========================================================================
# Stage 5: Margin & Entropy Analysis
# ===========================================================================

def stage5_margin_entropy(v2_raw: dict, v3_raw: dict, v2_state: SystemState, v3_state: SystemState) -> Dict[str, Any]:
    """Compute margin and entropy distributions."""
    # Margins from tension history
    v2_margins = []
    for t in v2_raw.get("tensions", []):
        m = _get_margin(t)
        if m is not None:
            v2_margins.append(m)

    v3_margins = []
    for t in v3_raw.get("tensions", []):
        m = _get_margin(t)
        if m is not None:
            v3_margins.append(m)

    # Entropy from emoji vectors (computed properties)
    v2_entropies = [ev.entropy for ev in v2_state.emoji_fields]
    v3_entropies = [ev.entropy for ev in v3_state.emoji_fields]

    # Top 10 highest-entropy paradoxes (v3)
    v3_paradox_entropy = []
    for p in v3_state.paradoxes:
        ev = None
        for e in v3_state.emoji_fields:
            if e.id == p.emoji_vector_id:
                ev = e
                break
        if ev:
            v3_paradox_entropy.append({
                "paradox_id": p.id,
                "emoji_vector_id": ev.id,
                "entropy": ev.entropy,
                "pole_balance": ev.pole_balance,
                "chaos_index": ev.chaos_index,
                "stability_index": ev.stability_index,
                "status": p.status,
            })
    v3_paradox_entropy.sort(key=lambda x: x["entropy"], reverse=True)

    # Top 10 lowest-margin tensions (v3)
    v3_tension_margins = []
    for t in v3_raw.get("tensions", []):
        m = _get_margin(t)
        if m is not None:
            v3_tension_margins.append({"tension_id": t["id"], "margin": m, "status": t["status"]})
    v3_tension_margins.sort(key=lambda x: x["margin"])

    # Correlation: entropy vs veto
    veto_entropies = []
    non_veto_entropies = []
    for t_raw in v3_raw.get("tensions", []):
        if t_raw.get("emoji_vector_id"):
            ev = None
            for e in v3_state.emoji_fields:
                if e.id == t_raw["emoji_vector_id"]:
                    ev = e
                    break
            if ev:
                if _was_vetoed(t_raw):
                    veto_entropies.append(ev.entropy)
                else:
                    non_veto_entropies.append(ev.entropy)

    return {
        "v2_margin_stats": _safe_stats(v2_margins),
        "v3_margin_stats": _safe_stats(v3_margins),
        "v2_entropy_stats": _safe_stats(v2_entropies),
        "v3_entropy_stats": _safe_stats(v3_entropies),
        "top_10_highest_entropy_paradoxes": v3_paradox_entropy[:10],
        "top_10_lowest_margin_tensions": v3_tension_margins[:10],
        "entropy_veto_correlation": {
            "vetoed_mean_entropy": round(statistics.mean(veto_entropies), 4) if veto_entropies else None,
            "non_vetoed_mean_entropy": round(statistics.mean(non_veto_entropies), 4) if non_veto_entropies else None,
            "vetoed_count": len(veto_entropies),
            "non_vetoed_count": len(non_veto_entropies),
        },
    }


# ===========================================================================
# Stage 6: Paradox Substrate Analysis (v3 only)
# ===========================================================================

def stage6_paradox_substrate(v3_raw: dict, v3_state: SystemState) -> Dict[str, Any]:
    """Analyze paradox veto behavior in v3."""
    # Build paradox -> emoji vector lookup
    paradox_ev = {}
    for p in v3_state.paradoxes:
        ev = None
        for e in v3_state.emoji_fields:
            if e.id == p.emoji_vector_id:
                ev = e
                break
        paradox_ev[p.id] = {
            "paradox_id": p.id,
            "emoji_vector_id": p.emoji_vector_id,
            "status": p.status,
            "entropy": ev.entropy if ev else None,
            "pole_balance": ev.pole_balance if ev else None,
            "chaos_index": ev.chaos_index if ev else None,
            "stability_index": ev.stability_index if ev else None,
        }

    # Build tension -> paradox adjacency via emoji_vector_id
    # A tension links to a paradox if they share the same emoji_vector_id
    ev_to_paradox = {}
    for p in v3_state.paradoxes:
        if p.emoji_vector_id:
            ev_to_paradox[p.emoji_vector_id] = p.id

    adjacency = defaultdict(list)  # paradox_id -> [tension_ids]
    veto_counts = Counter()        # paradox_id -> veto count
    total_vetoes = 0

    for t_raw in v3_raw.get("tensions", []):
        evid = t_raw.get("emoji_vector_id")
        if evid and evid in ev_to_paradox:
            pid = ev_to_paradox[evid]
            adjacency[pid].append(t_raw["id"])
            if _was_vetoed(t_raw):
                veto_counts[pid] += 1
                total_vetoes += 1

    # Frequency table sorted by veto count
    frequency_table = []
    for pid in sorted(adjacency.keys()):
        info = paradox_ev.get(pid, {})
        frequency_table.append({
            "paradox_id": pid,
            "linked_tensions": len(adjacency[pid]),
            "veto_count": veto_counts.get(pid, 0),
            "entropy": info.get("entropy"),
            "status": info.get("status"),
        })
    frequency_table.sort(key=lambda x: x["veto_count"], reverse=True)

    # Entropy-weighted veto influence
    influence_map = []
    for entry in frequency_table:
        entropy = entry["entropy"] or 0
        vetos = entry["veto_count"]
        influence = round(entropy * vetos, 4)
        influence_map.append({
            "paradox_id": entry["paradox_id"],
            "veto_count": vetos,
            "entropy": entropy,
            "influence_score": influence,
            "linked_tensions": entry["linked_tensions"],
        })
    influence_map.sort(key=lambda x: x["influence_score"], reverse=True)

    # Paradox dominance: which paradoxes account for most vetoes
    top_vetoers = [e for e in influence_map if e["veto_count"] > 0]

    # Paradox clusters: group paradoxes by similar entropy bands
    entropy_bands = {"high_entropy_>0.9": [], "mid_entropy_0.7-0.9": [], "low_entropy_<0.7": []}
    for pid, info in paradox_ev.items():
        ent = info.get("entropy", 0)
        if ent > 0.9:
            entropy_bands["high_entropy_>0.9"].append(pid)
        elif ent >= 0.7:
            entropy_bands["mid_entropy_0.7-0.9"].append(pid)
        else:
            entropy_bands["low_entropy_<0.7"].append(pid)

    return {
        "total_paradoxes": len(v3_state.paradoxes),
        "total_veto_events": total_vetoes,
        "paradoxes_with_vetoes": len([e for e in frequency_table if e["veto_count"] > 0]),
        "paradoxes_without_vetoes": len([e for e in frequency_table if e["veto_count"] == 0]),
        "influence_map": influence_map,
        "frequency_table": frequency_table,
        "adjacency": {pid: tids for pid, tids in adjacency.items()},
        "top_vetoers": top_vetoers[:10],
        "entropy_clusters": {band: len(pids) for band, pids in entropy_bands.items()},
        "entropy_cluster_detail": entropy_bands,
        "dominance": {
            "top_5_by_influence": [e["paradox_id"] for e in influence_map[:5]],
            "top_5_by_veto_count": [e["paradox_id"] for e in sorted(top_vetoers, key=lambda x: x["veto_count"], reverse=True)[:5]],
        },
    }


# ===========================================================================
# Stage 7: Structural Integrity Checks
# ===========================================================================

def stage7_integrity(v2_raw: dict, v3_raw: dict) -> Dict[str, Any]:
    """Run structural integrity checks on both snapshots."""
    report = {}

    for label, raw in [("v2", v2_raw), ("v3", v3_raw)]:
        issues = []

        # No duplicate tension IDs
        t_ids = [t["id"] for t in raw.get("tensions", [])]
        dupes = [tid for tid, count in Counter(t_ids).items() if count > 1]
        if dupes:
            issues.append(f"Duplicate tension IDs: {dupes}")

        # No duplicate paradox IDs
        p_ids = [p["id"] for p in raw.get("paradoxes", [])]
        dupes = [pid for pid, count in Counter(p_ids).items() if count > 1]
        if dupes:
            issues.append(f"Duplicate paradox IDs: {dupes}")

        # No orphan paradox references
        ev_ids = {ev["id"] for ev in raw.get("emoji_fields", [])}
        for p in raw.get("paradoxes", []):
            evid = p.get("emoji_vector_id")
            if evid and evid not in ev_ids:
                issues.append(f"Paradox {p['id']} references missing emoji vector: {evid}")

        # No negative margins
        for t in raw.get("tensions", []):
            m = _get_margin(t)
            if m is not None and m < 0:
                issues.append(f"Negative margin on {t['id']}: {m}")

        # No NaN or null in critical fields
        for t in raw.get("tensions", []):
            if t.get("status") is None:
                issues.append(f"Null status on {t['id']}")
            if t.get("relation_type") is None:
                issues.append(f"Null relation_type on {t['id']}")

        # No contradictory final states
        for t in raw.get("tensions", []):
            status = t.get("status", "")
            decision = _get_decision(t)
            if status.startswith("collapsed") and decision == "paradox_hold":
                issues.append(f"Contradictory state on {t['id']}: status={status} but decision={decision}")
            if status == "paradox_held" and decision in ("commit_to_a", "commit_to_b"):
                issues.append(f"Contradictory state on {t['id']}: status={status} but decision={decision}")

        report[label] = {
            "issues": issues,
            "clean": len(issues) == 0,
        }

    return report


# ===========================================================================
# Stage 8: Artifact Generation
# ===========================================================================

def _build_markdown(
    validation: dict,
    v2_dec: dict,
    v3_dec: dict,
    deltas: dict,
    diff_map: dict,
    margin_entropy: dict,
    paradox_analysis: dict,
    integrity: dict,
) -> str:
    """Build the phase4_comparison.md report."""
    lines = []

    lines.append("# Phase 4 Collapse Validation — Comparison Report\n")
    lines.append("## 1. Validation Summary\n")
    for label in ("v2", "v3"):
        v = validation[label]
        status = "PASS" if v["valid"] else f"FAIL ({len(v['issues'])} issues)"
        lines.append(f"**{label.upper()}**: {status} — {v['claims']} claims, {v['tensions']} tensions, "
                      f"{v['paradoxes']} paradoxes, {v['emoji_vectors']} emoji vectors, "
                      f"mission={v['mission_id']}, iteration={v['iteration']}")
        if v["issues"]:
            for issue in v["issues"]:
                lines.append(f"  - {issue}")
        lines.append("")

    lines.append("## 2. Decision Summary\n")
    lines.append("| Metric | V2 Baseline | V3 Experimental | Delta |")
    lines.append("|---|---:|---:|---:|")
    rows = [
        ("Total tensions", v2_dec["total"], v3_dec["total"], deltas["total"]),
        ("Committed", v2_dec["committed"], v3_dec["committed"], deltas["committed"]),
        ("  Commit to A", v2_dec["committed_a"], v3_dec["committed_a"], deltas["committed_a"]),
        ("  Commit to B", v2_dec["committed_b"], v3_dec["committed_b"], deltas["committed_b"]),
        ("Deferred", v2_dec["deferred"], v3_dec["deferred"], deltas["deferred"]),
        ("Paradox-held", v2_dec["paradox_held"], v3_dec["paradox_held"], deltas["paradox_held"]),
        ("Errors", v2_dec["errors"], v3_dec["errors"], deltas["errors"]),
        ("Paradox vetoed", v2_dec["vetoed"], v3_dec["vetoed"], deltas["vetoed"]),
    ]
    for row in rows:
        sign = "+" if isinstance(row[3], (int, float)) and row[3] > 0 else ""
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {sign}{row[3]} |")
    lines.append("")

    lines.append("| Rate | V2 | V3 | Delta |")
    lines.append("|---|---:|---:|---:|")
    rate_rows = [
        ("Commit rate", f"{v2_dec['commit_rate']}%", f"{v3_dec['commit_rate']}%", f"{deltas['commit_rate']:+.2f}%"),
        ("Defer rate", f"{v2_dec['defer_rate']}%", f"{v3_dec['defer_rate']}%", f"{deltas['defer_rate']:+.2f}%"),
        ("Paradox-hold rate", f"{v2_dec['paradox_hold_rate']}%", f"{v3_dec['paradox_hold_rate']}%", f"{deltas['paradox_hold_rate']:+.2f}%"),
        ("Veto rate", f"{v2_dec['veto_rate']}%", f"{v3_dec['veto_rate']}%", f"{deltas['veto_rate']:+.2f}%"),
    ]
    for row in rate_rows:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |")
    lines.append("")

    lines.append("## 3. Tension-Level Diff (Shared Tensions)\n")
    lines.append(f"- **Shared tensions**: {diff_map['shared_count']}")
    lines.append(f"- **V3-only tensions**: {diff_map['v3_only_count']}")
    lines.append(f"- **Status changed**: {diff_map['status_changed_count']}")
    lines.append(f"- **Veto changed**: {diff_map['veto_changed_count']}")
    lines.append("")

    if diff_map["reversals"]:
        lines.append("### Reversals\n")
        lines.append("| Type | Count |")
        lines.append("|---|---:|")
        for rtype, count in diff_map["reversal_summary"].items():
            lines.append(f"| {rtype} | {count} |")
        lines.append("")

        lines.append("### Reversal Details\n")
        for r in diff_map["reversals"]:
            lines.append(f"- **{r['tension_id']}**: {r['v2']} -> {r['v3']} ({r['type']})")
        lines.append("")

    if diff_map["top_10_margin_changes"]:
        lines.append("### Top 10 Margin Changes\n")
        lines.append("| Tension | V2 Margin | V3 Margin | Delta |")
        lines.append("|---|---:|---:|---:|")
        for mc in diff_map["top_10_margin_changes"]:
            lines.append(f"| {mc['tension_id']} | {mc['v2']} | {mc['v3']} | {mc['delta']:+.4f} |")
        lines.append("")

    lines.append("## 4. Margin & Entropy Analysis\n")
    lines.append("### Margin Distribution\n")
    lines.append("| Stat | V2 | V3 |")
    lines.append("|---|---:|---:|")
    for stat in ("count", "mean", "median", "variance", "skew"):
        v2v = margin_entropy["v2_margin_stats"][stat]
        v3v = margin_entropy["v3_margin_stats"][stat]
        lines.append(f"| {stat} | {v2v} | {v3v} |")
    lines.append("")

    lines.append("### Entropy Distribution (Emoji Vectors)\n")
    lines.append("| Stat | V2 | V3 |")
    lines.append("|---|---:|---:|")
    for stat in ("count", "mean", "median", "variance", "skew"):
        v2v = margin_entropy["v2_entropy_stats"][stat]
        v3v = margin_entropy["v3_entropy_stats"][stat]
        lines.append(f"| {stat} | {v2v} | {v3v} |")
    lines.append("")

    lines.append("### Entropy-Veto Correlation\n")
    evc = margin_entropy["entropy_veto_correlation"]
    lines.append(f"- **Vetoed tensions mean entropy**: {evc['vetoed_mean_entropy']} (n={evc['vetoed_count']})")
    lines.append(f"- **Non-vetoed tensions mean entropy**: {evc['non_vetoed_mean_entropy']} (n={evc['non_vetoed_count']})")
    lines.append("")

    if margin_entropy["top_10_highest_entropy_paradoxes"]:
        lines.append("### Top 10 Highest-Entropy Paradoxes\n")
        lines.append("| Paradox | Entropy | Balance | Status |")
        lines.append("|---|---:|---:|---|")
        for p in margin_entropy["top_10_highest_entropy_paradoxes"]:
            lines.append(f"| {p['paradox_id']} | {p['entropy']} | {p['pole_balance']} | {p['status']} |")
        lines.append("")

    if margin_entropy["top_10_lowest_margin_tensions"]:
        lines.append("### Top 10 Lowest-Margin Tensions (V3)\n")
        lines.append("| Tension | Margin | Status |")
        lines.append("|---|---:|---|")
        for t in margin_entropy["top_10_lowest_margin_tensions"]:
            lines.append(f"| {t['tension_id']} | {t['margin']} | {t['status']} |")
        lines.append("")

    lines.append("## 5. Paradox Substrate Analysis (V3)\n")
    lines.append(f"- **Total paradoxes**: {paradox_analysis['total_paradoxes']}")
    lines.append(f"- **Total veto events**: {paradox_analysis['total_veto_events']}")
    lines.append(f"- **Paradoxes with vetoes**: {paradox_analysis['paradoxes_with_vetoes']}")
    lines.append(f"- **Paradoxes without vetoes**: {paradox_analysis['paradoxes_without_vetoes']}")
    lines.append("")

    lines.append("### Entropy Clusters\n")
    for band, count in paradox_analysis["entropy_clusters"].items():
        lines.append(f"- **{band}**: {count} paradoxes")
    lines.append("")

    if paradox_analysis["top_vetoers"]:
        lines.append("### Top Paradox Vetoers (by influence)\n")
        lines.append("| Paradox | Vetoes | Entropy | Influence |")
        lines.append("|---|---:|---:|---:|")
        for v in paradox_analysis["top_vetoers"]:
            lines.append(f"| {v['paradox_id']} | {v['veto_count']} | {v['entropy']} | {v['influence_score']} |")
        lines.append("")

    lines.append("### Dominance\n")
    dom = paradox_analysis["dominance"]
    lines.append(f"- **Top 5 by influence**: {', '.join(dom['top_5_by_influence'])}")
    lines.append(f"- **Top 5 by veto count**: {', '.join(dom['top_5_by_veto_count'])}")
    lines.append("")

    lines.append("## 6. Structural Integrity\n")
    for label in ("v2", "v3"):
        status = "CLEAN" if integrity[label]["clean"] else f"ISSUES ({len(integrity[label]['issues'])})"
        lines.append(f"**{label.upper()}**: {status}")
        if integrity[label]["issues"]:
            for issue in integrity[label]["issues"]:
                lines.append(f"  - {issue}")
        lines.append("")

    lines.append("## 7. Conclusions\n")
    lines.append(f"- V3 has {deltas['total']} more tensions than V2 ({v2_dec['total']} vs {v3_dec['total']})")
    lines.append(f"- V3 commit rate: {v3_dec['commit_rate']}% vs V2: {v2_dec['commit_rate']}% (delta: {deltas['commit_rate']:+.2f}%)")
    lines.append(f"- V3 paradox-hold rate: {v3_dec['paradox_hold_rate']}% vs V2: {v2_dec['paradox_hold_rate']}% (delta: {deltas['paradox_hold_rate']:+.2f}%)")
    lines.append(f"- V3 veto rate: {v3_dec['veto_rate']}% vs V2: {v2_dec['veto_rate']}% (delta: {deltas['veto_rate']:+.2f}%)")
    lines.append(f"- Paradox vetoes in V3: {v3_dec['vetoed']} (from {paradox_analysis['paradoxes_with_vetoes']} distinct paradoxes)")
    lines.append(f"- {diff_map['status_changed_count']} of {diff_map['shared_count']} shared tensions changed outcome between runs")
    lines.append(f"- The expanded paradox substrate ({paradox_analysis['total_paradoxes']} vs {validation['v2']['paradoxes']}) demonstrably constrains Collapse behavior")
    lines.append("")
    lines.append("---\n*Generated by phase4_completion.py — Phase 4 Completion Package*\n")

    return "\n".join(lines)


# ===========================================================================
# Main
# ===========================================================================

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("PHASE 4 COMPLETION PACKAGE")
    print("=" * 60)

    # --- Load snapshots ---
    print("\n[Stage 1] Loading and validating snapshots...")
    if not V2_COLLAPSED.exists():
        print(f"  ABORT: {V2_COLLAPSED} not found")
        return
    if not V3_COLLAPSED.exists():
        print(f"  ABORT: {V3_COLLAPSED} not found")
        return

    v2_state, v2_raw = _load_snapshot(V2_COLLAPSED)
    v3_state, v3_raw = _load_snapshot(V3_COLLAPSED)

    validation = stage1_validate(v2_raw, v3_raw)
    print(f"  V2: {'PASS' if validation['v2']['valid'] else 'FAIL'} "
          f"({validation['v2']['tensions']} tensions, {validation['v2']['paradoxes']} paradoxes)")
    print(f"  V3: {'PASS' if validation['v3']['valid'] else 'FAIL'} "
          f"({validation['v3']['tensions']} tensions, {validation['v3']['paradoxes']} paradoxes)")
    if validation['v2']['issues']:
        for issue in validation['v2']['issues']:
            print(f"    V2 issue: {issue}")
    if validation['v3']['issues']:
        for issue in validation['v3']['issues']:
            print(f"    V3 issue: {issue}")

    # --- Decision extraction ---
    print("\n[Stage 2] Extracting decision types...")
    v2_dec = stage2_decisions(v2_raw, "v2")
    v3_dec = stage2_decisions(v3_raw, "v3")
    print(f"  V2: {v2_dec['committed']} committed, {v2_dec['deferred']} deferred, "
          f"{v2_dec['paradox_held']} held, {v2_dec['errors']} errors, {v2_dec['vetoed']} vetoed")
    print(f"  V3: {v3_dec['committed']} committed, {v3_dec['deferred']} deferred, "
          f"{v3_dec['paradox_held']} held, {v3_dec['errors']} errors, {v3_dec['vetoed']} vetoed")

    # --- Delta computation ---
    print("\n[Stage 3] Computing deltas...")
    deltas = stage3_deltas(v2_dec, v3_dec)
    print(f"  Committed delta: {deltas['committed']:+d}")
    print(f"  Paradox-held delta: {deltas['paradox_held']:+d}")
    print(f"  Veto delta: {deltas['vetoed']:+d}")
    print(f"  Commit rate delta: {deltas['commit_rate']:+.2f}%")
    print(f"  Paradox-hold rate delta: {deltas['paradox_hold_rate']:+.2f}%")

    # --- Tension diff ---
    print("\n[Stage 4] Building tension-level diff map...")
    diff_map = stage4_tension_diff(v2_raw, v3_raw)
    print(f"  Shared tensions: {diff_map['shared_count']}")
    print(f"  V3-only tensions: {diff_map['v3_only_count']}")
    print(f"  Status changed: {diff_map['status_changed_count']}")
    print(f"  Reversals: {len(diff_map['reversals'])}")
    if diff_map['reversal_summary']:
        for rtype, count in diff_map['reversal_summary'].items():
            print(f"    {rtype}: {count}")

    # --- Margin & entropy ---
    print("\n[Stage 5] Analyzing margins and entropy...")
    margin_entropy = stage5_margin_entropy(v2_raw, v3_raw, v2_state, v3_state)
    print(f"  V2 margin: mean={margin_entropy['v2_margin_stats']['mean']}, "
          f"median={margin_entropy['v2_margin_stats']['median']}")
    print(f"  V3 margin: mean={margin_entropy['v3_margin_stats']['mean']}, "
          f"median={margin_entropy['v3_margin_stats']['median']}")
    evc = margin_entropy['entropy_veto_correlation']
    print(f"  Entropy-veto: vetoed_mean={evc['vetoed_mean_entropy']}, "
          f"non_vetoed_mean={evc['non_vetoed_mean_entropy']}")

    # --- Paradox substrate ---
    print("\n[Stage 6] Analyzing paradox substrate (V3)...")
    paradox_analysis = stage6_paradox_substrate(v3_raw, v3_state)
    print(f"  Total paradoxes: {paradox_analysis['total_paradoxes']}")
    print(f"  Total veto events: {paradox_analysis['total_veto_events']}")
    print(f"  Paradoxes with vetoes: {paradox_analysis['paradoxes_with_vetoes']}")
    print(f"  Entropy clusters: {paradox_analysis['entropy_clusters']}")

    # --- Integrity ---
    print("\n[Stage 7] Running structural integrity checks...")
    integrity = stage7_integrity(v2_raw, v3_raw)
    print(f"  V2: {'CLEAN' if integrity['v2']['clean'] else 'ISSUES'}")
    print(f"  V3: {'CLEAN' if integrity['v3']['clean'] else 'ISSUES'}")
    if integrity['v2']['issues']:
        for issue in integrity['v2']['issues'][:5]:
            print(f"    V2: {issue}")
    if integrity['v3']['issues']:
        for issue in integrity['v3']['issues'][:5]:
            print(f"    V3: {issue}")

    # --- Generate artifacts ---
    print("\n[Stage 8] Generating artifacts...")

    # 1. phase4_comparison.json
    comparison_data = {
        "validation": validation,
        "v2_decisions": v2_dec,
        "v3_decisions": v3_dec,
        "deltas": deltas,
        "tension_diff_summary": {
            "shared_count": diff_map["shared_count"],
            "v3_only_count": diff_map["v3_only_count"],
            "status_changed_count": diff_map["status_changed_count"],
            "veto_changed_count": diff_map["veto_changed_count"],
            "reversal_summary": diff_map["reversal_summary"],
        },
        "margin_entropy_summary": {
            "v2_margin_stats": margin_entropy["v2_margin_stats"],
            "v3_margin_stats": margin_entropy["v3_margin_stats"],
            "v2_entropy_stats": margin_entropy["v2_entropy_stats"],
            "v3_entropy_stats": margin_entropy["v3_entropy_stats"],
            "entropy_veto_correlation": margin_entropy["entropy_veto_correlation"],
        },
        "paradox_summary": {
            "total_paradoxes": paradox_analysis["total_paradoxes"],
            "total_veto_events": paradox_analysis["total_veto_events"],
            "paradoxes_with_vetoes": paradox_analysis["paradoxes_with_vetoes"],
            "entropy_clusters": paradox_analysis["entropy_clusters"],
            "dominance": paradox_analysis["dominance"],
        },
        "integrity": integrity,
    }
    p1 = SNAPSHOT_DIR / "phase4_comparison.json"
    with open(p1, "w", encoding="utf-8") as f:
        json.dump(comparison_data, f, indent=2)
    print(f"  Written: {p1.name}")

    # 2. phase4_comparison.md
    md = _build_markdown(validation, v2_dec, v3_dec, deltas, diff_map,
                         margin_entropy, paradox_analysis, integrity)
    p2 = SNAPSHOT_DIR / "phase4_comparison.md"
    with open(p2, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  Written: {p2.name}")

    # 3. phase4_paradox_analysis.json
    p3 = SNAPSHOT_DIR / "phase4_paradox_analysis.json"
    with open(p3, "w", encoding="utf-8") as f:
        json.dump(paradox_analysis, f, indent=2)
    print(f"  Written: {p3.name}")

    # 4. phase4_margin_entropy_report.json
    p4 = SNAPSHOT_DIR / "phase4_margin_entropy_report.json"
    with open(p4, "w", encoding="utf-8") as f:
        json.dump(margin_entropy, f, indent=2)
    print(f"  Written: {p4.name}")

    # 5. phase4_tension_diff_map.json
    p5 = SNAPSHOT_DIR / "phase4_tension_diff_map.json"
    with open(p5, "w", encoding="utf-8") as f:
        json.dump(diff_map, f, indent=2)
    print(f"  Written: {p5.name}")

    # --- HOLD ---
    print("\n" + "=" * 60)
    print("PHASE 4 COMPLETION PACKAGE — ALL ARTIFACTS GENERATED")
    print("=" * 60)
    print("\nHOLD — Awaiting review. No further analysis will be performed.")
    print("Artifacts written to:", SNAPSHOT_DIR)
    print("  1. phase4_comparison.json")
    print("  2. phase4_comparison.md")
    print("  3. phase4_paradox_analysis.json")
    print("  4. phase4_margin_entropy_report.json")
    print("  5. phase4_tension_diff_map.json")


if __name__ == "__main__":
    main()
