"""
SovereignNEXT Dashboard — Phase 6 Observer API
A read-only FastAPI server that loads V5 pipeline snapshots, runs
sovereign_observe() to produce SovereignReports, and serves them
via GET-only endpoints.

Hard constraints (Glass Wall):
  - Zero write endpoints (no POST, PUT, DELETE, PATCH)
  - No state mutation — all data loaded once at startup, frozen
  - No prescriptive language in any response
  - Deterministic: same snapshot always yields same report

Run from repo root:
  python -m SovereignNEXT.dashboard.server
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# Path setup — ensure repo root is on sys.path for SovereignNEXT imports
# ---------------------------------------------------------------------------

DASHBOARD_DIR = Path(__file__).resolve().parent
SOVEREIGN_DIR = DASHBOARD_DIR.parent
REPO_ROOT = SOVEREIGN_DIR.parent
PIPELINE_DIR = SOVEREIGN_DIR / "pipeline"
FRONTEND_DIST = DASHBOARD_DIR / "frontend" / "dist"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.sovereign_observer import (
    sovereign_observe,
    SovereignReport,
    ParadoxDigest,
    OperatorLedger,
)

# ---------------------------------------------------------------------------
# Snapshot registry — loaded once at startup, never mutated
# ---------------------------------------------------------------------------

SNAPSHOT_FILES = {
    "pass1": PIPELINE_DIR / "v5_pass1_state_snapshot.json",
    "pass2": PIPELINE_DIR / "v5_pass2_state_snapshot.json",
    "pass3": PIPELINE_DIR / "v5_pass3_state_snapshot.json",
    "final": PIPELINE_DIR / "v5_final_state_snapshot.json",
}

CANONICAL_REPORT_FILE = PIPELINE_DIR / "v5_canonical_report.json"
SEAL_FILE = PIPELINE_DIR / "Sovereign-V5-Anchor.seal.json"


def _load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON file. Raises FileNotFoundError if missing."""
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _serialize_paradox_digest(d: ParadoxDigest) -> Dict[str, Any]:
    """Convert ParadoxDigest dataclass to JSON-safe dict."""
    return {
        "paradox_id": d.paradox_id,
        "status": d.status,
        "entropy": d.entropy,
        "balance": d.balance,
        "pole_a": d.pole_a,
        "pole_b": d.pole_b,
        "veto_state": d.veto_state,
        "recent_actions": d.recent_actions,
        "last_updated": d.last_updated,
    }


def _serialize_operator_ledger(ledger: OperatorLedger) -> Dict[str, Any]:
    """Convert OperatorLedger dataclass to JSON-safe dict."""
    return {
        "operator_name": ledger.operator_name,
        "action_counts": ledger.action_counts,
        "affected_paradox_ids": ledger.affected_paradox_ids,
    }


def _serialize_report(report: SovereignReport) -> Dict[str, Any]:
    """Convert SovereignReport to a JSON-safe dict."""
    return {
        "timestamp": report.timestamp,
        "state_hash": report.state_hash,
        "paradox_counts_by_status": report.paradox_counts_by_status,
        "entropy_band_distribution": report.entropy_band_distribution,
        "balance_window_distribution": report.balance_window_distribution,
        "veto_summary": report.veto_summary,
        "belief_stratification": report.belief_stratification,
        "integrity_attestations": report.integrity_attestations,
        "anomaly_flags": report.anomaly_flags,
        "paradox_digests": [_serialize_paradox_digest(d) for d in report.paradox_digests],
        "operator_ledgers": [_serialize_operator_ledger(led) for led in report.operator_ledgers],
    }


# ---------------------------------------------------------------------------
# Startup: load all snapshots and pre-compute reports
# ---------------------------------------------------------------------------

# These are populated at startup and never mutated
_states: Dict[str, SystemState] = {}
_reports: Dict[str, Dict[str, Any]] = {}
_canonical_report: Dict[str, Any] = {}
_seal: Dict[str, Any] = {}
_paradox_details: Dict[str, Dict[str, Dict[str, Any]]] = {}


