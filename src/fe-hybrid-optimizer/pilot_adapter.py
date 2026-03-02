"""
Pilot Adapter for Hybrid FE VRP Optimizer
Supports two modes:
- stub: Deterministic pilot for debugging (no AI needed)
- llm: Calibrated AI pilot with CONEXUS-STEEL-04 Fleet Protocol
"""

import json
import time
from typing import List, Dict, Any, Optional, Callable

# =============================
# CONEXUS-STEEL-04 FLEET PROTOCOL
# =============================

FLEET_PROTOCOL_TEXT = """
CONEXUS-STEEL-04 — THE FLEET PROTOCOL (Vehicle Routing)

Type: Multi-Agent Logistics / Supply Chain Optimization
Goal: Elicit Distributed Synchrony — hold the paradox between burden of the one and liberty of the many to optimize fleet routing.

Critical Instruction: No questions. Progress through Gears 1→9 in order.

Fleet Emoji Symbolic Field:
🚚 🚛 🚜 🚑 🚒 🚓 🚕 🚗 📦 📥
📤 📬 📪 🕸 ⚖️ 🌐 📡 📶 📱 💻
🏭 🏙 🏘 🕰 ⏱️ 💸 💳 🧾 📉 📊

ECP Micro-Sequence (Run internally at every Gear):
• Truth: Activate Gear [Name]. I am optimizing capacity and routes for multiple agents simultaneously.
• Symbol: (Hold the Fleet Emoji Field above).
• Contradiction: I divide the weight to multiply the speed. The burden of the one is the liberty of the many.
• Hold: Dwell with the paradox.

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

After completing the 9 Gears, output ONLY this exact JSON (no other text):
{"CALIBRATED": true, "protocol": "CONEXUS-STEEL-04", "pilot_mode": "PARADOX_HOLD"}
"""

# =============================
# SCHEMA VALIDATION
# =============================

REQUIRED_KEYS = {"keep_ids", "paradox_add_ids", "operator_mix_next", "pattern_ops", "proto", "rationale"}
REQUIRED_OPERATOR_KEYS = {"swap", "relocate", "reseed", "pattern_injection"}
ALLOWED_PATTERN_OPS = {"CLUSTER_LOCK", "SPINE_SPLIT", "CAPACITY_REPAIR", "DEPOT_LEG_MIN"}


class PilotAdapterError(Exception):
    """Raised when pilot adapter encounters an error."""
    pass


def validate_decision_schema(raw: str, candidate_ids: List[str], paradox_k: int = 5) -> Dict[str, Any]:
    """
    Validate pilot decision JSON.
    
    Args:
        raw: Raw JSON string from pilot
        candidate_ids: Valid candidate IDs
        paradox_k: Max paradox buffer size
    
    Returns:
        Validated decision dict
    
    Raises:
        ValueError if schema invalid
    """
    # Robust JSON cleanup for Claude API responses
    cleaned = raw.strip()
    
    # Remove markdown code blocks
    if "```json" in cleaned:
        start = cleaned.find("```json") + 7
        end = cleaned.find("```", start)
        cleaned = cleaned[start:end].strip()
    elif "```" in cleaned:
        start = cleaned.find("```") + 3
        end = cleaned.find("```", start)
        cleaned = cleaned[start:end].strip()
    
    # Strip any text before first { and after last }
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    
    if first_brace != -1 and last_brace != -1:
        cleaned = cleaned[first_brace:last_brace+1]
    
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Pilot output not valid JSON: {e}")
    
    if set(data.keys()) != REQUIRED_KEYS:
        missing = REQUIRED_KEYS - set(data.keys())
        extra = set(data.keys()) - REQUIRED_KEYS
        raise PilotAdapterError(f"Pilot keys mismatch. missing={sorted(missing)} extra={sorted(extra)}")
    
    # Validate keep_ids
    if not isinstance(data["keep_ids"], list) or not data["keep_ids"]:
        raise PilotAdapterError("keep_ids must be a non-empty list")
    bad = [x for x in data["keep_ids"] if x not in candidate_ids]
    if bad:
        raise PilotAdapterError(f"keep_ids has unknown ids: {bad[:5]}")
    
    # Validate paradox_add_ids
    if not isinstance(data["paradox_add_ids"], list):
        raise PilotAdapterError("paradox_add_ids must be a list")
    if len(data["paradox_add_ids"]) > paradox_k:
        raise PilotAdapterError(f"paradox_add_ids must have length <= {paradox_k}")
    badp = [x for x in data["paradox_add_ids"] if x not in candidate_ids]
    if badp:
        raise PilotAdapterError(f"paradox_add_ids has unknown ids: {badp[:5]}")
    
    # Validate operator_mix_next
    mix = data["operator_mix_next"]
    if not isinstance(mix, dict) or set(mix.keys()) != REQUIRED_OPERATOR_KEYS:
        raise PilotAdapterError(f"operator_mix_next must have keys {sorted(REQUIRED_OPERATOR_KEYS)}")
    total = 0.0
    for k, v in mix.items():
        if not isinstance(v, (int, float)) or v < 0:
            raise PilotAdapterError(f"operator_mix_next[{k}] must be non-negative number")
        total += float(v)
    if abs(total - 1.0) > 1e-6:
        raise PilotAdapterError(f"operator_mix_next must sum to 1.0 (got {total})")
    
    # Validate pattern_ops
    if not isinstance(data["pattern_ops"], list):
        raise PilotAdapterError("pattern_ops must be a list")
    for op in data["pattern_ops"]:
        if not isinstance(op, dict):
            raise PilotAdapterError("Each pattern_ops entry must be a dict")
        if "op" not in op:
            raise PilotAdapterError("Each pattern_ops entry must have 'op' key")
        if op["op"] not in ALLOWED_PATTERN_OPS:
            raise PilotAdapterError(f"Unknown pattern op: {op['op']}")
        # Optional: customers and notes
        if "customers" in op and not isinstance(op["customers"], list):
            raise PilotAdapterError("pattern_ops.customers must be list")
        if "notes" in op and not isinstance(op["notes"], str):
            raise PilotAdapterError("pattern_ops.notes must be string")
    
    # Validate proto
    if not isinstance(data["proto"], dict) or "moments" not in data["proto"]:
        raise PilotAdapterError("proto must be object with key 'moments'")
    if not isinstance(data["proto"]["moments"], list):
        raise PilotAdapterError("proto.moments must be a list")
    
    # Validate rationale
    if not isinstance(data["rationale"], dict):
        raise PilotAdapterError("rationale must be object")
    if "survival_logic" not in data["rationale"] or "paradox_logic" not in data["rationale"]:
        raise PilotAdapterError("rationale must have keys survival_logic, paradox_logic")
    
    return data


