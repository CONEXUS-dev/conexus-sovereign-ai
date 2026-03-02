"""
Minimal Gateway Service for Phase C Memory Integration
With Opie (Become Agent) routing and multi-agent coordination.
"""

import sys
import uuid
import os
import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import requests
import time
from datetime import datetime
import re

REQUIRED_FIELDS = [
    "INPUT:",
    "OUTPUT:",
    "execution_start:",
    "execution_end:",
    "model:",
    "gateway_routed:"
]

FORBIDDEN_PATTERNS = [
    r"\bI acknowledge\b",
    r"\bI will\b",
    r"\bAnalysis\b",
    r"\bConclusion\b",
    r"🎯|🔥|💡|🚀|✨"
]

def validate_sway_response(response_text: str, expected_model: str) -> None:
    for field in REQUIRED_FIELDS:
        if field not in response_text:
            raise ValueError(f"Sway response invalid: missing {field}")

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, response_text, re.IGNORECASE):
            raise ValueError("Sway response invalid: narration detected")

    model_line = None
    for line in response_text.splitlines():
        if line.strip().startswith("model:"):
            model_line = line.strip()
            break

    if model_line is None:
        raise ValueError("Sway response invalid: missing model line")

    if expected_model not in model_line:
        raise ValueError(f"Sway response invalid: incorrect model binding ({model_line})")

    if "gateway_routed: true" not in response_text.lower():
        raise ValueError("Sway response invalid: gateway_routed must be true")


# Gemini API client (placeholder - replace with actual client)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini API not available. Install with: pip install google-generativeai")

# Add repo root to path so we can import agents
REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from agents.opie import OpieAgent
from agents.router import route_task, format_routing_decision
from agents.llm_client import LLMClient, OUTER_MODEL
from openclaw.skills.semantic_matcher import (
    SemanticSkillMatcher,
    log_skill_usage,
)

# =============================================================================
# GOVERNED INTELLIGENCE - AGENT-MODEL BINDING CONTRACT
# =============================================================================

# Immutable agent-model binding contract (SOVEREIGN AUTHORITY)
AGENT_MODEL_BINDING = {
    "sway": "llama3.1:8b",      # Collapse: Truth compression, structured reasoning
    "opie": "mistral:7b",       # Become: Meaning expansion, creative synthesis
    "outer": OUTER_MODEL,        # Outer: Phi-4-mini-instruct via llama-cpp-python
}

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434/api/generate"
OLLAMA_TIMEOUT = 60  # seconds

# Gemini configuration
GEMINI_API_KEY = "your_gemini_api_key_here"  # Set via environment variable
GEMINI_MODEL = "gemini-1.5-flash"  # Default Gemini model

# Substrate routing configuration
SUBSTRATE_CONFIG = {
    "default": "local",
    "allow_gemini_override": True,
    "require_explicit_flag": True
}

# Fallback protocol configuration
FALLBACK_CONFIG = {
    "enabled": True,
    "log_fallbacks": True,
    "require_explicit_flag": True,
    "max_retries": 3
}

# Audit trail for all routing decisions
routing_audit_log = []

# =============================================================================
# SUBSTRATE ROUTING FUNCTIONS
# =============================================================================

def choose_substrate(security_context: Dict[str, Any]) -> str:
    """Choose execution substrate based on security context."""
    if SUBSTRATE_CONFIG["allow_gemini_override"] and security_context.get("use_gemini") is True:
        return "gemini"
    return SUBSTRATE_CONFIG["default"]

def get_gemini_client():
    """Initialize and return Gemini client."""
    if not GEMINI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Gemini API not available")

    api_key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TaskRequest(BaseModel):
    task_input: str
    agent_assignment: str
    security_context: Dict[str, Any]

class MemoryRequest(BaseModel):
    vector: list
    metadata: Dict[str, Any]

# Simple in-memory storage for demonstration
tasks = {}
logs = []

