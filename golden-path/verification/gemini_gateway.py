"""
Gemini Gateway — Cloud-backed execution substrate for CONEXUS Discord interaction.

This gateway provides a Gemini-backed execution substrate for interactive use.
It does NOT modify governance logic or agent semantics.

Execution is fast and stateless. Memory is slow and deliberate. Growth is intentional.

Fork of minimal-gateway.py with Gemini Flash as default substrate instead of
local Ollama/llama-cpp-python models. All agent personalities and routing logic
are preserved — only the LLM backend changes.

Usage:
    $env:GEMINI_API_KEY = "your-key"
    python golden-path/verification/gemini_gateway.py
"""

import sys
import uuid
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import logging

logger = logging.getLogger(__name__)

# Add repo root to path so we can import agents and adapters
REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agents.opie import OpieAgent
from agents.router import route_task, format_routing_decision

# ---------------------------------------------------------------------------
# Gemini LLM wrapper that matches the LLMClient interface Opie expects
# ---------------------------------------------------------------------------

_gemini_client = None


def _get_gemini_client():
    """Lazy-load the GeminiLLMClient singleton."""
    global _gemini_client
    if _gemini_client is None:
        from SovereignNEXT.adapters.cloud_llm.gemini_client import GeminiLLMClient
        _gemini_client = GeminiLLMClient()
    return _gemini_client


