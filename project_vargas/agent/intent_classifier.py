"""
Project Vargas — Intent Classifier

Pattern-based intent classification that runs before response generation.
Determines what Vargas should do with each message. Fast, reliable,
and does not consume an LLM call.

Intents:
  - converse: Normal conversation
  - challenge: (detected by the agent based on conversational patterns, not here)
  - memory_inspect: User wants to know what Vargas remembers
  - memory_modify: User wants to correct, add, or erase memory
  - web_search: User needs live information from the web
  - skill_invoke: User needs a specific capability (code, analysis, etc.)

Intent is never surfaced to the user. It only shapes internal routing.
"""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Regex to detect URLs in messages (includes bare domains like investor.example.media)
# Known TLDs that are unlikely to be plain English words
_DOMAIN_TLDS = (
    "com|org|net|edu|gov|io|co|dev|app|media|tech|ai|church|live|online|site|"
    "info|biz|me|us|uk|ca|au|de|fr|xyz|club|store|shop|blog|world|global|"
    "design|art|tv|fm|gg|cc|ly|to|in|es|it|nl|be|ch|at|pl|ru|br|jp|kr|cn"
)
_URL_REGEX = re.compile(
    r'https?://[^\s<>"]+|'
    r'www\.[^\s<>"]+|'
    r'\b[a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)*\.(?:' + _DOMAIN_TLDS + r')(?:/[^\s<>"]*)?',
    re.IGNORECASE,
)

VALID_INTENTS = [
    "converse",
    "challenge",
    "memory_inspect",
    "memory_modify",
    "web_search",
    "url_read",
    "skill_invoke",
    "skill_list",
    # V2 autonomous intents
    "task_execute",
    "browser_interact",
    "code_execute",
    "site_crawl",
]

# Pattern groups for classification
MEMORY_INSPECT_PATTERNS = [
    "what do you know about me",
    "what do you remember",
    "do you remember",
    "what have you learned",
    "what's in your memory",
    "what do you have on me",
    "show me your memory",
    "what are you holding",
    "tell me what you know",
]

MEMORY_MODIFY_PATTERNS = [
    "forget that", "forget everything", "forget my",
    "clear your memory", "wipe your memory", "reset your memory",
    "start fresh", "start over",
    "remember that", "remember this",
    "actually my name is", "actually i",
    "no that's wrong", "that's not right",
    "let me correct", "i should clarify",
]

WEB_SEARCH_PATTERNS = [
    "look up", "search for", "search the web",
    "google", "find me information",
    "what's the latest", "what's happening with",
    "current news", "recent news",
    "find out about", "look into",
    "what's going on with",
    "search and", "what can you find",
    "find information", "create a profile",
    "build a profile", "search online",
    "could you try searching", "try searching",
    "see what info you can find", "see what you can find",
    "find what you can", "what info can you find",
]

SKILL_LIST_PATTERNS = [
    "list your skills", "list all skills", "what skills do you have",
    "what can you do", "what are your skills", "what are your capabilities",
    "show me your skills", "what tools do you have", "what are your tools",
    "list your tools", "list your capabilities",
    "please list all your open claw skills",
    "list all your openclaw", "openclaw skills",
    "openclaw skills do you have", "list each skill", "please list each",
    "your skills", "your capabilities", "skills do you have",
    "what skills", "list skills", "show skills", "show your skills",
]

URL_READ_PATTERNS = [
    "read this url", "read this page", "read this site",
    "browse this", "go to this site", "go to this url",
    "check this link", "check this url", "check this site",
    "open this link", "open this url", "open this page",
    "what does this page say", "what does this site say",
    "read the page", "visit this", "pull up this",
    "can you read", "can you browse",
    # Link following from previously read pages
    "click the", "click on the", "follow the link",
    "follow that link", "open the link", "read the link",
    "read full story", "full story", "read more",
    "go to the", "navigate to", "take me to",
    "start on the", "start from the",
]