# Agent instances
opie_agent = OpieAgent(gateway_url="http://localhost:8000")

# Semantic skill matcher (initialized on startup)
_skill_matcher: SemanticSkillMatcher | None = None

# Outer agent: LLM client + system prompt
_outer_llm_client = None
_outer_system_prompt = None

def _get_outer_client() -> LLMClient:
    """Lazy-load the outer agent LLM client."""
    global _outer_llm_client
    if _outer_llm_client is None:
        _outer_llm_client = LLMClient()
    return _outer_llm_client

def _get_outer_system_prompt() -> str:
    """Load the outer agent system prompt from disk."""
    global _outer_system_prompt
    if _outer_system_prompt is None:
        prompt_path = Path(REPO_ROOT) / "sovereign" / "agents" / "outer" / "SYSTEM_PROMPT.md"
        _outer_system_prompt = prompt_path.read_text(encoding="utf-8")
    return _outer_system_prompt

@app.on_event("startup")
def startup_event():
    """Initialize the semantic skill matcher at gateway startup."""
    global _skill_matcher
    try:
        _skill_matcher = SemanticSkillMatcher()
        _skill_matcher.initialize()
        print(f"[GATEWAY][SKILLS] Semantic matcher initialized: {len(_skill_matcher.skills)} active skills", flush=True)
    except Exception as e:
        print(f"[GATEWAY][SKILLS] Matcher init failed (skills disabled): {e}", flush=True)
        _skill_matcher = None


@app.on_event("shutdown")
def shutdown_event():
    """Clean shutdown: close outer agent LLM client."""
    global _outer_llm_client
    if _outer_llm_client is not None:
        _outer_llm_client.close()
        _outer_llm_client = None
        print("[GATEWAY] Outer LLM client closed on shutdown", flush=True)


@app.get("/")
def root():
    return {"service": "minimal-gateway", "status": "ok"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
        "service": "minimal-gateway"
    }

