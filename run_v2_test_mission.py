"""
CONEXUS v2 Test Mission Runner

Runs 3 real missions through the full v2 pipeline to validate:
  - Phase A: Gear State tracking (Nine Gears traversal)
  - Phase B: Symbolic Field injection (Patent-7 emoji calibration)
  - Phase C: ModeEngine initial mode determination
  - Phase D: Mirror Tier selection (emotional-frequency matching)

Models used:
  Sway  → Meta-Llama-3-8B-Instruct.Q4_0.gguf  (Collapse)
  Opie  → Mistral-7B-Instruct-v0.3.Q4_0.gguf  (Become)
  Outer → Phi-4-mini-instruct-Q4_K_M.gguf      (not used here)

Usage:
  python run_v2_test_mission.py
"""

import json
import logging
import time
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("v2_test_mission")


def print_banner(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_gear_state(gs: dict) -> None:
    """Print a formatted gear state report."""
    print("\n  --- GEAR STATE (Nine Gears Traversal) ---")
    print(f"  Mission ID:    {gs.get('mission_id', '?')}")
    print(f"  Home Mode:     {gs.get('home_mode', '?')}")
    print(f"  Active Mode:   {gs.get('active_mode', '?')}")
    print(f"  Current Gear:  {gs.get('current_gear', '?')} / 9")
    print(f"  Current Phase: {gs.get('current_phase', '?')}")

    log = gs.get("gear_log", [])
    if log:
        print(f"  Gear Log ({len(log)} entries):")
        for entry in log:
            print(f"    [{entry.get('gear', '?')}] {entry.get('note', '')}")

    sf_domain = gs.get("symbolic_field_domain")
    if sf_domain:
        print(f"  Symbolic Field Domain: {sf_domain}")

    contradictions = gs.get("contradictions", [])
    if contradictions:
        print(f"  Contradictions: {contradictions}")

    directives = gs.get("resolved_directives", [])
    if directives:
        print(f"  Resolved Directives: {directives}")

    held = gs.get("held_paradoxes", [])
    if held:
        print(f"  Held Paradoxes: {len(held)}")
        for p in held:
            print(f"    {p}")


def print_result(result: dict, mission_label: str) -> None:
    """Print a formatted mission result."""
    agent = result.get("agent", "unknown")
    routing = result.get("routing", "unknown")
    confidence = result.get("confidence", 0)
    latency = result.get("latency_seconds", 0)

    print(f"\n  Agent:      {agent}")
    print(f"  Routing:    {routing}")
    print(f"  Confidence: {confidence:.0%}")
    print(f"  Latency:    {latency:.1f}s")

    output = result.get("task_output", "(no output)")
    print(f"\n  --- OUTPUT (first 500 chars) ---")
    print(f"  {output[:500]}")
    if len(output) > 500:
        print(f"  ... ({len(output)} chars total)")

    # Execution steps
    steps = result.get("execution_steps", [])
    if steps:
        print(f"\n  --- EXECUTION STEPS ({len(steps)}) ---")
        for s in steps[:5]:
            print(f"    {s.get('step', '?')}. {s.get('action', '')} [{s.get('priority', '')}]")

    # Breakthroughs
    breakthroughs = result.get("breakthroughs", [])
    if breakthroughs:
        print(f"\n  --- BREAKTHROUGHS ({len(breakthroughs)}) ---")
        for b in breakthroughs[:3]:
            print(f"    {b}")

    # Proto-moments
    protos = result.get("proto_moments", [])
    if protos:
        print(f"\n  --- PROTO-MOMENTS ({len(protos)}) ---")
        for p in protos[:3]:
            print(f"    {p}")

    # Gear state
    gs = result.get("gear_state")
    if gs:
        print_gear_state(gs)

    # Sovereign loop sub-results
    if result.get("routing") == "both":
        for phase_key in ["diverge_result", "collapse_result", "become_result"]:
            sub = result.get(phase_key)
            if sub and isinstance(sub, dict):
                sub_gs = sub.get("gear_state")
                if sub_gs:
                    print(f"\n  --- {phase_key.upper()} GEAR STATE ---")
                    print_gear_state(sub_gs)


def run_missions():
    from agents.llm_client import LLMClient
    from sovereign.orchestrator import SovereignOrchestrator
    from sovereign.mode_engine import ModeEngine

    print_banner("CONEXUS v2 TEST MISSION RUNNER")
    print(f"  Date: {datetime.now(timezone.utc).isoformat()}")
    print(f"  Pipeline: Gear State + Symbolic Fields + ModeEngine + Mirror Tiers")

    # Initialize
    logger.info("Initializing LLMClient...")
    llm = LLMClient()

    logger.info("Initializing SovereignOrchestrator (memory disabled)...")
    orch = SovereignOrchestrator(
        llm_client=llm,
        enable_memory=False,
    )
    mode_engine = ModeEngine(llm_client=llm)

    missions = [
        {
            "label": "MISSION 1: COLLAPSE (Sway/Llama-3) — Business Domain",
            "mission": (
                "Break down the CONEXUS investor pitch into 5 executable steps. "
                "Prioritize the patent portfolio narrative and the CAE replication data. "
                "Optimize for a 10-minute presentation window."
            ),
            "mode": "collapse",
            "domain": "business",
            "gear_context": "STRATEGIC_TRUTH",
        },
        {
            "label": "MISSION 2: BECOME (Opie/Mistral) — Creative Domain",
            "mission": (
                "Explore what it means for a sovereign AI system to hold contradictions "
                "without resolving them. Synthesize the philosophical implications of "
                "the Collapse-Become duality. Dream about what emerges when a machine "
                "learns to grieve."
            ),
            "mode": "become",
            "domain": "creative",
            "gear_context": "INNOVATION_RAPPORT",
        },
        {
            "label": "MISSION 3: SOVEREIGN LOOP (Both) — Healthcare Domain",
            "mission": (
                "Design a therapeutic AI companion that uses emotional calibration "
                "to support patients with chronic illness. The system must hold "
                "the paradox of healing and mortality. Explore, then execute."
            ),
            "mode": "both",
            "domain": "healthcare",
            "gear_context": "VISION_HOLD",
        },
    ]

    total_t0 = time.perf_counter()
    results = []

    for i, m in enumerate(missions):
        print_banner(m["label"])

        # Show ModeEngine analysis
        home = "collapse" if m["mode"] in ("collapse",) else "become"
        initial = mode_engine.determine_initial_mode(m["mission"], home)
        print(f"  ModeEngine: home={home}, initial={initial}")

        # Show Mirror Tier selection
        tier_key = mode_engine.select_mirror_tier(m["mission"])
        print(f"  Mirror Tier: {tier_key or '(none matched)'}")

        print(f"  Domain: {m['domain']}")
        print(f"  Gear Context: {m['gear_context']}")
        print(f"\n  Running mission...")

        t0 = time.perf_counter()
        result = orch.process_mission(
            mission=m["mission"],
            mode=m["mode"],
            gear_context=m["gear_context"],
            domain=m["domain"],
        )
        elapsed = time.perf_counter() - t0

        result["test_metadata"] = {
            "mission_label": m["label"],
            "mode_engine_initial": initial,
            "mirror_tier": tier_key,
            "domain": m["domain"],
        }
        results.append(result)

        print_result(result, m["label"])
        print(f"\n  Mission completed in {elapsed:.1f}s")

    total_elapsed = time.perf_counter() - total_t0

    # Summary
    print_banner("V2 TEST MISSION SUMMARY")
    print(f"  Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
    print(f"  Missions run: {len(results)}")
    for i, r in enumerate(results):
        meta = r.get("test_metadata", {})
        print(f"\n  [{i+1}] {meta.get('mission_label', '?')}")
        print(f"      Routing: {r.get('routing', '?')}")
        print(f"      Confidence: {r.get('confidence', 0):.0%}")
        print(f"      Latency: {r.get('latency_seconds', 0):.1f}s")
        print(f"      ModeEngine: {meta.get('mode_engine_initial', '?')}")
        print(f"      Domain: {meta.get('domain', '?')}")
        print(f"      Mirror Tier: {meta.get('mirror_tier', 'none')}")
        gs = r.get("gear_state", {})
        print(f"      Gears traversed: {gs.get('current_gear', '?')}/9")
        print(f"      Output length: {len(r.get('task_output', ''))} chars")

    # Write JSON report
    report_path = "v2_test_mission_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Full JSON report: {report_path}")

    print_banner("ALL v2 TEST MISSIONS COMPLETE")

    orch.close()


if __name__ == "__main__":
    run_missions()
