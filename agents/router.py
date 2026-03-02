"""
CONEXUS Smart Router — Agent Task Routing

Routes tasks to the appropriate agent (Outer, Sway, or Opie) based on task
content, explicit assignment, or smart analysis of the input.

The Outer agent (Phi-4-mini) is the default front layer for user interaction.
Sway and Opie are the deep cognitive engines invoked for specific tasks.

Human operator can always override routing via explicit agent_assignment.
"""

from typing import Any, Dict


# ---------------------------------------------------------------------------
# Routing Keywords
# ---------------------------------------------------------------------------

SWAY_SIGNALS = [
    "analyze", "execute", "plan", "implement", "build", "deploy",
    "optimize", "structure", "break down", "prioritize", "decide",
    "calculate", "measure", "benchmark", "audit", "verify",
    "fix", "debug", "configure", "install", "test",
]

OPIE_SIGNALS = [
    "create", "imagine", "synthesize", "expand", "narrative",
    "story", "vision", "identity", "meaning", "symbol",
    "innovate", "explore", "dream", "inspire", "reframe",
    "what if", "emerge", "evolve", "integrate", "reflect",
]

BOTH_SIGNALS = [
    "strategy", "comprehensive", "full analysis", "complete",
    "both perspectives", "collapse and become", "sovereign",
]


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def route_task(task_data: Dict[str, Any]) -> str:
    """
    Determine which agent should handle a task.

    Returns: "sway", "opie", or "both"

    Priority:
      1. Explicit agent_assignment from human operator (always wins)
      2. Smart routing based on task content
      3. Default to sway (cheaper, execution-oriented)
    """
    explicit = task_data.get("agent_assignment", "").lower().strip()

    # 1. Explicit assignment always wins
    if explicit in ("outer", "sway", "opie", "both"):
        return explicit

    # 2. Smart routing — outer is the default front layer
    task_input = task_data.get("task_input", "").lower()
    return _smart_route(task_input)


def _smart_route(task_input: str) -> str:
    """Analyze task input and determine best agent."""
    sway_score = sum(1 for s in SWAY_SIGNALS if s in task_input)
    opie_score = sum(1 for s in OPIE_SIGNALS if s in task_input)
    both_score = sum(1 for s in BOTH_SIGNALS if s in task_input)

    if both_score > 0:
        return "both"
    if opie_score > sway_score:
        return "opie"
    if sway_score > 0:
        return "sway"
    # Default to outer (persistent front layer for general interaction)
    return "outer"


def format_routing_decision(
    task_data: Dict[str, Any], routed_to: str
) -> Dict[str, Any]:
    """Return a structured routing decision for logging."""
    return {
        "routed_to": routed_to,
        "explicit_assignment": task_data.get("agent_assignment", ""),
        "routing_method": (
            "explicit" if task_data.get("agent_assignment", "").lower() in ("outer", "sway", "opie", "both")
            else "smart"
        ),
        "task_preview": task_data.get("task_input", "")[:100],
    }
