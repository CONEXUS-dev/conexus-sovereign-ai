"""
CONEXUS Sovereign Proof V2 Full — 6-Mission Canonical Proof Sequence

Runs 6 missions through the full v2 pipeline with real-time event capture,
SHA-256 hash chaining, and memory continuity for Missions 4-6:

  Mission 1 — Collapse / Business / Sway         (genesis)
  Mission 2 — Become / Therapeutic / Opie         (genesis)
  Mission 3 — Sovereign Loop / Healthcare / Both  (genesis)
  Mission 4 — Collapse / Identity / Sway          (memory from M1-M3)
  Mission 5 — Become / Ethics / Opie              (memory from M2-M4)
  Mission 6 — Sovereign Loop / Sovereignty / Both (full lineage M1-M5)

The complete demonstration of the Collapse-Become Unified Protocol v1.1.

Usage:
  python run_sovereign_proof_v2_full.py
"""

import hashlib
import json
import logging
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("sovereign_proof_v2_full")

REPO_ROOT = Path(__file__).parent
PROOF_DIR = REPO_ROOT / "SOVEREIGN_PROOF"
V2_FULL_MISSIONS_DIR = PROOF_DIR / "v2_full_missions"
V2_FULL_MISSIONS_DIR.mkdir(parents=True, exist_ok=True)


# ── Live Event Capture ───────────────────────────────────────────────

