"""
SovereignNEXT — Three-Model Governed Run Suite

Runs the canonical V5 pipeline three times (or once with --model),
each time binding ALL LLM calls to a single model:

  Run A: LLaMA   (Meta-Llama-3-8B-Instruct.Q4_0.gguf)
  Run B: Mistral (Mistral-7B-Instruct-v0.3.Q4_0.gguf)
  Run C: Phi     (Phi-4-mini-instruct-Q4_K_M.gguf)

Produces independent artifacts per model in:
  artifacts/three_model_run/<model_name>/

Phase 5 operator sequence is UNCHANGED: Collapse -> Become -> Paradox-Hold -> Observer.
No governance edits. No operator changes. No OpenClaw integration.

Phi requires a thin adapter because LLMClient.generate() uses GPT4All,
but Phi runs via llama-cpp-python (generate_outer path).

Default starting snapshot: SovereignNEXT/pipeline/v5_final_state_snapshot.json
  (Sovereign-V5-Anchor sealed baseline)

Usage:
  python -m SovereignNEXT.pipeline.run_three_model_suite --model llama
  python -m SovereignNEXT.pipeline.run_three_model_suite --model mistral
  python -m SovereignNEXT.pipeline.run_three_model_suite --model phi
  python -m SovereignNEXT.pipeline.run_three_model_suite --all
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

from agents.llm_client import LLMClient, SWAY_MODEL, OPIE_MODEL, OUTER_MODEL
from SovereignNEXT.pipeline.run_sovereign_pipeline_v5 import run_canonical_pipeline

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

MODEL_REGISTRY = {
    "llama": {
        "model_name": SWAY_MODEL,
        "label": "LLaMA-3.1-8B-Instruct",
        "backend": "gpt4all",
        "role": "collapse",
    },
    "mistral": {
        "model_name": OPIE_MODEL,
        "label": "Mistral-7B-Instruct-v0.3",
        "backend": "gpt4all",
        "role": "become",
    },
    "phi": {
        "model_name": OUTER_MODEL,
        "label": "Phi-4-mini-instruct",
        "backend": "llama-cpp",
        "role": "outer",
    },
}

ARTIFACTS_ROOT = REPO_ROOT / "artifacts" / "three_model_run"


# ---------------------------------------------------------------------------
# Phi adapter — wraps LLMClient so .generate() routes to .generate_outer()
# ---------------------------------------------------------------------------

class PhiLLMAdapter:
    """Thin adapter that makes Phi accessible via the standard generate() interface.

    The canonical pipeline calls llm.generate(model=..., system_prompt=..., user_prompt=..., ...).
    For LLaMA and Mistral, LLMClient.generate() handles this via GPT4All.
    For Phi, GPT4All can't load the model — it must go through llama-cpp.

    This adapter intercepts generate() calls and routes them to generate_outer(),
    while passing through embed() calls unchanged.
    """

    def __init__(self, client: LLMClient):
        self._client = client

    def generate(self, model: str, system_prompt: str, user_prompt: str,
                 temp: float = 0.4, max_tokens: int = 2048, **kwargs) -> str:
        """Route all generate() calls to the Phi llama-cpp backend."""
        return self._client.generate_outer(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
        )

    def embed(self, text):
        """Pass through to underlying client's embedding model."""
        return self._client.embed(text)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False


# ---------------------------------------------------------------------------
# Run metadata
# ---------------------------------------------------------------------------

