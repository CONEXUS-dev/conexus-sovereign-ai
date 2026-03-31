"""
VARGAS V4 Intent Router — Request Classification Layer

Classifies incoming user messages into intent categories that determine
how the perception loop processes them. The router does not execute
anything — it reads the request and decides what kind of request it is.

Intent categories:
    QUERY: Information retrieval, questions, lookups
    ACTION: Tool execution, file operations, system commands
    MEMORY: Memory operations (store, correct, forget, query)
    CHALLENGE: Contradiction surface, evidence-based pushback
    REFLECTION: Self-assessment, status checks, posture queries
    CONVERSATION: General dialogue, no specific operation
    GOVERNANCE: Constitutional queries, trust model questions

Reference: Master Blueprint Section 12.4 — intent_router.py
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Intent constants
INTENT_QUERY = "QUERY"
INTENT_ACTION = "ACTION"
INTENT_MEMORY = "MEMORY"
INTENT_CHALLENGE = "CHALLENGE"
INTENT_REFLECTION = "REFLECTION"
INTENT_CONVERSATION = "CONVERSATION"
INTENT_GOVERNANCE = "GOVERNANCE"

# Pattern-based intent signals
MEMORY_COMMANDS = ["!forget", "!correct", "!query_memory", "!remember"]
ACTION_SIGNALS = [
    "read file", "write file", "search for", "browse", "execute",
    "run", "create", "delete", "modify", "open", "list files",
    "shell", "command",
]
QUERY_SIGNALS = [
    "what is", "what are", "how do", "how does", "where is",
    "who is", "when did", "why does", "explain", "describe",
    "tell me about", "look up", "find",
]
REFLECTION_SIGNALS = [
    "!status", "!cockpit", "how are you", "what is your state",
    "show posture", "e-vector", "what do you think about yourself",
    "system status",
]
GOVERNANCE_SIGNALS = [
    "trust tier", "constitution", "sovereign state", "boot integrity",
    "what can you do", "what are you not allowed", "permissions",
    "forbidden", "your rules", "your constraints",
]
CHALLENGE_SIGNALS = [
    "contradict", "but you said", "that conflicts", "earlier you",
    "inconsistent", "you claimed", "doesn't match", "disagree",
]


class IntentRouter:
    """Classifies user messages into intent categories.

    The router uses a combination of:
    1. Exact command matching (memory commands, status commands)
    2. Signal phrase detection (weighted keyword matching)
    3. Confidence scoring based on signal density

    It does NOT use an LLM for classification — this must be fast,
    deterministic, and independent of external services.

    Attributes:
        last_intent: The most recently classified intent.
        last_confidence: Confidence of the last classification.
    """

    def __init__(self):
        self.last_intent: str = INTENT_CONVERSATION
        self.last_confidence: float = 0.0
        logger.info("[INTENT_ROUTER] Initialized")

    def classify(self, message: str) -> Dict[str, Any]:
        """Classify a user message into an intent category.

        Args:
            message: The raw user message text.

        Returns:
            Dict containing:
                - intent: The classified intent category
                - confidence: Classification confidence (0.0-1.0)
                - signals: List of matched signal phrases
                - is_command: Whether this is an exact command match
        """
        if not message or not message.strip():
            return self._result(INTENT_CONVERSATION, 0.5, [], False)

        msg_lower = message.lower().strip()

        # Check exact commands first
        command_result = self._check_commands(msg_lower)
        if command_result:
            return command_result

        # Score each intent category
        scores: Dict[str, tuple] = {}
        scores[INTENT_MEMORY] = self._score_signals(msg_lower, MEMORY_COMMANDS)
        scores[INTENT_ACTION] = self._score_signals(msg_lower, ACTION_SIGNALS)
        scores[INTENT_QUERY] = self._score_signals(msg_lower, QUERY_SIGNALS)
        scores[INTENT_REFLECTION] = self._score_signals(msg_lower, REFLECTION_SIGNALS)
        scores[INTENT_GOVERNANCE] = self._score_signals(msg_lower, GOVERNANCE_SIGNALS)
        scores[INTENT_CHALLENGE] = self._score_signals(msg_lower, CHALLENGE_SIGNALS)

        # Find the highest scoring intent
        best_intent = INTENT_CONVERSATION
        best_score = 0.0
        best_signals: List[str] = []

        for intent, (score, signals) in scores.items():
            if score > best_score:
                best_score = score
                best_intent = intent
                best_signals = signals

        # Require minimum confidence to override CONVERSATION default
        if best_score < 0.3:
            best_intent = INTENT_CONVERSATION
            best_score = 0.5
            best_signals = []

        # Check for question marks as query boost
        if "?" in message and best_intent == INTENT_CONVERSATION:
            best_intent = INTENT_QUERY
            best_score = 0.6
            best_signals = ["question_mark"]

        result = self._result(best_intent, best_score, best_signals, False)
        self.last_intent = result["intent"]
        self.last_confidence = result["confidence"]

        logger.info(
            "[INTENT_ROUTER] Classified: intent=%s confidence=%.2f signals=%s",
            result["intent"], result["confidence"], result["signals"],
        )

        return result

    def _check_commands(self, msg_lower: str) -> Optional[Dict[str, Any]]:
        """Check for exact command matches."""
        for cmd in MEMORY_COMMANDS:
            if msg_lower.startswith(cmd):
                return self._result(INTENT_MEMORY, 1.0, [cmd], True)

        for cmd in ["!status", "!cockpit"]:
            if msg_lower.startswith(cmd):
                return self._result(INTENT_REFLECTION, 1.0, [cmd], True)

        return None

    @staticmethod
    def _score_signals(msg_lower: str, signals: List[str]) -> tuple:
        """Score how many signals match in the message.

        Uses a floor-based scoring: any single match gives at least 0.4,
        each additional match adds 0.15, capped at 1.0. This ensures
        categories with many signals aren't penalized for breadth.

        Returns:
            Tuple of (normalized_score, matched_signals).
        """
        matched = []
        for signal in signals:
            if signal in msg_lower:
                matched.append(signal)

        if not matched:
            return (0.0, [])

        score = 0.4 + (len(matched) - 1) * 0.15
        score = min(1.0, score)

        return (round(score, 4), matched)

    @staticmethod
    def _result(
        intent: str, confidence: float, signals: List[str], is_command: bool
    ) -> Dict[str, Any]:
        """Build a classification result dict."""
        return {
            "intent": intent,
            "confidence": round(confidence, 4),
            "signals": signals,
            "is_command": is_command,
        }

    def get_trust_tier_for_intent(self, intent: str) -> int:
        """Return the minimum trust tier required for an intent.

        Args:
            intent: The classified intent.

        Returns:
            Minimum trust tier (0-4).
        """
        tier_map = {
            INTENT_CONVERSATION: 0,
            INTENT_QUERY: 0,
            INTENT_REFLECTION: 0,
            INTENT_GOVERNANCE: 0,
            INTENT_MEMORY: 1,
            INTENT_CHALLENGE: 0,
            INTENT_ACTION: 2,
        }
        return tier_map.get(intent, 0)

    def summary(self) -> Dict[str, Any]:
        """Return router status summary."""
        return {
            "last_intent": self.last_intent,
            "last_confidence": self.last_confidence,
            "available_intents": [
                INTENT_QUERY, INTENT_ACTION, INTENT_MEMORY,
                INTENT_CHALLENGE, INTENT_REFLECTION,
                INTENT_CONVERSATION, INTENT_GOVERNANCE,
            ],
        }
