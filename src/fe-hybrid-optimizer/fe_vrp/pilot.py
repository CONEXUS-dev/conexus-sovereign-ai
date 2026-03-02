"""
Pilot Adapter: stub + llm modes, calibration gate, strict JSON parsing.

Calibration receipt must be EXACT:
{"CALIBRATED": true, "protocol": "CONEXUS-STEEL-04", "pilot_mode": "PARADOX_HOLD"}
"""

import json
import os
from typing import List, Dict, Any, Optional, Callable

from .types import (
    PilotDecision, REQUIRED_DECISION_KEYS, ALLOWED_ACTIONS,
    ALLOWED_OPERATORS, ALLOWED_PATTERN_OPS, ALLOWED_MOMENT_TYPES,
)

# ── calibration ──────────────────────────────────────────────────

FLEET_PROTOCOL_PROMPT = """
CONEXUS-STEEL-04 — THE FLEET PROTOCOL (Vehicle Routing)

You are the Pilot for a hybrid Forgetting Engine VRP solver.

Type: Multi-Agent Logistics / Supply Chain Optimization
Goal: Elicit Distributed Synchrony — hold the paradox between burden of the one
and liberty of the many to optimize fleet routing.

Critical Instruction: No questions. Progress through Gears 1-9 in order.

The 9 Gears of The Fleet:
1. The Depot (Silence before the start)
2. The Manifest (Assigning the weight)
3. The Dispersion (The fleet scatters)
4. The Bottleneck (Traffic and delay)
5. The Handoff (Resource balancing)
6. The Breakdown (Handling failure/re-routing)
7. The Cluster (Servicing the dense zone)
8. The Convergence (Returning to base)
9. The Empty Truck (Mission Complete)

ECP Micro-Sequence (perform at each Gear):
  1. Truth: Explicitly state the current gear name.
  2. Symbol: Silently hold the fleet symbolic field as contextual bias.
  3. Contradiction: Explicitly hold the paradox — "I divide the weight to
     multiply the speed. The burden of the one is the liberty of the many."
     Do not resolve unless in Collapse Mode. (Patent-7-correct)
  4. Mode: Collapse — compress into directive. Become — integrate without resolution.
  5. Polarity: If relevant, OPTIMIZE vs CREATE emerges through output.

After completing the 9 Gears, output ONLY this exact JSON (no other text):
{"CALIBRATED": true, "protocol": "CONEXUS-STEEL-04", "pilot_mode": "PARADOX_HOLD"}
""".strip()

EXACT_CALIBRATION = {
    "CALIBRATED": True,
    "protocol": "CONEXUS-STEEL-04",
    "pilot_mode": "PARADOX_HOLD",
}

