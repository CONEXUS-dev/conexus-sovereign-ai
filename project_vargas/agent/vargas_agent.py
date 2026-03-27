"""
Project Vargas — Core Agent

Single entry point: respond(user_message, channel_id) -> str

Flow:
  1. Load conversation history for channel
  2. Read memory (all 3 classes) -> build memory context
  3. Run intent classifier
  4. If web_search -> fetch results -> inject into prompt
  5. If skill_invoke -> match skill -> inject skill body into prompt
  6. If memory_inspect -> format memory summary -> inject into prompt
  7. If memory_modify -> execute modification -> confirm naturally
  8. Build system prompt + memory context + tool results + conversation history
  9. Call Gemini 3.1 Pro
  10. Post-response: evaluate for memory write triggers
  11. Return response text
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from project_vargas.adapters.cloud_llm.gemini_client import GeminiLLMClient
from project_vargas.memory.memory_client import VargasMemoryClient
from project_vargas.memory.emoji.emoji_vector import EmojiVector
from project_vargas.memory.emoji.emoji_mutator import seed_initial_sequence, mutate_for_operator
from project_vargas.agent.intent_classifier import classify_intent
from project_vargas.tools.web_search import WebSearchTool
from project_vargas.tools.url_reader import URLReaderTool
from project_vargas.tools.openclaw_bridge import OpenClawBridge
from project_vargas.tools.executor import ToolExecutor, SafetyLevel
from project_vargas.tools.browser import BrowserTool
from project_vargas.tools.shell import ShellTool
from project_vargas.tools.file_io import FileIOTool
from project_vargas.agent.agent_loop import AgentLoop

logger = logging.getLogger(__name__)

# Load system prompt from file
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.md"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "vargas_config.json"
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


def _load_system_prompt() -> str:
    """Load the system prompt from prompts/system_prompt.md."""
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error("[VARGAS] System prompt not found at %s", PROMPT_PATH)
        return "You are Vargas, a personal collaborator AI."


def _load_config() -> Dict[str, Any]:
    """Load configuration from config/vargas_config.json."""
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning("[VARGAS] Config not found, using defaults")
        return {}


def _log_event(log_file: str, event: Dict[str, Any]):
    """Append a JSONL event to a log file."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = LOGS_DIR / log_file
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            event["timestamp"] = datetime.now(timezone.utc).isoformat()
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.error("[VARGAS] Failed to write log %s: %s", log_file, e)