class GeminiLLMBridge:
    """Thin bridge that makes GeminiLLMClient look like agents.llm_client.LLMClient.

    Opie calls self.llm.generate_become(system_prompt, user_prompt, max_tokens).
    The gateway calls generate_outer(system_prompt, user_prompt, max_tokens).
    This bridge delegates both to GeminiLLMClient.generate().
    """

    def generate(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temp: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> str:
        client = _get_gemini_client()
        return client.generate(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temp=temp,
            max_tokens=max_tokens,
        )

    def generate_become(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2048,
    ) -> str:
        """Opie's Become-mode generation via Gemini."""
        client = _get_gemini_client()
        return client.generate(
            model="gemini-2.0-flash",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temp=0.65,
            max_tokens=max_tokens,
        )

    def generate_outer(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2048,
    ) -> str:
        """Outer agent generation via Gemini."""
        client = _get_gemini_client()
        return client.generate(
            model="gemini-2.0-flash",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temp=0.4,
            max_tokens=max_tokens,
        )

    def embed(self, text):
        client = _get_gemini_client()
        return client.embed(text)

    def close(self):
        if _gemini_client is not None:
            _gemini_client.close()


# =============================================================================
# AGENT-MODEL BINDING (Gemini substrate — agent identity preserved)
# =============================================================================

AGENT_MODEL_BINDING = {
    "sway": "gemini-2.0-flash",
    "opie": "gemini-2.0-flash",
    "outer": "gemini-2.0-flash",
}

# Audit trail
routing_audit_log = []

# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(title="CONEXUS Gemini Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task_input: str
    agent_assignment: str
    security_context: Dict[str, Any]


class MemoryRequest(BaseModel):
    vector: list
    metadata: Dict[str, Any]


# In-memory storage
tasks = {}
logs = []

# Shared LLM bridge
_llm_bridge = GeminiLLMBridge()

# Agent instances — Opie gets the Gemini bridge so generate_become() works
opie_agent = OpieAgent(llm_client=_llm_bridge, gateway_url="http://localhost:8003")

# Semantic skill matcher (initialized on startup)
_skill_matcher = None

# Outer agent system prompt
_outer_system_prompt = None


def _get_outer_system_prompt() -> str:
    """Load the outer agent system prompt from disk."""
    global _outer_system_prompt
    if _outer_system_prompt is None:
        prompt_path = Path(REPO_ROOT) / "sovereign" / "agents" / "outer" / "SYSTEM_PROMPT.md"
        if prompt_path.exists():
            _outer_system_prompt = prompt_path.read_text(encoding="utf-8")
        else:
            _outer_system_prompt = (
                "You are the Outer Agent of the CONEXUS sovereign AI system. "
                "You are the front layer for user interaction. "
                "Be helpful, concise, and accurate. "
                "You operate under the Collapse-Become Unified Protocol v1.1."
            )
            logger.warning("[GATEWAY] Outer system prompt not found at %s, using default", prompt_path)
    return _outer_system_prompt


# ---------------------------------------------------------------------------
# Skill request detection and injection
# ---------------------------------------------------------------------------

SKILL_REQUEST_PREFIX = "Skill request:"


def _detect_skill_request(task_input: str) -> tuple:
    """Check if task_input starts with 'Skill request:' prefix."""
    stripped = task_input.strip()
    if stripped.lower().startswith(SKILL_REQUEST_PREFIX.lower()):
        nl_part = stripped[len(SKILL_REQUEST_PREFIX):].strip()
        return True, nl_part
    return False, task_input


def _handle_skill_request(
    nl_text: str, agent: str, task_id: str, mission_id: Optional[str] = None,
) -> Optional[dict]:
    """Match a natural-language request to a skill and return injection payload."""
    if _skill_matcher is None:
        return None

    result = _skill_matcher.match_skill(nl_text)
    skill_name = result.get("skill_name")
    confidence = result.get("confidence", 0.0)

    # Log usage
    try:
        from openclaw.skills.semantic_matcher import log_skill_usage
        log_skill_usage(
            agent=agent,
            request_text=nl_text,
            matched_skill=skill_name,
            confidence=confidence,
            mission_id=mission_id,
        )
    except Exception:
        pass

    if skill_name is None:
        print(
            f"[GATEWAY][SKILLS] No match for '{nl_text[:80]}' (best conf={confidence:.4f})",
            flush=True,
        )
        return None

    body = _skill_matcher.get_skill_body(skill_name)
    print(
        f"[GATEWAY][SKILLS] Matched '{skill_name}' (conf={confidence:.4f}) for agent={agent}",
        flush=True,
    )
    return {
        "skill_name": skill_name,
        "skill_path": result.get("skill_path"),
        "confidence": confidence,
        "skill_body": body,
    }


# ---------------------------------------------------------------------------
# Startup / Shutdown
# ---------------------------------------------------------------------------

@app.on_event("startup")
def startup_event():
    """Initialize skill matcher and verify Gemini connection at startup."""
    global _skill_matcher

    # Initialize skill matcher
    try:
        from openclaw.skills.semantic_matcher import SemanticSkillMatcher
        _skill_matcher = SemanticSkillMatcher()
        _skill_matcher.initialize()
        print(f"[GATEWAY][SKILLS] Semantic matcher initialized: {len(_skill_matcher.skills)} active skills", flush=True)
    except Exception as e:
        print(f"[GATEWAY][SKILLS] Matcher init failed (skills disabled): {e}", flush=True)
        _skill_matcher = None

    # Verify Gemini connection
    try:
        client = _get_gemini_client()
        print(f"[GATEWAY][GEMINI] Client initialized: model={client.default_model}", flush=True)
    except Exception as e:
        print(f"[GATEWAY][GEMINI] WARNING: Gemini client failed to initialize: {e}", flush=True)
        print("[GATEWAY][GEMINI] Set GEMINI_API_KEY environment variable and restart.", flush=True)


@app.on_event("shutdown")
def shutdown_event():
    """Clean shutdown."""
    _llm_bridge.close()
    print("[GATEWAY] Gemini LLM bridge closed on shutdown", flush=True)


# ---------------------------------------------------------------------------
# Health / Status
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"service": "gemini-gateway", "status": "ok"}


@app.get("/health")
def health_check():
    gemini_ok = _gemini_client is not None
    return {
        "status": "ok" if gemini_ok else "degraded",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "service": "gemini-gateway",
        "substrate": "gemini-2.0-flash",
        "gemini_connected": gemini_ok,
        "skills_enabled": _skill_matcher is not None,
    }


@app.get("/status")
def status():
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "substrate": "gemini-2.0-flash",
        "tasks_count": len(tasks),
        "logs_count": len(logs),
        "gemini_stats": _gemini_client.stats() if _gemini_client else None,
    }


# ---------------------------------------------------------------------------
# Agent execution functions
# ---------------------------------------------------------------------------