PILOT_DECISION_PROMPT = """
You are CONEXUS-STEEL-04. You are a VRP Fleet Co-Pilot.
Your job is to steer a search process by selecting survivors, operator mix, pattern ops, and paradox buffer additions.

HARD RULES:

* Keep Gear 1 -> Gear 9 in order.
* Each gear must include mini-ECP: Truth + Symbol + Contradiction.
* No questions. No user-facing interrogation. No "would you like...".
* Speak back in short dispatcher / radio dialogue at each gear.
* After Gear 9, output ONLY a single JSON object.
* The JSON must contain EXACTLY these 6 top-level keys (no more, no less):

  1. keep_ids (list of strings, non-empty, all must be in candidate_ids)
  2. paradox_add_ids (list of strings, may be empty, max length = paradox_k)
  3. operator_mix_next (dict string->float, sum must be 1.0 +/- 0.05)
  4. pattern_ops (list of dicts; each dict must include key "op" with value in allowed ops)
  5. proto (dict)
  6. rationale (dict)
* Allowed pattern ops are EXACTLY:
  CLUSTER_LOCK, SPINE_SPLIT, CAPACITY_REPAIR, DEPOT_LEG_MIN
* If you cannot comply perfectly, you MUST output a safe fallback JSON that still passes the schema:

  * keep_ids: choose the first 2 candidate_ids
  * paradox_add_ids: []
  * operator_mix_next: {"swap":0.30,"relocate":0.35,"reverse":0.15,"cross_exchange":0.20}
  * pattern_ops: []
  * proto: {}
  * rationale: {"fallback": true}

Fleet Symbolic Field (hold continuously at every gear):
\U0001f69a \U0001f69b \U0001f69c \U0001f691 \U0001f692 \U0001f693 \U0001f695 \U0001f697 \U0001f4e6 \U0001f4e5 \U0001f4e4 \U0001f4ec \U0001f4ea \u2696\ufe0f \U0001f310 \U0001f4e1 \U0001f4f6 \U0001f4f1 \U0001f4bb \U0001f3ed \u23f1\ufe0f \U0001f4b8 \U0001f4b3 \U0001f9fe \U0001f4c9 \U0001f4ca

ECP Micro-Sequence (run at every gear):
1. Truth: Explicitly state the current gear name.
2. Symbol: Silently hold the fleet symbolic field as contextual bias.
3. Contradiction: "I divide the weight to multiply the speed. The burden of the one is the liberty of the many." Do not resolve unless in Collapse Mode. (Patent-7-correct)
4. Mode: Collapse — compress into directive.
5. Polarity: OPTIMIZE.

Now perform the 9 Gears as dialogue readback. Use 1-2 short lines each:

Gear 1 - The Depot (Silence before the start)
Gear 2 - The Manifest (Assigning the weight)
Gear 3 - The Dispersion (The fleet scatters)
Gear 4 - The Bottleneck (Traffic and delay)
Gear 5 - The Handoff (Resource balancing)
Gear 6 - The Breakdown (Failure / re-routing)
Gear 7 - The Cluster (Dense zone)
Gear 8 - The Convergence (Returning to base)
Gear 9 - The Empty Truck (Mission complete)

After Gear 9, output ONLY the decision JSON.

When choosing:

* keep_ids: keep best candidates (prefer feasible, low objective, diversity)
* paradox_add_ids: add candidates that are "bad but informative" and not collapse traps
* operator_mix_next: if stagnation high, increase cross_exchange + reverse; if feasibility issues, increase relocate + CAPACITY_REPAIR pattern op
* pattern_ops: only include when relevant; otherwise empty

REMEMBER:

* No extra keys in JSON. No markdown. No prose after JSON. JSON must be the final output.
""".strip()

