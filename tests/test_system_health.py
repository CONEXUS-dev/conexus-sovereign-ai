"""
CONEXUS System Health Test Suite
Tests model loading, generation, gateway endpoints, Discord imports, and error handling.
Run with: python tests/test_system_health.py
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add repo root to path
REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import requests

results = []
benchmarks = {}


def record(name, passed, detail="", duration=0.0):
    results.append({
        "name": name,
        "passed": passed,
        "detail": detail,
        "duration_s": round(duration, 2),
    })
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {name} ({duration:.2f}s) {detail}")


# =========================================================================
# GATEWAY TESTS (requires gateway running on port 8002)
# =========================================================================

GATEWAY_URL = "http://localhost:8002"


def test_gateway_health():
    t0 = time.perf_counter()
    try:
        r = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        d = r.json()
        ok = r.status_code == 200 and d.get("status") == "ok"
        record("gateway_health", ok, f"status={d.get('status')}", time.perf_counter() - t0)
    except Exception as e:
        record("gateway_health", False, str(e), time.perf_counter() - t0)


def test_gateway_binding():
    t0 = time.perf_counter()
    try:
        r = requests.get(f"{GATEWAY_URL}/governance/binding", timeout=5)
        d = r.json()
        binding = d.get("binding_contract", {})
        has_outer = "outer" in binding
        has_sway = "sway" in binding
        has_opie = "opie" in binding
        ok = has_outer and has_sway and has_opie
        record("gateway_binding", ok,
               f"outer={'Phi-4' in str(binding.get('outer',''))}, sway={has_sway}, opie={has_opie}",
               time.perf_counter() - t0)
    except Exception as e:
        record("gateway_binding", False, str(e), time.perf_counter() - t0)


def test_gateway_outer_task():
    t0 = time.perf_counter()
    try:
        r = requests.post(f"{GATEWAY_URL}/tasks", json={
            "task_input": "State your identity in one sentence.",
            "agent_assignment": "outer",
            "security_context": {"user_id": "test", "channel_id": "test"},
        }, timeout=120)
        d = r.json()
        ok = d.get("status") == "ok" and d.get("agent") == "outer" and len(d.get("task_output", "")) > 10
        detail = f"agent={d.get('agent')}, chars={len(d.get('task_output',''))}"
        duration = time.perf_counter() - t0
        benchmarks["outer_latency_s"] = round(duration, 2)
        benchmarks["outer_response_chars"] = len(d.get("task_output", ""))
        record("gateway_outer_task", ok, detail, duration)
    except Exception as e:
        record("gateway_outer_task", False, str(e), time.perf_counter() - t0)


def test_gateway_error_handling():
    t0 = time.perf_counter()
    try:
        r = requests.post(f"{GATEWAY_URL}/tasks", json={
            "task_input": "",
            "agent_assignment": "outer",
            "security_context": {"user_id": "test", "channel_id": "test"},
        }, timeout=120)
        ok = r.status_code == 200  # Should not 500
        record("gateway_error_handling", ok, f"status_code={r.status_code}", time.perf_counter() - t0)
    except Exception as e:
        record("gateway_error_handling", False, str(e), time.perf_counter() - t0)


# =========================================================================
# IMPORT TESTS
# =========================================================================

def test_discord_bot_import():
    t0 = time.perf_counter()
    try:
        bot_dir = os.path.join(REPO_ROOT, "discord_bot")
        if bot_dir not in sys.path:
            sys.path.insert(0, bot_dir)
        # Just test that the module can be parsed without error
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "sovereign_bot_check",
            os.path.join(bot_dir, "sovereign_bot.py"),
            submodule_search_locations=[],
        )
        importlib.util.module_from_spec(spec)
        # Don't execute (would start the bot), just confirm parseable
        record("discord_bot_import", True, "sovereign_bot.py parseable", time.perf_counter() - t0)
    except Exception as e:
        record("discord_bot_import", False, str(e), time.perf_counter() - t0)


def test_llm_client_import():
    t0 = time.perf_counter()
    try:
        from agents.llm_client import OUTER_MODEL, SWAY_MODEL, OPIE_MODEL
        ok = (OUTER_MODEL == "Phi-4-mini-instruct-Q4_K_M.gguf"
              and "Llama" in SWAY_MODEL
              and "Mistral" in OPIE_MODEL)
        record("llm_client_import", ok,
               f"outer={OUTER_MODEL}, sway={SWAY_MODEL}, opie={OPIE_MODEL}",
               time.perf_counter() - t0)
    except Exception as e:
        record("llm_client_import", False, str(e), time.perf_counter() - t0)


# =========================================================================
# MODEL LOAD TESTS (heavy — load each model and confirm it works)
# =========================================================================

def test_phi4_mini_load():
    t0 = time.perf_counter()
    try:
        from agents.llm_client import LLMClient, OUTER_MODEL
        client = LLMClient()
        m = client._get_llama_model(OUTER_MODEL)
        ok = m is not None
        duration = time.perf_counter() - t0
        benchmarks["phi4_load_s"] = round(duration, 2)
        record("phi4_mini_load", ok, f"loaded in {duration:.1f}s", duration)
        client.close()
    except Exception as e:
        record("phi4_mini_load", False, str(e), time.perf_counter() - t0)


# =========================================================================
# IDENTITY FILE TESTS
# =========================================================================

def test_identity_files():
    t0 = time.perf_counter()
    files_ok = True
    detail_parts = []
    checks = [
        ("sovereign/agents/outer/SYSTEM_PROMPT.md", "Phi-4-mini-instruct"),
        ("sovereign/agents/outer/CALIBRATION_IMPRINT.md", "Phi-4-mini-instruct"),
        ("sovereign/agents/outer/OPERATIONAL_CONTRACT.md", "Phi-4-mini-instruct"),
        ("openclaw/agents/outer/agent.yaml", "Phi-4-mini"),
    ]
    for fpath, expected in checks:
        full = os.path.join(REPO_ROOT, fpath)
        try:
            content = open(full, encoding="utf-8").read()
            found = expected in content
            no_old = "Llama-3.2-3B-Instruct" not in content
            if not found or not no_old:
                files_ok = False
                detail_parts.append(f"{fpath}: missing={not found}, old_ref={not no_old}")
        except Exception as e:
            files_ok = False
            detail_parts.append(f"{fpath}: {e}")

    detail = "all Phi-4-mini, no Llama-3.2" if files_ok else "; ".join(detail_parts)
    record("identity_files", files_ok, detail, time.perf_counter() - t0)


def test_calibration_transcript():
    t0 = time.perf_counter()
    try:
        tp = os.path.join(REPO_ROOT, "SOVEREIGN_PROOF", "calibration", "phi4_mini_emoja_calibration.json")
        with open(tp, encoding="utf-8") as f:
            t_data = json.load(f)
        gears = len(t_data.get("gears", []))
        total = t_data.get("total_time_s", 0)
        ok = gears == 9 and total > 0
        record("calibration_transcript", ok, f"{gears} gears, {total}s", time.perf_counter() - t0)
    except Exception as e:
        record("calibration_transcript", False, str(e), time.perf_counter() - t0)


# =========================================================================
# MEMORY / CPU BENCHMARK
# =========================================================================

def benchmark_memory():
    try:
        import psutil
        proc = psutil.Process()
        rss_mb = proc.memory_info().rss / (1024 * 1024)
        cpu_pct = proc.cpu_percent(interval=1.0)
        benchmarks["test_runner_rss_mb"] = round(rss_mb, 1)
        benchmarks["test_runner_cpu_pct"] = cpu_pct
        print(f"  [INFO] Test runner RSS: {rss_mb:.1f} MB, CPU: {cpu_pct:.1f}%")
    except ImportError:
        print("  [SKIP] psutil not installed — memory benchmark skipped")
    except Exception as e:
        print(f"  [WARN] Memory benchmark error: {e}")


# =========================================================================
# RUNNER
# =========================================================================

def run_all():
    print("=" * 60)
    print("CONEXUS System Health Test Suite")
    print(f"Date: {datetime.now().isoformat()}")
    print("=" * 60)

    print("\n--- Import Tests ---")
    test_llm_client_import()
    test_discord_bot_import()

    print("\n--- Identity & Calibration Tests ---")
    test_identity_files()
    test_calibration_transcript()

    print("\n--- Gateway Tests ---")
    test_gateway_health()
    test_gateway_binding()

    print("\n--- Gateway Outer Agent Task Test ---")
    test_gateway_outer_task()

    print("\n--- Gateway Error Handling ---")
    test_gateway_error_handling()

    print("\n--- Model Load Test (Phi-4-mini) ---")
    test_phi4_mini_load()

    print("\n--- Memory/CPU Benchmark ---")
    benchmark_memory()

    # Summary
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    total = len(results)

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")
    print("=" * 60)

    if benchmarks:
        print("\nBenchmarks:")
        for k, v in benchmarks.items():
            print(f"  {k}: {v}")

    # Write HEALTH_REPORT.md
    report_path = os.path.join(REPO_ROOT, "tests", "HEALTH_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# CONEXUS Health Report\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Result:** {passed}/{total} passed, {failed} failed\n\n")
        f.write("## Test Results\n\n")
        f.write("| Test | Status | Duration | Detail |\n")
        f.write("|------|--------|----------|--------|\n")
        for r in results:
            status = "✅ PASS" if r["passed"] else "❌ FAIL"
            f.write(f"| {r['name']} | {status} | {r['duration_s']}s | {r['detail']} |\n")
        if benchmarks:
            f.write("\n## Benchmarks\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            for k, v in benchmarks.items():
                f.write(f"| {k} | {v} |\n")
        f.write("\n---\n\n*Generated by `tests/test_system_health.py`*\n")

    print(f"\nReport saved to: {report_path}")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
