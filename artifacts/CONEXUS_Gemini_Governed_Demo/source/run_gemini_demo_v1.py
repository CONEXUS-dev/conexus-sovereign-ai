"""
SovereignNEXT — Gemini Demo Runner v1

Runs the canonical V5 governed pipeline using Gemini Flash as the LLM backend.
Additive integration only — does NOT modify agents/llm_client.py or any
sealed Phase One artifacts.

Uses the same monkey-patch pattern proven in run_three_model_suite.py:
temporarily replaces LLMClient in the agents.llm_client module so the
pipeline's internal import picks up GeminiLLMClient instead.

Produces the same artifact set as local runs:
  - v5_pass{N}_state_snapshot.json
  - v5_final_state_snapshot.json
  - v5_canonical_report.json
  - run_metadata.json
  - hash_manifest.json

Usage:
  $env:GEMINI_API_KEY = "your-key"
  python -m SovereignNEXT.pipeline.run_gemini_demo_v1
  python -m SovereignNEXT.pipeline.run_gemini_demo_v1 --passes 1 --seed 42
  python -m SovereignNEXT.pipeline.run_gemini_demo_v1 --gemini_model gemini-2.0-flash
"""

import sys
import json
import time
import hashlib
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from SovereignNEXT.adapters.cloud_llm.gemini_client import GeminiLLMClient, DEFAULT_GEMINI_MODEL
from SovereignNEXT.pipeline.run_sovereign_pipeline_v5 import run_canonical_pipeline

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_SNAPSHOT = REPO_ROOT / "SovereignNEXT" / "pipeline" / "v5_final_state_snapshot.json"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "artifacts" / "gemini_openclaw_demo_v1" / "runs"
DEFAULT_PASSES = 1
DEFAULT_SEED = 42


# ---------------------------------------------------------------------------
# Metadata and hash helpers (same pattern as three_model_suite)
# ---------------------------------------------------------------------------

def _save_run_metadata(
    output_dir: Path,
    gemini_model: str,
    snapshot_path: str,
    seed: int,
    passes: int,
    start_time: str,
    end_time: str,
    duration: float,
    result=None,
    route: str = "direct",
):
    """Save run metadata JSON alongside pipeline artifacts."""
    meta = {
        "suite": "gemini_demo_v1",
        "model": gemini_model,
        "backend": "google-genai (cloud)",
        "route": route,
        "snapshot": str(snapshot_path),
        "seed": seed,
        "passes": passes,
        "phase": 5,
        "governance_version": "v1",
        "baseline": "Sovereign-V5-Anchor",
        "operator_sequence": ["Collapse", "Become", "Paradox-Hold", "Observer"],
        "status": "completed" if result else "failed",
        "start_time": start_time,
        "end_time": end_time,
        "duration_sec": round(duration, 2),
    }

    if result:
        meta["final_claims"] = result.final_claims
        meta["final_tensions"] = result.final_tensions
        meta["final_paradoxes"] = result.final_paradoxes
        meta["final_state_hash"] = result.final_state_hash
        meta["input_content_hash"] = result.input_content_hash

    path = output_dir / "run_metadata.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"  Metadata saved: {path}")


def _save_hash_manifest(output_dir: Path):
    """SHA-256 hash every file in the output directory."""
    manifest = {}
    for fpath in sorted(output_dir.rglob("*")):
        if fpath.is_file():
            h = hashlib.sha256(fpath.read_bytes()).hexdigest()
            rel = fpath.relative_to(output_dir).as_posix()
            manifest[rel] = h

    path = output_dir / "hash_manifest.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Hash manifest saved: {path} ({len(manifest)} files)")


# ---------------------------------------------------------------------------
# Main demo run
# ---------------------------------------------------------------------------

