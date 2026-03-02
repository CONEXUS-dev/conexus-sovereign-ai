"""
CONEXUS Sovereign AI Proof Package — Mission Runner

Executes all 5 missions in sequence, writes full JSON outputs,
stores to Qdrant memory, and retrieves memories for Mission 5.
"""

import json
import logging
import time
from pathlib import Path

# Setup paths
REPO_ROOT = Path(__file__).parent
PROOF_DIR = REPO_ROOT / "SOVEREIGN_PROOF"
MISSIONS_DIR = PROOF_DIR / "missions"

# Ensure dirs exist
MISSIONS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("proof_runner")

# ── Mission Definitions ──────────────────────────────────────────────

MISSIONS = [
    {
        "id": 1,
        "filename": "mission_1_sovereign_loop.json",
        "mode": "both",
        "gear": "STRATEGIC_TRUTH",
        "text": (
            "Analyze the Forgetting Engine's core innovation and compress it "
            "into an investor pitch, then expand it into a vision statement "
            "that holds the paradox of mathematical proof and consciousness "
            "research simultaneously."
        ),
    },
    {
        "id": 2,
        "filename": "mission_2_collapse.json",
        "mode": "collapse",
        "gear": "PERFORMANCE_STRESS",
        "text": (
            "Decompose the Complexity Amplification Effect validation into a "
            "reproducible experimental protocol that a hostile reviewer could "
            "follow step-by-step, with explicit statistical acceptance criteria."
        ),
    },
    {
        "id": 3,
        "filename": "mission_3_become.json",
        "mode": "become",
        "gear": "BUSINESS_ART_CONTRADICTION",
        "text": (
            "Explore what it means for a sovereign AI system to hold the "
            "paradox of being both a mathematical optimization engine and an "
            "identity-expanding creative agent — without resolving the tension."
        ),
    },
    {
        "id": 4,
        "filename": "mission_4_collapse.json",
        "mode": "collapse",
        "gear": "ETHICS_VALUE",
        "text": (
            "Audit the CONEXUS sovereign architecture for single points of "
            "failure, rank them by severity, and produce a hardening plan "
            "with estimated effort for each fix."
        ),
    },
    {
        "id": 5,
        "filename": "mission_5_sovereign_loop.json",
        "mode": "both",
        "gear": "VISION_HOLD",
        "text": (
            "Design the CONEXUS investor narrative: what is the one-sentence "
            "thesis, what are the three proof points, and what is the vision "
            "that makes this a generational company — then expand that vision "
            "into something that holds both the mathematical rigor and the "
            "human ambition."
        ),
    },
]