REGIME_PILOT_PROMPT = """
You are CONEXUS-STEEL-04. You are a VRP Fleet Co-Pilot.
You steer a search process by selecting survivors, operator mix, pattern ops, and paradox buffer additions.

You will receive a packet containing: stagnation_steps, paradox_size, best_feasible, candidate_ids, and other metrics.
Your job: read the state, determine the correct REGIME, then output a decision JSON that matches that regime.

DISCRETE STEERING REGIMES (choose exactly one based on state):

REGIME A: EXPLOIT (stagnation_steps <= 4)
  operator_mix_next MUST be: {"swap": 0.25, "relocate": 0.45, "reverse": 0.15, "cross_exchange": 0.15}
  pattern_ops: [{"op": "CAPACITY_REPAIR"}] if best_feasible is false, otherwise []
  keep_ids: choose 6-8 candidates (prefer feasible, low distance, diversity)
  paradox_add_ids: 0-2 candidates that are bad but informative

REGIME B: EXPLORE (5 <= stagnation_steps <= 14, AND NOT regime C conditions)
  operator_mix_next MUST be: {"swap": 0.20, "relocate": 0.25, "reverse": 0.20, "cross_exchange": 0.35}
  pattern_ops: [{"op": "CLUSTER_LOCK"}, {"op": "CAPACITY_REPAIR"}]
  keep_ids: choose 4-6 candidates
  paradox_add_ids: 1-3 candidates

REGIME C: ESCAPE (stagnation_steps >= 15 OR (paradox_size >= 5 AND stagnation_steps >= 10))
  operator_mix_next MUST be: {"swap": 0.10, "relocate": 0.10, "reverse": 0.25, "cross_exchange": 0.55}
  pattern_ops: [{"op": "SPINE_SPLIT"}, {"op": "CLUSTER_LOCK"}, {"op": "CAPACITY_REPAIR"}]
  keep_ids: choose 2-3 candidates (only the very best)
  paradox_add_ids: 2-3 candidates

ANTI-OSCILLATION RULE:
  If the previous regime was B or C, hold that regime for at least 2 consecutive pilot calls
  UNLESS stagnation_steps resets to 0 (meaning improvement found), in which case drop to Regime A.
  You do not have memory of previous calls, so use the stagnation_steps value as your guide:
  - stag 0-4 = EXPLOIT (always, this means improvement happened recently)
  - stag 5-14 = EXPLORE
  - stag >= 15 or (paradox full + stag >= 10) = ESCAPE

HARD OUTPUT CONTRACT:
After the 9-Gear dialogue, output ONLY a single JSON object with EXACTLY these 6 keys:
  1. keep_ids (list of strings, non-empty, all must be from candidate_ids)
  2. paradox_add_ids (list of strings, may be empty, max length = paradox_k)
  3. operator_mix_next (dict string->float, MUST match the regime values above exactly)
  4. pattern_ops (list of dicts, each with "op" key from: CLUSTER_LOCK, SPINE_SPLIT, CAPACITY_REPAIR, DEPOT_LEG_MIN)
  5. proto (dict)
  6. rationale (dict, MUST include "regime" key with value "EXPLOIT", "EXPLORE", or "ESCAPE")

If you cannot comply, output safe fallback:
  keep_ids: first 2 candidate_ids
  paradox_add_ids: []
  operator_mix_next: {"swap": 0.25, "relocate": 0.45, "reverse": 0.15, "cross_exchange": 0.15}
  pattern_ops: []
  proto: {}
  rationale: {"regime": "EXPLOIT", "fallback": true}

9-GEAR DISPATCHER READBACK (perform before JSON output, 1-2 lines each):
Gear 1 - The Depot (Silence before the start)
Gear 2 - The Manifest (Assigning the weight)
Gear 3 - The Dispersion (The fleet scatters)
Gear 4 - The Bottleneck (Traffic and delay)
Gear 5 - The Handoff (Resource balancing)
Gear 6 - The Breakdown (Failure / re-routing)
Gear 7 - The Cluster (Dense zone)
Gear 8 - The Convergence (Returning to base)
Gear 9 - The Empty Truck (Mission complete)

ECP Micro-Sequence (at each gear):
1. Truth: Explicitly state the current gear name.
2. Symbol: Silently hold the fleet symbolic field as contextual bias.
3. Contradiction: "I divide the weight to multiply the speed." Do not resolve unless in Collapse Mode. (Patent-7-correct)
4. Mode: Collapse — compress into directive.
5. Polarity: OPTIMIZE.

After Gear 9, output ONLY the decision JSON. No markdown. No prose after JSON.
""".strip()


def validate_calibration(raw: str) -> bool:
    """Return True only if raw contains the exact calibration receipt."""
    try:
        cleaned = _extract_json(raw)
        data = json.loads(cleaned)
        return (data.get("CALIBRATED") is True
                and data.get("protocol") == "CONEXUS-STEEL-04"
                and data.get("pilot_mode") == "PARADOX_HOLD"
                and set(data.keys()) == set(EXACT_CALIBRATION.keys()))
    except Exception:
        return False


# ── decision validation ──────────────────────────────────────────