SKILL_INVOKE_PATTERNS = [
    "write a function", "write code", "write a script",
    "help me code", "help me write",
    "analyze this", "strategic analysis",
    "extract data", "parse this",
    "regex", "sql query",
    "create a plan", "build a",
    "debug this", "fix this code",
]

# V2 — Task execution patterns (multi-step autonomous tasks)
TASK_EXECUTE_PATTERNS = [
    "go do", "go and", "please do", "i need you to",
    "can you do", "could you do", "would you",
    "take care of", "handle this", "execute this",
    "complete this task", "do this for me",
    "set up", "set this up", "configure",
    "automate", "run this task", "perform",
    "get this done", "make it happen",
    "download", "install", "deploy",
    "save this to", "write this to a file",
    "create a file", "make a file",
    "you are authorized", "authorized",
    "i confirm", "i approve",
]

# V2 — Browser interaction patterns
BROWSER_INTERACT_PATTERNS = [
    "go to the website", "go to the site",
    "browse to", "navigate to the",
    "open the website", "open the site",
    "log into", "log in to", "sign into",
    "fill out the form", "fill in the form",
    "click the button", "click on",
    "submit the form", "interact with",
    "screenshot of", "take a screenshot",
    "what's on the page", "what does the page look like",
    "scroll down", "scroll up",
]

# V2 — Site crawl detection: keyword combination approach
# If message has a CRAWL_ACTION word AND a CRAWL_SCOPE word, it's a site_crawl
CRAWL_ACTION_WORDS = [
    "crawl", "spider", "map",
]
CRAWL_SCOPE_WORDS = [
    "site", "website", "domain", "homepage",
    "all the links", "all the pages", "every page", "all pages",
    "entire", "whole", "everything",
]
# Additional explicit phrases that always mean site_crawl
SITE_CRAWL_PATTERNS = [
    "crawl my site", "crawl my domain", "crawl the site",
    "crawl my website", "crawl the website",
    "read the whole site", "read the entire site",
    "read my whole site", "read my entire site",
    "look through all the links", "look through all the pages",
    "read all the pages", "read every page",
    "go through my site", "go through the site",
    "go through all the links", "go through all the pages",
    "spider my site", "spider the site",
    "map my site", "map the site",
    "read everything on my site", "read everything on the site",
    "start on the homepage", "start from the homepage",
]


def _is_site_crawl(lower_msg: str) -> bool:
    """Detect site crawl intent using flexible keyword combos + explicit patterns."""
    # Check explicit patterns first
    for pattern in SITE_CRAWL_PATTERNS:
        if pattern in lower_msg:
            return True
    # Check keyword combinations: action + scope
    has_action = any(w in lower_msg for w in CRAWL_ACTION_WORDS)
    has_scope = any(w in lower_msg for w in CRAWL_SCOPE_WORDS)
    if has_action and has_scope:
        return True
    # Check "read/go through" + scope (broader action words that need scope context)
    broad_actions = ["read", "go through", "look through"]
    has_broad = any(w in lower_msg for w in broad_actions)
    scope_with_broad = ["whole", "entire", "all the links", "all the pages",
                        "every page", "all pages", "everything on"]
    has_scope_broad = any(w in lower_msg for w in scope_with_broad)
    if has_broad and has_scope_broad:
        return True
    return False

# V2 — Code execution patterns
CODE_EXECUTE_PATTERNS = [
    "run this command", "run this script",
    "execute this", "run the following",
    "run python", "run node", "run npm",
    "pip install", "npm install",
    "git clone", "git pull", "git push",
    "compile", "make build",
    "check the output of", "what does this command output",
]