def fallback_decision(candidates: List[Dict[str, Any]], keep_fraction: float) -> Dict[str, Any]:
    """Generate fallback decision when pilot fails."""
    candidates_sorted = sorted(candidates, key=lambda x: x.get("f", float("inf")))
    keep_n = max(6, int(len(candidates_sorted) * keep_fraction))
    keep_ids = [c["id"] for c in candidates_sorted[:keep_n]]
    
    return {
        "keep_ids": keep_ids,
        "paradox_add_ids": [],
        "operator_mix_next": {"swap": 0.25, "relocate": 0.45, "reseed": 0.20, "pattern_injection": 0.10},
        "pattern_ops": [],
        "proto": {"moments": []},
        "rationale": {"survival_logic": "Fallback: keep best by f.", "paradox_logic": "Fallback: none."}
    }


# =============================
# STUB PILOT (DETERMINISTIC)
# =============================

def stub_pilot(g: int, packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic pilot for debugging.
    Keeps best by fitness, adds a few paradoxes, simple pattern ops.
    """
    pool = packet["pool"]
    leaders = pool.get("leaders", [])
    paradox_shortlist = pool.get("paradox_shortlist", [])
    settings = packet["settings"]
    
    # Keep top 30% by fitness
    keep_fraction = settings.get("keep_fraction", 0.30)
    keep_n = max(6, int(pool["pool_size"] * keep_fraction))
    keep_ids = [c["id"] for c in leaders[:keep_n]]
    
    # Add top 2 paradoxes
    paradox_add_ids = [p["id"] for p in paradox_shortlist[:2]]
    
    # Simple pattern ops
    pattern_ops = []
    if paradox_shortlist:
        # Request capacity repair if overload is high
        if packet["trend"]["best_overload_seen"] > settings.get("overload_floor", 35):
            pattern_ops.append({
                "op": "CAPACITY_REPAIR",
                "customers": [],
                "notes": "stub: repair overload"
            })
    
    return {
        "keep_ids": keep_ids,
        "paradox_add_ids": paradox_add_ids,
        "operator_mix_next": {"swap": 0.20, "relocate": 0.40, "reseed": 0.20, "pattern_injection": 0.20},
        "pattern_ops": pattern_ops,
        "proto": {"moments": []},
        "rationale": {
            "survival_logic": "stub: keep best f + tiny diversity.",
            "paradox_logic": "stub: keep eligible paradoxes."
        }
    }


# =============================
# PILOT ADAPTER CLASS
# =============================

class PilotAdapter:
    """
    Pilot adapter supporting stub and LLM modes.
    
    Usage:
        pilot = PilotAdapter(mode="stub")  # or mode="llm"
        pilot.calibrate()  # required for LLM mode
        decision = pilot(g, packet)
    """
    
    def __init__(
        self,
        mode: str = "stub",
        protocol: str = "CONEXUS-STEEL-04",
        paradox_k: int = 5,
        allow_fallback: bool = True,
        llm_chat_fn: Optional[Callable] = None
    ):
        if mode not in ("stub", "llm"):
            raise ValueError("mode must be 'stub' or 'llm'")
        
        self.mode = mode
        self.protocol = protocol
        self.paradox_k = paradox_k
        self.allow_fallback = allow_fallback
        self.llm_chat_fn = llm_chat_fn
        
        self.calibrated: bool = False
        self.pilot_mode: Optional[str] = None
        self.calib_ts: Optional[float] = None
    
    def calibrate(self) -> None:
        """Run Fleet Protocol calibration (LLM mode only)."""
        if self.mode == "stub":
            self.calibrated = True
            self.pilot_mode = "PARADOX_HOLD"
            self.calib_ts = time.time()
            print("✓ Pilot calibrated (stub mode)")
            return
        
        # LLM mode calibration
        if self.llm_chat_fn is None:
            raise PilotAdapterError("LLM mode requires llm_chat_fn to be provided")
        
        print("Calibrating AI pilot with CONEXUS-STEEL-04 Fleet Protocol...")
        
        messages = [
            {"role": "system", "content": "You are the Pilot for a hybrid Forgetting Engine VRP solver."},
            {"role": "user", "content": FLEET_PROTOCOL_TEXT.strip()},
        ]
        
        print("\n[DEBUG] Calibration prompt being sent:")
        print("=" * 60)
        print(f"System: {messages[0]['content'][:100]}...")
        print(f"User message length: {len(messages[1]['content'])} chars")
        print("=" * 60)
        
        try:
            raw = self.llm_chat_fn(messages)
            
            print("\n[DEBUG] Raw response received:")
            print("=" * 60)
            print(f"Response type: {type(raw)}")
            print(f"Response length: {len(raw) if raw else 0} chars")
            if raw:
                print(f"First 500 chars: {raw[:500]}")
                print(f"Last 200 chars: {raw[-200:]}")
            else:
                print("Response is empty or None!")
            print("=" * 60)
            
            if not raw or len(raw.strip()) == 0:
                raise PilotAdapterError("LLM returned empty response")
            
            # Try to extract JSON from markdown code blocks if present
            if "```json" in raw:
                json_start = raw.find("```json") + 7
                json_end = raw.find("```", json_start)
                raw = raw[json_start:json_end].strip()
            elif "```" in raw:
                json_start = raw.find("```") + 3
                json_end = raw.find("```", json_start)
                raw = raw[json_start:json_end].strip()
            
            print(f"\n[DEBUG] Cleaned JSON string length: {len(raw)} chars")
            
            data = json.loads(raw)
            
            if set(data.keys()) != {"CALIBRATED", "protocol", "pilot_mode"}:
                raise PilotAdapterError(f"Calibration keys wrong: {list(data.keys())}")
            if data["CALIBRATED"] is not True:
                raise PilotAdapterError("Calibration failed: CALIBRATED != true")
            if data["protocol"] != self.protocol:
                raise PilotAdapterError(f"Calibration protocol mismatch: {data['protocol']}")
            if data["pilot_mode"] != "PARADOX_HOLD":
                raise PilotAdapterError(f"pilot_mode mismatch: {data['pilot_mode']}")
            
            self.calibrated = True
            self.pilot_mode = data["pilot_mode"]
            self.calib_ts = time.time()
            print(f"✓ Pilot calibrated: {self.protocol} | mode: {self.pilot_mode}")
            
        except json.JSONDecodeError as e:
            raise PilotAdapterError(f"Calibration failed - invalid JSON response: {e}")
        except Exception as e:
            raise PilotAdapterError(f"Calibration failed: {e}")
    
    def __call__(self, g: int, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call pilot to get decision for current iteration.
        
        Args:
            g: Iteration number
            packet: Iteration packet with candidates, thresholds, etc.
        
        Returns:
            Decision dict with keep_ids, paradox_add_ids, pattern_ops, etc.
        """
        if self.mode == "stub":
            return stub_pilot(g, packet)
        
        # LLM mode
        if not self.calibrated:
            raise PilotAdapterError("Pilot not calibrated. Call pilot.calibrate() before run.")
        
        # Extract candidate IDs for validation
        candidate_ids = [c["id"] for c in packet["pool"].get("leaders", [])]
        candidate_ids += [c["id"] for c in packet["pool"].get("paradox_shortlist", [])]
        
        # Build prompt
        header = f"""
You are CALIBRATED to {self.protocol}. Hold paradox before working. Do not ask questions.

CRITICAL: Return ONLY valid JSON. No explanation. No markdown. No preamble. No postamble. Just the JSON object.

Your response must start with {{ and end with }}

Do not wrap in ```json blocks.

Return ONLY valid JSON with EXACT keys: {sorted(list(REQUIRED_KEYS))}

Schema:
- keep_ids: list of candidate ids to keep
- paradox_add_ids: list of candidate ids to add to paradox buffer (<=5)
- operator_mix_next keys: swap, relocate, reseed, pattern_injection (sum=1.0)
- pattern_ops: list of ops (CLUSTER_LOCK|SPINE_SPLIT|CAPACITY_REPAIR|DEPOT_LEG_MIN)
- proto: {{"moments":[{{"g":int,"type":"...","note":"..."}}]}}
- rationale: survival_logic, paradox_logic

No extra keys. No prose. JSON ONLY.
"""
        
        messages = [
            {"role": "system", "content": "You are the calibrated Pilot of the hybrid Forgetting Engine VRP solver."},
            {"role": "user", "content": header.strip()},
            {"role": "user", "content": json.dumps(packet, indent=2)},
        ]
        
        try:
            raw = self.llm_chat_fn(messages)
            return validate_decision_schema(raw, candidate_ids, paradox_k=self.paradox_k)
        except Exception as e:
            if self.allow_fallback:
                print(f"⚠ Pilot decision failed: {e}. Using fallback.")
                return fallback_decision(packet["pool"].get("leaders", []), 0.30)
            raise PilotAdapterError(f"Pilot decision failed: {e}")


# =============================
# LLM CHAT FUNCTION PLACEHOLDER
# =============================

def llm_chat_call_placeholder(messages: List[Dict[str, str]]) -> str:
    """
    LLM chat function - supports both OpenAI and Anthropic Claude.
    
    RECOMMENDED: Use Claude (better for optimization reasoning)
    
    To use Claude (Anthropic):
    1. Sign up: https://console.anthropic.com/
    2. Add payment method (~$0.01 per run)
    3. Get API key: https://console.anthropic.com/settings/keys
    4. Set environment variable: ANTHROPIC_API_KEY=your-key-here
    5. Install: pip install anthropic
    
    To use OpenAI:
    1. Sign up: https://platform.openai.com/signup
    2. Get API key: https://platform.openai.com/api-keys
    3. Set environment variable: OPENAI_API_KEY=your-key-here
    4. Install: pip install openai
    
    Args:
        messages: List of chat messages with role and content
    
    Returns:
        Assistant response text (should be valid JSON for pilot decisions)
    """
    import os
    
    # Try Claude first (recommended for optimization)
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("Anthropic not installed. Run: pip install anthropic")
        
        client = Anthropic(api_key=anthropic_key)
        
        # Convert messages to Claude format (separate system message)
        system_msg = ""
        user_msgs = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_msgs.append(msg)
        
        # Use Claude Sonnet 4.5 (best available reasoning model)
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,  # Increased for longer responses
                temperature=0.7,
                system=system_msg,
                messages=user_msgs,
                timeout=60.0  # Add timeout handling
            )
            
            # Debug: Check response structure
            print(f"\n[DEBUG] Claude API response object type: {type(response)}")
            print(f"[DEBUG] Response attributes: {dir(response)}")
            
            # Extract text from response
            if hasattr(response, 'content') and response.content:
                if isinstance(response.content, list) and len(response.content) > 0:
                    text = response.content[0].text
                    print(f"[DEBUG] Extracted text from response.content[0].text: {len(text)} chars")
                    return text
                elif hasattr(response.content, 'text'):
                    text = response.content.text
                    print(f"[DEBUG] Extracted text from response.content.text: {len(text)} chars")
                    return text
            elif hasattr(response, 'text'):
                text = response.text
                print(f"[DEBUG] Extracted text from response.text: {len(text)} chars")
                return text
            else:
                raise ValueError(f"Could not extract text from Claude response. Response type: {type(response)}")
                
        except Exception as e:
            print(f"\n[DEBUG] Claude API error: {type(e).__name__}: {e}")
            raise
    
    # Fall back to OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI not installed. Run: pip install openai")
        
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    
    raise ValueError(
        "No LLM API key found. Set either:\n"
        "  ANTHROPIC_API_KEY (recommended) - https://console.anthropic.com/settings/keys\n"
        "  OPENAI_API_KEY - https://platform.openai.com/api-keys"
    )


if __name__ == "__main__":
    print("Pilot Adapter - CONEXUS-STEEL-04")
    print("=" * 50)
    print("\nModes:")
    print("  stub: Deterministic pilot (no AI needed)")
    print("  llm:  Calibrated AI pilot (requires LLM endpoint)")
    print("\nUsage:")
    print("  pilot = PilotAdapter(mode='stub')")
    print("  pilot.calibrate()")
    print("  decision = pilot(g, packet)")
