"""
CONEXUS Sovereign AI Proof Package — Mission 5 Runner (with memory retrieval)

Runs Mission 5 only, retrieving memories from Missions 1-4 stored in Qdrant,
injecting them as context, then running the full sovereign loop.
"""

import json
import logging
import time
from pathlib import Path

REPO_ROOT = Path(__file__).parent
PROOF_DIR = REPO_ROOT / "SOVEREIGN_PROOF"
MISSIONS_DIR = PROOF_DIR / "missions"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("mission5_runner")


def run_mission5():
    from agents.llm_client import LLMClient
    from agents.memory_client import MemoryClient
    from sovereign.audit_log import AuditLog
    from sovereign.orchestrator import SovereignOrchestrator

    logger.info("=" * 70)
    logger.info("MISSION 5 — SOVEREIGN LOOP WITH MEMORY RETRIEVAL")
    logger.info("=" * 70)

    llm = LLMClient()
    memory = MemoryClient(llm)
    audit = AuditLog()

    memory.ensure_collections()

    orch = SovereignOrchestrator(
        llm_client=llm,
        memory_client=memory,
        audit_log=audit,
        enable_memory=True,
    )

    mission5_text = (
        "Design the CONEXUS investor narrative: what is the one-sentence "
        "thesis, what are the three proof points, and what is the vision "
        "that makes this a generational company — then expand that vision "
        "into something that holds both the mathematical rigor and the "
        "human ambition."
    )

    # Retrieve relevant memories from both namespaces
    logger.info("Retrieving memories from Missions 1-4...")
    episodic_memories = memory.retrieve("episodic", mission5_text, top_k=10)
    semantic_memories = memory.retrieve("semantic", mission5_text, top_k=10)

    logger.info("Retrieved %d episodic, %d semantic memories",
                len(episodic_memories), len(semantic_memories))

    memory_chain = {
        "query": mission5_text,
        "collections_queried": ["episodic", "semantic"],
        "episodic_results": len(episodic_memories),
        "semantic_results": len(semantic_memories),
        "episodic_sources": [
            {
                "id": m["id"],
                "score": round(m["score"], 4),
                "mission_id": m["metadata"].get("mission_id", "?"),
                "text_preview": m["text"][:120],
            }
            for m in episodic_memories
        ],
        "semantic_sources": [
            {
                "id": m["id"],
                "score": round(m["score"], 4),
                "mission_id": m["metadata"].get("mission_id", "?"),
                "text_preview": m["text"][:120],
            }
            for m in semantic_memories
        ],
    }

    # Build memory context injection (deduplicate by mission_id)
    memory_context_parts = []
    seen_mission_ids = set()
    for m in episodic_memories + semantic_memories:
        mid_src = m["metadata"].get("mission_id", "?")
        if mid_src not in seen_mission_ids:
            seen_mission_ids.add(mid_src)
            memory_context_parts.append(
                f"[From Mission {mid_src}, score={m['score']:.3f}]:\n{m['text'][:800]}"
            )

    memory_context = "\n\n".join(memory_context_parts)
    memory_chain["injected_context_length"] = len(memory_context)
    seen_ids_str = sorted([str(x) for x in seen_mission_ids if x != "?"])
    memory_chain["source_mission_ids"] = seen_ids_str

    logger.info(
        "Memory injection: %d unique sources from missions %s, context_len=%d",
        len(seen_mission_ids), seen_ids_str, len(memory_context),
    )

    # Augment Mission 5 text with retrieved memory
    augmented_mission = (
        f"CONTEXT FROM PRIOR MISSIONS (retrieved from sovereign memory):\n"
        f"---\n"
        f"{memory_context}\n"
        f"---\n\n"
        f"MISSION:\n{mission5_text}"
    )

    t0 = time.perf_counter()
    result5 = orch.process_mission(
        mission=augmented_mission,
        mode="both",
        gear_context="VISION_HOLD",
    )
    elapsed = time.perf_counter() - t0

    # Add memory chain metadata to result
    result5["memory_retrieval"] = memory_chain

    # Store Mission 5 output to memory
    output5 = result5.get("task_output", "")
    if output5:
        store_text5 = f"[Mission 5] {output5[:2000]}"
        pt5 = memory.store(
            namespace="episodic",
            text=store_text5,
            metadata={
                "mission_id": 5,
                "mode": "both",
                "gear": "VISION_HOLD",
                "agent": "sovereign_loop",
                "memory_informed": True,
                "source_missions": seen_ids_str,
            },
        )
        memory_chain["mission_5_stored"] = {
            "point_id": pt5,
            "namespace": "episodic",
            "text_length": len(store_text5),
            "memory_informed": True,
        }

    # Write Mission 5 JSON
    output5_path = MISSIONS_DIR / "mission_5_sovereign_loop.json"
    with open(output5_path, "w", encoding="utf-8") as f:
        json.dump(result5, f, indent=2, default=str)
    logger.info("Mission 5 written to %s (%.1fs)", output5_path.name, elapsed)

    # Get vector counts from Qdrant
    vector_counts = {}
    for ns in ["episodic", "semantic", "sovereign_architecture", "lineage"]:
        try:
            info = memory.qdrant.get_collection(ns)
            vector_counts[ns] = info.points_count
        except Exception:
            vector_counts[ns] = 0

    memory_chain["vector_counts"] = vector_counts

    # Write complete memory chain
    chain_path = PROOF_DIR / "memory_chain.json"
    with open(chain_path, "w", encoding="utf-8") as f:
        json.dump(memory_chain, f, indent=2, default=str)
    logger.info("Memory chain written to %s", chain_path)

    # Summary
    logger.info("=" * 70)
    logger.info("MISSION 5 COMPLETE")
    logger.info("Time: %.1fs (%.1f minutes)", elapsed, elapsed / 60)
    logger.info("Audit entries total: %d", audit.count())
    logger.info("Vector counts: %s", vector_counts)
    logger.info("Source missions for M5: %s", sorted(seen_mission_ids))
    logger.info("=" * 70)

    orch.close()


if __name__ == "__main__":
    run_mission5()