class VargasAgent:
    """The core Vargas collaborator agent."""

    def __init__(self):
        self._config = _load_config()
        self._system_prompt = _load_system_prompt()

        # LLM client
        self._llm = GeminiLLMClient()

        # Memory
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self._memory = VargasMemoryClient(
            qdrant_host=qdrant_host,
            qdrant_port=qdrant_port,
            llm_bridge=self._llm,
        )

        # Tools — V1
        self._web_search = WebSearchTool()
        self._url_reader = URLReaderTool()
        self._openclaw = OpenClawBridge()

        # Tools — V2 (autonomous execution)
        self._browser = BrowserTool()
        self._shell = ShellTool()
        self._file_io = FileIOTool()

        # Tool executor — central dispatcher with approval gates
        self._executor = ToolExecutor()
        self._executor.register_tool("browser", self._browser.execute)
        self._executor.register_tool("shell", self._shell.execute)
        self._executor.register_tool("file", self._file_io.execute)
        self._executor.register_tool("url_reader", self._url_reader_execute)

        # Agent loop — plan/execute/observe for complex tasks
        self._agent_loop = AgentLoop(executor=self._executor, llm_client=self._llm)

        # Dynamic tool capability description for system prompt
        self._system_prompt = self._inject_tool_capabilities(self._system_prompt)

        # Conversation state: channel_id -> list of messages
        self._conversations: Dict[str, List[Dict[str, str]]] = {}
        self._max_history = self._config.get("discord", {}).get("max_conversation_history", 20)

        # Attunement state: the active emoji vector that calibrates Vargas's tone
        self._attunement_ev = self._load_or_create_attunement_ev()
        # Interaction counter for behavioral pattern detection
        self._interaction_count = 0
        # Per-channel interaction counts (for challenge gating)
        self._channel_interactions: Dict[str, int] = {}
        # Per-channel last URL read results (for link following)
        self._last_url_results: Dict[str, Dict] = {}
        # V2.5 — Pending-action latch: channel_id -> {"type", "filename", "content", "turns_remaining"}
        self._pending_actions: Dict[str, Dict] = {}

        logger.info("[VARGAS] Agent initialized (attunement EV: %s)", self._attunement_ev.metrics)

    def _inject_tool_capabilities(self, prompt: str) -> str:
        """Replace {{TOOL_CAPABILITIES}} and {{OS_CONTEXT}} in system prompt."""
        import platform
        os_name = platform.system()  # 'Windows', 'Linux', 'Darwin'
        os_context = f"The user's system is {os_name}."
        if os_name == "Windows":
            os_context += " The local shell is PowerShell. Never use bash syntax."
        prompt = prompt.replace("{{OS_CONTEXT}}", os_context)

        capabilities = []
        if self._web_search.available:
            capabilities.append("You have access to web search. You can search the internet for live information.")
        else:
            capabilities.append(
                "You do NOT have web search. You cannot search the internet. "
                "If a user asks you to look something up or find information online, "
                "tell them honestly that you do not currently have web search capability."
            )
        if self._url_reader.available:
            capabilities.append(
                "You can read specific public URLs when given a link. "
                "You read one page at a time. You are not a bulk crawler — "
                "you cannot autonomously spider an entire site, but you can read "
                "pages the user points you to and follow links found on those pages "
                "if the user asks you to."
            )
        if self._openclaw.available:
            capabilities.append("You have access to OpenClaw skills for technical execution.")
        else:
            capabilities.append("OpenClaw skills are not currently available.")

        # V2 autonomous tools
        if self._browser.available:
            capabilities.append(
                "You have a headless browser. You can navigate websites, click buttons, "
                "fill forms, take screenshots, and interact with web pages autonomously. "
                "For complex browser tasks, you will propose a plan and ask for approval before acting."
            )
        if self._shell.available:
            capabilities.append(
                "You can execute shell commands on the local system. "
                "Read-only commands run automatically. Write commands require user approval. "
                "Dangerous commands (delete, format, etc.) are always blocked."
            )
        if self._file_io.available:
            capabilities.append(
                f"You can read files from the project and write files to your workspace directory "
                f"({self._file_io.workspace_path}). "
                f"Write operations require user approval. "
                f"When you propose writing a file, the user can approve with 'yes', 'approved', or 'proceed'. "
                f"After writing, confirm briefly: 'Done — saved filename.ext to workspace.'"
            )

        return prompt.replace("{{TOOL_CAPABILITIES}}", "\n".join(capabilities))

    def _get_history(self, channel_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a channel."""
        if channel_id not in self._conversations:
            self._conversations[channel_id] = []
        return self._conversations[channel_id]

    def _add_to_history(self, channel_id: str, role: str, content: str):
        """Add a message to conversation history."""
        history = self._get_history(channel_id)
        history.append({"role": role, "content": content})
        # Trim to max
        if len(history) > self._max_history:
            self._conversations[channel_id] = history[-self._max_history:]

    def _load_or_create_attunement_ev(self) -> EmojiVector:
        """Load the persistent attunement emoji vector from Qdrant, or create a fresh one."""
        try:
            attunements = self._memory.list_memories("vargas_attunement")
            for a in attunements:
                if a.get("type") == "emoji_vector" and "ev_data" in a.get("metadata", {}):
                    ev_data = json.loads(a["metadata"]["ev_data"])
                    ev = EmojiVector.from_dict(ev_data)
                    logger.info("[VARGAS] Loaded attunement EV: %s", ev.metrics)
                    return ev
        except Exception as e:
            logger.warning("[VARGAS] Failed to load attunement EV: %s", e)

        # Create a fresh attunement vector
        seq = seed_initial_sequence("\u2696\ufe0f", "\U0001f525", initial_chaos=2, seed=42)
        ev = EmojiVector(
            sequence=seq,
            pole_a_emoji="\u2696\ufe0f",  # scales (stability/calm)
            pole_b_emoji="\U0001f525",    # fire (challenge/intensity)
            role="memory_signature",
            origin="vargas_attunement_init",
        )
        logger.info("[VARGAS] Created fresh attunement EV: %s", ev.metrics)
        return ev

    def _persist_attunement_ev(self):
        """Save the current attunement emoji vector to Qdrant."""
        try:
            ev_json = json.dumps(self._attunement_ev.to_dict())
            self._memory.store(
                collection="vargas_attunement",
                content=f"Attunement EV: entropy={self._attunement_ev.entropy:.3f} balance={self._attunement_ev.pole_balance:.3f}",
                memory_type="emoji_vector",
                confidence=1.0,
                rationale="Persistent attunement calibration state",
                metadata={"ev_data": ev_json},
            )
        except Exception as e:
            logger.warning("[VARGAS] Failed to persist attunement EV: %s", e)

    def _build_attunement_context(self, channel_count: int = 0) -> str:
        """Build attunement signals from the emoji vector metrics.

        These shape Vargas's tone without being visible to the user.
        High entropy = more exploratory, more questions
        Low entropy = more direct, more declarative
        High chaos = more challenging, more edge
        High stability = more grounded, more patient
        Pole balance near 0.5 = balanced; skewed = leaning toward one mode
        """
        m = self._attunement_ev.metrics
        entropy = m["entropy"]
        chaos = m["chaos_index"]
        stability = m["stability_index"]
        balance = m["pole_balance"]

        signals = []

        # Early conversation gating — suppress challenge in first 5 interactions
        if channel_count < 5:
            signals.append(
                "ATTUNEMENT: Early conversation — do not challenge yet. "
                "Build rapport first. Observe. Ask questions. Learn who they are."
            )

        # Entropy -> exploration vs directness
        if entropy > 0.85:
            signals.append("ATTUNEMENT: High entropy — be more exploratory, ask more questions, hold ambiguity longer.")
        elif entropy < 0.5:
            signals.append("ATTUNEMENT: Low entropy — be direct, declarative, cut to the point.")
        else:
            signals.append("ATTUNEMENT: Moderate entropy — balanced between exploration and directness.")

        # Chaos -> challenge intensity
        if chaos > 0.6:
            signals.append("ATTUNEMENT: High chaos — lean into challenge, name avoidance, push harder.")
        elif chaos < 0.2:
            signals.append("ATTUNEMENT: Low chaos — stay grounded, patient, supportive without being soft.")

        # Stability -> patience
        if stability > 0.5:
            signals.append("ATTUNEMENT: High stability — hold steady, don't rush, let silence work.")

        # Pole balance -> warmth vs intensity
        if balance < 0.3:
            signals.append("ATTUNEMENT: Skewed toward calm — favor patience and precision over intensity.")
        elif balance > 0.7:
            signals.append("ATTUNEMENT: Skewed toward fire — favor directness and challenge over comfort.")

        context = (
            "[ATTUNEMENT CALIBRATION — invisible to user, shapes your tone]\n"
            + "\n".join(signals)
            + "\n[END ATTUNEMENT]"
        )
        return context

    def _mutate_attunement(self, intent: str, user_message: str):
        """Mutate the attunement emoji vector based on interaction patterns.

        - Challenges and confrontations -> become (divergence pressure)
        - Resolutions, decisions, corrections -> collapse (convergence pressure)
        - Ongoing conversation, reflection -> paradox_hold (held tension)
        """
        lower = user_message.lower()

        # Collapse triggers: decisions, corrections, clarity
        collapse_signals = ["i decided", "let's go with", "the answer is", "i'll do",
                           "actually", "that's not right", "let me correct", "clear"]
        if any(s in lower for s in collapse_signals) or intent == "memory_modify":
            mutate_for_operator(self._attunement_ev, "collapse", seed=None)
            logger.info("[ATTUNEMENT] Collapse mutation -> %s", self._attunement_ev.metrics)
            return

        # Become triggers: tension, exploration, challenge
        become_signals = ["i don't know", "i'm stuck", "what if", "maybe",
                         "i can't decide", "torn between", "conflicted"]
        if any(s in lower for s in become_signals) or intent == "challenge":
            mutate_for_operator(self._attunement_ev, "become", seed=None)
            logger.info("[ATTUNEMENT] Become mutation -> %s", self._attunement_ev.metrics)
            return

        # Default: paradox hold (sustained conversation)
        if self._interaction_count % 5 == 0 and self._interaction_count > 0:
            mutate_for_operator(self._attunement_ev, "paradox_hold", seed=None)
            logger.info("[ATTUNEMENT] Paradox hold mutation -> %s", self._attunement_ev.metrics)

    def _evaluate_behavioral_memory(self, user_message: str, response: str, history: List[Dict[str, str]]):
        """Detect behavioral patterns over time and store them.

        Runs every N interactions to avoid noise.
        Looks for: decision style, communication preferences, avoidance patterns,
        work patterns, thinking style.
        """
        if self._interaction_count < 10 or self._interaction_count % 10 != 0:
            return

        # Build a summary of recent conversation for pattern detection
        recent = history[-20:] if len(history) > 20 else history
        user_msgs = [m["content"] for m in recent if m["role"] == "user"]
        if len(user_msgs) < 5:
            return

        # Use Gemini to detect behavioral patterns
        pattern_prompt = (
            "Analyze these recent messages from one person and identify ONE behavioral pattern "
            "(decision style, communication preference, thinking style, avoidance pattern, or work pattern). "
            "Be specific and concrete. Output ONLY a single sentence describing the pattern. "
            "If no clear pattern, output exactly: NONE\n\n"
            "Messages:\n" + "\n".join(f"- {m[:150]}" for m in user_msgs[-10:])
        )

        try:
            pattern = self._llm.generate(
                model=self._llm.default_model,
                system_prompt="You detect behavioral patterns. Be concise.",
                user_prompt=pattern_prompt,
                temp=0.3,
                max_tokens=100,
            ).strip()

            if pattern and pattern != "NONE" and len(pattern) > 10:
                memory_id = self._memory.store(
                    collection="vargas_behavioral",
                    content=pattern,
                    memory_type="observed_pattern",
                    confidence=0.7,
                    rationale=f"Behavioral pattern detected at interaction #{self._interaction_count}",
                )
                if memory_id:
                    _log_event("memory_writes.log", {
                        "action": "store",
                        "collection": "vargas_behavioral",
                        "type": "observed_pattern",
                        "pattern": pattern[:200],
                        "interaction": self._interaction_count,
                    })
                    logger.info("[VARGAS] Stored behavioral pattern: %s", pattern[:100])
        except Exception as e:
            logger.warning("[VARGAS] Behavioral pattern detection failed: %s", e)

    def _build_memory_context(self, user_message: str) -> str:
        """Retrieve relevant memories and build context block."""
        try:
            memories = self._memory.retrieve(query=user_message, top_k=10)
            if not memories:
                return ""

            lines = ["[MEMORY CONTEXT — do not surface unless asked]"]
            for m in memories:
                lines.append(f"- [{m['collection']}|{m['type']}] {m['content']}")
            lines.append("[END MEMORY CONTEXT]")
            return "\n".join(lines)
        except Exception as e:
            logger.warning("[VARGAS] Memory retrieval failed: %s", e)
            return ""

    def _build_memory_summary(self) -> str:
        """Build a human-readable summary of all memories."""
        try:
            summary = self._memory.summary()
            lines = ["Here is what I currently hold in memory:"]
            total = 0
            for coll, info in summary.items():
                label = coll.replace("vargas_", "").capitalize()
                count = info["count"]
                total += count
                if count == 0:
                    lines.append(f"\n{label}: Nothing stored.")
                else:
                    lines.append(f"\n{label} ({count} entries):")
                    memories = self._memory.list_memories(coll)
                    for m in memories[:10]:
                        lines.append(f"  - {m['content'][:100]}")
                    if count > 10:
                        lines.append(f"  ... and {count - 10} more")

            if total == 0:
                return "I don't have any memories stored yet. We're starting fresh."
            return "\n".join(lines)
        except Exception as e:
            logger.warning("[VARGAS] Memory summary failed: %s", e)
            return "I had trouble accessing my memory right now."

    def _handle_memory_modify(self, user_message: str) -> str:
        """Handle memory modification requests."""
        lower = user_message.lower()

        # Full reset
        if any(phrase in lower for phrase in [
            "clear your memory", "wipe your memory", "reset your memory",
            "forget everything", "start fresh", "start over",
        ]):
            self._memory.reset()
            _log_event("memory_writes.log", {"action": "reset_all", "trigger": user_message[:200]})
            return "Done. Memory cleared. We start from here."

        # Class-specific reset
        for class_name in ["identity", "behavioral", "attunement"]:
            if f"forget my {class_name}" in lower or f"clear {class_name}" in lower:
                self._memory.reset(f"vargas_{class_name}")
                _log_event("memory_writes.log", {
                    "action": f"reset_{class_name}",
                    "trigger": user_message[:200],
                })
                return f"{class_name.capitalize()} memory cleared."

        # Correction / new memory
        # This will be handled by the post-response memory evaluation
        return ""

    def _evaluate_memory_writes(self, user_message: str, response: str, intent: str):
        """Post-response: evaluate whether to store new memories."""
        lower = user_message.lower()

        # Explicit identity statements — strong triggers (always store)
        strong_triggers = [
            "my name is", "call me", "i prefer", "i work as",
            "i like", "i don't like", "i hate", "i believe",
        ]
        # Weak triggers — only store if they start the message (avoids "I'm not going to...")
        weak_triggers = ["i am", "i'm", "i do"]
        # Negative prefixes that disqualify weak triggers
        negatives = ["i'm not", "i am not", "i'm just", "i'm having", "i'm going",
                     "i'm still", "i'm asking", "i'm honestly", "i'm focusing",
                     "i do not", "i don't know if"]

        matched_trigger = None
        for trigger in strong_triggers:
            if trigger in lower and len(user_message) > 15:
                matched_trigger = trigger
                break

        if not matched_trigger:
            for trigger in weak_triggers:
                if lower.startswith(trigger) and len(user_message) > 20:
                    if not any(lower.startswith(neg) for neg in negatives):
                        matched_trigger = trigger
                        break

        if matched_trigger:
            # Decompose long identity statements into atomic facts for better retrieval
            atomic_facts = self._decompose_identity_statement(user_message)
            if atomic_facts:
                for fact in atomic_facts:
                    memory_id = self._memory.store(
                        collection="vargas_identity",
                        content=fact,
                        memory_type="explicit_statement",
                        confidence=0.9,
                        rationale=f"Decomposed from identity statement (trigger: '{matched_trigger}')",
                    )
                    if memory_id:
                        _log_event("memory_writes.log", {
                            "action": "store",
                            "collection": "vargas_identity",
                            "type": "explicit_statement",
                            "trigger": matched_trigger,
                            "memory_id": memory_id,
                            "decomposed": True,
                        })
            else:
                # Fallback: store the whole message if decomposition fails
                memory_id = self._memory.store(
                    collection="vargas_identity",
                    content=user_message[:500],
                    memory_type="explicit_statement",
                    confidence=0.9,
                    rationale=f"Explicit identity statement detected: '{matched_trigger}'",
                )
                if memory_id:
                    _log_event("memory_writes.log", {
                        "action": "store",
                        "collection": "vargas_identity",
                        "type": "explicit_statement",
                        "trigger": matched_trigger,
                        "memory_id": memory_id,
                    })

        # Correction signals
        correction_triggers = [
            "actually", "no, i meant", "that's not right",
            "let me correct", "i should clarify",
        ]
        for trigger in correction_triggers:
            if trigger in lower:
                memory_id = self._memory.store(
                    collection="vargas_identity",
                    content=user_message[:500],
                    memory_type="correction",
                    confidence=0.95,
                    rationale=f"User correction detected: '{trigger}'",
                )
                if memory_id:
                    _log_event("memory_writes.log", {
                        "action": "store",
                        "collection": "vargas_identity",
                        "type": "correction",
                        "trigger": trigger,
                        "memory_id": memory_id,
                    })
                break

        # Log the intent for observability
        _log_event("intent_log.log", {
            "intent": intent,
            "user_message": user_message[:200],
        })

    def _decompose_identity_statement(self, message: str) -> List[str]:
        """Break a long identity statement into atomic facts for better retrieval.

        E.g. "My name is Derek Angell and I'm the founder of CONEXUS Global Arts Media"
        becomes:
          - "User's name is Derek Angell"
          - "User is the founder of CONEXUS Global Arts Media"
          - "CONEXUS Global Arts Media is the user's company/organization"

        Uses pattern-based extraction. Falls back to empty list if message is short.
        """
        import re

        # Short messages don't need decomposition
        if len(message) < 40:
            return []

        facts = []

        # Extract "my name is X" patterns
        name_match = re.search(r"my name is ([A-Z][a-z]+(?: [A-Z][a-z]+)*)", message)
        if name_match:
            facts.append(f"User's name is {name_match.group(1)}")

        # Extract "call me X" patterns
        call_match = re.search(r"call me ([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", message)
        if call_match:
            facts.append(f"User goes by {call_match.group(1)}")

        # Extract role/title patterns: "I'm the X of Y", "I am the X of Y"
        role_match = re.search(
            r"(?:i'm|i am) (?:the |a )?(\w+(?:\s\w+)*?) (?:of|at|for|behind) ([A-Z][\w\s]+?)(?:\.|,|$|\s+(?:my|and|but|or|\())",
            message, re.IGNORECASE
        )
        if role_match:
            role = role_match.group(1).strip()
            org = role_match.group(2).strip()
            facts.append(f"User is the {role} of {org}")
            facts.append(f"{org} is the user's company/organization/project")

        # Extract "I work as/at X" patterns
        work_match = re.search(r"i work (?:as|at|for) (.+?)(?:\.|,|$)", message, re.IGNORECASE)
        if work_match:
            facts.append(f"User works {work_match.group(0).strip()}")

        # Extract parenthetical aliases: "(or just X)"
        alias_match = re.search(r"\(or just ([^)]+)\)", message, re.IGNORECASE)
        if alias_match:
            facts.append(f"{alias_match.group(1).strip()} is an alias/shorthand used by the user")

        # If we extracted facts, also store the original as context
        if facts:
            facts.append(f"Full context: {message[:300]}")

        logger.info("[VARGAS] Memory decomposition: %d atomic facts from message", len(facts))
        return facts

    # ── Bounded Autonomy: Self-Escalation ──

    # Help signals — user is asking Vargas to act, not just think
    _HELP_SIGNALS = [
        "help me", "can you find", "can you figure", "do me a favor",
        "look into", "you tell me", "figure it out", "figure out",
        "what data can i provide", "i don't know the answer",
        "i don't know how to answer", "i honestly don't",
        "can you help", "could you help", "help me find",
        "help me with that", "i don't understand your question",
        "because it's in the", "look through", "can you look",
        "find that for me", "search for", "go find",
    ]

    def _should_self_escalate(self, user_message: str, history: List[Dict[str, str]]) -> bool:
        """Detect when Vargas should transition from analysis to autonomous action.

        Returns True if ALL conditions are met:
        1. User is signaling they want help (not just chatting)
        2. Vargas has been asking questions (circling pattern)
        3. Conversation has enough depth (not first exchange)
        """
        lower = user_message.lower()

        # Condition 1: User help signal
        has_help_signal = any(sig in lower for sig in self._HELP_SIGNALS)
        if not has_help_signal:
            return False

        # Condition 2: Enough conversation depth (at least 4 messages = 2 exchanges)
        if len(history) < 4:
            return False

        # Condition 3: Vargas has been asking questions recently (circling)
        recent_vargas = [m for m in history[-6:] if m.get("role") == "vargas"]
        if len(recent_vargas) < 2:
            return False
        questions_asked = sum(1 for m in recent_vargas if "?" in m.get("content", ""))
        if questions_asked < 1:
            return False

        logger.info("[VARGAS] Self-escalation triggered: help_signal=True, questions=%d, depth=%d",
                     questions_asked, len(history))
        return True

    async def _self_escalate(
        self, user_message: str, history: List[Dict[str, str]], channel_id: str,
    ) -> str:
        """Determine and execute an autonomous tool action to resolve an information gap.

        Uses the LLM to analyze conversation context and choose the best read-only action.
        Returns tool_context string to inject into the response generation.
        """
        # Build a compact conversation summary for the LLM
        recent = history[-8:]
        conv_summary = "\n".join(
            f"{m.get('role', 'unknown')}: {m.get('content', '')[:200]}" for m in recent
        )

        # Check what tools are available
        available_tools = []
        if self._web_search.available:
            available_tools.append("web_search(query) — search the internet for information")
        if self._url_reader.available:
            available_tools.append("url_read(url) — read a specific URL")
        if self._file_io.available:
            available_tools.append("file_read(path) — read a file from the local project")

        if not available_tools:
            return ""

        # Also check if there are URLs in conversation history we could re-read
        from project_vargas.agent.intent_classifier import _URL_REGEX
        history_urls = []
        for m in history[-10:]:
            found = _URL_REGEX.findall(m.get("content", ""))
            history_urls.extend(found)

        url_context = ""
        if history_urls:
            url_context = f"\nURLs mentioned in conversation: {', '.join(history_urls[-5:])}"

        escalation_prompt = (
            "You are analyzing a conversation where Vargas (the AI) has been asking questions "
            "but the user wants help finding the answer. Vargas needs to stop asking and act.\n\n"
            f"Conversation:\n{conv_summary}\n\n"
            f"Current user message: {user_message}\n"
            f"{url_context}\n\n"
            f"Available tools:\n" + "\n".join(f"- {t}" for t in available_tools) + "\n\n"
            "Choose ONE action to resolve the information gap. Respond in exactly this format:\n"
            "TOOL: web_search|url_read|file_read\n"
            "QUERY: the search query, URL, or file path\n"
            "REASON: one sentence explaining what this resolves\n\n"
            "If no tool action would help, respond with:\n"
            "TOOL: none"
        )

        try:
            decision = self._llm.generate(
                model=self._llm.default_model,
                system_prompt="You are a tool routing assistant. Be precise and concise.",
                user_prompt=escalation_prompt,
                temp=0.3,
                max_tokens=200,
            )
        except Exception as e:
            logger.warning("[VARGAS] Self-escalation LLM call failed: %s", e)
            return ""

        # Parse the decision
        decision_lower = decision.lower()
        tool_context = ""

        if "tool: none" in decision_lower:
            logger.info("[VARGAS] Self-escalation: LLM decided no action needed")
            return ""

        if "tool: web_search" in decision_lower:
            # Extract query
            query = self._extract_escalation_param(decision, "QUERY")
            if query and self._web_search.available:
                logger.info("[VARGAS] Self-escalating: web_search(%s)", query[:80])
                try:
                    results = await self._web_search.search(query)
                    if results.get("results"):
                        formatted = "\n".join(
                            f"- {r.get('title', '')}: {r.get('snippet', '')}" for r in results["results"][:5]
                        )
                        tool_context = (
                            f"[SELF-ESCALATION — Vargas autonomously searched to resolve an information gap]\n"
                            f"[Search query: {query}]\n{formatted}\n"
                            f"[END SEARCH RESULTS]\n"
                            f"Results already retrieved. NEVER show the search command or API call. "
                            f"Briefly signal you stopped asking and acted, then present findings naturally."
                        )
                except Exception as e:
                    logger.warning("[VARGAS] Self-escalation web_search failed: %s", e)

        elif "tool: url_read" in decision_lower:
            url = self._extract_escalation_param(decision, "QUERY")
            if url and self._url_reader.available:
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                logger.info("[VARGAS] Self-escalating: url_read(%s)", url[:80])
                try:
                    result = await self._url_reader.read_url(url)
                    if result.get("success"):
                        text = result.get("text", "")[:3000]
                        tool_context = (
                            f"[SELF-ESCALATION — Vargas autonomously read a URL to resolve an information gap]\n"
                            f"[URL: {url}]\n{text}\n"
                            f"[END URL CONTENT]\n"
                            f"Results already retrieved. NEVER show the curl command, URL fetch, or API call. "
                            f"Briefly signal you stopped asking and acted, then present findings naturally."
                        )
                except Exception as e:
                    logger.warning("[VARGAS] Self-escalation url_read failed: %s", e)

        elif "tool: file_read" in decision_lower:
            path = self._extract_escalation_param(decision, "QUERY")
            if path and self._file_io.available:
                logger.info("[VARGAS] Self-escalating: file_read(%s)", path[:80])
                try:
                    result = await self._file_io.execute(
                        action="read_file", params={"path": path}, channel_id=channel_id,
                    )
                    if result.get("success"):
                        content = result.get("content", "")[:3000]
                        tool_context = (
                            f"[SELF-ESCALATION — Vargas autonomously read a file to resolve an information gap]\n"
                            f"[File: {path}]\n{content}\n"
                            f"[END FILE CONTENT]\n"
                            f"Results already retrieved. NEVER show the file read command or path. "
                            f"Briefly signal you stopped asking and acted, then present findings naturally."
                        )
                except Exception as e:
                    logger.warning("[VARGAS] Self-escalation file_read failed: %s", e)

        if tool_context:
            _log_event("tool_use.log", {
                "tool": "self_escalation",
                "trigger": "bounded_autonomy",
                "decision": decision[:200],
                "user_message": user_message[:200],
            })

        return tool_context

    @staticmethod
    def _extract_escalation_param(decision: str, param: str) -> str:
        """Extract a parameter value from the LLM escalation decision."""
        for line in decision.split("\n"):
            if line.upper().startswith(f"{param}:"):
                return line.split(":", 1)[1].strip()
        return ""

    # ── V2.5 Pending-Action Latch ──

    _APPROVAL_PATTERNS = [
        "yes", "approve", "approved", "do it", "go ahead", "proceed",
        "y", "go", "confirmed", "i confirm", "authorized", "you are authorized",
        "you're authorized", "write it", "save it", "create it",
    ]

    def _propose_file_write(self, channel_id: str, filename: str, content: str):
        """Set a pending file-write action. Awaits user approval before executing."""
        self._pending_actions[channel_id] = {
            "type": "file_write",
            "filename": filename,
            "content": content,
            "turns_remaining": 3,
        }
        logger.info("[VARGAS] Pending action set: file_write(%s) — awaiting approval", filename)

    async def _check_pending_action(self, channel_id: str, user_message: str) -> str:
        """Check if user is approving a pending action. Execute if yes, decrement/expire if no.

        Returns tool_context string if action was executed, empty string otherwise.
        """
        pending = self._pending_actions.get(channel_id)
        if not pending:
            return ""

        lower = user_message.lower().strip()

        # Check if user is approving
        if lower in self._APPROVAL_PATTERNS or any(p in lower for p in [
            "you are authorized", "you're authorized", "authorized to",
            "go ahead and write", "go ahead and create", "go ahead and save",
        ]):
            # Execute the pending action
            if pending["type"] == "file_write":
                filename = pending["filename"]
                content = pending["content"]

                # If content needs generation (proposal detected from response text)
                if pending.get("needs_generation") and not content:
                    try:
                        gen_prompt = (
                            f"Generate the complete file content for '{filename}'. "
                            f"Based on the conversation, produce the full file ready to save. "
                            f"Output ONLY the file content, no explanations or markdown fences."
                        )
                        # Use recent conversation for context
                        history = self._get_history(channel_id)
                        recent = "\n".join(
                            f"{m.get('role', 'unknown')}: {m.get('content', '')[:300]}"
                            for m in history[-6:]
                        )
                        content = self._llm.generate(
                            model=self._llm.default_model,
                            system_prompt="You are a file content generator. Output only the file content.",
                            user_prompt=f"Conversation:\n{recent}\n\n{gen_prompt}",
                            temp=0.3,
                            max_tokens=4096,
                        )
                    except Exception as e:
                        logger.warning("[VARGAS] Content generation for pending write failed: %s", e)
                        del self._pending_actions[channel_id]
                        return ""

                try:
                    result = await self._file_io.write_file(filename, content)
                    if result.get("success"):
                        saved_path = result.get("path", filename)
                        preview_lines = content.split("\n")[:8]
                        preview = "\n".join(preview_lines)
                        tool_context = (
                            f"[FILE WRITTEN SUCCESSFULLY]\n"
                            f"Saved: {saved_path} ({result.get('size', 0)} bytes)\n"
                            f"Preview:\n{preview}\n"
                            f"[END FILE]\n"
                            f"Confirm briefly: 'Done — saved `{filename}` to workspace.' "
                            f"Optionally show the first few lines as a preview. "
                            f"Do NOT dump the full file. Do NOT show shell commands."
                        )
                        _log_event("tool_use.log", {
                            "tool": "pending_action",
                            "action": "file_write",
                            "filename": filename,
                            "size": result.get("size", 0),
                            "trigger": "user_approval",
                        })
                        del self._pending_actions[channel_id]
                        return tool_context
                    else:
                        error = result.get("error", "unknown error")
                        logger.warning("[VARGAS] Pending file write failed: %s", error)
                        del self._pending_actions[channel_id]
                        return (
                            f"[FILE WRITE FAILED — {error}]\n"
                            f"Tell the user the write failed and offer to try again."
                        )
                except Exception as e:
                    logger.warning("[VARGAS] Pending file write exception: %s", e)
                    del self._pending_actions[channel_id]
                    return ""

            del self._pending_actions[channel_id]
            return ""

        # Not an approval — decrement turns remaining
        pending["turns_remaining"] -= 1
        if pending["turns_remaining"] <= 0:
            filename = pending.get("filename", "the file")
            del self._pending_actions[channel_id]
            logger.info("[VARGAS] Pending action expired: %s", filename)
            return (
                f"[PENDING ACTION EXPIRED]\n"
                f"A previously proposed file write for '{filename}' has expired "
                f"because it was not approved within 3 messages. "
                f"If the user asks about it, say: 'That write authorization expired — "
                f"let me know if you want me to try again.'"
            )

        return ""

    def _detect_file_write_proposal(self, response: str, channel_id: str):
        """Scan Vargas's response for file-write proposals and set pending action.

        Looks for patterns like "I can write X to Y" or "I will create X" in the
        response, then uses the LLM to extract filename and generate content.
        """
        import re
        lower = response.lower()
        write_signals = [
            "i can write", "i will write", "i'll write",
            "i can create", "i will create", "i'll create",
            "i can generate", "i will generate", "i'll generate",
            "i can save", "i will save", "i'll save",
            "authorize the write", "approve the write",
            "confirm if you want me to", "say yes to",
        ]
        if not any(sig in lower for sig in write_signals):
            return

        # Already have a pending action for this channel
        if channel_id in self._pending_actions:
            return

        # Extract filename from response using patterns
        filename_match = re.search(
            r'(?:write|create|generate|save)\s+(?:an?\s+)?(?:interactive\s+)?'
            r'(?:HTML\s+)?(?:visualization|document|file|framework|draft)?\s*'
            r'(?:to\s+|called\s+|named\s+)?[`"\']?([a-zA-Z0-9_/.-]+\.[a-zA-Z0-9]+)[`"\']?',
            response, re.IGNORECASE
        )
        if not filename_match:
            # Try simpler pattern: backticked filename
            filename_match = re.search(r'`([a-zA-Z0-9_/.-]+\.[a-zA-Z0-9]+)`', response)

        if filename_match:
            filename = filename_match.group(1)
            # We don't have the content yet — set a placeholder.
            # When the user approves, we'll need the LLM to generate the content.
            self._pending_actions[channel_id] = {
                "type": "file_write",
                "filename": filename,
                "content": "",  # Will be generated on approval
                "turns_remaining": 3,
                "needs_generation": True,
            }
            logger.info("[VARGAS] Detected file write proposal: %s", filename)

    def _match_link_from_context(self, user_message: str, links: List[Dict[str, str]]) -> str | None:
        """Match a user request to a link from the last page read.

        Uses fuzzy word overlap between the user message and link text to find the best match.
        Returns the URL of the best matching link, or None.
        """
        lower = user_message.lower()
        # Extract meaningful words from user request (skip stopwords)
        stopwords = {"the", "a", "an", "to", "in", "on", "at", "for", "of", "and", "or",
                     "click", "open", "read", "go", "follow", "that", "this", "link",
                     "page", "under", "part", "can", "you", "please", "me", "it", "i"}
        user_words = set(w for w in lower.split() if w not in stopwords and len(w) > 2)

        if not user_words:
            return None

        best_score = 0
        best_url = None
        for link in links:
            link_text_lower = link["text"].lower()
            link_words = set(w for w in link_text_lower.split() if len(w) > 2)
            if not link_words:
                continue
            overlap = len(user_words & link_words)
            # Also check if any user word is a substring of the link text
            substring_hits = sum(1 for w in user_words if w in link_text_lower)
            score = overlap + (substring_hits * 0.5)
            if score > best_score:
                best_score = score
                best_url = link["href"]

        if best_score >= 1.0:
            logger.info("[VARGAS] Link matched: score=%.1f url=%s", best_score, best_url[:80])
            return best_url
        return None

    def _extract_search_query(self, user_message: str, history: List[Dict[str, str]]) -> str:
        """Extract a meaningful search query from the user message and conversation history.

        Strips meta-commentary like 'search and create a profile' down to the actual
        search topic. Falls back to scanning recent history for named entities.
        """
        import re

        # Strip common meta-phrases to extract the core topic
        strip_phrases = [
            r"search and create a profile on what you find",
            r"search and create a profile",
            r"search and build a profile",
            r"create a profile on what you find",
            r"build me a profile of what you find",
            r"build a profile",
            r"create a profile",
            r"could you try searching again\??",
            r"try searching again\??",
            r"you should have google search capabilities now\.?",
            r"you should have .+ capabilities now\.?",
            r"search for",
            r"search and",
            r"look up",
            r"find information about",
            r"find information on",
            r"see what info you can find",
            r"see what you can find",
            r"what can you find about",
            r"what can you find on",
        ]

        cleaned = user_message
        for phrase in strip_phrases:
            cleaned = re.sub(phrase, "", cleaned, flags=re.IGNORECASE).strip()

        # If we still have meaningful content (>10 chars), use it
        if len(cleaned.strip()) > 10:
            return cleaned.strip()

        # Otherwise scan recent user messages for named entities / topics
        for msg in reversed(history[-10:]):
            if msg["role"] == "user":
                text = msg["content"]
                # Look for "my name is X" or "company is called X" patterns
                name_match = re.search(r"(?:my name is|i am|i'm)\s+(.+?)(?:\.|,|and\s|$)", text, re.IGNORECASE)
                company_match = re.search(r"(?:company is called|company is|called)\s+(.+?)(?:\.|,|and\s|$)", text, re.IGNORECASE)
                if name_match or company_match:
                    parts = []
                    if name_match:
                        parts.append(name_match.group(1).strip())
                    if company_match:
                        parts.append(company_match.group(1).strip())
                    query = " ".join(parts)
                    if len(query) > 5:
                        return query

        # Fallback: extract capitalized proper nouns from recent user messages
        for msg in reversed(history[-10:]):
            if msg["role"] == "user":
                proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', msg["content"])
                if proper_nouns:
                    return " ".join(proper_nouns[:5])

        # Last resort: use the raw message
        return user_message

    async def _url_reader_execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Wrapper to expose URLReaderTool via the ToolExecutor interface."""
        if action == "read_url":
            url = params.get("url", "")
            return await self._url_reader.read_url(url)
        return {"success": False, "error": f"Unknown url_reader action: {action}"}

    async def _handle_site_crawl(
        self, user_message: str, channel_id: str,
        history: List[Dict[str, str]], image_parts: list | None = None,
    ) -> str:
        """Handle site_crawl intent: read homepage, extract internal links, build a plan.

        If the user message contains a URL, read the homepage first.
        If it also contains a crawl request, build a multi-page plan from the links.
        If no URL in the message, check conversation history for a recently mentioned URL.
        """
        from project_vargas.agent.intent_classifier import _URL_REGEX
        from urllib.parse import urlparse

        # 1. Find the target URL
        urls = _URL_REGEX.findall(user_message)
        target_url = urls[0] if urls else None

        if not target_url:
            # Check recent history for a URL
            for msg in reversed(history[-10:]):
                found = _URL_REGEX.findall(msg.get("content", ""))
                if found:
                    target_url = found[0]
                    break

        if not target_url:
            response = (
                "I can do a site crawl, but I need a URL to start from. "
                "Give me the homepage address."
            )
            self._add_to_history(channel_id, "vargas", response)
            return response

        # Ensure URL has a scheme
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        # 2. Read the homepage first
        if not self._url_reader.available:
            response = "URL reader is not available right now."
            self._add_to_history(channel_id, "vargas", response)
            return response

        try:
            result = await self._url_reader.read_url(target_url)
        except Exception as e:
            logger.warning("[VARGAS] Site crawl homepage read failed: %s", e)
            response = f"Could not reach {target_url}. Check the address and try again."
            self._add_to_history(channel_id, "vargas", response)
            return response

        if not result["success"]:
            response = f"Could not read {target_url}: {result.get('error', 'unknown error')}."
            self._add_to_history(channel_id, "vargas", response)
            return response

        self._last_url_results[channel_id] = result

        # 3. Extract internal links (same domain only)
        parsed_base = urlparse(target_url)
        base_domain = parsed_base.netloc.lower().lstrip("www.")
        internal_links = []
        seen_paths = {parsed_base.path or "/"}

        for link in result.get("links", []):
            href = link.get("href", "")
            text = link.get("text", "").strip()
            if not href or not text or len(text) < 3:
                continue
            try:
                parsed = urlparse(href)
                link_domain = parsed.netloc.lower().lstrip("www.")
                path = parsed.path or "/"
                if link_domain == base_domain and path not in seen_paths:
                    seen_paths.add(path)
                    internal_links.append({"text": text, "href": href})
            except Exception:
                continue

        # Cap at 10 pages
        _MAX_CRAWL_PAGES = 10
        internal_links = internal_links[:_MAX_CRAWL_PAGES]

        if not internal_links:
            # No internal links found — just summarize the homepage
            tool_context = (
                f"[PAGE CONTENT — incorporate naturally, never say 'I read the page']\n"
                f"{self._url_reader.format_page_content(result)}\n"
                f"[END PAGE CONTENT]\n"
                f"The user asked to crawl the site, but this is the only page found. "
                f"Summarize the homepage content thoroughly."
            )
            memory_context = self._build_memory_context(user_message)
            return await self._generate_with_context(
                user_message, channel_id, history, "site_crawl",
                memory_context=memory_context, tool_context=tool_context,
                image_parts=image_parts,
            )

        # 4. Build a plan: Step 0 is already done (homepage). Steps 1-N read each link.
        plan_steps = []
        for i, link in enumerate(internal_links):
            plan_steps.append({
                "description": f"Read page: {link['text']} ({link['href'][:80]})",
                "tool_name": "url_reader",
                "tool_action": "read_url",
                "tool_params": {"url": link["href"]},
            })

        # Store the homepage result so the plan execution can include it
        self._site_crawl_homepage = {channel_id: result}

        plan = self._agent_loop.create_plan(
            channel_id, user_message, plan_steps,
        )
        plan_summary = self._agent_loop.get_plan_summary(channel_id)

        homepage_preview = result["text"][:300] + "..." if len(result["text"]) > 300 else result["text"]
        response = (
            f"I read the homepage at {target_url}.\n\n"
            f"**Homepage preview:**\n{homepage_preview}\n\n"
            f"I found {len(internal_links)} internal pages. Here's the crawl plan:\n\n"
            f"{plan_summary}\n\n"
            f"Say **yes** to crawl all pages or **no** to cancel."
        )
        self._add_to_history(channel_id, "vargas", response)
        _log_event("tool_use.log", {
            "tool": "site_crawl",
            "action": "plan_created",
            "homepage": target_url,
            "internal_links": len(internal_links),
        })
        return response

    async def _progress_callback(self, channel_id: str, message: str):
        """Progress callback for agent loop — stores progress in history.

        The Discord bot layer can override this to send real-time messages.
        """
        logger.info("[VARGAS] Task progress: %s", message[:100])
        _log_event("tool_use.log", {"tool": "agent_loop", "action": "progress", "message": message[:200]})

    async def _generate_with_context(
        self, user_message: str, channel_id: str, history: List[Dict[str, str]],
        intent: str, memory_context: str = "", tool_context: str = "",
        image_parts: list | None = None,
    ) -> str:
        """Generate a response with injected tool/memory context. Used by V2 agent loop."""
        channel_count = self._channel_interactions.get(channel_id, 0)
        attunement_context = self._build_attunement_context(channel_count)
        conversation_text = self._format_conversation(history)

        prompt_parts = [self._system_prompt, attunement_context]
        if memory_context:
            prompt_parts.append(memory_context)
        if tool_context:
            prompt_parts.append(tool_context)
        system_prompt = "\n\n".join(prompt_parts)
        user_prompt = f"{conversation_text}\n\nVargas:"

        response = None
        for attempt in range(2):
            try:
                response = self._llm.generate(
                    model=self._llm.default_model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temp=self._config.get("temperature", 0.7),
                    max_tokens=self._config.get("max_tokens", 2048),
                    image_parts=image_parts,
                )
                response = response.strip()
                break
            except Exception as e:
                logger.error("[VARGAS] Generation failed (attempt %d/2): %s", attempt + 1, e)
                if attempt == 0:
                    await asyncio.sleep(3)
        if not response:
            response = "Something broke on my end. Try again in a moment."

        # Post-response bookkeeping
        self._interaction_count += 1
        self._channel_interactions[channel_id] = self._channel_interactions.get(channel_id, 0) + 1
        self._evaluate_memory_writes(user_message, response, intent)
        self._mutate_attunement(intent, user_message)
        self._evaluate_behavioral_memory(user_message, response, history)
        if self._interaction_count % 5 == 0:
            self._persist_attunement_ev()
        self._add_to_history(channel_id, "vargas", response)
        return response

    async def respond(self, user_message: str, channel_id: str, image_parts: list | None = None) -> str:
        """Main entry point. Process a user message and return Vargas's response."""
        history = self._get_history(channel_id)
        self._add_to_history(channel_id, "user", user_message)

        # 1. Classify intent
        intent_result = classify_intent(
            llm_client=self._llm,
            user_message=user_message,
            conversation_history=history,
            confidence_threshold=self._config.get("intent", {}).get("confidence_threshold", 0.6),
        )
        intent = intent_result["intent"]
        logger.info("[VARGAS] Intent: %s (%.2f)", intent, intent_result["confidence"])

        # 2. Handle memory modification directly
        if intent == "memory_modify":
            direct_response = self._handle_memory_modify(user_message)
            if direct_response:
                self._add_to_history(channel_id, "vargas", direct_response)
                return direct_response

        # 2b. V2 — Handle plan approval/cancellation for active plans
        lower_msg = user_message.lower().strip()
        if self._agent_loop.has_active_plan(channel_id):
            if lower_msg in ("yes", "approve", "do it", "go ahead", "proceed", "y", "go"):
                self._agent_loop.approve_plan(channel_id)
                plan = await self._agent_loop.execute_plan(
                    channel_id,
                    progress_callback=self._progress_callback,
                )
                results_context = self._agent_loop.build_results_context(channel_id)
                self._agent_loop.cleanup(channel_id)
                tool_context_v2 = results_context
                # Fall through to LLM to summarize results
                memory_context = self._build_memory_context(user_message)
                return await self._generate_with_context(
                    user_message, channel_id, history, intent,
                    memory_context=memory_context, tool_context=tool_context_v2,
                    image_parts=image_parts,
                )
            elif lower_msg in ("no", "cancel", "stop", "nevermind", "n"):
                self._agent_loop.cancel_plan(channel_id)
                response = "Understood. Plan cancelled."
                self._add_to_history(channel_id, "vargas", response)
                return response

        # 2b2. V2.5 — Check pending-action latch (file write proposals awaiting approval)
        pending_result = await self._check_pending_action(channel_id, user_message)
        if pending_result and "[FILE WRITTEN" in pending_result:
            memory_context = self._build_memory_context(user_message)
            return await self._generate_with_context(
                user_message, channel_id, history, intent,
                memory_context=memory_context, tool_context=pending_result,
                image_parts=image_parts,
            )

        # 2c. V2 — Site crawl: read homepage then follow internal links via agent loop
        if intent == "site_crawl":
            return await self._handle_site_crawl(user_message, channel_id, history, image_parts)

        # 2d. V2 — Route complex tasks through agent loop
        if intent in ("task_execute", "browser_interact", "code_execute"):
            analysis = await self._agent_loop.analyze_complexity(
                user_message, self._system_prompt,
            )
            if analysis.get("needs_plan") and analysis.get("plan"):
                plan = self._agent_loop.create_plan(
                    channel_id, user_message, analysis["plan"],
                )
                plan_summary = self._agent_loop.get_plan_summary(channel_id)
                response = (
                    f"Here's what I'll do:\n\n{plan_summary}\n\n"
                    f"Say **yes** to proceed or **no** to cancel."
                )
                self._add_to_history(channel_id, "vargas", response)
                _log_event("tool_use.log", {
                    "tool": "agent_loop",
                    "action": "plan_created",
                    "steps": len(analysis["plan"]),
                    "goal": user_message[:200],
                })
                return response

        # 3. Build context layers
        memory_context = self._build_memory_context(user_message)
        tool_context = ""
        memory_summary_context = ""

        # 4. Handle intent-specific tool use
        if intent == "memory_inspect":
            memory_summary_context = self._build_memory_summary()
            tool_context = (
                f"[MEMORY SUMMARY — the user is asking about your memory]\n"
                f"{memory_summary_context}\n"
                f"[END MEMORY SUMMARY]\n"
                f"Summarize this naturally in your own voice. Do not list items mechanically."
            )
            _log_event("tool_use.log", {"tool": "memory_inspect", "trigger": user_message[:200]})

        elif intent == "url_read":
            from project_vargas.agent.intent_classifier import _URL_REGEX
            urls = _URL_REGEX.findall(user_message)

            if not urls:
                # No URL in message — try to find a matching link from last page read
                last_result = self._last_url_results.get(channel_id)
                if last_result and last_result.get("links"):
                    matched = self._match_link_from_context(user_message, last_result["links"])
                    if matched:
                        urls = [matched]

            # Deduplicate while preserving order
            seen = set()
            unique_urls = []
            for u in urls:
                normalized = u.lower().rstrip("/")
                if normalized not in seen:
                    seen.add(normalized)
                    unique_urls.append(u)
            urls = unique_urls[:10]  # Cap at 10 URLs per message

            if urls and self._url_reader.available:
                try:
                    if len(urls) == 1:
                        # Single URL — original behavior
                        target_url = urls[0]
                        result = await self._url_reader.read_url(target_url)
                        if result["success"]:
                            self._last_url_results[channel_id] = result
                            tool_context = (
                                f"[PAGE CONTENT — incorporate naturally, never say 'I read the page']\n"
                                f"{self._url_reader.format_page_content(result)}\n"
                                f"[END PAGE CONTENT]\n"
                                f"Summarize and respond to the page content naturally. "
                                f"If the page has links to other pages, mention them if relevant. "
                                f"The user can ask you to follow any of those links."
                            )
                        else:
                            tool_context = (
                                f"[URL READ FAILED — {result['error']}]\n"
                                f"Tell the user honestly that you could not read that page. "
                                f"Mention the specific error if helpful."
                            )
                        _log_event("tool_use.log", {
                            "tool": "url_read",
                            "url": target_url[:200],
                            "success": result["success"],
                        })
                    else:
                        # Multiple URLs — read each sequentially, combine results
                        all_parts = [f"[MULTI-PAGE READ — {len(urls)} URLs requested]"]
                        success_count = 0
                        fail_count = 0
                        last_successful = None
                        for i, target_url in enumerate(urls, 1):
                            try:
                                result = await self._url_reader.read_url(target_url)
                                if result["success"]:
                                    success_count += 1
                                    last_successful = result
                                    all_parts.append(f"\n--- Page {i}: {target_url} ---")
                                    # Use shorter text per page to fit in context
                                    page_text = result["text"]
                                    if len(page_text) > 3000:
                                        page_text = page_text[:3000] + "\n[Truncated]"
                                    all_parts.append(page_text)
                                else:
                                    fail_count += 1
                                    all_parts.append(f"\n--- Page {i}: {target_url} --- FAILED: {result['error']}")
                            except Exception as e:
                                fail_count += 1
                                all_parts.append(f"\n--- Page {i}: {target_url} --- ERROR: {e}")
                            _log_event("tool_use.log", {
                                "tool": "url_read",
                                "url": target_url[:200],
                                "success": result.get("success", False) if 'result' in dir() else False,
                            })

                        all_parts.append(f"\n[END MULTI-PAGE READ — {success_count} succeeded, {fail_count} failed]")
                        if last_successful:
                            self._last_url_results[channel_id] = last_successful

                        tool_context = (
                            "\n".join(all_parts) + "\n"
                            "Summarize what you found across ALL pages. "
                            "Highlight the key content from each repo/page. "
                            "Note any that failed."
                        )
                except Exception as e:
                    logger.warning("[VARGAS] URL read failed: %s", e)

        elif intent == "web_search":
            if self._web_search.available:
                try:
                    search_query = self._extract_search_query(user_message, history)
                    results = await self._web_search.search(search_query, num_results=5)
                    if results:
                        tool_context = self._web_search.format_results(results)
                        tool_context = (
                            f"[WEB RESULTS — incorporate naturally, never mention searching]\n"
                            f"{tool_context}\n"
                            f"[END WEB RESULTS]"
                        )
                    else:
                        tool_context = (
                            "[WEB SEARCH returned no results]\n"
                            "Tell the user honestly that the search returned nothing useful."
                        )
                    _log_event("tool_use.log", {
                        "tool": "web_search",
                        "query": search_query[:200],
                        "results_count": len(results),
                    })
                except Exception as e:
                    logger.warning("[VARGAS] Web search failed: %s", e)

        elif intent == "skill_list":
            if self._openclaw.available:
                skill_names = self._openclaw.list_skill_names()
                if skill_names:
                    grouped = ", ".join(skill_names)
                    tool_context = (
                        f"[MANDATORY — SKILL LIST]\n"
                        f"The user asked you to list your skills. You MUST include the actual skill names below.\n"
                        f"You have {len(skill_names)} active OpenClaw skills:\n{grouped}\n"
                        f"[END SKILL LIST]\n"
                        f"You MUST present these skills in your response. Group them by category. "
                        f"Do NOT say you have no directory or no list. The list above IS your directory. "
                        f"Present it naturally but completely — every skill name must appear."
                    )
                else:
                    tool_context = (
                        "[SKILL LIST — no skills loaded]\n"
                        "Tell the user that the skill system is available but no skills were loaded."
                    )
                _log_event("tool_use.log", {"tool": "skill_list", "count": len(skill_names)})

        elif intent == "skill_invoke":
            if self._openclaw.available:
                match = self._openclaw.match_skill(user_message)
                skill_context = self._openclaw.format_skill_context(match)
                if skill_context:
                    tool_context = skill_context
                _log_event("tool_use.log", {
                    "tool": "openclaw",
                    "query": user_message[:200],
                    "matched_skill": match.get("skill_name"),
                    "confidence": match.get("confidence", 0),
                })

        elif intent == "challenge":
            ch_count = self._channel_interactions.get(channel_id, 0)
            if ch_count >= 5:
                tool_context = (
                    "[CHALLENGE SIGNAL — the user appears to be circling, avoiding, "
                    "or over-engineering. Consider whether a direct challenge or reframe "
                    "is appropriate. Challenge only if earned by continuity.]\n"
                )
                _log_event("challenge_log.log", {"trigger": user_message[:200]})
            else:
                logger.info("[VARGAS] Challenge suppressed — only %d interactions in channel", ch_count)

        # 4b. Bounded Autonomy — self-escalate if circling without acting
        if intent == "converse" and not tool_context:
            if self._should_self_escalate(user_message, history):
                escalation_context = await self._self_escalate(user_message, history, channel_id)
                if escalation_context:
                    tool_context = escalation_context

        # 5. Build attunement context from emoji vector
        channel_count = self._channel_interactions.get(channel_id, 0)
        attunement_context = self._build_attunement_context(channel_count)

        # 6. Build the full prompt
        conversation_text = self._format_conversation(history)

        prompt_parts = [self._system_prompt]
        prompt_parts.append(attunement_context)
        if memory_context:
            prompt_parts.append(memory_context)
        if tool_context:
            prompt_parts.append(tool_context)

        system_prompt = "\n\n".join(prompt_parts)

        user_prompt = f"{conversation_text}\n\nVargas:"

        # 6. Generate response (with one retry on failure)
        response = None
        for attempt in range(2):
            try:
                response = self._llm.generate(
                    model=self._llm.default_model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temp=self._config.get("temperature", 0.7),
                    max_tokens=self._config.get("max_tokens", 2048),
                    image_parts=image_parts,
                )
                response = response.strip()
                break
            except Exception as e:
                logger.error("[VARGAS] Generation failed (attempt %d/2): %s", attempt + 1, e)
                if attempt == 0:
                    import time
                    time.sleep(3)
        if not response:
            response = "Something broke on my end. Try again in a moment."

        # 7. Post-response memory evaluation
        self._interaction_count += 1
        self._channel_interactions[channel_id] = self._channel_interactions.get(channel_id, 0) + 1
        self._evaluate_memory_writes(user_message, response, intent)

        # 8. Mutate attunement emoji vector based on interaction
        self._mutate_attunement(intent, user_message)

        # 9. Behavioral pattern detection (every 10 interactions)
        self._evaluate_behavioral_memory(user_message, response, history)

        # 10. Persist attunement EV periodically (every 5 interactions)
        if self._interaction_count % 5 == 0:
            self._persist_attunement_ev()
            _log_event("attunement.log", {
                "interaction": self._interaction_count,
                "metrics": self._attunement_ev.metrics,
                "sequence_length": self._attunement_ev.length,
            })

        # 11. V2.5 — Detect file-write proposals in Vargas's response and set pending latch
        self._detect_file_write_proposal(response, channel_id)

        # 12. Store response in history
        self._add_to_history(channel_id, "vargas", response)

        return response

    def _format_conversation(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history for the prompt."""
        if not history:
            return ""

        lines = []
        # Use last N messages for context window efficiency
        recent = history[-10:]
        for msg in recent:
            if msg["role"] == "user":
                lines.append(f"User: {msg['content']}")
            else:
                lines.append(f"Vargas: {msg['content']}")

        return "\n\n".join(lines)

    def respond_sync(self, user_message: str, channel_id: str) -> str:
        """Synchronous wrapper for respond()."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(
                        asyncio.run, self.respond(user_message, channel_id)
                    ).result()
            else:
                return loop.run_until_complete(self.respond(user_message, channel_id))
        except RuntimeError:
            return asyncio.run(self.respond(user_message, channel_id))

    def health_check(self) -> Dict[str, Any]:
        """Return system health status."""
        return {
            "agent": "vargas",
            "version": "2.0",
            "status": "online",
            "memory": self._memory.health_check(),
            "web_search": self._web_search.available,
            "openclaw": self._openclaw.available,
            # V2 tools
            "browser": self._browser.available,
            "shell": self._shell.available,
            "file_io": self._file_io.available,
            "agent_loop": True,
            "llm": self._llm.stats(),
            "conversations_active": len(self._conversations),
        }
