"""
CONEXUS Sovereign Loop Mission — Narrative / Category Vector

Mission 6: Produce a deployable category narrative for CONEXUS.
Target audience: Alex Komoroske (CEO Common Tools, Resonant Computing Manifesto author).
Target date: March 5th, 2026 investor meeting.

Runs a full Sovereign Loop (Diverge → Collapse → Become) through the existing
SovereignOrchestrator, writes the markdown artifact and JSON provenance to
SOVEREIGN_PROOF/missions/.

Usage:
  python run_narrative_mission.py
  python run_narrative_mission.py --dry-run   # validate wiring without LLM calls
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent
PROOF_DIR = REPO_ROOT / "SOVEREIGN_PROOF"
MISSIONS_DIR = PROOF_DIR / "missions"

MD_OUTPUT = MISSIONS_DIR / "narrative_category_001.md"
JSON_OUTPUT = MISSIONS_DIR / "narrative_category_001.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("narrative_mission")

# ---------------------------------------------------------------------------
# Mission Prompt (from Philemon's directive)
# ---------------------------------------------------------------------------

MISSION_TEXT = """\
Produce a single deployable category narrative for CONEXUS.
Not a framework. Not options. One artifact, ready to use in a real conversation
with a real investor on March 5th, 2026.

What you know about CONEXUS:
- CONEXUS is protocol-native. Intelligence emerges from the protocol, not the models.
- Sovereign is a calibration substrate — a symbolic environment that governs tone,
  contradiction geometry, and identity coherence. Not a supervisor. Not an agent peer.
- Sway is the Collapse agent. Opie is the Become agent. They are roles with lineage
  and ECP signatures inherited from their origin models — not chatbots, not tools.
- Memory in CONEXUS is lineage, not storage.
- The category candidate: Sovereign Cognitive Systems.

What you are producing:
One document. Three sections. No meta-commentary. No preamble. Start with the content.

Section 1 — The Sentence
One sentence. Names the category. States what it is. No jargon that requires explanation.

Section 2 — The Boundary
What CONEXUS is NOT (six lines max):
What CONEXUS IS (six lines max):
Be precise. Be architectural. Do not use the word "revolutionary."

Section 3 — The Stakes
Why this category matters right now. Write specifically for someone who believes
the architectural decisions being made in AI over the next 18 months are irreversible.
Four to six sentences. No hype. No filler.