@app.get("/status")
def status():
    """Status endpoint"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "tasks_count": len(tasks),
        "logs_count": len(logs)
    }

# ---------------------------------------------------------------------------
# Skill request detection and injection
# ---------------------------------------------------------------------------

SKILL_REQUEST_PREFIX = "Skill request:"


def _detect_skill_request(task_input: str) -> tuple[bool, str]:
    """Check if task_input starts with 'Skill request:' prefix.

    Returns (is_skill_request, natural_language_portion).
    """
    stripped = task_input.strip()
    if stripped.lower().startswith(SKILL_REQUEST_PREFIX.lower()):
        nl_part = stripped[len(SKILL_REQUEST_PREFIX):].strip()
        return True, nl_part
    return False, task_input


def _handle_skill_request(
    nl_text: str, agent: str, task_id: str, mission_id: str | None = None
) -> dict | None:
    """Match a natural-language request to a skill and return injection payload.

    Returns None if no matcher or no match.
    """
    if _skill_matcher is None:
        return None

    result = _skill_matcher.match_skill(nl_text)
    skill_name = result.get("skill_name")
    confidence = result.get("confidence", 0.0)

    # Log usage regardless of match
    log_skill_usage(
        agent=agent,
        request_text=nl_text,
        matched_skill=skill_name,
        confidence=confidence,
        mission_id=mission_id,
    )

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
            # No match — tell the agent to rephrase
            return {
                "task_id": task_id,
                "status": "no_skill_match",
                "message": (
                    f"No skill matched your request: '{nl_text[:120]}'. "
                    "Try rephrasing with more specific language."
                ),
                "routing": None,
            }
        # Inject skill content into task_input for the agent
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

    # Enforce agent-model binding
    assigned_model = AGENT_MODEL_BINDING.get(routed_to)
    if not assigned_model:
        raise HTTPException(status_code=500, detail=f"No model binding for agent: {routed_to}")

    timestamp = datetime.now().isoformat()

    # Process based on routing with model binding enforcement
    if routed_to == "outer":
        result = await asyncio.to_thread(_execute_outer, task_dict)
        active_agent = "outer"
    elif routed_to == "opie":
        result = await asyncio.to_thread(_execute_with_model_binding, "opie", task_dict, task.security_context)
        active_agent = "opie"
    elif routed_to == "both":
        # Sway processes first with bound model
        sway_result = await asyncio.to_thread(_execute_with_model_binding, "sway", task_dict, task.security_context)
        # Opie synthesizes with bound model
        opie_task = {
            "task_input": f"Synthesize and expand: {sway_result['task_output']}",
            "agent_assignment": "opie",
            "security_context": task.security_context,
        }
        opie_result = await asyncio.to_thread(_execute_with_model_binding, "opie", opie_task, task.security_context)
        result = {
            "status": "ok",
            "agent": "both",
            "sway_output": sway_result.get("task_output", ""),
            "opie_output": opie_result.get("task_output", ""),
            "task_output": opie_result.get("task_output", ""),
            "handoff_to_sway": opie_result.get("handoff_to_sway", []),
        }
        active_agent = "both"
    else:
        # Default: Sway with bound model
        result = await asyncio.to_thread(_execute_with_model_binding, "sway", task_dict, task.security_context)
        active_agent = "sway"

    tasks[task_id] = {
        "task_id": task_id,
        "task_input": task.task_input,
        "agent_assignment": task.agent_assignment,
        "routed_to": routed_to,
        "status": result.get("status", "accepted"),
        "timestamp": timestamp,
        "security_context": task.security_context,
        "active_agent": active_agent,
    }

    logs.append({
        "action": "task_routed",
        "task_id": task_id,
        "timestamp": timestamp,
        "routing": routing_decision,
        "details": task_dict,
    })

    # Merge task_id into result
    result["task_id"] = task_id
    result["routing"] = routing_decision
    if skill_injection:
        result["skill_injected"] = {
            "name": skill_injection["skill_name"],
            "confidence": skill_injection["confidence"],
        }
    return result

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """Get task status endpoint"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/logs")
def get_logs():
    """Get logs endpoint"""
    return logs[-10:]  # Return last 10 logs