def classify_intent(
    llm_client: Any,
    user_message: str,
    conversation_history: List[Dict[str, str]],
    confidence_threshold: float = 0.6,
) -> Dict[str, Any]:
    """Classify the user's intent from their message and conversation context.

    Uses fast pattern matching. No LLM call required.

    Args:
        llm_client: GeminiLLMClient instance (unused, kept for interface compatibility)
        user_message: The latest message from the user
        conversation_history: List of {"role": "user"|"vargas", "content": "..."}
        confidence_threshold: Below this, default to "converse"

    Returns:
        {"intent": str, "confidence": float, "reasoning": str}
    """
    lower = user_message.lower().strip()

    # Check memory modify first (higher priority than inspect)
    for pattern in MEMORY_MODIFY_PATTERNS:
        if pattern in lower:
            logger.info("[INTENT] memory_modify — matched: '%s'", pattern)
            return {"intent": "memory_modify", "confidence": 0.9, "reasoning": f"Matched: {pattern}"}

    # Check memory inspect
    for pattern in MEMORY_INSPECT_PATTERNS:
        if pattern in lower:
            logger.info("[INTENT] memory_inspect — matched: '%s'", pattern)
            return {"intent": "memory_inspect", "confidence": 0.9, "reasoning": f"Matched: {pattern}"}

    # V2 — Check site crawl (before url_read — more specific)
    if _is_site_crawl(lower):
        logger.info("[INTENT] site_crawl — keyword combo or pattern matched")
        return {"intent": "site_crawl", "confidence": 0.90, "reasoning": "Site crawl keywords detected"}

    # Check URL read — detect URLs in message or explicit "read this" patterns
    if _URL_REGEX.search(user_message):
        logger.info("[INTENT] url_read — URL detected in message")
        return {"intent": "url_read", "confidence": 0.95, "reasoning": "URL detected in message"}
    for pattern in URL_READ_PATTERNS:
        if pattern in lower:
            logger.info("[INTENT] url_read — matched: '%s'", pattern)
            return {"intent": "url_read", "confidence": 0.9, "reasoning": f"Matched: {pattern}"}

    # Check web search
    for pattern in WEB_SEARCH_PATTERNS:
        if pattern in lower:
            logger.info("[INTENT] web_search — matched: '%s'", pattern)
            return {"intent": "web_search", "confidence": 0.85, "reasoning": f"Matched: {pattern}"}

    # Check skill list (before skill invoke — more specific)
    for pattern in SKILL_LIST_PATTERNS:
        if pattern in lower:
            logger.info("[INTENT] skill_list — matched: '%s'", pattern)
            return {"intent": "skill_list", "confidence": 0.9, "reasoning": f"Matched: {pattern}"}

    # Check skill invoke
    for pattern in SKILL_INVOKE_PATTERNS:
        if pattern in lower:
            logger.info("[INTENT] skill_invoke — matched: '%s'", pattern)
            return {"intent": "skill_invoke", "confidence": 0.85, "reasoning": f"Matched: {pattern}"}

    # V2 — Check browser interaction
    for pattern in BROWSER_INTERACT_PATTERNS:
        if pattern in lower:
            logger.info("[INTENT] browser_interact — matched: '%s'", pattern)
            return {"intent": "browser_interact", "confidence": 0.85, "reasoning": f"Matched: {pattern}"}

    # V2 — Check code execution
    for pattern in CODE_EXECUTE_PATTERNS:
        if pattern in lower:
            logger.info("[INTENT] code_execute — matched: '%s'", pattern)
            return {"intent": "code_execute", "confidence": 0.85, "reasoning": f"Matched: {pattern}"}

    # V2 — Check task execution (broadest — check last)
    for pattern in TASK_EXECUTE_PATTERNS:
        if pattern in lower:
            logger.info("[INTENT] task_execute — matched: '%s'", pattern)
            return {"intent": "task_execute", "confidence": 0.80, "reasoning": f"Matched: {pattern}"}

    # Default: converse
    logger.info("[INTENT] converse — no special pattern matched")
    return {"intent": "converse", "confidence": 0.9, "reasoning": "Default conversation"}