def _save_run_metadata(output_dir: Path, model_key: str, model_info: dict,
                       snapshot_path: str, seed: int, passes: int,
                       start_time: str, end_time: str, duration_sec: float,
                       result=None):
    """Save structured run metadata JSON."""
    metadata = {
        "suite": "Three-Model Governed Run",
        "model_key": model_key,
        "model_name": model_info["model_name"],
        "model_label": model_info["label"],
        "model_backend": model_info["backend"],
        "snapshot": snapshot_path,
        "seed": seed,
        "passes": passes,
        "phase": 5,
        "governance_version": "v1",
        "baseline": "Sovereign-V5-Anchor",
        "operator_sequence": "Collapse -> Become -> Paradox-Hold -> Observer",
        "start_time": start_time,
        "end_time": end_time,
        "duration_sec": round(duration_sec, 2),
        "status": "completed" if result is not None else "failed",
    }

    if result is not None:
        metadata["final_state_hash"] = result.final_state_hash
        metadata["input_content_hash"] = result.input_content_hash
        metadata["final_claims"] = result.final_claims
        metadata["final_tensions"] = result.final_tensions
        metadata["final_paradoxes"] = result.final_paradoxes
        metadata["final_emoji"] = result.final_emoji

    path = output_dir / "run_metadata.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"  Run metadata saved: {path}")
    return metadata


def _save_hash_manifest(output_dir: Path):
    """Compute SHA-256 for all JSON files in output_dir and save manifest."""
    manifest = {}
    for fp in sorted(output_dir.glob("*.json")):
        h = hashlib.sha256()
        with open(fp, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        manifest[fp.name] = h.hexdigest()

    path = output_dir / "hash_manifest.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Hash manifest saved: {path}")
    return manifest


# ---------------------------------------------------------------------------
# Single model run
# ---------------------------------------------------------------------------

def run_single_model(model_key: str, snapshot_path: str, passes: int, seed: int):
    """Execute one full governed pipeline run with a specific model."""
    if model_key not in MODEL_REGISTRY:
        print(f"ERROR: Unknown model key '{model_key}'. Choose from: {list(MODEL_REGISTRY.keys())}")
        return None

    model_info = MODEL_REGISTRY[model_key]
    output_dir = ARTIFACTS_ROOT / model_key
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print(f"THREE-MODEL SUITE — Run: {model_key.upper()}")
    print(f"  Model: {model_info['model_name']}")
    print(f"  Label: {model_info['label']}")
    print(f"  Backend: {model_info['backend']}")
    print(f"  Output: {output_dir}")
    print(f"  Snapshot: {snapshot_path}")
    print(f"  Passes: {passes} | Seed: {seed} | Phase: 5")
    print("=" * 70)

    start_time = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()

    try:
        if model_info["backend"] == "llama-cpp":
            # Phi needs the adapter — pipeline will receive PhiLLMAdapter
            # which routes generate() -> generate_outer().
            # We need to monkey-patch the pipeline's LLM init for this.
            # Instead, we use model_override with a special marker and
            # handle it in the pipeline. But that's invasive.
            #
            # Cleaner approach: run the pipeline with model_override set,
            # but we need the pipeline to use our adapter.
            #
            # Simplest: temporarily patch LLMClient to route generate()
            # for Phi model through generate_outer().
            print("  NOTE: Phi backend uses llama-cpp adapter")
            result = _run_with_phi_adapter(snapshot_path, passes, seed, output_dir)
        else:
            # LLaMA and Mistral — standard GPT4All path
            result = run_canonical_pipeline(
                snapshot_path=snapshot_path,
                phase=5,
                passes=passes,
                seed=seed,
                model_override=model_info["model_name"],
                output_dir=str(output_dir),
            )
    except Exception as e:
        duration = time.perf_counter() - t0
        end_time = datetime.now(timezone.utc).isoformat()
        print(f"\n  RUN FAILED after {duration:.1f}s: {e}")
        import traceback
        traceback.print_exc()
        _save_run_metadata(output_dir, model_key, model_info,
                           snapshot_path, seed, passes,
                           start_time, end_time, duration, result=None)
        return None

    duration = time.perf_counter() - t0
    end_time = datetime.now(timezone.utc).isoformat()

    _save_run_metadata(output_dir, model_key, model_info,
                       snapshot_path, seed, passes,
                       start_time, end_time, duration, result=result)
    _save_hash_manifest(output_dir)

    print(f"\n  Run {model_key.upper()} complete: {duration:.1f}s ({duration/60:.1f}m)")
    return result