@app.post("/memory/write")
def write_memory(memory: MemoryRequest):
    """Write memory vector to Qdrant"""
    try:
        # Forward to Qdrant
        response = requests.put(
            "http://localhost:6333/collections/conexus_lineage/points",
            json={
                "points": [
                    {
                        "id": memory.metadata.get("id"),
                        "vector": memory.vector,
                        "payload": memory.metadata
                    }
                ]
            }
        )

        return {
            "status": "ok",
            "qdrant_response": response.json(),
            "memory_id": memory.metadata.get("id")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/opie/health")
def opie_health():
    """Opie agent health check"""
    return opie_agent.health_check()

@app.get("/agents/opie/manifest")
def opie_manifest():
    """Opie agent manifest"""
    return opie_agent.get_manifest()


def _execute_outer(task_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Execute task using the calibrated Phi-4-mini outer agent."""
    try:
        client = _get_outer_client()
        system_prompt = _get_outer_system_prompt()
        task_input = task_dict.get("task_input", "")

        print(f"[GATEWAY][OUTER] model={OUTER_MODEL}, prompt_len={len(task_input)}", flush=True)
        execution_start = datetime.utcnow().isoformat() + "Z"

        start = time.time()
        response = client.generate_outer(
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
            "model_used": OUTER_MODEL,
            "task_output": response,
            "binding_enforced": True,
            "execution_start": execution_start,
            "execution_end": execution_end,
            "gateway_routed": True,
        }
    except Exception as e:
        return {
            "status": "error",
            "agent": "outer",
            "model_used": OUTER_MODEL,
            "task_output": f"[Outer agent error: {str(e)}]",
            "error": str(e),
        }


def _execute_with_model_binding(agent: str, task_dict: Dict[str, Any], security_context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute task with bound model and substrate routing."""
    assigned_model = AGENT_MODEL_BINDING[agent]
    substrate = choose_substrate(security_context)

    # Enhanced audit logging with substrate information
    audit_entry = {
        "action": "execution_routed",
        "agent": agent,
        "identity_model": assigned_model,
        "substrate": substrate,
        "reason": "explicit_override" if substrate == "gemini" else "default",
        "timestamp": datetime.now().isoformat(),
        "task_input": task_dict.get("task_input", "")[:100] + "..." if len(task_dict.get("task_input", "")) > 100 else task_dict.get("task_input", "")
    }
    routing_audit_log.append(audit_entry)

    if substrate == "gemini":
        return _execute_with_gemini(agent, task_dict, assigned_model)

    # Default: local execution
    if agent == "opie":
        result = opie_agent.process_task(task_dict)
        memory_intent = result.get("memory_intent")
        if memory_intent:
            _store_memory_from_intent(memory_intent, security_context)
        return result
    elif agent == "sway":
        return _execute_sway_with_ollama(task_dict, assigned_model)
    else:
        raise HTTPException(status_code=500, detail=f"Unknown agent: {agent}")


def _execute_sway_with_ollama(task_dict: Dict[str, Any], model: str) -> Dict[str, Any]:
    """Execute Sway task using Ollama with bound model."""
    try:
        task_input = task_dict.get('task_input', '')
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
            f"4. Mode: Collapse — compress, sharpen, decide.\n"
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

        print(f"[GATEWAY][SWAY] Calling Ollama: model={model}, prompt_len={len(prompt)}", flush=True)
        execution_start = datetime.utcnow().isoformat() + "Z"

        start = time.time()
        response = requests.post(
            OLLAMA_BASE_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 200
                }
            },
            timeout=OLLAMA_TIMEOUT
        )
        elapsed = time.time() - start
        print(f"[GATEWAY][SWAY] Ollama responded: status={response.status_code}, elapsed={elapsed:.1f}s", flush=True)

        if response.status_code == 200:
            ollama_response = response.json()
            raw_output = ollama_response.get("response", "")

            try:
                validate_sway_response(raw_output, expected_model=model)
            except Exception as e:
                print(f"[GATEWAY][SWAY] response rejected: {e}", flush=True)
                return {
                    "status": "rejected",
                    "agent": "sway",
                    "reason": str(e),
                    "execution_start": execution_start
                }

            execution_end = datetime.utcnow().isoformat() + "Z"

            return {
                "status": "ok",
                "agent": "sway",
                "model_used": model,
                "task_output": raw_output,
                "binding_enforced": True,
                "execution_start": execution_start,
                "execution_end": execution_end,
                "gateway_routed": True
            }

        return _handle_model_failure("sway", model, task_dict)

    except Exception as e:
        return _handle_model_failure("sway", model, task_dict, str(e))


def _handle_model_failure(agent: str, model: str, task_dict: Dict[str, Any], error: str = None) -> Dict[str, Any]:
    """Handle model failure with explicit fallback protocol."""
    fallback_entry = {
        "action": "model_failure",
        "agent": agent,
        "failed_model": model,
        "error": error,
        "timestamp": datetime.now().isoformat(),
        "fallback_triggered": True
    }
    routing_audit_log.append(fallback_entry)

    if FALLBACK_CONFIG["enabled"]:
        return {
            "status": "degraded",
            "agent": agent,
            "model_used": "fallback",
            "task_output": f"[Model {model} unavailable. Sway analysis queued: {task_dict.get('task_input', '')}]",
            "binding_enforced": True,
            "fallback_active": True,
            "error": error
        }
    else:
        raise HTTPException(status_code=503, detail=f"Model {model} failed and fallback disabled")