def _build_paradox_detail(paradox_dict: Dict[str, Any], ev_dict: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a detailed paradox view including emoji sequence as glyphs."""
    poles = paradox_dict.get("poles", {})
    detail = {
        "id": paradox_dict.get("id", ""),
        "status": paradox_dict.get("status", ""),
        "pole_a": poles.get("a", {}),
        "pole_b": poles.get("b", {}),
        "metrics": paradox_dict.get("metrics", {}),
        "constraints": paradox_dict.get("constraints", {}),
        "history": paradox_dict.get("history", []),
        "rubric_scores": paradox_dict.get("rubric_scores", []),
        "links": paradox_dict.get("links", {}),
        "timestamp": paradox_dict.get("timestamp", ""),
    }
    if ev_dict:
        core = ev_dict.get("core", {})
        detail["emoji_vector"] = {
            "id": ev_dict.get("id", ""),
            "sequence": core.get("sequence", []),
            "sequence_display": "".join(core.get("sequence", [])),
            "poles": core.get("poles", {}),
            "length": core.get("length", 0),
            "metrics": ev_dict.get("metrics", {}),
        }
    else:
        detail["emoji_vector"] = None
    return detail


def _startup_load():
    """Load all pipeline artifacts at startup. Called once."""
    global _canonical_report, _seal

    print("[OBSERVER] Loading pipeline artifacts...", flush=True)

    # Load canonical report
    try:
        _canonical_report = _load_json(CANONICAL_REPORT_FILE)
        print(f"  Canonical report loaded: {len(_canonical_report.get('per_pass', []))} passes", flush=True)
    except FileNotFoundError as e:
        print(f"  WARNING: {e}", flush=True)

    # Load seal
    try:
        _seal = _load_json(SEAL_FILE)
        print(f"  Seal loaded: {_seal.get('baseline_id', 'unknown')}", flush=True)
    except FileNotFoundError as e:
        print(f"  WARNING: {e}", flush=True)

    # Load state snapshots and compute observer reports
    for pass_id, path in SNAPSHOT_FILES.items():
        try:
            raw = _load_json(path)
            state = SystemState.from_dict(raw)
            _states[pass_id] = state

            # Run sovereign observer
            report = sovereign_observe(state)
            _reports[pass_id] = _serialize_report(report)

            # Build per-paradox detail index
            ev_index = {ev.get("id"): ev for ev in raw.get("emoji_fields", [])}
            paradox_details = {}
            for p_dict in raw.get("paradoxes", []):
                pid = p_dict.get("id", "")
                ev_id = p_dict.get("emoji_vector_id")
                ev_dict = ev_index.get(ev_id) if ev_id else None
                paradox_details[pid] = _build_paradox_detail(p_dict, ev_dict)
            _paradox_details[pass_id] = paradox_details

            print(f"  {pass_id}: {len(state.claims)} claims, {len(state.paradoxes)} paradoxes, "
                  f"{len(report.anomaly_flags)} anomalies", flush=True)
        except FileNotFoundError as e:
            print(f"  WARNING: {e}", flush=True)
        except Exception as e:
            print(f"  ERROR loading {pass_id}: {e}", flush=True)

    print(f"[OBSERVER] Ready: {len(_reports)} snapshots loaded", flush=True)


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Sovereign Observer Dashboard",
    description="Phase 6: Read-only epistemic visibility into the Sovereign-V5-Anchor",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    _startup_load()


# ---------------------------------------------------------------------------
# GET-only endpoints (Glass Wall: zero write authority)
# ---------------------------------------------------------------------------

@app.get("/api/passes")
def list_passes():
    """List available snapshot passes."""
    available = []
    for pass_id in SNAPSHOT_FILES:
        if pass_id in _reports:
            state = _states[pass_id]
            available.append({
                "pass_id": pass_id,
                "claims": len(state.claims),
                "tensions": len(state.tensions),
                "paradoxes": len(state.paradoxes),
                "emoji_vectors": len(state.emoji_fields),
                "state_hash": _reports[pass_id]["state_hash"],
            })
    return {"passes": available}


@app.get("/api/observe/{pass_id}")
def get_observation(pass_id: str):
    """Get the SovereignReport for a specific pass."""
    if pass_id not in _reports:
        raise HTTPException(404, f"Pass '{pass_id}' not found. Available: {list(_reports.keys())}")
    return _reports[pass_id]


@app.get("/api/observe/{pass_id}/paradox/{paradox_id}")
def get_paradox_detail(pass_id: str, paradox_id: str):
    """Get detailed view of a single paradox including emoji glyphs."""
    if pass_id not in _paradox_details:
        raise HTTPException(404, f"Pass '{pass_id}' not found.")
    details = _paradox_details[pass_id]
    if paradox_id not in details:
        raise HTTPException(404, f"Paradox '{paradox_id}' not found in pass '{pass_id}'.")
    return details[paradox_id]


@app.get("/api/report")
def get_canonical_report():
    """Get the v5_canonical_report.json."""
    if not _canonical_report:
        raise HTTPException(404, "Canonical report not loaded.")
    return _canonical_report


@app.get("/api/seal")
def get_seal():
    """Get the Sovereign-V5-Anchor seal."""
    if not _seal:
        raise HTTPException(404, "Seal file not loaded.")
    return _seal


@app.get("/api/health")
def health():
    """Dashboard health check."""
    return {
        "status": "ok",
        "service": "sovereign-observer-dashboard",
        "snapshots_loaded": len(_reports),
        "seal_loaded": bool(_seal),
        "canonical_report_loaded": bool(_canonical_report),
    }


# ---------------------------------------------------------------------------
# Serve frontend static files (if built)
# ---------------------------------------------------------------------------

if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8100"))
    uvicorn.run(
        "SovereignNEXT.dashboard.server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