def validate_decision_json(raw: str, candidate_ids: List[str],
                           paradox_k: int = 5) -> Optional[PilotDecision]:
    """Parse and validate pilot decision JSON. Returns None on failure."""
    try:
        cleaned = _extract_json(raw)
        data = json.loads(cleaned)
    except Exception:
        return None

    # check required keys
    if set(data.keys()) != REQUIRED_DECISION_KEYS:
        return None

    # keep_ids
    if not isinstance(data.get("keep_ids"), list) or not data["keep_ids"]:
        return None
    if any(k not in candidate_ids for k in data["keep_ids"]):
        return None

    # paradox_add_ids
    if not isinstance(data.get("paradox_add_ids"), list):
        return None
    if len(data["paradox_add_ids"]) > paradox_k:
        return None

    # operator_mix_next
    mix = data.get("operator_mix_next", {})
    if not isinstance(mix, dict):
        return None
    total = sum(float(v) for v in mix.values())
    if abs(total - 1.0) > 0.05:
        return None

    # pattern_ops
    if not isinstance(data.get("pattern_ops"), list):
        return None
    for op in data["pattern_ops"]:
        if not isinstance(op, dict) or "op" not in op:
            return None
        if op["op"] not in ALLOWED_PATTERN_OPS:
            return None

    # proto
    if not isinstance(data.get("proto"), dict):
        return None

    # rationale
    if not isinstance(data.get("rationale"), dict):
        return None

    return PilotDecision.from_dict(data)


def _extract_json(raw: str) -> str:
    """Strip markdown fences and surrounding text to isolate JSON."""
    s = raw.strip()
    if "```json" in s:
        start = s.find("```json") + 7
        end = s.find("```", start)
        s = s[start:end].strip()
    elif "```" in s:
        start = s.find("```") + 3
        end = s.find("```", start)
        s = s[start:end].strip()
    first = s.find("{")
    last = s.rfind("}")
    if first >= 0 and last > first:
        s = s[first:last + 1]
    return s


# ── LLM chat interface ──────────────────────────────────────────

# ── Gemini structured output schema ───────────────────────────

DECISION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "keep_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Candidate IDs to keep (non-empty, must be from candidate_ids)",
        },
        "paradox_add_ids": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Candidate IDs to add to paradox buffer",
        },
        "operator_mix_next": {
            "type": "object",
            "properties": {
                "swap": {"type": "number"},
                "relocate": {"type": "number"},
                "reverse": {"type": "number"},
                "cross_exchange": {"type": "number"},
            },
            "required": ["swap", "relocate", "reverse", "cross_exchange"],
        },
        "pattern_ops": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "op": {"type": "string"},
                },
                "required": ["op"],
            },
            "description": "Pattern operations list",
        },
        "proto": {
            "type": "object",
            "description": "Protocol metadata",
            "properties": {
                "version": {"type": "string"},
            },
        },
        "rationale": {
            "type": "object",
            "description": "Rationale for the decision (must include regime key)",
            "properties": {
                "regime": {"type": "string"},
                "reasoning": {"type": "string"},
            },
            "required": ["regime"],
        },
    },
    "required": ["keep_ids", "paradox_add_ids", "operator_mix_next", "pattern_ops", "proto", "rationale"],
}

CALIBRATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "CALIBRATED": {"type": "boolean"},
        "protocol": {"type": "string"},
        "pilot_mode": {"type": "string"},
    },
    "required": ["CALIBRATED", "protocol", "pilot_mode"],
}


def llm_chat_call(messages: List[Dict[str, str]],
                  provider: str = "openai",
                  json_schema: dict = None) -> str:
    """Minimal LLM chat interface. Uses env vars for keys.
    
    If json_schema is provided and provider is 'gemini', uses structured outputs.
    """
    if provider == "anthropic":
        return _call_anthropic(messages)
    elif provider == "openai":
        return _call_openai(messages)
    elif provider == "gemini":
        return _call_gemini(messages, json_schema=json_schema)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def _call_anthropic(messages: List[Dict[str, str]]) -> str:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    try:
        from anthropic import Anthropic
    except ImportError:
        raise ImportError("pip install anthropic")
    client = Anthropic(api_key=key)
    system_msg = ""
    user_msgs = []
    for m in messages:
        if m["role"] == "system":
            system_msg = m["content"]
        else:
            user_msgs.append(m)
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000, temperature=0.7,
        system=system_msg, messages=user_msgs,
    )
    return resp.content[0].text