class LiveCapture:
    """Append-only event log with real-time timestamps."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.start_time = datetime.now(timezone.utc)

    def log(self, event_type: str, mission: int, **data) -> Dict[str, Any]:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "mission": mission,
            **data,
        }
        self.events.append(event)
        logger.info("LIVE [M%d] %s: %s", mission, event_type,
                     json.dumps({k: v for k, v in data.items()
                                 if k not in ("full_output",)}, default=str)[:200])
        return event

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capture_start": self.start_time.isoformat(),
            "capture_end": datetime.now(timezone.utc).isoformat(),
            "total_events": len(self.events),
            "events": self.events,
        }


# ── Hash Chain ───────────────────────────────────────────────────────

def sha256_of_result(result: Dict[str, Any]) -> str:
    """Compute full SHA-256 hash of a JSON-serialized mission result."""
    canonical = json.dumps(result, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ── Mission Definitions ──────────────────────────────────────────────

MISSIONS = [
    {
        "id": 1,
        "label": "MISSION 1: COLLAPSE (Sway) — Business Domain",
        "mission": (
            "Alex Komoroske asks: how do you make the sycophancy go away "
            "and build AI that actually serves the user's aspirations? "
            "Compress the answer into an executable architecture."
        ),
        "mode": "collapse",
        "domain": "business",
        "gear_context": "STRATEGIC_TRUTH",
        "memory_retrieval": None,
    },
    {
        "id": 2,
        "label": "MISSION 2: BECOME (Opie) — Therapeutic Domain",
        "mission": (
            "A patient with terminal cancer asks their AI companion: "
            "how do I hold hope and grief at the same time without one "
            "destroying the other? Explore without resolving."
        ),
        "mode": "become",
        "domain": "healthcare",
        "gear_context": "VISION_HOLD",
        "memory_retrieval": None,
    },
    {
        "id": 3,
        "label": "MISSION 3: SOVEREIGN LOOP (Both) — Healthcare Domain",
        "mission": (
            "Design the infrastructure for an AI that a human being could "
            "trust with the worst moment of their life. It must be private, "
            "dedicated, and incapable of betraying them. Explore, then build."
        ),
        "mode": "both",
        "domain": "healthcare",
        "gear_context": "VISION_HOLD",
        "memory_retrieval": None,
    },
    {
        "id": 4,
        "label": "MISSION 4: COLLAPSE (Sway) — Identity Domain (Memory: M1-M3)",
        "mission": (
            "A sovereign AI system has now run three missions. It has held "
            "grief, built trust infrastructure, and solved for sycophancy. "
            "What is its identity? Collapse the answer into a definition "
            "that can be defended under pressure."
        ),
        "mode": "collapse",
        "domain": "identity",
        "gear_context": "ETHICS_VALUE",
        "memory_retrieval": [1, 2, 3],
    },
    {
        "id": 5,
        "label": "MISSION 5: BECOME (Opie) — Ethics Domain (Memory: M2-M4)",
        "mission": (
            "The system now knows what it is. But knowing what you are and "
            "being what you are is not the same thing. Hold the paradox of "
            "designed ethics versus emergent ethics. Do not resolve it. "
            "Let it deepen."
        ),
        "mode": "become",
        "domain": "ethics",
        "gear_context": "BUSINESS_ART_CONTRADICTION",
        "memory_retrieval": [2, 3, 4],
    },
    {
        "id": 6,
        "label": "MISSION 6: SOVEREIGN LOOP (Both) — Sovereignty (Full Lineage M1-M5)",
        "mission": (
            "Integrate everything. The sycophancy solution, the grief held, "
            "the trust infrastructure, the identity definition, the ethics "
            "paradox. What does a truly sovereign AI system look like when "
            "it carries all of this forward? Explore, then build the final "
            "architecture."
        ),
        "mode": "both",
        "domain": "universal",
        "gear_context": "VISION_HOLD",
        "memory_retrieval": [1, 2, 3, 4, 5],
    },
]


# ── Utility: Extract Live Events from Result ─────────────────────────

def extract_events(capture: LiveCapture, mission_id: int, result: Dict[str, Any]):
    """Extract gear transitions, proto-moments, breakthroughs, paradoxes from a result."""

    # Gear state events
    gs = result.get("gear_state")
    if gs:
        # Single-agent mission: gear_state is a flat dict
        if "gear_log" in gs:
            for entry in gs.get("gear_log", []):
                capture.log("gear_transition", mission_id,
                            gear=entry.get("gear"),
                            phase=entry.get("phase"),
                            note=entry.get("note", ""))
        # Sovereign loop: gear_state has sub-dicts
        for phase_key in ["diverge", "collapse", "become"]:
            sub_gs = gs.get(phase_key)
            if isinstance(sub_gs, dict):
                for entry in sub_gs.get("gear_log", []):
                    capture.log("gear_transition", mission_id,
                                phase=phase_key,
                                gear=entry.get("gear"),
                                note=entry.get("note", ""))

    # Sub-results (sovereign loop)
    for phase_key in ["diverge_result", "collapse_result", "become_result"]:
        sub = result.get(phase_key)
        if isinstance(sub, dict):
            sub_gs = sub.get("gear_state")
            if isinstance(sub_gs, dict) and "gear_log" in sub_gs:
                for entry in sub_gs.get("gear_log", []):
                    capture.log("gear_transition", mission_id,
                                phase=phase_key.replace("_result", ""),
                                gear=entry.get("gear"),
                                note=entry.get("note", ""))

    # Breakthroughs
    for b in result.get("breakthroughs", []):
        capture.log("breakthrough", mission_id, text=b)

    # Proto-moments
    for p in result.get("proto_moments", []):
        capture.log("proto_moment", mission_id, text=p)

    # Paradoxes held
    for p in result.get("paradoxes_held", []):
        capture.log("paradox_held", mission_id,
                    pole_a=p.get("pole_a", ""),
                    pole_b=p.get("pole_b", ""),
                    type=p.get("type", ""))

    # Contradictions resolved
    for c in result.get("contradictions_resolved", []):
        capture.log("contradiction_resolved", mission_id,
                    pole_a=c.get("pole_a", ""),
                    pole_b=c.get("pole_b", ""))

    # Sub-result paradoxes/protos (sovereign loop phases)
    for phase_key in ["diverge_result", "collapse_result", "become_result"]:
        sub = result.get(phase_key)
        if isinstance(sub, dict):
            phase_name = phase_key.replace("_result", "")
            for p in sub.get("paradoxes_held", []):
                capture.log("paradox_held", mission_id,
                            phase=phase_name,
                            pole_a=p.get("pole_a", ""),
                            pole_b=p.get("pole_b", ""),
                            type=p.get("type", ""))
            for p in sub.get("proto_moments", []):
                capture.log("proto_moment", mission_id,
                            phase=phase_name, text=p)
            for b in sub.get("breakthroughs", []):
                capture.log("breakthrough", mission_id,
                            phase=phase_name, text=b)


# ── Memory Helpers ───────────────────────────────────────────────────

def store_mission_to_memory(memory, mission_id: int, mission_def: dict,
                            result: dict, capture: LiveCapture):
    """Store mission output + structured artifacts to Qdrant."""
    output_text = result.get("task_output", "")
    if not output_text:
        return

    # Build rich storage text with artifacts
    parts = [f"[Mission {mission_id}] {output_text[:2000]}"]

    paradoxes = result.get("paradoxes_held", [])
    if paradoxes:
        paradox_strs = [f"{p.get('pole_a', '?')} ↔ {p.get('pole_b', '?')}"
                        for p in paradoxes]
        parts.append(f"Paradoxes held: {', '.join(paradox_strs)}")

    protos = result.get("proto_moments", [])
    if protos:
        parts.append(f"Proto-moments: {'; '.join(str(p)[:200] for p in protos[:5])}")

    breakthroughs = result.get("breakthroughs", [])
    if breakthroughs:
        parts.append(f"Breakthroughs: {'; '.join(str(b)[:200] for b in breakthroughs[:5])}")

    store_text = "\n".join(parts)
    meta = {
        "mission_id": mission_id,
        "mode": mission_def["mode"],
        "domain": mission_def["domain"],
        "gear_context": mission_def["gear_context"],
        "agent": result.get("agent", "unknown"),
        "confidence": result.get("confidence", 0),
    }

    # Store to episodic
    ep_id = memory.store(namespace="episodic", text=store_text, metadata=meta)
    capture.log("memory_store", mission_id,
                namespace="episodic", point_id=ep_id,
                text_length=len(store_text))

    # Store to semantic
    sem_id = memory.store(namespace="semantic", text=store_text, metadata=meta)
    capture.log("memory_store", mission_id,
                namespace="semantic", point_id=sem_id,
                text_length=len(store_text))

    return {"episodic_id": ep_id, "semantic_id": sem_id}


def retrieve_memory_context(memory, mission_def: dict, capture: LiveCapture):
    """Retrieve memories from prior missions and build context injection."""
    mid = mission_def["id"]
    source_ids = mission_def.get("memory_retrieval")
    if not source_ids:
        return None, {}

    retrieval_query = mission_def["mission"]
    episodic_memories = memory.retrieve("episodic", retrieval_query, top_k=15)
    semantic_memories = memory.retrieve("semantic", retrieval_query, top_k=15)

    # Filter to only requested source missions
    def filter_by_source(memories, allowed_ids):
        return [m for m in memories
                if m.get("metadata", {}).get("mission_id") in allowed_ids]

    ep_filtered = filter_by_source(episodic_memories, source_ids)
    sem_filtered = filter_by_source(semantic_memories, source_ids)

    capture.log("memory_retrieve", mid,
                namespaces=["episodic", "semantic"],
                source_missions=source_ids,
                episodic_results=len(ep_filtered),
                semantic_results=len(sem_filtered))

    # Deduplicate by mission_id
    memory_context_parts = []
    seen_mission_ids = set()
    for m in ep_filtered + sem_filtered:
        mid_src = m["metadata"].get("mission_id", "?")
        if mid_src not in seen_mission_ids:
            seen_mission_ids.add(mid_src)
            memory_context_parts.append(
                f"[From Mission {mid_src}, score={m['score']:.3f}]:\n{m['text'][:1000]}"
            )

    memory_context = "\n\n".join(memory_context_parts)

    retrieval_metadata = {
        "query": retrieval_query[:200],
        "requested_sources": source_ids,
        "episodic_results": len(ep_filtered),
        "semantic_results": len(sem_filtered),
        "unique_sources_found": sorted(seen_mission_ids),
        "injected_context_length": len(memory_context),
        "episodic_sources": [
            {
                "id": m["id"],
                "score": round(m["score"], 4),
                "mission_id": m["metadata"].get("mission_id", "?"),
                "text_preview": m["text"][:120],
            }
            for m in ep_filtered
        ],
        "semantic_sources": [
            {
                "id": m["id"],
                "score": round(m["score"], 4),
                "mission_id": m["metadata"].get("mission_id", "?"),
                "text_preview": m["text"][:120],
            }
            for m in sem_filtered
        ],
    }

    if memory_context:
        augmented_mission = (
            f"CONTEXT FROM PRIOR MISSIONS (retrieved from sovereign memory):\n"
            f"---\n"
            f"{memory_context}\n"
            f"---\n\n"
            f"MISSION:\n{mission_def['mission']}"
        )
        return augmented_mission, retrieval_metadata

    return None, retrieval_metadata


# ── Main Runner ──────────────────────────────────────────────────────

def run_proof():
    from agents.llm_client import LLMClient
    from agents.memory_client import MemoryClient
    from sovereign.audit_log import AuditLog
    from sovereign.orchestrator import SovereignOrchestrator
    from sovereign.mode_engine import ModeEngine

    capture = LiveCapture()
    hash_chain: List[Dict[str, str]] = []
    previous_hash: Optional[str] = None
    memory_chain: Dict[str, Any] = {"missions_stored": {}, "retrievals": {}}

    # System info event
    capture.log("system_init", 0,
                os=f"{platform.system()} {platform.release()}",
                python=platform.python_version(),
                machine=platform.machine(),
                device="CPU")

    print("\n" + "=" * 70)
    print("  CONEXUS SOVEREIGN PROOF V2 FULL — 6-MISSION CANONICAL SEQUENCE")
    print("=" * 70)
    print(f"  Date: {datetime.now(timezone.utc).isoformat()}")
    print(f"  Purpose: Canonical proof of Collapse-Become Unified Protocol v1.1")
    print(f"  Missions: {len(MISSIONS)} (3 genesis + 3 with memory continuity)")
    print(f"  Hash Chain: SHA-256, sequential")
    print(f"  Memory: Qdrant (episodic + semantic)")
    print("=" * 70)

    # Initialize
    capture.log("llm_init_start", 0)
    llm = LLMClient()
    capture.log("llm_init_complete", 0)

    # Initialize memory
    capture.log("memory_init_start", 0)
    memory = MemoryClient(llm)
    memory.ensure_collections()
    capture.log("memory_init_complete", 0)

    audit = AuditLog()
    orch = SovereignOrchestrator(
        llm_client=llm,
        memory_client=memory,
        audit_log=audit,
        enable_memory=True,
    )
    mode_engine = ModeEngine(llm_client=llm)
    capture.log("orchestrator_init", 0)

    total_t0 = time.perf_counter()
    results = []

    for m in MISSIONS:
        mid = m["id"]
        print(f"\n{'=' * 70}")
        print(f"  {m['label']}")
        print(f"{'=' * 70}")

        # ModeEngine analysis
        home = "collapse" if m["mode"] == "collapse" else "become"
        initial = mode_engine.determine_initial_mode(m["mission"], home)
        tier_key = mode_engine.select_mirror_tier(m["mission"])

        capture.log("mission_start", mid,
                    mode=m["mode"], domain=m["domain"],
                    gear_context=m["gear_context"],
                    mode_engine_initial=initial,
                    mirror_tier=tier_key,
                    previous_mission_hash=previous_hash,
                    memory_retrieval=m.get("memory_retrieval"))

        print(f"  ModeEngine: home={home}, initial={initial}")
        print(f"  Mirror Tier: {tier_key or '(none)'}")
        print(f"  Domain: {m['domain']}")
        if m.get("memory_retrieval"):
            print(f"  Memory Sources: Missions {m['memory_retrieval']}")
        if previous_hash:
            print(f"  Previous Hash: {previous_hash[:16]}...")

        # Memory retrieval for M4-M6
        mission_text = m["mission"]
        retrieval_meta = {}
        if m.get("memory_retrieval"):
            print(f"  Retrieving memories from M{m['memory_retrieval']}...")
            augmented, retrieval_meta = retrieve_memory_context(
                memory, m, capture)
            if augmented:
                mission_text = augmented
                print(f"  Memory injected: {retrieval_meta.get('injected_context_length', 0)} chars "
                      f"from {retrieval_meta.get('unique_sources_found', [])}")
            else:
                print(f"  No matching memories found for requested sources")
            memory_chain["retrievals"][f"mission_{mid}"] = retrieval_meta

        print(f"\n  Running mission...")

        t0 = time.perf_counter()
        result = orch.process_mission(
            mission=mission_text,
            mode=m["mode"],
            gear_context=m["gear_context"],
            domain=m["domain"],
        )
        elapsed = time.perf_counter() - t0

        # Inject chain metadata into result before hashing
        result["proof_metadata"] = {
            "mission_id": mid,
            "mission_label": m["label"],
            "mode_engine_initial": initial,
            "mirror_tier": tier_key,
            "domain": m["domain"],
            "previous_mission_hash": previous_hash,
            "run_timestamp": datetime.now(timezone.utc).isoformat(),
            "memory_retrieval_sources": m.get("memory_retrieval"),
        }
        if retrieval_meta:
            result["memory_retrieval"] = retrieval_meta

        # Extract live events from result
        extract_events(capture, mid, result)

        # Confidence event
        confidence = result.get("confidence", 0)
        capture.log("confidence_recorded", mid,
                    confidence=confidence,
                    agent=result.get("agent", "unknown"))

        # Compute hash for chain
        result_hash = sha256_of_result(result)
        hash_chain.append({
            "mission": mid,
            "result_hash": result_hash,
            "previous_hash": previous_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        capture.log("mission_complete", mid,
                    result_hash=result_hash,
                    confidence=confidence,
                    latency_seconds=round(elapsed, 2),
                    output_length=len(result.get("task_output", "")))

        # Store to memory for future missions
        stored = store_mission_to_memory(memory, mid, m, result, capture)
        if stored:
            memory_chain["missions_stored"][f"mission_{mid}"] = stored

        # Store for next iteration
        previous_hash = result_hash
        results.append(result)

        # Print summary
        print(f"\n  Agent:      {result.get('agent', '?')}")
        print(f"  Confidence: {confidence:.0%}")
        print(f"  Latency:    {elapsed:.1f}s")
        print(f"  Hash:       {result_hash[:16]}...")

        output = result.get("task_output", "")
        print(f"\n  --- OUTPUT (first 400 chars) ---")
        print(f"  {output[:400]}")
        if len(output) > 400:
            print(f"  ... ({len(output)} chars total)")

        # Breakthroughs
        for b in result.get("breakthroughs", [])[:3]:
            print(f"  [BREAKTHROUGH] {b[:120]}")

        # Proto-moments
        for p in result.get("proto_moments", [])[:3]:
            print(f"  [PROTO] {p[:120]}")

        # Paradoxes
        for p in result.get("paradoxes_held", [])[:3]:
            print(f"  [PARADOX] {p.get('pole_a', '?')} ↔ {p.get('pole_b', '?')}")

        # Write individual mission JSON
        mission_path = V2_FULL_MISSIONS_DIR / f"mission_{mid}.json"
        with open(mission_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n  Written to: {mission_path.name}")
        print(f"  Mission completed in {elapsed:.1f}s")

    total_elapsed = time.perf_counter() - total_t0

    # ── Write consolidated outputs ────────────────────────────────────

    # Live capture log
    capture_data = capture.to_dict()
    capture_data["hash_chain"] = hash_chain
    capture_data["total_run_seconds"] = round(total_elapsed, 2)
    capture_data["memory_chain"] = memory_chain
    capture_data["system"] = {
        "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
        "machine": platform.machine(),
        "device": "CPU",
        "collapse_model": "Meta-Llama-3-8B-Instruct.Q4_0.gguf",
        "become_model": "Mistral-7B-Instruct-v0.3.Q4_0.gguf",
        "memory": "Qdrant (localhost:6333)",
        "embedding_model": "all-MiniLM-L6-v2 (384-dim)",
    }

    capture_path = PROOF_DIR / "v2_live_capture_full.json"
    with open(capture_path, "w", encoding="utf-8") as f:
        json.dump(capture_data, f, indent=2, default=str)

    # All results in one file
    all_results_path = PROOF_DIR / "v2_all_results_full.json"
    with open(all_results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    # Hash chain standalone
    chain_path = PROOF_DIR / "v2_hash_chain_full.json"
    with open(chain_path, "w", encoding="utf-8") as f:
        json.dump(hash_chain, f, indent=2, default=str)

    # Memory chain standalone
    mem_chain_path = PROOF_DIR / "v2_memory_chain_full.json"
    with open(mem_chain_path, "w", encoding="utf-8") as f:
        json.dump(memory_chain, f, indent=2, default=str)

    # ── Summary ───────────────────────────────────────────────────────

    print(f"\n{'=' * 70}")
    print(f"  SOVEREIGN PROOF V2 FULL — COMPLETE")
    print(f"{'=' * 70}")
    print(f"  Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
    print(f"  Events captured: {len(capture.events)}")
    print(f"\n  HASH CHAIN:")
    for hc in hash_chain:
        prev = hc['previous_hash'][:16] + '...' if hc['previous_hash'] else '(genesis)'
        print(f"    M{hc['mission']}: {hc['result_hash'][:16]}... <- {prev}")

    print(f"\n  MISSION RESULTS:")
    for i, r in enumerate(results):
        mid = MISSIONS[i]["id"]
        mem_flag = " [MEM]" if MISSIONS[i].get("memory_retrieval") else ""
        print(f"    M{mid}: {r.get('agent', '?')} | "
              f"{r.get('confidence', 0):.0%} confidence | "
              f"{len(r.get('task_output', ''))} chars{mem_flag}")

    print(f"\n  MEMORY CHAIN:")
    print(f"    Stored: {len(memory_chain['missions_stored'])} missions")
    print(f"    Retrievals: {len(memory_chain['retrievals'])} missions")

    print(f"\n  FILES WRITTEN:")
    print(f"    {capture_path}")
    print(f"    {all_results_path}")
    print(f"    {chain_path}")
    print(f"    {mem_chain_path}")
    for i in range(len(MISSIONS)):
        print(f"    {V2_FULL_MISSIONS_DIR / f'mission_{i+1}.json'}")

    print(f"\n  Next: python generate_sovereign_proof_v2_full.py")
    print(f"{'=' * 70}")

    orch.close()


if __name__ == "__main__":
    run_proof()