def _run_with_phi_adapter(snapshot_path: str, passes: int, seed: int, output_dir: Path):
    """Run the canonical pipeline using the Phi adapter.

    Since the pipeline creates its own LLMClient internally, we need to
    monkey-patch the import so it uses our PhiLLMAdapter instead.
    This is the minimal-invasive approach.
    """
    # The pipeline imports LLMClient at line 424 (inside the function).
    # We'll override the LLMClient class temporarily so that when the
    # pipeline instantiates it, generate() routes to generate_outer().
    #
    # CONSTRAINT: The patch is LOCAL to this function and restored in the
    # finally block below. It must NOT modify LLMClient behavior globally
    # or bleed into other runs.

    class _PatchedLLMClient(LLMClient):
        """LLMClient subclass that routes generate() through Phi's llama-cpp path."""

        def generate(self, model: str, system_prompt: str, user_prompt: str,
                     temp: float = 0.4, max_tokens: int = 2048, **kwargs) -> str:
            return self.generate_outer(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
            )

    # Temporarily patch the agents.llm_client module
    import agents.llm_client as llm_module
    original_class = llm_module.LLMClient
    llm_module.LLMClient = _PatchedLLMClient

    try:
        result = run_canonical_pipeline(
            snapshot_path=snapshot_path,
            phase=5,
            passes=passes,
            seed=seed,
            model_override=OUTER_MODEL,
            output_dir=str(output_dir),
        )
    finally:
        # Restore original
        llm_module.LLMClient = original_class

    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="SovereignNEXT Three-Model Governed Run Suite",
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=list(MODEL_REGISTRY.keys()),
        help="Which model to run (llama, mistral, phi)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all three models sequentially",
    )
    parser.add_argument(
        "--snapshot",
        type=str,
        default=None,
        help="Path to starting snapshot (default: v5_final_state_snapshot.json — Sovereign-V5-Anchor)",
    )
    parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Number of LLM + operator passes (default: 3)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="RNG seed for Phase 5 operators (default: 42)",
    )

    args = parser.parse_args()

    if not args.model and not args.all:
        parser.error("Specify --model {llama,mistral,phi} or --all")

    snapshot = args.snapshot
    if snapshot is None:
        default_snap = REPO_ROOT / "SovereignNEXT" / "pipeline" / "v5_final_state_snapshot.json"
        snapshot = str(default_snap)

    if args.all:
        models_to_run = ["llama", "mistral", "phi"]
    else:
        models_to_run = [args.model]

    print("\n" + "#" * 70)
    print("# CONEXUS SOVEREIGN — THREE-MODEL GOVERNED RUN SUITE")
    print(f"# Models: {', '.join(m.upper() for m in models_to_run)}")
    print(f"# Snapshot: {Path(snapshot).name}")
    print(f"# Passes: {args.passes} | Seed: {args.seed}")
    print("# Governance: v1 | Phase: 5")
    print("# Operator sequence: Collapse -> Become -> Paradox-Hold -> Observer")
    print("#" * 70)

    results = {}
    for model_key in models_to_run:
        results[model_key] = run_single_model(
            model_key=model_key,
            snapshot_path=snapshot,
            passes=args.passes,
            seed=args.seed,
        )

    # Summary
    print("\n" + "=" * 70)
    print("SUITE SUMMARY")
    print("=" * 70)
    for model_key, result in results.items():
        if result is not None:
            print(f"  {model_key.upper():>8}: COMPLETED | "
                  f"claims={result.final_claims} tensions={result.final_tensions} "
                  f"paradoxes={result.final_paradoxes} | "
                  f"hash={result.final_state_hash[:16]}...")
        else:
            print(f"  {model_key.upper():>8}: FAILED")
    print("=" * 70)


if __name__ == "__main__":
    main()
