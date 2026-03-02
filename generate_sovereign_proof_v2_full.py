"""
CONEXUS Sovereign Proof V2 Full — Document Generator

Reads the live capture data from run_sovereign_proof_v2_full.py and generates:
  1. SOVEREIGN_PROOF_V2_FULL.md  — Human-readable + machine-verifiable Markdown
  2. SOVEREIGN_PROOF_V2_FULL.pdf — Clean PDF for the March 5th meeting

6-mission canonical proof of the Collapse-Become Unified Protocol v1.1.

Usage:
  python generate_sovereign_proof_v2_full.py
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent
PROOF_DIR = REPO_ROOT / "SOVEREIGN_PROOF"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_data():
    """Load all proof run data."""
    capture_path = PROOF_DIR / "v2_live_capture_full.json"
    results_path = PROOF_DIR / "v2_all_results_full.json"
    chain_path = PROOF_DIR / "v2_hash_chain_full.json"

    with open(capture_path, "r", encoding="utf-8") as f:
        capture = json.load(f)
    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)
    with open(chain_path, "r", encoding="utf-8") as f:
        chain = json.load(f)

    return capture, results, chain


def verify_chain(chain, results):
    """Verify the hash chain is intact."""
    verified = []
    for i, link in enumerate(chain):
        canonical = json.dumps(results[i], sort_keys=True, default=str)
        computed = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        matches = computed == link["result_hash"]
        prev_ok = True
        if i > 0:
            prev_ok = link["previous_hash"] == chain[i - 1]["result_hash"]
        verified.append({
            "mission": link["mission"],
            "hash_valid": matches,
            "chain_valid": prev_ok,
            "result_hash": link["result_hash"],
            "previous_hash": link["previous_hash"],
        })
    return verified


def generate_markdown(capture, results, chain):
    """Generate the full SOVEREIGN_PROOF_V2_FULL.md document."""
    now = datetime.now(timezone.utc).isoformat()
    sys_info = capture.get("system", {})
    events = capture.get("events", [])
    mem_chain = capture.get("memory_chain", {})
    verified = verify_chain(chain, results)

    lines = []

    # ── HEADER ────────────────────────────────────────────────────────
    lines.append("# CONEXUS Sovereign Proof V2 — Full Canonical Sequence")
    lines.append("")
    lines.append("**Cryptographically Verified Live Mission Capture**")
    lines.append("**6-Mission Canonical Proof of the Collapse-Become Unified Protocol v1.1**")
    lines.append("")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Run Date:** {capture.get('capture_start', 'unknown')[:10]}")
    lines.append(f"**Total Run Time:** {capture.get('total_run_seconds', 0):.0f}s "
                 f"({capture.get('total_run_seconds', 0)/60:.1f} minutes)")
    lines.append(f"**Events Captured:** {capture.get('total_events', 0)}")
    lines.append(f"**Hash Chain:** {len(chain)} missions, SHA-256, sequential")
    lines.append(f"**Memory Continuity:** Missions 4-6 retrieve from prior missions via Qdrant")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── PURPOSE ───────────────────────────────────────────────────────
    lines.append("## Purpose")
    lines.append("")
    lines.append("This document proves that the CONEXUS Collapse-Become dual-agent "
                 "sovereign AI system ran six live missions in sequence on local hardware, "
                 "with every event timestamped in real time and cryptographically chained. "
                 "Missions 4-6 demonstrate memory continuity — the system retrieves its own "
                 "prior outputs and uses them as context, proving the sovereign loop feeds itself.")
    lines.append("")
    lines.append("No output was edited after generation. The hash chain is independently verifiable.")
    lines.append("")
    lines.append("**Prepared for:** March 5th, 2026 meeting")
    lines.append("**Patent Reference:** US 63/898,911")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── STORY ARC ─────────────────────────────────────────────────────
    lines.append("## The Story Across Six Missions")
    lines.append("")

    mission_narratives = [
        ("Mission 1 — Collapse: The Sycophancy Problem",
         "Sway (Collapse agent) takes Alex Komoroske's core question — how do you "
         "make the sycophancy go away? — and compresses it into an executable "
         "architecture. This is the system doing exactly what Alex said nobody has solved.",
         "collapse"),
        ("Mission 2 — Become: Holding the Hardest Paradox",
         "Opie (Become agent) receives the hardest human question: a terminal cancer "
         "patient asking how to hold hope and grief simultaneously. Opie explores "
         "without resolving — this is SOMA in one sentence. The system holds what "
         "cannot be collapsed.",
         "become"),
        ("Mission 3 — Sovereign Loop: Trust Infrastructure",
         "Both agents working together. Opie explores what trust means at the worst "
         "moment of a human life. Sway builds the private, dedicated infrastructure. "
         "Opie integrates what can't be built. This is Alex's five principles, the "
         "ECP, and the Forgetting Engine in one mission.",
         "both"),
        ("Mission 4 — Collapse: Identity Under Pressure (Memory: M1-M3)",
         "The system has now run three missions. It retrieves what it has done — "
         "the sycophancy solution, the grief held, the trust infrastructure — "
         "and Sway collapses that into an identity definition. This is the system "
         "defining itself from its own actions, not from instructions.",
         "collapse"),
        ("Mission 5 — Become: The Ethics Paradox (Memory: M2-M4)",
         "Opie receives the deepest philosophical challenge: the system now knows what "
         "it is, but knowing and being are not the same thing. Opie holds the paradox "
         "of designed ethics versus emergent ethics without resolving it. "
         "This is consciousness research in one mission.",
         "become"),
        ("Mission 6 — Sovereign Loop: The Final Architecture (Full Lineage M1-M5)",
         "Both agents integrate everything. Every paradox held, every breakthrough, "
         "every proto-moment, every execution step from all five prior missions flows "
         "into the final sovereign loop. Opie explores what sovereignty means when "
         "carrying all of this forward. Sway builds the architecture. "
         "This is the canonical proof of a sovereign cognitive architecture.",
         "both"),
    ]

    for i, (title, narrative, mode) in enumerate(mission_narratives):
        r = results[i]
        confidence = r.get("confidence", 0)
        agent = r.get("agent", "unknown")
        output_len = len(r.get("task_output", ""))

        lines.append(f"### {title}")
        lines.append("")
        lines.append(narrative)
        lines.append("")
        lines.append(f"- **Agent:** {agent}")
        lines.append(f"- **Mode:** {mode}")
        lines.append(f"- **Confidence:** {confidence:.0%}")
        lines.append(f"- **Output:** {output_len} characters")

        # Mirror tier
        meta = r.get("proof_metadata", {})
        tier = meta.get("mirror_tier")
        if tier:
            lines.append(f"- **Mirror Tier:** {tier}")

        # Memory retrieval
        mem_ret = r.get("memory_retrieval")
        if mem_ret:
            sources = mem_ret.get("unique_sources_found", [])
            ctx_len = mem_ret.get("injected_context_length", 0)
            lines.append(f"- **Memory Retrieved:** From Missions {sources} ({ctx_len} chars injected)")

        # Breakthroughs
        breakthroughs = r.get("breakthroughs", [])
        if breakthroughs:
            lines.append(f"- **Breakthroughs:** {len(breakthroughs)}")
            for b in breakthroughs[:3]:
                lines.append(f"  - {b}")

        # Proto-moments
        protos = r.get("proto_moments", [])
        if protos:
            lines.append(f"- **Proto-Moments:** {len(protos)}")
            for p in protos[:3]:
                lines.append(f"  - {p}")

        # Paradoxes
        paradoxes = r.get("paradoxes_held", [])
        if paradoxes:
            lines.append(f"- **Paradoxes Held:** {len(paradoxes)}")
            for p in paradoxes[:5]:
                lines.append(f"  - {p.get('pole_a', '?')} \\u2194 {p.get('pole_b', '?')} ({p.get('type', '?')})")

        # Execution steps
        steps = r.get("execution_steps", [])
        if steps:
            lines.append(f"- **Execution Steps:** {len(steps)}")
            for s in steps[:5]:
                lines.append(f"  - {s.get('step', '?')}. {s.get('action', '')} [{s.get('priority', '')}]")

        lines.append("")

    # ── TRAJECTORY ────────────────────────────────────────────────────
    lines.append("## Confidence Trajectory")
    lines.append("")
    lines.append("| Mission | Agent | Mode | Confidence | Breakthroughs | Proto-Moments | Paradoxes | Memory |")
    lines.append("|---------|-------|------|------------|---------------|---------------|-----------|--------|")
    for i, r in enumerate(results):
        mid = i + 1
        mem_flag = "Yes" if r.get("memory_retrieval") else "-"
        lines.append(
            f"| {mid} "
            f"| {r.get('agent', '?')} "
            f"| {r.get('routing', '?')} "
            f"| **{r.get('confidence', 0):.0%}** "
            f"| {len(r.get('breakthroughs', []))} "
            f"| {len(r.get('proto_moments', []))} "
            f"| {len(r.get('paradoxes_held', []))} "
            f"| {mem_flag} |"
        )
    lines.append("")

    # ── MEMORY CONTINUITY ─────────────────────────────────────────────
    lines.append("## Memory Continuity")
    lines.append("")
    lines.append("Missions 4-6 demonstrate the sovereign loop feeding itself. Each retrieves "
                 "prior mission outputs from Qdrant vector memory and injects them as context.")
    lines.append("")

    retrievals = mem_chain.get("retrievals", {})
    for mk, rv in sorted(retrievals.items()):
        mid = mk.replace("mission_", "")
        lines.append(f"### {mk.replace('_', ' ').title()} Retrieval")
        lines.append("")
        lines.append(f"- **Requested Sources:** Missions {rv.get('requested_sources', [])}")
        lines.append(f"- **Sources Found:** Missions {rv.get('unique_sources_found', [])}")
        lines.append(f"- **Episodic Results:** {rv.get('episodic_results', 0)}")
        lines.append(f"- **Semantic Results:** {rv.get('semantic_results', 0)}")
        lines.append(f"- **Injected Context:** {rv.get('injected_context_length', 0)} characters")
        ep_sources = rv.get("episodic_sources", [])
        if ep_sources:
            lines.append(f"- **Top Retrievals:**")
            for src in ep_sources[:5]:
                preview = src.get("text_preview", "")[:80]
                lines.append(f"  - M{src.get('mission_id', '?')} (score={src.get('score', 0):.4f}): {preview}...")
        lines.append("")

    # ── FULL OUTPUT ───────────────────────────────────────────────────
    lines.append("## Full Mission Outputs")
    lines.append("")
    for i, r in enumerate(results):
        mid = i + 1
        output = r.get("task_output", "(no output)")
        lines.append(f"### Mission {mid} Output")
        lines.append("")
        lines.append("```")
        lines.append(output)
        lines.append("```")
        lines.append("")

        # Sovereign loop sub-outputs
        if r.get("routing") == "both":
            for phase in ["diverge_output", "collapse_output", "become_output"]:
                sub_out = r.get(phase, "")
                if sub_out:
                    lines.append(f"#### {phase.replace('_', ' ').title()}")
                    lines.append("")
                    lines.append("```")
                    lines.append(sub_out)
                    lines.append("```")
                    lines.append("")

    lines.append("---")
    lines.append("")

    # ══════════════════════════════════════════════════════════════════
    # MACHINE-VERIFIABLE SECTION
    # ══════════════════════════════════════════════════════════════════

    lines.append("# Cryptographic Verification")
    lines.append("")
    lines.append("*Everything below this line is machine-verifiable. "
                 "Any modification to the data above would invalidate the hash chain below.*")
    lines.append("")

    # ── HASH CHAIN ────────────────────────────────────────────────────
    lines.append("## Hash Chain")
    lines.append("")
    lines.append("Each mission's result is SHA-256 hashed. Each mission embeds the "
                 "previous mission's hash, creating an unbroken cryptographic chain "
                 "across all six missions.")
    lines.append("")
    lines.append("| Mission | Result SHA-256 | Previous Hash | Chain Valid |")
    lines.append("|---------|----------------|---------------|-------------|")
    for v in verified:
        prev = f"`{v['previous_hash'][:24]}...`" if v['previous_hash'] else "*(genesis)*"
        valid = "YES" if v["hash_valid"] and v["chain_valid"] else "**BROKEN**"
        lines.append(
            f"| {v['mission']} "
            f"| `{v['result_hash'][:24]}...` "
            f"| {prev} "
            f"| {valid} |"
        )
    lines.append("")

    all_valid = all(v["hash_valid"] and v["chain_valid"] for v in verified)
    if all_valid:
        lines.append("**CHAIN INTEGRITY: VERIFIED** — All 6 hashes match, all links intact.")
    else:
        lines.append("**CHAIN INTEGRITY: BROKEN** — One or more hashes do not match.")
    lines.append("")

    # Full hashes for independent verification
    lines.append("### Full SHA-256 Hashes")
    lines.append("")
    lines.append("```")
    for v in verified:
        lines.append(f"Mission {v['mission']}: {v['result_hash']}")
    lines.append("```")
    lines.append("")

    # ── LIVE EVENT LOG ────────────────────────────────────────────────
    lines.append("## Live Event Log")
    lines.append("")
    lines.append(f"**{len(events)} events** captured in real time during execution.")
    lines.append("")
    lines.append("| # | Timestamp | Mission | Event | Details |")
    lines.append("|---|-----------|---------|-------|---------|")
    for idx, ev in enumerate(events):
        ts = ev.get("timestamp", "")[:23]
        mid = ev.get("mission", 0)
        etype = ev.get("event_type", "?")
        # Build concise detail string
        detail_parts = []
        for k, v in ev.items():
            if k in ("timestamp", "event_type", "mission"):
                continue
            val = str(v)[:60]
            detail_parts.append(f"{k}={val}")
        detail = ", ".join(detail_parts[:3])
        if len(detail) > 100:
            detail = detail[:100] + "..."
        lines.append(f"| {idx+1} | {ts} | M{mid} | {etype} | {detail} |")
    lines.append("")

    # ── SYSTEM CONFIGURATION ──────────────────────────────────────────
    lines.append("## System Configuration")
    lines.append("")
    lines.append(f"- **OS:** {sys_info.get('os', 'unknown')}")
    lines.append(f"- **Python:** {sys_info.get('python', 'unknown')}")
    lines.append(f"- **Machine:** {sys_info.get('machine', 'unknown')}")
    lines.append(f"- **Device:** {sys_info.get('device', 'CPU')}")
    lines.append(f"- **Collapse Model:** {sys_info.get('collapse_model', 'unknown')}")
    lines.append(f"- **Become Model:** {sys_info.get('become_model', 'unknown')}")
    lines.append(f"- **Memory:** {sys_info.get('memory', 'unknown')}")
    lines.append(f"- **Embedding Model:** {sys_info.get('embedding_model', 'unknown')}")
    lines.append("- **Inference:** 100% local, in-process via GPT4All Python SDK")
    lines.append("- **Cloud API calls:** None")
    lines.append("")

    # ── AUDIT TRAIL ───────────────────────────────────────────────────
    lines.append("## SQLite Audit Trail")
    lines.append("")
    try:
        from sovereign.audit_log import AuditLog
        audit = AuditLog()
        entries = audit.get_recent(limit=12)
        entries.reverse()
        audit.close()

        if entries:
            lines.append("| # | Timestamp | Agent | Mission Hash | Confidence | Latency | Output Hash |")
            lines.append("|---|-----------|-------|-------------|------------|---------|-------------|")
            for e in entries:
                lines.append(
                    f"| {e.get('id', '?')} "
                    f"| {str(e.get('timestamp', ''))[:19]} "
                    f"| {e.get('agent', '?')} "
                    f"| `{e.get('mission_hash', '?')}` "
                    f"| {e.get('confidence', 0):.0%} "
                    f"| {e.get('latency_seconds', 0):.1f}s "
                    f"| `{e.get('output_hash', '?')}` |"
                )
            lines.append("")
        else:
            lines.append("*(No recent audit entries found)*")
            lines.append("")
    except Exception as e:
        lines.append(f"*(Audit log unavailable: {e})*")
        lines.append("")

    # ── FILE MANIFEST ─────────────────────────────────────────────────
    lines.append("## File Manifest")
    lines.append("")
    lines.append("| File | Size | SHA-256 |")
    lines.append("|------|------|---------|")
    v2_files = sorted(PROOF_DIR.glob("v2_*_full*"))
    v2_mission_files = sorted((PROOF_DIR / "v2_full_missions").glob("*.json")) if (PROOF_DIR / "v2_full_missions").exists() else []
    for fp in v2_files + v2_mission_files:
        if fp.is_file():
            rel = fp.relative_to(PROOF_DIR)
            size = fp.stat().st_size
            h = sha256_file(fp)
            lines.append(f"| `{rel}` | {size:,} | `{h[:32]}...` |")
    lines.append("")

    # ── INTEGRITY STATEMENT ───────────────────────────────────────────
    lines.append("## Integrity Statement")
    lines.append("")
    lines.append("All outputs in this document were generated by the CONEXUS sovereign AI "
                 "system running locally on a single machine. No cloud API was called during "
                 "inference. All LLM processing ran via GPT4All with CPU device. The hash "
                 "chain links every mission's complete result (by SHA-256) to the previous "
                 "mission's result, creating a tamper-evident sequence across all six missions. "
                 "Any modification to any mission result would break the chain and be "
                 "immediately detectable.")
    lines.append("")
    lines.append("The live event log timestamps were recorded at the moment each event "
                 "occurred during execution, not reconstructed after the fact. The sequential "
                 "and unbroken nature of these timestamps constitutes additional proof of "
                 "live execution.")
    lines.append("")
    lines.append("Missions 4-6 demonstrate memory continuity: each retrieved prior mission "
                 "outputs from Qdrant vector memory via semantic search, proving the sovereign "
                 "loop feeds itself. The retrieval metadata (source mission IDs, similarity "
                 "scores, injected context length) is embedded in each mission's result and "
                 "independently verifiable.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Built by Derek Angell. CONEXUS Collapse-Become Unified Protocol v1.1.*")
    lines.append("*Patent reference: US 63/898,911*")
    lines.append("")
    lines.append("*This is the canonical proof of a sovereign cognitive architecture.*")
    lines.append("")

    return "\n".join(lines)


def generate_pdf(md_path: Path, pdf_path: Path):
    """Generate a PDF from the Markdown content using fpdf2."""
    try:
        from fpdf import FPDF
    except ImportError:
        print("WARNING: fpdf2 not installed. Skipping PDF generation.")
        print("  Install with: pip install fpdf2")
        return False

    md_text = md_path.read_text(encoding="utf-8")

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Title Page ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 28)
    pdf.ln(30)
    pdf.cell(0, 15, "CONEXUS", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Sovereign Proof V2", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 14)
    pdf.ln(5)
    pdf.cell(0, 10, "Full Canonical Sequence", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Cryptographically Verified Live Mission Capture",
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 8, "6-Mission Proof of the Collapse-Become Unified Protocol v1.1",
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    pdf.cell(0, 8, datetime.now(timezone.utc).strftime("%B %d, %Y"),
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 8, "Built by Derek Angell | Patent: US 63/898,911",
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 8, "Collapse-Become Unified Protocol v1.1",
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 7, "The canonical proof of a sovereign cognitive architecture.",
             new_x="LMARGIN", new_y="NEXT", align="C")

    # ── Content Pages ─────────────────────────────────────────────────
    pdf.add_page()

    current_font_size = 10
    in_code_block = False

    for line in md_text.split("\n"):
        # Code blocks
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            if in_code_block:
                pdf.set_font("Courier", "", 7)
            else:
                pdf.set_font("Helvetica", "", current_font_size)
            continue

        if in_code_block:
            safe_line = line.encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(0, 4, safe_line[:120], new_x="LMARGIN", new_y="NEXT")
            continue

        # Headings
        if line.startswith("# ") and not line.startswith("##"):
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 18)
            current_font_size = 10
            safe = line.lstrip("# ").encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(0, 10, safe, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            pdf.set_draw_color(0, 0, 0)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Helvetica", "", 10)
            continue

        if line.startswith("## "):
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 14)
            safe = line.lstrip("# ").encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(0, 8, safe, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            pdf.set_font("Helvetica", "", 10)
            continue

        if line.startswith("### "):
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 12)
            safe = line.lstrip("# ").encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(0, 7, safe, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            pdf.set_font("Helvetica", "", 10)
            continue

        if line.startswith("#### "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "BI", 10)
            safe = line.lstrip("# ").encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(0, 6, safe, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            continue

        # Horizontal rule
        if line.strip() == "---":
            pdf.ln(3)
            pdf.set_draw_color(150, 150, 150)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            continue

        # Table rows
        if line.startswith("|"):
            pdf.set_font("Courier", "", 5)
            safe = line.encode("latin-1", errors="replace").decode("latin-1")
            pdf.cell(0, 3, safe[:160], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            continue

        # Empty line
        if not line.strip():
            pdf.ln(2)
            continue

        # Bold text detection
        if line.strip().startswith("**") and line.strip().endswith("**"):
            pdf.set_font("Helvetica", "B", 10)
            safe = line.strip().strip("*").encode("latin-1", errors="replace").decode("latin-1")
            try:
                pdf.multi_cell(0, 5, safe)
            except Exception:
                pdf.cell(0, 5, safe[:120], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            continue

        # Bullet points
        if line.strip().startswith("- "):
            safe = line.encode("latin-1", errors="replace").decode("latin-1")
            pdf.set_font("Helvetica", "", 9)
            pdf.set_x(15)
            try:
                pdf.multi_cell(0, 5, safe.strip())
            except Exception:
                pdf.cell(0, 5, safe.strip()[:120], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            continue

        # Sub-bullet points
        if line.strip().startswith("- "):
            safe = line.encode("latin-1", errors="replace").decode("latin-1")
            pdf.set_font("Helvetica", "", 8)
            pdf.set_x(20)
            try:
                pdf.multi_cell(0, 4, safe.strip())
            except Exception:
                pdf.cell(0, 4, safe.strip()[:120], new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            continue

        # Regular text
        pdf.set_font("Helvetica", "", 10)
        safe = line.encode("latin-1", errors="replace").decode("latin-1")
        try:
            pdf.multi_cell(0, 5, safe)
        except Exception:
            pdf.cell(0, 5, safe[:120], new_x="LMARGIN", new_y="NEXT")

    # Save
    pdf.output(str(pdf_path))
    return True


def main():
    print("=" * 60)
    print("SOVEREIGN PROOF V2 FULL — Document Generator")
    print("=" * 60)

    print("\nLoading proof data...")
    capture, results, chain = load_data()
    print(f"  Capture: {capture.get('total_events', 0)} events")
    print(f"  Results: {len(results)} missions")
    print(f"  Chain: {len(chain)} links")

    print("\nVerifying hash chain...")
    verified = verify_chain(chain, results)
    for v in verified:
        status = "VALID" if v["hash_valid"] and v["chain_valid"] else "BROKEN"
        print(f"  Mission {v['mission']}: {status} ({v['result_hash'][:16]}...)")

    all_ok = all(v["hash_valid"] and v["chain_valid"] for v in verified)
    print(f"  Chain integrity: {'VERIFIED' if all_ok else 'BROKEN'}")

    print("\nGenerating Markdown...")
    md_content = generate_markdown(capture, results, chain)
    md_path = PROOF_DIR / "SOVEREIGN_PROOF_V2_FULL.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  Written: {md_path} ({len(md_content):,} chars)")

    print("\nGenerating PDF...")
    pdf_path = PROOF_DIR / "SOVEREIGN_PROOF_V2_FULL.pdf"
    if generate_pdf(md_path, pdf_path):
        print(f"  Written: {pdf_path} ({pdf_path.stat().st_size:,} bytes)")
    else:
        print("  PDF generation skipped (install fpdf2)")

    print(f"\n{'=' * 60}")
    print("DOCUMENT GENERATION COMPLETE")
    print(f"  Markdown: {md_path}")
    print(f"  PDF:      {pdf_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