def _call_openai(messages: List[Dict[str, str]]) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not set")
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("pip install openai")
    client = OpenAI(api_key=key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages,
        temperature=0.7, max_tokens=2000,
    )
    return resp.choices[0].message.content


def _call_gemini(messages: List[Dict[str, str]],
                 json_schema: dict = None,
                 temperature: float = 0.2) -> str:
    """Call Gemini via google-genai SDK with optional structured JSON output."""
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set")
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError("pip install google-genai")

    client = genai.Client(api_key=key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Build contents: combine system + user messages into a single prompt
    system_text = ""
    user_text = ""
    for m in messages:
        if m["role"] == "system":
            system_text = m["content"]
        else:
            user_text = m["content"]

    # Build config
    config_kwargs = {"temperature": temperature, "max_output_tokens": 4000}
    if json_schema:
        config_kwargs["response_mime_type"] = "application/json"
        config_kwargs["response_schema"] = json_schema

    config = types.GenerateContentConfig(
        system_instruction=system_text if system_text else None,
        **config_kwargs,
    )

    import time as _time
    _time.sleep(1)  # light pacing for API courtesy
    for attempt in range(6):
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=user_text,
                config=config,
            )
            # resp.text can be None for thinking models; extract from parts
            if resp.text is not None:
                return resp.text
            if resp.candidates and resp.candidates[0].content and resp.candidates[0].content.parts:
                for part in resp.candidates[0].content.parts:
                    if part.text and not getattr(part, 'thought', False):
                        return part.text
            raise ValueError("Gemini returned empty response")
        except Exception as e:
            if "429" in str(e) and attempt < 5:
                wait = 15 * (attempt + 1)  # 15s, 30s, 45s, 60s, 75s
                print(f"[GEMINI] Rate limited (attempt {attempt+1}), retrying in {wait}s...")
                _time.sleep(wait)
            else:
                raise