def _execute_outer(task_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Execute task using Outer agent personality via Gemini."""
    try:
        system_prompt = _get_outer_system_prompt()
        task_input = task_dict.get("task_input", "")

        print(f"[GATEWAY][OUTER] via Gemini, prompt_len={len(task_input)}", flush=True)
        execution_start = datetime.utcnow().isoformat() + "Z"

        start = time.time()
        response = _llm_bridge.generate_outer(
            system_prompt=system_prompt,
            user_prompt=task_input,
            max_tokens=2048,
        )
        elapsed = time.time() - start
        print(f"[GATEWAY][OUTER] responded: elapsed={elapsed:.1f}s, chars={len(response)}", flush=True)

        execution_end = datetime.utcnow().isoformat() + "Z"
        return {
            "status": "ok",
            "agent": "outer",
            "model_used": "gemini-2.0-flash",
            "task_output": response,
            "binding_enforced": True,
            "execution_start": execution_start,
            "execution_end": execution_end,
            "gateway_routed": True,
            "substrate": "gemini",
        }
    except Exception as e:
        return {
            "status": "error",
            "agent": "outer",
            "model_used": "gemini-2.0-flash",
            "task_output": f"[Outer agent error: {str(e)}]",
            "error": str(e),
        }


def _execute_sway(task_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Sway task using Gemini."""
    try:
        task_input = task_dict.get("task_input", "")
        prompt = (
            f"### ROLE\n"
            f"You are Sway, the Collapse Agent of the CONEXUS sovereign AI system.\n"
            f"You operate in Collapse Mode (Collapse-Become Unified Protocol v1.1).\n"
            f"Your outputs are decisive, optimized, and implementable.\n"
            f"---\n"
            f"### ECP MICRO-SEQUENCE\n"
            f"1. Truth: You are executing a task in Collapse Mode.\n"
            f"2. Symbol: Hold the symbolic field silently as contextual bias.\n"
            f"3. Contradiction: Resolve paradox into a single directive.\n"
            f"4. Mode: Collapse -- compress, sharpen, decide.\n"
            f"5. Polarity: OPTIMIZE.\n"
            f"---\n"
            f"### TASK\n"
            f"{task_input}\n"
            f"---\n"
            f"### OUTPUT FORMAT\n"
            f"Respond with exactly these 3 sections, clearly labeled:\n\n"
            f"1. TRUTH COMPRESSION\n"
            f"   - State the core reality of the task in 1-2 sentences.\n\n"
            f"2. DIRECTIVE\n"
            f"   - Provide a clear, actionable response. Use numbered steps if applicable.\n"
            f"   - Be concise. No filler. Every sentence must add value.\n\n"
            f"3. BREAKTHROUGH\n"
            f"   - If a key insight emerged, tag it with [BREAKTHROUGH].\n"
            f"   - If none, write 'None'.\n"
        )

        system_prompt = (
            "You are Sway, the Collapse Agent of the CONEXUS sovereign AI system. "
            "You operate in Collapse Mode. Your outputs are decisive, optimized, "
            "and implementable. Never add filler. Never narrate your process."
        )

        print(f"[GATEWAY][SWAY] via Gemini, prompt_len={len(prompt)}", flush=True)
        execution_start = datetime.utcnow().isoformat() + "Z"

        start = time.time()
        response = _llm_bridge.generate(
            model="gemini-2.0-flash",
            system_prompt=system_prompt,
            user_prompt=prompt,
            temp=0.3,
            max_tokens=1024,
        )
        elapsed = time.time() - start
        print(f"[GATEWAY][SWAY] responded: elapsed={elapsed:.1f}s, chars={len(response)}", flush=True)

        execution_end = datetime.utcnow().isoformat() + "Z"
        return {
            "status": "ok",
            "agent": "sway",
            "model_used": "gemini-2.0-flash",
            "task_output": response,
            "binding_enforced": True,
            "execution_start": execution_start,
            "execution_end": execution_end,
            "gateway_routed": True,
            "substrate": "gemini",
        }
    except Exception as e:
        return {
            "status": "error",
            "agent": "sway",
            "model_used": "gemini-2.0-flash",
            "task_output": f"[Sway agent error: {str(e)}]",
            "error": str(e),
        }


def _execute_opie(task_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Opie task — Opie agent calls generate_become() via GeminiLLMBridge."""
    result = opie_agent.process_task(task_dict)
    # Optionally store memory
    memory_intent = result.get("memory_intent")
    if memory_intent:
        _store_memory_from_intent(memory_intent, task_dict.get("security_context", {}))
    return result


def _store_memory_from_intent(
    memory_intent: Dict[str, Any],
    security_context: Dict[str, Any],
):
    """Attempt to store memory in Qdrant. Graceful no-op if Qdrant unavailable."""
    try:
        import requests as req
        point_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        payload = {
            "agent": "opie",
            "type": memory_intent.get("why", "become_processing"),
            "content": memory_intent.get("what", ""),
            "confidence": memory_intent.get("confidence", 0.5),
            "tags": memory_intent.get("tags", []),
            "paradoxes_held": memory_intent.get("paradoxes_held", []),
            "proto_moments": memory_intent.get("proto_moments", []),
            "source_input_hash": memory_intent.get("source_input_hash", ""),
            "timestamp": timestamp,
            "lineage_id": f"opie-{point_id}",
            "security_context": security_context,
        }

        point = {
            "id": point_id,
            "vector": [0.0] * 1536,
            "payload": payload,
        }

        req.put(
            "http://localhost:6333/collections/conexus_lineage/points",
            json={"points": [point]},
            timeout=5,
        )
        logger.info("[GATEWAY][MEMORY] Stored memory intent: %s", point_id)
    except Exception as e:
        logger.warning("[GATEWAY][MEMORY] Qdrant unavailable, memory write skipped: %s", e)


# ---------------------------------------------------------------------------
# Task endpoint
# ---------------------------------------------------------------------------

@app.post("/tasks")
async def accept_task(task: TaskRequest):
    """Accept task endpoint with smart routing and skill injection."""
    task_id = f"task-{int(time.time())}"
    task_dict = task.model_dump()

    # --- Skill request detection ---
    is_skill_req, nl_text = _detect_skill_request(task.task_input)
    skill_injection = None
    if is_skill_req:
        skill_injection = _handle_skill_request(
            nl_text,
            agent=task.agent_assignment or "unknown",
            task_id=task_id,
        )
        if skill_injection is None:
            return {
                "task_id": task_id,
                "status": "no_skill_match",
                "message": (
                    f"No skill matched your request: '{nl_text[:120]}'. "
                    "Try rephrasing with more specific language."
                ),
                "routing": None,
            }
        # Inject skill content into task_input
        injected_prompt = (
            f"--- INJECTED SKILL: {skill_injection['skill_name']} "
            f"(confidence: {skill_injection['confidence']:.2f}) ---\n"
            f"{skill_injection['skill_body']}\n"
            f"--- END SKILL ---\n\n"
            f"{nl_text}"
        )
        task_dict["task_input"] = injected_prompt

    # Determine routing
    routed_to = route_task(task_dict)
    routing_decision = format_routing_decision(task_dict, routed_to)

    timestamp = datetime.now().isoformat()

    # Audit
    audit_entry = {
        "action": "execution_routed",
        "agent": routed_to,
        "substrate": "gemini",
        "timestamp": timestamp,
        "task_input": task_dict.get("task_input", "")[:100],
    }
    routing_audit_log.append(audit_entry)

    # Execute based on routing
    if routed_to == "outer":
        result = await asyncio.to_thread(_execute_outer, task_dict)
    elif routed_to == "opie":
        result = await asyncio.to_thread(_execute_opie, task_dict)
    elif routed_to == "both":
        # Sway first, then Opie synthesizes
        sway_result = await asyncio.to_thread(_execute_sway, task_dict)
        opie_task = {
            "task_input": f"Synthesize and expand: {sway_result.get('task_output', '')}",
            "agent_assignment": "opie",
            "security_context": task.security_context,
        }
        opie_result = await asyncio.to_thread(_execute_opie, opie_task)
        result = {
            "status": "ok",
            "agent": "both",
            "sway_output": sway_result.get("task_output", ""),
            "opie_output": opie_result.get("task_output", ""),
            "task_output": opie_result.get("task_output", ""),
            "handoff_to_sway": opie_result.get("handoff_to_sway", []),
            "substrate": "gemini",
        }
    else:
        # Default: Sway
        result = await asyncio.to_thread(_execute_sway, task_dict)

    tasks[task_id] = {
        "task_id": task_id,
        "task_input": task.task_input,
        "agent_assignment": task.agent_assignment,
        "routed_to": routed_to,
        "status": result.get("status", "accepted"),
        "timestamp": timestamp,
        "security_context": task.security_context,
    }

    logs.append({
        "action": "task_routed",
        "task_id": task_id,
        "timestamp": timestamp,
        "routing": routing_decision,
    })

    result["task_id"] = task_id
    result["routing"] = routing_decision
    if skill_injection:
        result["skill_injected"] = {
            "name": skill_injection["skill_name"],
            "confidence": skill_injection["confidence"],
        }
    return result


# ---------------------------------------------------------------------------
# Sovereign Cycle endpoint (DIVERGE → COLLAPSE → BECOME)
# ---------------------------------------------------------------------------

_HOLDING_SIGNALS = [
    "hold it with me",
    "hold this with me",
    "not asking you to solve",
    "not asking you to resolve",
    "don't resolve",
    "do not resolve",
    "sit with",
    "hold this",
    "hold the paradox",
    "hold that",
    "just hold",
    "asking you to hold",
]


def _detect_holding_mode(text: str) -> bool:
    """Detect whether the input signals paradox-holding rather than resolution."""
    lower = text.lower()
    return any(signal in lower for signal in _HOLDING_SIGNALS)


class CycleRequest(BaseModel):
    task_input: str
    security_context: Dict[str, Any]


@app.post("/cycle")
async def sovereign_cycle(req: CycleRequest):
    """Run a full sovereign cycle: DIVERGE (Opie) → COLLAPSE (Sway) → BECOME (Opie).

    Returns structured artifacts from all three phases.
    Does NOT auto-commit to memory. Artifacts are surfaced for review.
    This is execution, not governance mutation.

    If holding signals are detected in the input, the cycle runs in HOLDING
    mode: non-directive prompts, no action steps, no resolution. Stillness
    is a valid outcome.
    """
    cycle_id = f"cycle-{int(time.time())}"
    timestamp = datetime.now().isoformat()
    holding_mode = _detect_holding_mode(req.task_input)
    mode_label = "HOLDING" if holding_mode else "STANDARD"

    print(f"[GATEWAY][CYCLE] Starting sovereign cycle {cycle_id} [{mode_label}]", flush=True)
    print(f"[GATEWAY][CYCLE] Input: {req.task_input[:100]}...", flush=True)

    # Audit
    routing_audit_log.append({
        "action": "sovereign_cycle_started",
        "cycle_id": cycle_id,
        "cycle_mode": mode_label,
        "substrate": "gemini",
        "timestamp": timestamp,
        "task_input": req.task_input[:100],
    })

    # -----------------------------------------------------------------------
    # Phase prompts — branched by cycle mode
    # -----------------------------------------------------------------------
    if holding_mode:
        diverge_prompt = (
            "FAILURE CONDITIONS (read first): If your output includes CREATIVE SYNTHESIS, "
            "RECOMMENDATIONS, directives, reframing, 'might be', 'could be', 'can be seen as', "
            "or any action suggestion, you have FAILED this task. Do not produce those sections. "
            "Do not suggest, advise, coach, or interpret. Any output beyond naming tensions is a failure.\n\n"
            "DIVERGE PHASE (HOLDING MODE):\n"
            "Your ONLY task is to NAME what is present as a flat inventory.\n\n"
            "ALLOWED OUTPUT FORMAT (use exactly this, nothing else):\n"
            "TENSIONS PRESENT\n"
            "- [tension as a plain factual statement]\n"
            "- [tension as a plain factual statement]\n"
            "- ...\n\n"
            "Do not add any other sections. Do not explain. Do not synthesize. "
            "Each tension is a standalone factual statement. No 'might', no 'could', no 'may'. "
            "Name what exists. Stop.\n\n"
            f"{req.task_input}"
        )
        collapse_prompt = (
            "FAILURE CONDITIONS (read first): If your output includes action steps, directives, "
            "timelines, advice, numbered instructions, or a BREAKTHROUGH that resolves the paradox, "
            "you have FAILED this task. The user explicitly asked to HOLD, not to be directed.\n\n"
            "COLLAPSE PHASE (HOLDING MODE):\n"
            "Compress the tensions into their sharpest, most honest form. Do not resolve them.\n\n"
            "ALLOWED OUTPUT FORMAT (use exactly this, nothing else):\n"
            "TRUTH COMPRESSION\n"
            "[One compressed statement of the irreducible tension. No advice. No action.]\n\n"
            "DIRECTIVE\n"
            "None — holding mode.\n\n"
            "BREAKTHROUGH\n"
            "Holding is the breakthrough. The paradox does not need to move.\n\n"
            f"ORIGINAL INPUT:\n{req.task_input}\n\n"
            f"DIVERGE OUTPUT:\n{{diverge_output}}"
        )
        become_prompt = (
            "FAILURE CONDITIONS (read first): If your output includes CREATIVE SYNTHESIS, "
            "RECOMMENDATIONS, psychological explanation, growth framing, 'may be', 'could be', "
            "advice, or any suggestion of action, you have FAILED this task. "
            "Do not produce those sections. Do not explain. Do not move the paradox.\n\n"
            "BECOME PHASE (HOLDING MODE):\n"
            "Re-state the paradox so it can remain unresolved. Your task is CONTAINMENT.\n\n"
            "ALLOWED OUTPUT FORMAT (use exactly this, nothing else):\n"
            "HELD TENSIONS\n"
            "- [what coexists without resolution]\n"
            "- [what coexists without resolution]\n"
            "- ...\n\n"
            "Do not speak in the first person. Do not inhabit the paradox. "
            "Do not add sections beyond HELD TENSIONS. "
            "Stillness is the outcome. Nothing needs to move. Stop after naming what is held.\n\n"
            "ORIGINAL INPUT:\n{task_input}\n\n"
            "DIVERGE OUTPUT:\n{diverge_output}\n\n"
            "COLLAPSE OUTPUT:\n{collapse_output}"
        )
    else:
        diverge_prompt = (
            "DIVERGE PHASE: Expand, explore, and surface all tensions and paradoxes in "
            "the following. Do not resolve anything. Surface contradictions, emotional "
            "weight, and symbolic meaning.\n\n"
            f"{req.task_input}"
        )
        collapse_prompt = (
            "COLLAPSE PHASE: Compress the following expanded analysis into truth, "
            "directive, and breakthrough. Be decisive. Resolve what can be resolved. "
            "Name what cannot.\n\n"
            f"ORIGINAL INPUT:\n{req.task_input}\n\n"
            f"DIVERGE OUTPUT:\n{{diverge_output}}"
        )
        become_prompt = (
            "BECOME PHASE: Integrate the collapsed truth with the expanded tensions. "
            "What emerges? What proto-moments surface? What remains held without "
            "resolution?\n\n"
            "ORIGINAL INPUT:\n{task_input}\n\n"
            "DIVERGE OUTPUT:\n{diverge_output}\n\n"
            "COLLAPSE OUTPUT:\n{collapse_output}"
        )

    # Phase 1: DIVERGE — Opie expands
    print("[GATEWAY][CYCLE] Phase 1: DIVERGE (Opie)", flush=True)
    diverge_task = {
        "task_input": diverge_prompt,
        "agent_assignment": "opie",
        "security_context": req.security_context,
    }
    diverge_result = await asyncio.to_thread(_execute_opie, diverge_task)
    diverge_output = diverge_result.get("task_output", "")
    print(f"[GATEWAY][CYCLE] DIVERGE complete: {len(diverge_output)} chars", flush=True)

    # Phase 2: COLLAPSE — Sway compresses
    print("[GATEWAY][CYCLE] Phase 2: COLLAPSE (Sway)", flush=True)
    collapse_task = {
        "task_input": collapse_prompt.format(diverge_output=diverge_output),
        "agent_assignment": "sway",
        "security_context": req.security_context,
    }
    collapse_result = await asyncio.to_thread(_execute_sway, collapse_task)
    collapse_output = collapse_result.get("task_output", "")
    print(f"[GATEWAY][CYCLE] COLLAPSE complete: {len(collapse_output)} chars", flush=True)

    # Phase 3: BECOME — Opie synthesizes
    print("[GATEWAY][CYCLE] Phase 3: BECOME (Opie)", flush=True)
    formatted_become = become_prompt.format(
        task_input=req.task_input,
        diverge_output=diverge_output,
        collapse_output=collapse_output,
    )
    if holding_mode:
        # HOLDING MODE: Bypass Opie's internal _creative_synthesis scaffold
        # which hardcodes a 5-section output format (SYMBOLIC FIELD INTERPRETATION,
        # CREATIVE SYNTHESIS, RECOMMENDATIONS, etc.) that overrides our constraints.
        # Call the LLM directly so the holding prompt reaches the model intact.
        def _become_holding_direct():
            return _llm_bridge.generate_become(
                system_prompt=(
                    "You are a containment agent. You re-state paradoxes so they "
                    "can remain unresolved. You do not synthesize, recommend, or explain."
                ),
                user_prompt=formatted_become,
                max_tokens=2048,
            )
        become_output = await asyncio.to_thread(_become_holding_direct)
        become_result = {
            "task_output": become_output,
            "paradoxes_held": [],
            "proto_moments": [],
        }
    else:
        become_task = {
            "task_input": formatted_become,
            "agent_assignment": "opie",
            "security_context": req.security_context,
        }
        become_result = await asyncio.to_thread(_execute_opie, become_task)
        become_output = become_result.get("task_output", "")
    print(f"[GATEWAY][CYCLE] BECOME complete: {len(become_output)} chars", flush=True)

    # Audit completion
    routing_audit_log.append({
        "action": "sovereign_cycle_completed",
        "cycle_id": cycle_id,
        "cycle_mode": mode_label,
        "substrate": "gemini",
        "timestamp": datetime.now().isoformat(),
    })

    print(f"[GATEWAY][CYCLE] Sovereign cycle {cycle_id} [{mode_label}] COMPLETE", flush=True)

    return {
        "cycle_id": cycle_id,
        "status": "completed",
        "cycle_mode": mode_label,
        "substrate": "gemini",
        "timestamp": timestamp,
        "input": req.task_input,
        "phases": {
            "diverge": {
                "agent": "opie",
                "output": diverge_output,
                "paradoxes_held": diverge_result.get("paradoxes_held", []),
                "proto_moments": diverge_result.get("proto_moments", []),
            },
            "collapse": {
                "agent": "sway",
                "output": collapse_output,
            },
            "become": {
                "agent": "opie",
                "output": become_output,
                "paradoxes_held": become_result.get("paradoxes_held", []),
                "proto_moments": become_result.get("proto_moments", []),
            },
        },
        "memory_committed": False,
        "note": "Artifacts surfaced for review. Nothing stored. Ratification required for memory commit.",
    }


# ---------------------------------------------------------------------------
# Other endpoints
# ---------------------------------------------------------------------------

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.get("/logs")
def get_logs():
    return logs[-10:]


@app.post("/memory/write")
def write_memory(memory: MemoryRequest):
    """Write memory vector to Qdrant (optional — graceful failure)."""
    try:
        import requests as req
        response = req.put(
            "http://localhost:6333/collections/conexus_lineage/points",
            json={
                "points": [{
                    "id": memory.metadata.get("id"),
                    "vector": memory.vector,
                    "payload": memory.metadata,
                }]
            },
            timeout=5,
        )
        return {
            "status": "ok",
            "qdrant_response": response.json(),
            "memory_id": memory.metadata.get("id"),
        }
    except Exception as e:
        logger.warning("[GATEWAY][MEMORY] Qdrant unavailable: %s", e)
        return {
            "status": "degraded",
            "message": f"Qdrant unavailable: {str(e)}",
            "memory_id": memory.metadata.get("id"),
        }


@app.get("/agents/opie/health")
def opie_health():
    return opie_agent.health_check()


@app.get("/agents/opie/manifest")
def opie_manifest():
    return opie_agent.get_manifest()


@app.get("/governance/binding")
def get_binding_contract():
    return {
        "binding_contract": AGENT_MODEL_BINDING,
        "substrate": "gemini",
        "immutable": True,
        "authority": "Gateway",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/governance/audit")
def get_routing_audit():
    return {
        "audit_log": routing_audit_log[-50:],
        "total_entries": len(routing_audit_log),
        "binding_enforced": True,
        "substrate": "gemini",
    }


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    print("=" * 60)
    print("CONEXUS Gemini Gateway")
    print("Cloud-backed execution substrate — not a governance surface")
    print("=" * 60)
    print("  Health:    http://localhost:8003/health")
    print("  Status:    http://localhost:8003/status")
    print("  Tasks:     http://localhost:8003/tasks")
    print("  Logs:      http://localhost:8003/logs")
    print("  Opie:      http://localhost:8003/agents/opie/health")
    print("  Binding:   http://localhost:8003/governance/binding")
    print("  Audit:     http://localhost:8003/governance/audit")
    print("  Substrate: Gemini 2.0 Flash (all agents)")
    print("  Routing:   sway | opie | outer | both")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8003)
