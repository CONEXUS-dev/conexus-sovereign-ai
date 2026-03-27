"""
Phase 1 Preflight — Dry-load all three models + capture environment metadata.
This script does NOT modify any existing files or state.
"""

import sys
import os
import platform
import time
import hashlib
import json
from pathlib import Path

# Ensure repo root is on path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agents.llm_client import LLMClient, SWAY_MODEL, OPIE_MODEL, OUTER_MODEL


def get_file_sha256(filepath):
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    output_dir = Path(__file__).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # ---- Environment metadata ----
    env_info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "os": platform.system(),
        "os_version": platform.version(),
        "cwd": os.getcwd(),
        "repo_root": str(REPO_ROOT),
        "gpt4all_device": os.environ.get("GPT4ALL_DEVICE", "cpu (default)"),
        "gpt4all_ctx": os.environ.get("GPT4ALL_CTX", "4096 (default)"),
        "gpt4all_model_path": os.environ.get(
            "GPT4ALL_MODEL_PATH",
            str(Path.home() / ".cache" / "gpt4all") + " (default)",
        ),
    }

    model_dir = os.environ.get(
        "GPT4ALL_MODEL_PATH",
        str(Path.home() / ".cache" / "gpt4all"),
    )

    print("=" * 60)
    print("PHASE 1 PREFLIGHT — CONEXUS Sovereign Three-Model Suite")
    print("=" * 60)

    # ---- File inventory ----
    print("\n--- File Inventory ---")
    baseline_files = [
        REPO_ROOT / "SovereignNEXT" / "pipeline" / "Sovereign-V5-Anchor.seal.json",
        REPO_ROOT / "SovereignNEXT" / "pipeline" / "v5_final_state_snapshot.json",
        REPO_ROOT / "SovereignNEXT" / "pipeline" / "v5_canonical_report.json",
        REPO_ROOT / "SovereignNEXT" / "tests" / "v3_final_state_snapshot.json",
    ]

    file_inventory = []
    for fp in baseline_files:
        exists = fp.is_file()
        size = fp.stat().st_size if exists else 0
        entry = {
            "path": str(fp.relative_to(REPO_ROOT)),
            "exists": exists,
            "size_bytes": size,
        }
        file_inventory.append(entry)
        status = "OK" if exists else "MISSING"
        print(f"  {status:>7}  {size:>12,} bytes  {entry['path']}")

    model_files = [SWAY_MODEL, OPIE_MODEL, OUTER_MODEL]
    model_inventory = []
    for mf in model_files:
        mpath = Path(model_dir) / mf
        exists = mpath.is_file()
        size = mpath.stat().st_size if exists else 0
        entry = {
            "filename": mf,
            "path": str(mpath),
            "exists": exists,
            "size_bytes": size,
        }
        model_inventory.append(entry)
        status = "OK" if exists else "MISSING"
        print(f"  {status:>7}  {size:>15,} bytes  {mf}")

    # Save file inventory
    inv_path = output_dir / "file_inventory.txt"
    with open(inv_path, "w", encoding="utf-8") as f:
        f.write("BASELINE ARTIFACTS\n")
        f.write("-" * 60 + "\n")
        for entry in file_inventory:
            status = "OK" if entry["exists"] else "MISSING"
            f.write(f"{status:>7}  {entry['size_bytes']:>12,} bytes  {entry['path']}\n")
        f.write("\nMODEL FILES\n")
        f.write("-" * 60 + "\n")
        for entry in model_inventory:
            status = "OK" if entry["exists"] else "MISSING"
            f.write(f"{status:>7}  {entry['size_bytes']:>15,} bytes  {entry['filename']}\n")
            f.write(f"         path: {entry['path']}\n")
    print(f"\n  Saved: {inv_path.name}")

    # ---- Dry-load each model ----
    print("\n--- Model Dry-Load Test ---")
    test_system = "You are a test agent. Be concise."
    test_prompt = "Say hello in exactly 5 words."

    load_results = []

    client = LLMClient()

    # Test 1: LLaMA (Collapse path)
    print(f"\n  Loading LLaMA ({SWAY_MODEL})...")
    t0 = time.perf_counter()
    try:
        r1 = client.generate_collapse(
            system_prompt=test_system,
            user_prompt=test_prompt,
            max_tokens=64,
        )
        t1 = time.perf_counter()
        load_results.append({
            "model": SWAY_MODEL,
            "role": "collapse",
            "status": "OK",
            "load_and_generate_sec": round(t1 - t0, 2),
            "response_chars": len(r1),
            "response_preview": r1[:100],
        })
        print(f"  OK — {len(r1)} chars in {t1 - t0:.2f}s")
        print(f"  Response: {r1[:80]}")
    except Exception as e:
        t1 = time.perf_counter()
        load_results.append({
            "model": SWAY_MODEL,
            "role": "collapse",
            "status": "FAILED",
            "error": str(e),
            "duration_sec": round(t1 - t0, 2),
        })
        print(f"  FAILED — {e}")

    # Test 2: Mistral (Become path)
    print(f"\n  Loading Mistral ({OPIE_MODEL})...")
    t0 = time.perf_counter()
    try:
        r2 = client.generate_become(
            system_prompt=test_system,
            user_prompt=test_prompt,
            max_tokens=64,
        )
        t1 = time.perf_counter()
        load_results.append({
            "model": OPIE_MODEL,
            "role": "become",
            "status": "OK",
            "load_and_generate_sec": round(t1 - t0, 2),
            "response_chars": len(r2),
            "response_preview": r2[:100],
        })
        print(f"  OK — {len(r2)} chars in {t1 - t0:.2f}s")
        print(f"  Response: {r2[:80]}")
    except Exception as e:
        t1 = time.perf_counter()
        load_results.append({
            "model": OPIE_MODEL,
            "role": "become",
            "status": "FAILED",
            "error": str(e),
            "duration_sec": round(t1 - t0, 2),
        })
        print(f"  FAILED — {e}")

    # Test 3: Phi (Outer path — llama-cpp)
    print(f"\n  Loading Phi ({OUTER_MODEL})...")
    t0 = time.perf_counter()
    try:
        r3 = client.generate_outer(
            system_prompt=test_system,
            user_prompt=test_prompt,
            max_tokens=64,
        )
        t1 = time.perf_counter()
        load_results.append({
            "model": OUTER_MODEL,
            "role": "outer",
            "status": "OK",
            "load_and_generate_sec": round(t1 - t0, 2),
            "response_chars": len(r3),
            "response_preview": r3[:100],
        })
        print(f"  OK — {len(r3)} chars in {t1 - t0:.2f}s")
        print(f"  Response: {r3[:80]}")
    except Exception as e:
        t1 = time.perf_counter()
        load_results.append({
            "model": OUTER_MODEL,
            "role": "outer",
            "status": "FAILED",
            "error": str(e),
            "duration_sec": round(t1 - t0, 2),
        })
        print(f"  FAILED — {e}")

    client.close()

    # ---- Save model load log ----
    log_path = output_dir / "model_load_log.txt"
    with open(log_path, "w", encoding="utf-8") as f:
        for r in load_results:
            f.write(json.dumps(r, indent=2) + "\n\n")
    print(f"\n  Saved: {log_path.name}")

    # ---- Save preflight report ----
    all_ok = all(r["status"] == "OK" for r in load_results)
    all_files_ok = all(e["exists"] for e in file_inventory + model_inventory)

    report_path = output_dir / "preflight_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Phase 1 Preflight Report\n\n")
        f.write(f"**Timestamp:** {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        f.write(f"**Status:** {'PASS' if (all_ok and all_files_ok) else 'FAIL'}\n\n")

        f.write("## Environment\n\n")
        for k, v in env_info.items():
            f.write(f"- **{k}:** {v}\n")

        f.write("\n## Baseline Artifacts\n\n")
        f.write("| File | Exists | Size |\n|---|---|---|\n")
        for entry in file_inventory:
            status = "YES" if entry["exists"] else "**NO**"
            f.write(f"| `{entry['path']}` | {status} | {entry['size_bytes']:,} bytes |\n")

        f.write("\n## Model Files\n\n")
        f.write("| Model | Exists | Size |\n|---|---|---|\n")
        for entry in model_inventory:
            status = "YES" if entry["exists"] else "**NO**"
            f.write(f"| `{entry['filename']}` | {status} | {entry['size_bytes']:,} bytes |\n")

        f.write("\n## Dry-Load Results\n\n")
        f.write("| Model | Role | Status | Duration | Response chars |\n|---|---|---|---|---|\n")
        for r in load_results:
            dur = r.get("load_and_generate_sec", r.get("duration_sec", "?"))
            chars = r.get("response_chars", "N/A")
            f.write(f"| `{r['model']}` | {r['role']} | {r['status']} | {dur}s | {chars} |\n")

        f.write("\n## Phase 2 Readiness\n\n")
        if all_ok and all_files_ok:
            f.write("**YES** — All models loaded and generated successfully. All baseline files present.\n")
        else:
            f.write("**NO** — See failures above.\n")
            if not all_files_ok:
                missing = [e for e in file_inventory + model_inventory if not e["exists"]]
                f.write(f"\nMissing files: {[e.get('path', e.get('filename')) for e in missing]}\n")
            failed = [r for r in load_results if r["status"] != "OK"]
            if failed:
                f.write(f"\nFailed models: {[r['model'] for r in failed]}\n")
                for r in failed:
                    f.write(f"  Error: {r.get('error', 'unknown')}\n")

    print(f"  Saved: {report_path.name}")

    # ---- Summary ----
    print("\n" + "=" * 60)
    print(f"PREFLIGHT: {'PASS' if (all_ok and all_files_ok) else 'FAIL'}")
    print(f"  Files: {'all present' if all_files_ok else 'MISSING FILES'}")
    print(f"  Models: {sum(1 for r in load_results if r['status'] == 'OK')}/3 OK")
    print(f"  Phase 2 ready: {'YES' if (all_ok and all_files_ok) else 'NO'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