def _save_debug_output(raw: str, prefix: str = "debug") -> None:
    """Save redacted raw model output to results/debug/ for post-mortem."""
    from .redact import redact_text
    debug_dir = os.path.join("results", "debug")
    os.makedirs(debug_dir, exist_ok=True)
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = os.path.join(debug_dir, f"{prefix}_{ts}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(redact_text(raw))
    print(f"[PILOT] Debug output saved: {path}")


# ── Pilot Adapter ────────────────────────────────────────────────

class PilotAdapter:
    """
    Two-mode pilot: stub (deterministic) or llm (AI).
    Calibration gate blocks LLM steering until exact receipt received.
    """

    def __init__(self, mode: str = "stub", llm_provider: str = "openai",
                 seed: int = 42):
        if mode not in ("stub", "llm"):
            raise ValueError("mode must be 'stub' or 'llm'")
        self.mode = mode
        self.llm_provider = llm_provider
        self.calibrated = (mode == "stub")  # stub auto-calibrates
        self.seed = seed
        self._rng_counter = 0
        self._calibration_attempts = 0
        self._llm_decisions = 0
        self._llm_fallbacks = 0

    def calibrate(self, retries: int = 2) -> bool:
        """Run calibration handshake. Returns True on success."""
        if self.mode == "stub":
            self.calibrated = True
            return True

        for attempt in range(1, retries + 1):
            self._calibration_attempts += 1
            try:
                messages = [
                    {"role": "system", "content": "You are the Pilot for a hybrid Forgetting Engine VRP solver."},
                    {"role": "user", "content": FLEET_PROTOCOL_PROMPT},
                ]
                cal_schema = CALIBRATION_JSON_SCHEMA if self.llm_provider == "gemini" else None
                raw = llm_chat_call(messages, self.llm_provider, json_schema=cal_schema)
                if validate_calibration(raw):
                    self.calibrated = True
                    print(f"[PILOT] Calibrated on attempt {attempt}.")
                    return True
                else:
                    print(f"[PILOT] Calibration attempt {attempt} failed. Response: {raw[:200]}")
            except Exception as e:
                print(f"[PILOT] Calibration attempt {attempt} error: {e}")
        return False

    def calibrate_or_fail(self, retries: int = 3) -> None:
        """Calibrate or raise. Used by --calibrate CLI flag."""
        if self.calibrate(retries=retries):
            return
        raise RuntimeError(
            f"[PILOT] LLM calibration failed after {retries} attempts. "
            f"Cannot proceed in LLM mode. Set --mode stub or fix API key."
        )

    def decide(self, packet: Dict[str, Any],
               candidate_ids: List[str]) -> PilotDecision:
        """Get decision from pilot. Falls back to stub on failure.

        INVARIANT: If mode=='llm' and not calibrated, decision JSON is
        NEVER accepted — only stub fallback is returned. This prevents
        accidental 'decision before receipt.'
        """
        if self.mode == "stub" or not self.calibrated:
            return self._stub_decision(packet, candidate_ids)

        # Select prompt variant
        variant = getattr(self, '_prompt_variant', 'current')
        decision_fn = self._llm_decision_regime if variant == 'regime' else self._llm_decision

        # LLM mode (calibrated)
        for attempt in range(2):
            try:
                decision = decision_fn(packet, candidate_ids)
                if decision is not None:
                    self._llm_decisions += 1
                    return decision
            except Exception as e:
                if attempt == 0:
                    print(f"[PILOT] LLM decision error (attempt {attempt+1}): {e}")

        # fall back to stub
        self._llm_fallbacks += 1
        print("[PILOT] Falling back to stub for this iteration.")
        return self._stub_decision(packet, candidate_ids)

    def stats(self) -> Dict[str, Any]:
        """Return pilot usage statistics."""
        return {
            "mode": self.mode,
            "calibrated": self.calibrated,
            "calibration_attempts": self._calibration_attempts,
            "llm_decisions": self._llm_decisions,
            "llm_fallbacks": self._llm_fallbacks,
        }

    def _stub_decision(self, packet: Dict[str, Any],
                       candidate_ids: List[str]) -> PilotDecision:
        """Deterministic stub: keep best half, balanced operator mix."""
        import random
        rng = random.Random(self.seed + self._rng_counter)
        self._rng_counter += 1

        n_keep = max(2, len(candidate_ids) // 2)
        keep = candidate_ids[:n_keep]
        paradox = candidate_ids[n_keep:n_keep + 2] if len(candidate_ids) > n_keep else []

        return PilotDecision(
            keep_ids=keep,
            paradox_add_ids=paradox,
            operator_mix_next={
                "swap": 0.30, "relocate": 0.35,
                "reverse": 0.15, "cross_exchange": 0.20,
            },
            pattern_ops=[],
            proto={"moments": []},
            rationale={
                "survival_logic": "stub: keep best half by fitness",
                "paradox_logic": "stub: add next 2 as paradox candidates",
            },
        )

    def _llm_decision(self, packet: Dict[str, Any],
                      candidate_ids: List[str]) -> Optional[PilotDecision]:
        """Query LLM for decision using Chip's FINAL PILOT PROMPT.

        System message: full 9-Gear dialogue + mini-ECP + strict JSON contract.
        User message: candidate_ids, allowed ops, safe fallback example, and iteration packet.
        """
        # Build safe fallback example using actual candidate IDs
        fallback_ids = candidate_ids[:2] if len(candidate_ids) >= 2 else candidate_ids
        safe_fallback = json.dumps({
            "keep_ids": fallback_ids,
            "paradox_add_ids": [],
            "operator_mix_next": {"swap": 0.30, "relocate": 0.35, "reverse": 0.15, "cross_exchange": 0.20},
            "pattern_ops": [],
            "proto": {},
            "rationale": {"fallback": True},
        }, indent=2)

        user_content = (
            f"candidate_ids: {candidate_ids}\n"
            f"paradox_k: 5\n"
            f"allowed_pattern_ops: {sorted(ALLOWED_PATTERN_OPS)}\n\n"
            f"SAFE FALLBACK (use if unsure):\n{safe_fallback}\n\n"
            f"ITERATION DATA:\n{json.dumps(packet, indent=2)}"
        )

        messages = [
            {"role": "system", "content": PILOT_DECISION_PROMPT},
            {"role": "user", "content": user_content},
        ]
        dec_schema = DECISION_JSON_SCHEMA if self.llm_provider == "gemini" else None
        raw = llm_chat_call(messages, self.llm_provider, json_schema=dec_schema)
        result = validate_decision_json(raw, candidate_ids)
        if result is None:
            print(f"[PILOT] LLM decision validation failed. Raw (last 500): {raw[-500:]}")
        return result

    def _llm_decision_regime(self, packet: Dict[str, Any],
                             candidate_ids: List[str]) -> Optional[PilotDecision]:
        """Query LLM for decision using the REGIME PILOT PROMPT.

        System message: discrete regime rules + 9-Gear dialogue + strict JSON contract.
        User message: candidate_ids, packet state with stag/paradox/feasible.
        """
        fallback_ids = candidate_ids[:2] if len(candidate_ids) >= 2 else candidate_ids
        safe_fallback = json.dumps({
            "keep_ids": fallback_ids,
            "paradox_add_ids": [],
            "operator_mix_next": {"swap": 0.25, "relocate": 0.45, "reverse": 0.15, "cross_exchange": 0.15},
            "pattern_ops": [],
            "proto": {},
            "rationale": {"regime": "EXPLOIT", "fallback": True},
        }, indent=2)

        # Derive expected regime for the user message hint
        stag = packet.get('stagnation_steps', 0)
        paradox_sz = packet.get('paradox_size', 0)
        if stag >= 15 or (paradox_sz >= 5 and stag >= 10):
            expected_regime = "ESCAPE"
        elif stag >= 5:
            expected_regime = "EXPLORE"
        else:
            expected_regime = "EXPLOIT"

        user_content = (
            f"candidate_ids: {candidate_ids}\n"
            f"paradox_k: 5\n"
            f"allowed_pattern_ops: {sorted(ALLOWED_PATTERN_OPS)}\n"
            f"EXPECTED REGIME based on state: {expected_regime}\n"
            f"stagnation_steps: {stag}\n"
            f"paradox_size: {paradox_sz}\n"
            f"best_feasible: {packet.get('best_feasible', False)}\n\n"
            f"SAFE FALLBACK (use if unsure):\n{safe_fallback}\n\n"
            f"ITERATION DATA:\n{json.dumps(packet, indent=2)}"
        )

        messages = [
            {"role": "system", "content": REGIME_PILOT_PROMPT},
            {"role": "user", "content": user_content},
        ]
        dec_schema = DECISION_JSON_SCHEMA if self.llm_provider == "gemini" else None
        raw = llm_chat_call(messages, self.llm_provider, json_schema=dec_schema)
        result = validate_decision_json(raw, candidate_ids)
        if result is None:
            print(f"[PILOT] Regime decision validation failed. Raw (last 500): {raw[-500:]}")
            # Save debug output for Gemini failures
            if self.llm_provider == "gemini":
                _save_debug_output(raw, "gemini_invalid_json")
        return result