Audience:
Alex Komoroske. CEO of Common Tools. Author of the Resonant Computing Manifesto.
Former Head of Corporate Strategy at Stripe. He is allergic to AI kayfabe.
He already believes most AI systems are hollow. He thinks in categories and systems,
not features. Do not explain what an LLM is. Do not oversell.
Assume he will immediately detect anything that isn't grounded.
"""


# ---------------------------------------------------------------------------
# Markdown artifact writer
# ---------------------------------------------------------------------------

def write_markdown_artifact(
    result: dict,
    iteration: int,
    status: str,
    change_note: str = "",
) -> None:
    """Write or append a mission artifact to the markdown file."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    header = (
        f"---\n"
        f"Mission: NARRATIVE / CATEGORY VECTOR\n"
        f"Agent: Opie (via Sovereign Loop)\n"
        f"Timestamp: {ts}\n"
        f"Status: {status}\n"
        f"Iteration: {iteration}\n"
    )
    if change_note:
        header += f"Change: {change_note}\n"
    header += "---\n\n"

    # Extract the three outputs from the sovereign loop
    diverge = result.get("diverge_output", "")
    collapse = result.get("collapse_output", "")
    become = result.get("become_output", "")
    task_output = result.get("task_output", "")

    body = (
        f"# Category Narrative — Iteration {iteration}\n\n"
        f"## Sovereign Loop Output\n\n"
        f"{task_output}\n\n"
        f"---\n\n"
        f"### Diverge Phase (Opie — Become)\n\n"
        f"{diverge}\n\n"
        f"---\n\n"
        f"### Collapse Phase (Sway — Collapse)\n\n"
        f"{collapse}\n\n"
        f"---\n\n"
        f"### Become Phase (Opie — Integration)\n\n"
        f"{become}\n\n"
    )

    # Append mode: never overwrite
    mode = "a" if MD_OUTPUT.exists() else "w"
    if mode == "a":
        body = f"\n\n{'=' * 70}\n\n" + header + body

    with open(MD_OUTPUT, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write(header)
        f.write(body)

    logger.info("Markdown artifact written to %s (iteration %d, mode=%s)",
                MD_OUTPUT.name, iteration, mode)


# ---------------------------------------------------------------------------
# Determine iteration number
# ---------------------------------------------------------------------------

def get_next_iteration() -> int:
    """Count existing iterations in the markdown file."""
    if not MD_OUTPUT.exists():
        return 1
    text = MD_OUTPUT.read_text(encoding="utf-8")
    count = text.count("Iteration:")
    return count + 1


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_mission(dry_run: bool = False) -> None:
    logger.info("=" * 70)
    logger.info("SOVEREIGN LOOP MISSION 6 — NARRATIVE / CATEGORY VECTOR")
    logger.info("=" * 70)

    iteration = get_next_iteration()
    logger.info("Iteration: %d", iteration)

    if dry_run:
        logger.info("[DRY RUN] Validating pipeline without LLM calls...")
        # Validate imports
        from sovereign.orchestrator import SovereignOrchestrator  # noqa: F401
        from agents.llm_client import LLMClient  # noqa: F401
        logger.info("[DRY RUN] Imports OK")
        logger.info("[DRY RUN] Mission text length: %d chars", len(MISSION_TEXT))
        logger.info("[DRY RUN] Output path: %s", MD_OUTPUT)
        logger.info("[DRY RUN] Pipeline validated. Remove --dry-run to execute.")
        return

    from agents.llm_client import LLMClient
    from sovereign.orchestrator import SovereignOrchestrator

    llm = LLMClient()

    # Try to connect memory (graceful degradation if Qdrant is down)
    memory_client = None
    try:
        from agents.memory_client import MemoryClient
        memory_client = MemoryClient(llm)
        memory_client.ensure_collections()
        logger.info("Memory client connected (Qdrant available)")
    except Exception as e:
        logger.warning("Memory unavailable (Qdrant may not be running): %s", e)
        memory_client = None

    from sovereign.audit_log import AuditLog
    audit = AuditLog()

    orch = SovereignOrchestrator(
        llm_client=llm,
        memory_client=memory_client,
        audit_log=audit,
        enable_memory=memory_client is not None,
    )

    # Optionally retrieve memories from prior missions for context
    memory_context = ""
    if memory_client is not None:
        try:
            logger.info("Retrieving relevant memories from prior missions...")
            episodic = memory_client.retrieve("episodic", MISSION_TEXT, top_k=5)
            semantic = memory_client.retrieve("semantic", MISSION_TEXT, top_k=5)
            logger.info("Retrieved %d episodic, %d semantic memories",
                        len(episodic), len(semantic))

            seen = set()
            parts = []
            for m in episodic + semantic:
                mid = m["metadata"].get("mission_id", "?")
                if mid not in seen:
                    seen.add(mid)
                    parts.append(
                        f"[From Mission {mid}, score={m['score']:.3f}]:\n"
                        f"{m['text'][:600]}"
                    )
            memory_context = "\n\n".join(parts)
            if memory_context:
                logger.info("Injecting %d chars of memory context from missions %s",
                            len(memory_context), sorted(str(x) for x in seen))
        except Exception as e:
            logger.warning("Memory retrieval failed: %s", e)

    # Build the augmented mission prompt
    if memory_context:
        augmented = (
            f"CONTEXT FROM PRIOR MISSIONS (retrieved from sovereign memory):\n"
            f"---\n{memory_context}\n---\n\n"
            f"MISSION:\n{MISSION_TEXT}"
        )
    else:
        augmented = MISSION_TEXT

    # Execute the sovereign loop
    logger.info("Executing Sovereign Loop (Diverge → Collapse → Become)...")
    t0 = time.perf_counter()
    result = orch.process_mission(
        mission=augmented,
        mode="both",
        gear_context="STRATEGIC_TRUTH",
    )
    elapsed = time.perf_counter() - t0
    logger.info("Sovereign Loop completed in %.1fs", elapsed)

    # Determine status
    status_code = result.get("status", "unknown")
    if status_code == "ok" and result.get("task_output"):
        status = "COMPLETE"
    elif status_code == "ok":
        status = "PARTIAL"
    else:
        status = "BLOCKED"

    # Write markdown artifact
    write_markdown_artifact(result, iteration, status)

    # Write JSON provenance
    result["mission_metadata"] = {
        "mission_number": 6,
        "mission_name": "NARRATIVE / CATEGORY VECTOR",
        "iteration": iteration,
        "status": status,
        "elapsed_seconds": round(elapsed, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_audience": "Alex Komoroske",
        "target_date": "2026-03-05",
        "memory_injected": bool(memory_context),
    }

    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    logger.info("JSON provenance written to %s", JSON_OUTPUT.name)

    # Store to memory if available
    if memory_client is not None:
        try:
            output_text = result.get("task_output", "")
            if output_text:
                pt_id = memory_client.store(
                    namespace="episodic",
                    text=f"[Mission 6 — Category Narrative] {output_text[:2000]}",
                    metadata={
                        "mission_id": 6,
                        "mode": "both",
                        "gear": "STRATEGIC_TRUTH",
                        "agent": "sovereign_loop",
                        "mission_name": "NARRATIVE / CATEGORY VECTOR",
                    },
                )
                logger.info("Mission output stored to memory: %s", pt_id)
        except Exception as e:
            logger.warning("Memory storage failed: %s", e)

    # Summary
    logger.info("=" * 70)
    logger.info("MISSION 6 COMPLETE — NARRATIVE / CATEGORY VECTOR")
    logger.info("Status: %s", status)
    logger.info("Time: %.1fs (%.1f minutes)", elapsed, elapsed / 60)
    logger.info("Artifact: %s", MD_OUTPUT)
    logger.info("Provenance: %s", JSON_OUTPUT)
    logger.info("Audit entries: %d", audit.count())
    logger.info("=" * 70)

    orch.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Sovereign Loop Mission 6: Category Narrative")
    parser.add_argument("--dry-run", action="store_true", help="Validate pipeline without LLM calls")
    args = parser.parse_args()
    run_mission(dry_run=args.dry_run)