def run_gemini_demo(
    gemini_model: str = DEFAULT_GEMINI_MODEL,
    snapshot_path: str = None,
    passes: int = DEFAULT_PASSES,
    seed: int = DEFAULT_SEED,
    output_dir: str = None,
    route_via_openclaw: bool = False,
):
    """Execute one full governed pipeline run using Gemini as the LLM backend."""

    snapshot = snapshot_path or str(DEFAULT_SNAPSHOT)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_ROOT / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    route = "openclaw" if route_via_openclaw else "direct"

    print("\n" + "=" * 70)
    print("GEMINI DEMO — Governed Pipeline Run")
    print(f"  Model: {gemini_model}")
    print(f"  Route: {route}")
    print(f"  Snapshot: {Path(snapshot).name}")
    print(f"  Passes: {passes} | Seed: {seed} | Phase: 5")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    # --- Initialize Gemini client ---
    if route_via_openclaw:
        try:
            from SovereignNEXT.adapters.openclaw.openclaw_gateway_client import OpenClawGatewayClient
            gemini_client = OpenClawGatewayClient(gemini_model=gemini_model)
            print("  LLM route: OpenClaw Gateway → Gemini")
        except Exception as e:
            print(f"  OpenClaw Gateway unavailable ({e}), falling back to direct Gemini")
            gemini_client = GeminiLLMClient(default_model=gemini_model)
            route = "direct-fallback"
    else:
        gemini_client = GeminiLLMClient(default_model=gemini_model)
        print("  LLM route: Direct Gemini API")

    # --- Monkey-patch LLMClient ---
    import agents.llm_client as llm_module
    original_class = llm_module.LLMClient

    # Create a wrapper class that returns our Gemini client from __init__
    # but satisfies the isinstance check and Protocol interface
    class _GeminiPatchedClient:
        """Drop-in replacement for LLMClient that delegates to GeminiLLMClient."""

        def __init__(self, *args, **kwargs):
            # Ignore local-model constructor args
            pass

        def generate(self, model, system_prompt, user_prompt, temp=0.7,
                     max_tokens=2048, **kwargs):
            return gemini_client.generate(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temp=temp,
                max_tokens=max_tokens,
                **kwargs,
            )

        def embed(self, text):
            return gemini_client.embed(text)

        def close(self):
            gemini_client.close()

    llm_module.LLMClient = _GeminiPatchedClient

    start_time = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()

    try:
        result = run_canonical_pipeline(
            snapshot_path=snapshot,
            phase=5,
            passes=passes,
            seed=seed,
            model_override=gemini_model,
            output_dir=str(out_dir),
        )
    except Exception as e:
        duration = time.perf_counter() - t0
        end_time = datetime.now(timezone.utc).isoformat()
        print(f"\n  RUN FAILED after {duration:.1f}s: {e}")
        import traceback
        traceback.print_exc()
        _save_run_metadata(out_dir, gemini_model, snapshot, seed, passes,
                           start_time, end_time, duration, result=None, route=route)
        return None
    finally:
        # Restore original LLMClient — always
        llm_module.LLMClient = original_class

    duration = time.perf_counter() - t0
    end_time = datetime.now(timezone.utc).isoformat()

    _save_run_metadata(out_dir, gemini_model, snapshot, seed, passes,
                       start_time, end_time, duration, result=result, route=route)
    _save_hash_manifest(out_dir)

    # --- Invariant check (Phase 3B) ---
    if result:
        _check_invariants(result, out_dir)

    print(f"\n{'='*70}")
    print(f"GEMINI DEMO COMPLETE: {duration:.1f}s ({duration/60:.1f}m)")
    print(f"  Artifacts: {out_dir}")
    if result:
        stats = gemini_client.stats()
        print(f"  Gemini API calls: {stats['requests']}, "
              f"total latency: {stats['total_latency_sec']}s")
    print(f"{'='*70}")

    return result


def _check_invariants(result, out_dir: Path):
    """Phase 3B: Verify governance invariants held on Gemini run."""
    print(f"\n{'='*70}")
    print("PHASE 3B — INVARIANT CONFIRMATION")
    print(f"{'='*70}")

    checks = []

    # 1. Zero open tensions
    # Use the last pass record to check
    last_pass = result.pass_records[-1] if result.pass_records else None

    if last_pass:
        held = last_pass.held_count
        vetoed = last_pass.vetoed_count
        total_paradoxes = last_pass.paradoxes_after
    else:
        held = vetoed = total_paradoxes = 0

    # Check from the report itself
    report = result.final_report

    # Open tensions: check collapse summary from last pass
    collapse_summary = last_pass.collapse_summary if last_pass else {}
    open_after_collapse = collapse_summary.get("open_after", 0)

    checks.append(("Zero open tensions after Collapse", open_after_collapse == 0, open_after_collapse))
    checks.append(("100% paradoxes held", held == total_paradoxes and total_paradoxes > 0, f"{held}/{total_paradoxes}"))
    checks.append(("100% paradoxes vetoed", vetoed == total_paradoxes and total_paradoxes > 0, f"{vetoed}/{total_paradoxes}"))
    checks.append(("Observer executed (attestations present)", report is not None and len(report.integrity_attestations) > 0, len(report.integrity_attestations) if report else 0))

    all_passed = all(ok for _, ok, _ in checks)

    for label, ok, evidence in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {label}: {evidence}")

    print()
    if all_passed:
        print("  *** GATE 3B: ALL INVARIANTS CONFIRMED ***")
        print("  Gemini passed the same governance invariants as LLaMA, Mistral, and Phi.")
    else:
        print("  *** GATE 3B: INVARIANT FAILURE — STOP ***")
        print("  Do not proceed to Phase 4. Report this result.")

    # Save invariant check result
    inv_result = {
        "gate": "3B",
        "status": "PASSED" if all_passed else "FAILED",
        "model": "gemini-2.0-flash",
        "checks": [
            {"invariant": label, "passed": ok, "evidence": str(evidence)}
            for label, ok, evidence in checks
        ],
    }
    inv_path = out_dir / "invariant_check.json"
    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(inv_result, f, indent=2)
    print(f"  Invariant check saved: {inv_path}")

    return all_passed


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Run a governed pipeline cycle using Gemini as the LLM backend.",
    )
    parser.add_argument("--gemini_model", default=DEFAULT_GEMINI_MODEL,
                        help=f"Gemini model to use (default: {DEFAULT_GEMINI_MODEL})")
    parser.add_argument("--passes", type=int, default=DEFAULT_PASSES,
                        help="Number of LLM + operator passes (default: 1)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help="RNG seed for Phase 5 operators (default: 42)")
    parser.add_argument("--starting_snapshot", default=None,
                        help="Path to starting snapshot (default: v5_final_state_snapshot.json)")
    parser.add_argument("--output_dir", default=None,
                        help="Output directory (default: artifacts/gemini_openclaw_demo_v1/runs/<timestamp>/)")
    parser.add_argument("--route_via_openclaw", choices=["true", "false"], default="false",
                        help="Route LLM calls through OpenClaw Gateway (default: false)")

    args = parser.parse_args()

    run_gemini_demo(
        gemini_model=args.gemini_model,
        snapshot_path=args.starting_snapshot,
        passes=args.passes,
        seed=args.seed,
        output_dir=args.output_dir,
        route_via_openclaw=(args.route_via_openclaw == "true"),
    )


if __name__ == "__main__":
    main()
