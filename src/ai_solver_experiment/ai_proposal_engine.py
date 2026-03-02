"""
AI Proposal Engine — LLM-based VRP solution proposer.

Two modes:
  - uncalibrated: bare solving prompt
  - calibrated: ECP protocol injected before solving

Supports Anthropic (Claude), OpenAI, and Gemini backends.
Parses JSON route proposals from LLM output.
"""

import json
import os
import re
import time
from typing import Dict, Any, List, Optional

from .calibration_protocols import build_messages
from .vrp_instance import VRPInstance


# ── JSON Extraction ──────────────────────────────────────────────

def extract_json(raw: str) -> Optional[str]:
    """Extract the first JSON object from raw LLM output."""
    # Try to find JSON in code blocks first
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if m:
        return m.group(1)

    # Find first { ... } block
    depth = 0
    start = None
    for i, ch in enumerate(raw):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                return raw[start : i + 1]
    return None


def parse_routes(raw: str, n_customers: int) -> Optional[List[List[int]]]:
    """
    Parse route proposal from LLM output.
    Returns list of routes (each a list of 0-indexed customer IDs), or None.
    """
    json_str = extract_json(raw)
    if not json_str:
        return None

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return None

    routes = data.get("routes")
    if not isinstance(routes, list):
        return None

    # Validate: all entries are lists of ints
    parsed = []
    for route in routes:
        if not isinstance(route, list):
            return None
        int_route = []
        for c in route:
            if not isinstance(c, (int, float)):
                return None
            int_route.append(int(c))
        parsed.append(int_route)

    return parsed


# ── LLM Dispatch ─────────────────────────────────────────────────

def _call_anthropic(messages: list, model: str, max_tokens: int, temperature: float = 0.7) -> str:
    """Call Anthropic Claude API."""
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=api_key)

    # Anthropic uses system param separately
    system_msg = ""
    chat_msgs = []
    for m in messages:
        if m["role"] == "system":
            system_msg = m["content"]
        else:
            chat_msgs.append(m)

    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_msg,
        messages=chat_msgs,
        temperature=temperature,
    )
    return resp.content[0].text


def _call_openai(messages: list, model: str, max_tokens: int, temperature: float = 0.7) -> str:
    """Call OpenAI API."""
    import openai

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = openai.OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def _call_gemini(messages: list, model: str, max_tokens: int, temperature: float = 0.7) -> str:
    """Call Google Gemini API using the new google.genai library."""
    from google import genai
    from google.genai import types as gtypes

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY not set")

    client = genai.Client(api_key=api_key)
    model_name = model

    # Convert messages to Gemini contents format
    system_instruction = None
    contents = []
    for m in messages:
        if m["role"] == "system":
            system_instruction = m["content"]
        elif m["role"] == "user":
            contents.append(gtypes.Content(role="user", parts=[gtypes.Part(text=m["content"])]))
        elif m["role"] == "assistant":
            contents.append(gtypes.Content(role="model", parts=[gtypes.Part(text=m["content"])]))

    config = gtypes.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
        system_instruction=system_instruction,
    )

    # Retry with backoff for 429 rate limits
    backoff_delays = [10, 30, 60, 90, 120]
    last_err = None
    for attempt in range(len(backoff_delays) + 1):
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
            # Log finish reason for debugging truncation
            if resp.candidates:
                fr = resp.candidates[0].finish_reason
                if fr and "STOP" not in str(fr):
                    import sys
                    print(f"  [gemini] finish_reason={fr}", file=sys.stderr)
            return resp.text
        except Exception as e:
            last_err = e
            err_str = str(e)
            if "429" in err_str or "ResourceExhausted" in err_str:
                if attempt < len(backoff_delays):
                    delay = backoff_delays[attempt]
                    import sys
                    print(f"  [gemini] 429 rate limit, retry in {delay}s (attempt {attempt+1})", file=sys.stderr)
                    time.sleep(delay)
                    continue
            raise
    raise RuntimeError(f"Gemini failed after retries: {last_err}")


LLM_BACKENDS = {
    "anthropic": _call_anthropic,
    "openai": _call_openai,
    "gemini": _call_gemini,
}

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "gemini": "gemini-2.0-flash",
}


# ── Proposal Engine ──────────────────────────────────────────────

class AIProposalEngine:
    """
    LLM-based VRP solution proposer.

    Accepts a VRP instance, outputs candidate solutions.
    Two modes: uncalibrated and calibrated (ECP protocol injected).
    """

    def __init__(
        self,
        provider: str = "anthropic",
        model: str = None,
        max_tokens: int = 8192,
        pacing_delay: float = 1.0,
        temperature: float = 0.7,
    ):
        if provider not in LLM_BACKENDS:
            raise ValueError(f"Unknown provider: {provider}. Use: {list(LLM_BACKENDS)}")

        self.provider = provider
        self.model = model or DEFAULT_MODELS[provider]
        self.max_tokens = max_tokens
        self.pacing_delay = pacing_delay
        self.temperature = temperature
        self._call_fn = LLM_BACKENDS[provider]
        self.call_count = 0
        self.total_latency = 0.0

    def propose(
        self,
        instance: VRPInstance,
        iteration: int,
        feedback: str = "",
        calibrated: bool = False,
        conversation_history: list = None,
    ) -> Dict[str, Any]:
        """
        Generate a route proposal from the LLM.

        Returns:
            dict with keys: routes (or None), raw_response, latency_s,
                            parse_success, call_number
        """
        messages = build_messages(
            instance_json=instance.to_json_for_ai(),
            iteration=iteration,
            feedback=feedback,
            calibrated=calibrated,
            conversation_history=conversation_history,
            n_customers=instance.n_customers,
        )

        # Pacing
        if self.call_count > 0 and self.pacing_delay > 0:
            time.sleep(self.pacing_delay)

        self.call_count += 1
        call_num = self.call_count

        t0 = time.time()
        try:
            raw = self._call_fn(messages, self.model, self.max_tokens, self.temperature)
        except Exception as e:
            return {
                "routes": None,
                "raw_response": f"ERROR: {e}",
                "latency_s": time.time() - t0,
                "parse_success": False,
                "call_number": call_num,
                "error": str(e),
            }
        latency = time.time() - t0
        self.total_latency += latency

        routes = parse_routes(raw, instance.n_customers)

        return {
            "routes": routes,
            "raw_response": raw,
            "latency_s": latency,
            "parse_success": routes is not None,
            "call_number": call_num,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Return engine statistics."""
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "total_calls": self.call_count,
            "total_latency_s": self.total_latency,
            "avg_latency_s": self.total_latency / max(1, self.call_count),
        }