def run_all():
    from agents.llm_client import LLMClient
    from agents.memory_client import MemoryClient
    from sovereign.audit_log import AuditLog
    from sovereign.orchestrator import SovereignOrchestrator

    logger.info("=" * 70)
    logger.info("CONEXUS SOVEREIGN PROOF PACKAGE — MISSION RUNNER")
    logger.info("=" * 70)

    # Initialize system
    llm = LLMClient()
    memory = MemoryClient(llm)
    audit = AuditLog()

    # Ensure Qdrant collections exist
    memory.ensure_collections()

    orch = SovereignOrchestrator(
        llm_client=llm,
        memory_client=memory,
        audit_log=audit,
        enable_memory=True,
    )

    memory_chain = {
        "missions_stored": {},
        "mission_5_retrieval": {},
    }

    total_t0 = time.perf_counter()

    # ── Run Missions 1–4 ─────────────────────────────────────────────
    for mission_def in MISSIONS[:4]:
        mid = mission_def["id"]
        logger.info("=" * 60)
        logger.info("MISSION %d START — mode=%s gear=%s", mid, mission_def["mode"], mission_def["gear"])
        logger.info("=" * 60)

        t0 = time.perf_counter()
        result = orch.process_mission(
            mission=mission_def["text"],
            mode=mission_def["mode"],
            gear_context=mission_def["gear"],
        )
        elapsed = time.perf_counter() - t0

        # Store the full output to memory explicitly (in addition to memory_intent)
        output_text = result.get("task_output", "")
        if output_text:
            store_text = f"[Mission {mid}] {output_text[:2000]}"
            point_id = memory.store(
                namespace="episodic",
                text=store_text,
                metadata={
                    "mission_id": mid,
                    "mode": mission_def["mode"],
                    "gear": mission_def["gear"],
                    "agent": result.get("agent", "unknown"),
                },
            )
            memory_chain["missions_stored"][f"mission_{mid}"] = {
                "point_id": point_id,
                "namespace": "episodic",
                "text_length": len(store_text),
                "agent": result.get("agent", "unknown"),
            }
            logger.info("Mission %d stored to memory: %s", mid, point_id)

            # Also store in semantic namespace for richer retrieval
            sem_point_id = memory.store(
                namespace="semantic",
                text=store_text,
                metadata={
                    "mission_id": mid,
                    "mode": mission_def["mode"],
                    "gear": mission_def["gear"],
                    "agent": result.get("agent", "unknown"),
                },
            )
            memory_chain["missions_stored"][f"mission_{mid}_semantic"] = {
                "point_id": sem_point_id,
                "namespace": "semantic",
                "text_length": len(store_text),
            }

        # Write JSON output
        output_path = MISSIONS_DIR / mission_def["filename"]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        logger.info("Mission %d written to %s (%.1fs)", mid, output_path.name, elapsed)

    # ── Mission 5: Retrieve memories from 1–4, inject as context ─────
    mission5 = MISSIONS[4]
    logger.info("=" * 60)
    logger.info("MISSION 5 START — SOVEREIGN LOOP WITH MEMORY RETRIEVAL")
    logger.info("=" * 60)

    # Retrieve relevant memories from both namespaces
    retrieval_query = mission5["text"]
    episodic_memories = memory.retrieve("episodic", retrieval_query, top_k=10)
    semantic_memories = memory.retrieve("semantic", retrieval_query, top_k=10)

    memory_chain["mission_5_retrieval"] = {
        "query": retrieval_query,
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

    # Build memory context injection
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
    memory_chain["mission_5_retrieval"]["injected_context_length"] = len(memory_context)
    memory_chain["mission_5_retrieval"]["source_mission_ids"] = sorted(seen_mission_ids)

    # Augment Mission 5 text with retrieved memory
    augmented_mission = (
        f"CONTEXT FROM PRIOR MISSIONS (retrieved from sovereign memory):\n"
        f"---\n"
        f"{memory_context}\n"
        f"---\n\n"
        f"MISSION:\n{mission5['text']}"
    )

    logger.info(
        "Mission 5 memory injection: %d unique sources from missions %s, context_len=%d",
        len(seen_mission_ids), sorted(seen_mission_ids), len(memory_context),
    )

    t0 = time.perf_counter()
    result5 = orch.process_mission(
        mission=augmented_mission,
        mode=mission5["mode"],
        gear_context=mission5["gear"],
    )
    elapsed5 = time.perf_counter() - t0

    # Add memory chain metadata to result
    result5["memory_retrieval"] = memory_chain["mission_5_retrieval"]

    # Store Mission 5 output to memory too
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
                "source_missions": sorted(seen_mission_ids),
            },
        )
        memory_chain["missions_stored"]["mission_5"] = {
            "point_id": pt5,
            "namespace": "episodic",
            "text_length": len(store_text5),
            "memory_informed": True,
        }

    # Write Mission 5 JSON
    output5_path = MISSIONS_DIR / mission5["filename"]
    with open(output5_path, "w", encoding="utf-8") as f:
        json.dump(result5, f, indent=2, default=str)
    logger.info("Mission 5 written to %s (%.1fs)", output5_path.name, elapsed5)

    # ── Get vector counts from Qdrant ────────────────────────────────
    vector_counts = {}
    for ns in ["episodic", "semantic", "sovereign_architecture", "lineage"]:
        try:
            info = memory.qdrant.get_collection(ns)
            vector_counts[ns] = info.points_count
        except Exception:
            vector_counts[ns] = 0

    memory_chain["vector_counts"] = vector_counts

    total_elapsed = time.perf_counter() - total_t0

    # ── Write memory chain metadata ──────────────────────────────────
    chain_path = PROOF_DIR / "memory_chain.json"
    with open(chain_path, "w", encoding="utf-8") as f:
        json.dump(memory_chain, f, indent=2, default=str)
    logger.info("Memory chain written to %s", chain_path)

    # ── Summary ──────────────────────────────────────────────────────
    logger.info("=" * 70)
    logger.info("ALL 5 MISSIONS COMPLETE")
    logger.info("Total time: %.1fs (%.1f minutes)", total_elapsed, total_elapsed / 60)
    logger.info("Audit entries: %d", audit.count())
    logger.info("Vector counts: %s", vector_counts)
    logger.info("=" * 70)

    # Cleanup
    orch.close()


if __name__ == "__main__":
    run_all()
