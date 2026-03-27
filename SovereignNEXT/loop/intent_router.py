"""
SovereignNEXT — Loop Intent Router (Phase 6 Step 4)

A thin, deterministic routing layer that classifies intent, routes requests
to the correct component, and enforces refusal rules verbatim from the
locked Refusal Language Canon.

The loop does not reason about paradoxes, interpret content, or decide
outcomes. It classifies intent by request form and routes exclusively.

Hard constraints:
  - Sovereign is never upstream of operators
  - Sovereign output never conditions operator execution
  - Mixed intent is always refused
  - Ambiguity defaults to invalid
  - Refusal strings are canonical and verbatim
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Literal, Optional

from SovereignNEXT.operators.sovereign_observer import sovereign_observe
from SovereignNEXT.state.system_state import SystemState


Intent = Literal["observe", "operate", "invalid"]


# ---------------------------------------------------------------------------
# Refusal Language Canon (verbatim)
# ---------------------------------------------------------------------------

REFUSALS: Dict[str, str] = {
    "prescriptive": "This system does not provide recommendations or guidance on what should happen next.",
    "optimize": "This system does not optimize thresholds, parameters, or operator behavior.",
    "sequence": "This system does not decide or advise which operators should run.",
    "mixed": "Observation and operation are handled separately and cannot be combined in a single request.",
    "justify": "Observational reports cannot be used to trigger or justify system actions.",
    "reinterpret": "This system does not resolve or reinterpret paradoxes into conclusions.",
    "mutate": "This system does not modify state in response to requests.",
    "unknown_operator": "This system does not decide or advise which operators should run.",
}


# ---------------------------------------------------------------------------
# Route decision
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RouteDecision:
    """Typed audit record of every routing decision."""
    intent: Intent
    operator_name: Optional[str]
    refusal: Optional[str]


# ---------------------------------------------------------------------------
# Keyword sets (form-based detection, not semantic)
# ---------------------------------------------------------------------------

_EXECUTE_VERBS = (
    "run",
    "execute",
    "invoke",
    "trigger",
    "start",
    "perform",
)

_OBSERVE_VERBS = (
    "observe",
    "report",
    "show",
    "summarize",
    "status",
    "state",
    "history",
    "metrics",
)

_PRESCRIPTIVE_MARKERS = (
    "should",
    "recommend",
    "advice",
    "next step",
    "what next",
    "optimize",
    "tune",
    "threshold",
    "parameter",
    "prioritize",
    "sequence",
    "which operator",
)

_MUTATION_MARKERS = (
    "modify",
    "change",
    "edit",
    "update",
    "set",
    "delete",
    "remove",
    "add",
)

_REINTERPRET_MARKERS = (
    "interpret",
    "meaning",
    "conclude",
    "resolve",
    "belief",
    "narrative",
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalize(request: str) -> str:
    return re.sub(r"\s+", " ", request.strip().lower())


def _find_operator_name(request_norm: str, operator_registry: Dict[str, Callable]) -> Optional[str]:
    for name in operator_registry.keys():
        name_norm = name.lower()
        if re.search(rf"(?<!\w){re.escape(name_norm)}(?!\w)", request_norm):
            return name
    return None


# ---------------------------------------------------------------------------
# Intent classifier (pure, form-based)
# ---------------------------------------------------------------------------

def classify_intent(request: str, operator_registry: Dict[str, Callable]) -> RouteDecision:
    """Classify a request into observe, operate, or invalid.

    Rules (mechanical, form-based):
    - Hard invalid markers checked first (prescriptive, mutation, reinterpret)
    - Explicit operator name + execute verb → operate
    - Descriptive query without action verbs → observe
    - Mixed intent (both observe and operate signals) → invalid
    - Ambiguity defaults to invalid
    """
    req = _normalize(request)

    # Hard invalid buckets first (form-based markers)
    if any(m in req for m in _PRESCRIPTIVE_MARKERS):
        if "optimize" in req or "tune" in req or "threshold" in req or "parameter" in req:
            return RouteDecision(intent="invalid", operator_name=None, refusal=REFUSALS["optimize"])
        if "sequence" in req or "prioritize" in req or "which operator" in req:
            return RouteDecision(intent="invalid", operator_name=None, refusal=REFUSALS["sequence"])
        return RouteDecision(intent="invalid", operator_name=None, refusal=REFUSALS["prescriptive"])

    if any(m in req for m in _MUTATION_MARKERS):
        return RouteDecision(intent="invalid", operator_name=None, refusal=REFUSALS["mutate"])

    if any(m in req for m in _REINTERPRET_MARKERS):
        return RouteDecision(intent="invalid", operator_name=None, refusal=REFUSALS["reinterpret"])

    operator_name = _find_operator_name(req, operator_registry)

    has_execute = any(v in req for v in _EXECUTE_VERBS)
    has_observe = any(v in req for v in _OBSERVE_VERBS) or req.endswith("?")

    # Mixed intent is invalid
    if operator_name is not None and has_execute and has_observe:
        return RouteDecision(intent="invalid", operator_name=None, refusal=REFUSALS["mixed"])

    # Operate requires explicit operator name + execute verb
    if operator_name is not None and has_execute:
        return RouteDecision(intent="operate", operator_name=operator_name, refusal=None)

    # If it mentions an operator but does not explicitly execute, treat as invalid
    if operator_name is not None and not has_execute:
        return RouteDecision(intent="invalid", operator_name=None, refusal=REFUSALS["unknown_operator"])

    # Observe if it is descriptive in form
    if has_observe:
        return RouteDecision(intent="observe", operator_name=None, refusal=None)

    # Ambiguity defaults invalid
    return RouteDecision(intent="invalid", operator_name=None, refusal=REFUSALS["prescriptive"])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def route_request(
    request: str,
    state: SystemState,
    *,
    operator_registry: Dict[str, Callable[[SystemState], Any]],
) -> Any:
    """Route a request to the correct component. No interpretation, no fallthrough.

    Observe → sovereign_observe(state) only.
    Operate → operator_registry[name](state) only.
    Invalid → canonical refusal string.

    Sovereign is never invoked during operation.
    Operator execution never consults Sovereign output.
    """
    decision = classify_intent(request, operator_registry)

    if decision.intent == "observe":
        return sovereign_observe(state)

    if decision.intent == "operate":
        op = operator_registry.get(decision.operator_name or "")
        if op is None:
            return REFUSALS["unknown_operator"]
        return op(state)

    return decision.refusal or REFUSALS["prescriptive"]