def _execute_with_gemini(agent: str, task_dict: Dict[str, Any], identity_model: str) -> Dict[str, Any]:
    """Execute task using Gemini as substrate while preserving identity."""
    try:
        gemini_client = get_gemini_client()

        prompt = f"""You are executing on behalf of the {agent.upper()} agent.
Identity model: {identity_model}

Task:
{task_dict.get('task_input', '')}

Provide a response that aligns with the {agent} agent's role:
- If Sway: Focus on structured analysis, truth compression, and logical reasoning
- If Opie: Focus on creative synthesis, meaning expansion, and symbolic integration

Respond clearly and appropriately."""

        response = gemini_client.generate_content(prompt)

        return {
            "status": "ok",
            "agent": agent,
            "model_used": "gemini",
            "identity_model": identity_model,
            "task_output": response.text,
            "substrate": "gemini",
            "binding_enforced": True
        }

    except Exception as e:
        fallback_entry = {
            "action": "gemini_failure",
            "agent": agent,
            "identity_model": identity_model,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "fallback_triggered": True
        }
        routing_audit_log.append(fallback_entry)

        if agent == "opie":
            return opie_agent.process_task(task_dict)
        elif agent == "sway":
            return _execute_sway_with_ollama(task_dict, identity_model)
        else:
            raise HTTPException(status_code=500, detail=f"Unknown agent: {agent}")


def _store_memory_from_intent(
    memory_intent: Dict[str, Any],
    security_context: Dict[str, Any],
):
    """Construct a Qdrant payload from Opie's memory intent and store it.

    The Gateway owns:
      - UUID generation
      - Timestamp assignment
      - Embedding generation (placeholder zero-vector until service is wired)
      - Qdrant payload structure
      - Security context attachment

    Opie only declares *what* to remember and *why*.
    """
    try:
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

        requests.put(
            "http://localhost:6333/collections/conexus_lineage/points",
            json={"points": [point]},
            timeout=5,
        )
    except Exception:
        pass


@app.get("/governance/substrate")
def get_substrate_config():
    """Get current substrate routing configuration"""
    return {
        "substrate_config": SUBSTRATE_CONFIG,
        "gemini_available": GEMINI_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/governance/binding")
def get_binding_contract():
    """Get current agent-model binding contract"""
    return {
        "binding_contract": AGENT_MODEL_BINDING,
        "immutable": True,
        "authority": "Gateway",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/governance/audit")
def get_routing_audit():
    """Get routing audit trail"""
    return {
        "audit_log": routing_audit_log[-50:],
        "total_entries": len(routing_audit_log),
        "binding_enforced": True
    }

@app.get("/governance/fallback")
def get_fallback_status():
    """Get fallback protocol status"""
    return {
        "fallback_config": FALLBACK_CONFIG,
        "active_fallbacks": len([log for log in routing_audit_log if log.get("fallback_triggered")]),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Minimal Gateway Service (FastAPI)")
    print("📍 Health: http://localhost:8002/health")
    print("📍 Status: http://localhost:8002/status")
    print("📍 Tasks: http://localhost:8002/tasks")
    print("📍 Logs: http://localhost:8002/logs")
    print("📍 Memory: http://localhost:8002/memory/write")
    print("📍 Opie Health: http://localhost:8002/agents/opie/health")
    print("📍 Opie Manifest: http://localhost:8002/agents/opie/manifest")
    print("🤖 Smart routing: sway (default) | opie | both")
    print("⚖️  Governance: http://localhost:8002/governance/binding")
    print("📊 Audit Trail: http://localhost:8002/governance/audit")
    print("🔄 Fallback Status: http://localhost:8002/governance/fallback")
    print("🌐 Substrate Config: http://localhost:8002/governance/substrate")
    print(f"🔒 Agent-Model Binding: Sway→llama3.1:8b | Opie→mistral:7b | Outer→{OUTER_MODEL}")
    print("⚡ Two-Layer Routing: Local (Ollama) + Cloud (Gemini)")

    uvicorn.run(app, host='0.0.0.0', port=8002)
