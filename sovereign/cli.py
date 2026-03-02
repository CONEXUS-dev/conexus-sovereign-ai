"""
CONEXUS Sovereign CLI — Command-line interface for the dual-agent system.

Usage:
  python -m sovereign.cli "Write a creative brief for the CONEXUS website redesign"
  python -m sovereign.cli --mode collapse "Break down the FE replication into steps"
  python -m sovereign.cli --mode become "Synthesize the meaning of the CAE finding"
  python -m sovereign.cli --mode both "Analyze and reimagine the sovereign architecture"
  python -m sovereign.cli --health
  python -m sovereign.cli --audit
"""

import argparse
import json
import logging
import sys

from sovereign.orchestrator import SovereignOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CONEXUS Sovereign AI — Collapse-Become Dual-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Modes:\n"
            "  auto      Router decides (default)\n"
            "  collapse  Sway only — compression, execution planning\n"
            "  become    Opie only — synthesis, expansion, identity\n"
            "  both      Full sovereign loop (Diverge → Collapse → Become)\n"
        ),
    )
    parser.add_argument("mission", nargs="?", help="The mission/task text")
    parser.add_argument(
        "--mode", "-m",
        choices=["auto", "collapse", "become", "both"],
        default="auto",
        help="Agent routing mode (default: auto)",
    )
    parser.add_argument(
        "--gear", "-g",
        help="Nine Gears context label (e.g., STRATEGIC_TRUTH)",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Run system health check",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Show recent audit entries",
    )
    parser.add_argument(
        "--audit-count", "-n",
        type=int,
        default=10,
        help="Number of audit entries to show (default: 10)",
    )
    parser.add_argument(
        "--domain", "-d",
        default="universal",
        help="Symbolic field domain (e.g., universal, business, creative, healthcare, therapeutic, gaming, educational)",
    )
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Disable memory storage for this run",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output raw JSON instead of formatted text",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="GPT4All device (cpu, cuda, kompute). Overrides GPT4ALL_DEVICE env var.",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.device:
        import os
        os.environ["GPT4ALL_DEVICE"] = args.device

    if not args.mission and not args.health and not args.audit:
        parser.print_help()
        sys.exit(0)

    from agents.llm_client import LLMClient

    llm = LLMClient() if (args.mission or args.health) else None

    with SovereignOrchestrator(
        llm_client=llm,
        enable_memory=not args.no_memory,
    ) as orch:

        if args.health:
            _print_health(orch, args.json_output)
            return

        if args.audit:
            _print_audit(orch, args.audit_count, args.json_output)
            return

        if args.mission:
            result = orch.process_mission(
                mission=args.mission,
                mode=args.mode,
                gear_context=args.gear,
                domain=args.domain,
            )
            if args.json_output:
                print(json.dumps(result, indent=2, default=str))
            else:
                _print_result(result)


def _print_result(result: dict) -> None:
    agent = result.get("agent", "unknown")
    routing = result.get("routing", "unknown")
    confidence = result.get("confidence", 0)
    latency = result.get("latency_seconds", 0)

    print()
    print("=" * 70)
    print(f"  CONEXUS Sovereign AI — {agent.upper()} ({routing})")
    print(f"  Confidence: {confidence:.0%} | Latency: {latency:.1f}s")
    print("=" * 70)
    print()
    print(result.get("task_output", "(no output)"))
    print()

    # Execution steps (Collapse mode)
    steps = result.get("execution_steps", [])
    if steps:
        print("-" * 40)
        print("EXECUTION STEPS:")
        for step in steps:
            print(f"  {step.get('step', '?')}. {step.get('action', '')} "
                  f"[{step.get('priority', '')}] ({step.get('effort', '')})")
        print()

    # Breakthroughs
    breakthroughs = result.get("breakthroughs", [])
    if breakthroughs:
        print("-" * 40)
        print("BREAKTHROUGHS:")
        for b in breakthroughs:
            print(f"  {b}")
        print()

    # Proto-moments (Become mode)
    protos = result.get("proto_moments", [])
    if protos:
        print("-" * 40)
        print("PROTO-MOMENTS:")
        for p in protos:
            print(f"  {p}")
        print()

    # Contradictions resolved (Collapse mode)
    resolved = result.get("contradictions_resolved", [])
    if resolved:
        print("-" * 40)
        print("CONTRADICTIONS RESOLVED:")
        for r in resolved:
            print(f"  {r.get('from', '')} → {r.get('resolved_to', '')}")
        print()

    # Paradoxes held (Become mode)
    paradoxes = result.get("paradoxes_held", [])
    if paradoxes:
        print("-" * 40)
        print("PARADOXES HELD:")
        for p in paradoxes:
            print(f"  {p.get('pole_a', '')} ↔ {p.get('pole_b', '')} [{p.get('status', '')}]")
        print()

    # Memory
    mem_id = result.get("memory_stored")
    if mem_id:
        print(f"[Memory stored: {mem_id}]")

    audit_id = result.get("audit_entry_id")
    if audit_id:
        print(f"[Audit entry: #{audit_id}]")
    print()


def _print_health(orch: SovereignOrchestrator, json_output: bool) -> None:
    health = orch.health_check()
    if json_output:
        print(json.dumps(health, indent=2, default=str))
    else:
        print()
        print("CONEXUS System Health")
        print("=" * 40)
        print(f"  Overall:  {health.get('status', 'unknown')}")
        print(f"  Sway:     {health.get('sway', {}).get('status', 'unknown')}")
        print(f"  Opie:     {health.get('opie', {}).get('status', 'unknown')}")
        print(f"  Memory:   {health.get('memory', {}).get('status', 'unknown')}")
        print(f"  Audit:    {health.get('audit_entries', 0)} entries")
        print()


def _print_audit(orch: SovereignOrchestrator, count: int, json_output: bool) -> None:
    entries = orch.audit.get_recent(limit=count)
    if json_output:
        print(json.dumps(entries, indent=2, default=str))
    else:
        print()
        print(f"CONEXUS Audit Log — Last {count} Entries")
        print("=" * 70)
        if not entries:
            print("  (no entries)")
        for e in entries:
            print(f"  #{e.get('id', '?')} | {e.get('timestamp', '')[:19]} | "
                  f"{e.get('agent', '?'):>6} | "
                  f"conf={e.get('confidence', 0):.0%} | "
                  f"{e.get('latency_seconds', 0):.1f}s | "
                  f"{e.get('mission', '')[:40]}")
        print()


if __name__ == "__main__":
    main()
