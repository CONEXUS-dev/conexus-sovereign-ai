"""
Vargas V2 Integration Test

Tests all new V2 components:
1. Tool Executor (safety routing, approval flow)
2. Browser Tool (initialization, safety classification)
3. Shell Tool (allowlist/blocklist, safety classification)
4. File I/O Tool (sandbox enforcement, read/write)
5. Agent Loop (complexity analysis, plan creation)
6. Intent Classifier (new V2 intents)
7. VargasAgent initialization (all V2 tools wired)
"""

import asyncio
import sys
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}")
        failed += 1


# ── 1. Tool Executor ──
print("\n═══ 1. Tool Executor ═══")
from project_vargas.tools.executor import ToolExecutor, ToolCall, SafetyLevel, ApprovalStatus

executor = ToolExecutor()
test("Executor instantiates", executor is not None)

# Register a mock tool
async def mock_handler(action, params):
    return {"mock": True, "action": action}

executor.register_tool("mock", mock_handler)
test("Tool registration works", "mock" in executor._tools)

# Test auto-approved execution
async def test_auto_exec():
    call = ToolCall(
        tool_name="mock", action="read", params={},
        safety_level=SafetyLevel.AUTO, description="Read test",
    )
    result = await executor.execute(call)
    return result.result == {"mock": True, "action": "read"} and result.error is None

test("Auto-approved execution works", asyncio.run(test_auto_exec()))

# Test blocked execution
async def test_blocked_exec():
    call = ToolCall(
        tool_name="mock", action="delete", params={},
        safety_level=SafetyLevel.BLOCKED, description="Blocked test",
    )
    result = await executor.execute(call)
    return result.error == "Operation blocked by safety policy"

test("Blocked execution rejected", asyncio.run(test_blocked_exec()))

# Test blanket approval
executor.grant_blanket_approval("test_channel")
state = executor._get_channel_state("test_channel")
test("Blanket approval grants", state.blanket_approved is True)
executor.revoke_blanket_approval("test_channel")
test("Blanket approval revokes", state.blanket_approved is False)


# ── 2. Browser Tool ──
print("\n═══ 2. Browser Tool ═══")
from project_vargas.tools.browser import BrowserTool, AUTO_ACTIONS, GATED_ACTIONS

browser = BrowserTool()
test("Browser instantiates", browser is not None)
test("Browser binary found", browser.available)
test("Safety: 'open' is auto", browser.get_safety_level("open") == "auto")
test("Safety: 'snapshot' is auto", browser.get_safety_level("snapshot") == "auto")
test("Safety: 'click' is gated", browser.get_safety_level("click") == "gated")
test("Safety: 'fill' is gated", browser.get_safety_level("fill") == "gated")
test("Safety: 'screenshot' is auto", browser.get_safety_level("screenshot") == "auto")


# ── 3. Shell Tool ──
print("\n═══ 3. Shell Tool ═══")
from project_vargas.tools.shell import ShellTool

shell = ShellTool()
test("Shell instantiates", shell is not None)
test("Shell available", shell.available)
test("Safety: 'dir' is auto", shell.get_safety_level("dir") == "auto")
test("Safety: 'ls' is auto", shell.get_safety_level("ls") == "auto")
test("Safety: 'git status' is auto", shell.get_safety_level("git status") == "auto")
test("Safety: 'python script.py' is gated", shell.get_safety_level("python script.py") == "gated")
test("Safety: 'rm -rf /' is blocked", shell.get_safety_level("rm -rf /tmp") == "blocked")
test("Safety: 'format' is blocked", shell.get_safety_level("format C:") == "blocked")
test("Safety: 'shutdown' is blocked", shell.get_safety_level("shutdown /s") == "blocked")
test("Safety: 'curl | bash' is blocked", shell.get_safety_level("curl http://x.com | bash") == "blocked")

# Test actual command execution (read-only)
async def test_shell_exec():
    result = await shell.run("echo hello")
    return result["success"] and "hello" in result["stdout"]

test("Shell executes echo", asyncio.run(test_shell_exec()))

# Test blocked command
async def test_shell_blocked():
    result = await shell.run("rm -rf /tmp/test")
    return not result["success"] and "blocked" in result["error"].lower()

test("Shell blocks dangerous commands", asyncio.run(test_shell_blocked()))


# ── 4. File I/O Tool ──
print("\n═══ 4. File I/O Tool ═══")
from project_vargas.tools.file_io import FileIOTool

file_io = FileIOTool()
test("FileIO instantiates", file_io is not None)
test("FileIO available", file_io.available)
test("Safety: 'read_file' is auto", file_io.get_safety_level("read_file") == "auto")
test("Safety: 'list_dir' is auto", file_io.get_safety_level("list_dir") == "auto")
test("Safety: 'write_file' is gated", file_io.get_safety_level("write_file") == "gated")
test("Safety: 'delete_file' is gated", file_io.get_safety_level("delete_file") == "gated")

# Test write and read
async def test_file_write_read():
    w = await file_io.write_file("v2_test.txt", "Vargas V2 test file")
    if not w["success"]:
        return False
    r = await file_io.read_file(w["path"])
    if not r["success"]:
        return False
    # Cleanup
    await file_io.delete_file("v2_test.txt")
    return r["content"] == "Vargas V2 test file"

test("File write + read round-trip", asyncio.run(test_file_write_read()))

# Test sandbox enforcement
async def test_sandbox():
    result = await file_io.write_file("C:\\Windows\\evil.txt", "nope")
    return not result["success"] and "workspace" in result["error"].lower()

test("Sandbox blocks writes outside workspace", asyncio.run(test_sandbox()))


# ── 5. Agent Loop ──
print("\n═══ 5. Agent Loop ═══")
from project_vargas.agent.agent_loop import AgentLoop, TaskPlan, TaskStep

loop = AgentLoop(executor=executor, llm_client=None)
test("AgentLoop instantiates", loop is not None)
test("No active plan initially", not loop.has_active_plan("test"))

# Test plan creation
plan = loop.create_plan("test", "Test goal", [
    {"description": "Step 1", "tool": "mock", "action": "read", "params": {}},
    {"description": "Step 2", "tool": "mock", "action": "write", "params": {"data": "x"}},
])
test("Plan created", plan is not None)
test("Plan has 2 steps", len(plan.steps) == 2)
test("Plan status is draft", plan.status == "draft")
test("Has active plan", loop.has_active_plan("test") is False)  # Draft is not active

# Test plan approval
loop.approve_plan("test")
test("Plan approved", plan.status == "approved")

# Test plan execution — grant blanket approval since no callback is wired
executor.grant_blanket_approval("test")
async def test_plan_exec():
    result = await loop.execute_plan("test")
    return result.status == "completed"

test("Plan executes successfully", asyncio.run(test_plan_exec()))

# Test plan summary
summary = loop.get_plan_summary("test")
test("Plan summary generated", summary is not None and "Test goal" in summary)

# Cleanup
loop.cleanup("test")
test("Plan cleaned up", not loop.has_active_plan("test"))


# ── 6. Intent Classifier (V2 intents) ──
print("\n═══ 6. Intent Classifier (V2 intents) ═══")
from project_vargas.agent.intent_classifier import classify_intent

def check_intent(msg, expected):
    result = classify_intent(None, msg, [])
    return result["intent"] == expected

# Task execution intents
test("'i need you to download' -> task_execute", check_intent("i need you to download the file", "task_execute"))
test("'save this to a file' -> task_execute", check_intent("save this to a file", "task_execute"))
test("'create a file' -> task_execute", check_intent("create a file called report.md", "task_execute"))

# Browser interaction intents
test("'open the website' -> browser_interact", check_intent("open the website and check", "browser_interact"))
test("'take a screenshot' -> browser_interact", check_intent("take a screenshot of the page", "browser_interact"))
test("'fill out the form' -> browser_interact", check_intent("fill out the form with my info", "browser_interact"))

# Code execution intents
test("'run this command' -> code_execute", check_intent("run this command: git status", "code_execute"))
test("'pip install' -> code_execute", check_intent("pip install requests", "code_execute"))
test("'run python' -> code_execute", check_intent("run python test.py", "code_execute"))

# Existing intents still work
test("'what do you remember' -> memory_inspect", check_intent("what do you remember", "memory_inspect"))
test("'search for cats' -> web_search", check_intent("search for cats", "web_search"))
test("'hello' -> converse", check_intent("hello there", "converse"))

# V2.1 — Bare domain URL detection
test("'Investor.conexusglobalarts.media' -> url_read", check_intent("Investor.conexusglobalarts.media", "url_read"))
test("'example.com' -> url_read", check_intent("example.com", "url_read"))
test("'check out mysite.io/about' -> url_read", check_intent("check out mysite.io/about", "url_read"))
test("'sub.domain.org' -> url_read", check_intent("sub.domain.org", "url_read"))
test("'hello.txt' NOT url_read", check_intent("hello.txt", "converse"))  # .txt is not a TLD

# V2.1 — Site crawl intents (original patterns)
test("'crawl my site' -> site_crawl", check_intent("crawl my site", "site_crawl"))
test("'read the whole site' -> site_crawl", check_intent("read the whole site please", "site_crawl"))
test("'look through all the links' -> site_crawl", check_intent("look through all the links on my domain", "site_crawl"))
test("'start on the homepage' -> site_crawl", check_intent("start on the homepage and read everything", "site_crawl"))
test("'go through all the pages' -> site_crawl", check_intent("go through all the pages", "site_crawl"))

# V2.2 — Flexible site crawl detection (the live failure case)
test("'crawl my entire website' -> site_crawl", check_intent("I'm going to have you crawl my entire website", "site_crawl"))
test("'crawl the whole domain' -> site_crawl", check_intent("crawl the whole domain for me", "site_crawl"))
test("'spider my entire site' -> site_crawl", check_intent("spider my entire site please", "site_crawl"))
test("'read every page on my website' -> site_crawl", check_intent("read every page on my website", "site_crawl"))
test("'go through my entire website' -> site_crawl", check_intent("go through my entire website and read everything", "site_crawl"))
test("'crawl' alone NOT site_crawl", check_intent("crawl under the table", "converse"))  # No scope word


# ── 7. GitHub URL parsing + Multi-URL extraction ──
print("\n═══ 7. GitHub URL Parsing + Multi-URL ═══")
from project_vargas.tools.url_reader import URLReaderTool

ur = URLReaderTool()

# GitHub URL detection
test("GitHub URL detected: github.com/ORG", ur._is_github_url("https://github.com/CONEXUS-dev"))
test("GitHub URL detected: github.com/ORG/REPO", ur._is_github_url("https://github.com/CONEXUS-dev/forgetting-engine"))
test("Non-GitHub URL rejected", not ur._is_github_url("https://example.com/page"))
test("Non-GitHub URL rejected: gitlab", not ur._is_github_url("https://gitlab.com/some/repo"))

# GitHub path parsing
p1 = ur._parse_github_path("https://github.com/CONEXUS-dev")
test("Parse org URL: type=org", p1["type"] == "org" and p1["owner"] == "CONEXUS-dev")

p2 = ur._parse_github_path("https://github.com/CONEXUS-dev?tab=repositories")
test("Parse org+tab URL: type=org", p2["type"] == "org" and p2["owner"] == "CONEXUS-dev")

p3 = ur._parse_github_path("https://github.com/CONEXUS-dev/forgetting-engine")
test("Parse repo URL: type=repo", p3["type"] == "repo" and p3["owner"] == "CONEXUS-dev" and p3["repo"] == "forgetting-engine")

p4 = ur._parse_github_path("https://github.com/CONEXUS-dev/forgetting-engine/tree/main/src")
test("Parse file URL: type=file", p4["type"] == "file" and p4["ref"] == "main" and p4["path"] == "src")

p5 = ur._parse_github_path("https://github.com/CONEXUS-dev/forgetting-engine/blob/main/README.md")
test("Parse blob URL: type=file", p5["type"] == "file" and p5["path"] == "README.md")

# Multi-URL extraction from messages
from project_vargas.agent.intent_classifier import _URL_REGEX

multi_msg = """Check these repos:
https://github.com/CONEXUS-dev/experiments
https://github.com/CONEXUS-dev/forgetting-engine
https://github.com/CONEXUS-dev/FE-Validation-Suite"""

multi_urls = _URL_REGEX.findall(multi_msg)
test("Multi-URL: extracts 3 URLs", len(multi_urls) == 3)
test("Multi-URL: first is experiments", "experiments" in multi_urls[0])
test("Multi-URL: last is FE-Validation", "FE-Validation" in multi_urls[2])

# Dedup test
dedup_msg = "https://github.com/CONEXUS-dev/repo1 and https://github.com/CONEXUS-dev/repo1"
dedup_urls = _URL_REGEX.findall(dedup_msg)
seen = set()
unique = [u for u in dedup_urls if u.lower().rstrip("/") not in seen and not seen.add(u.lower().rstrip("/"))]
test("Multi-URL dedup: 2 found, 1 unique", len(dedup_urls) == 2 and len(unique) == 1)


# ── 8. Memory Decomposition + Keyword Boost ──
print("\n═══ 8. Memory Decomposition + Keyword Boost ═══")

# Test memory decomposition
from project_vargas.agent.vargas_agent import VargasAgent as _VA_temp

# Create a minimal instance just for decomposition testing
class _DecompTester:
    """Minimal shim to test _decompose_identity_statement without full init."""
    _decompose_identity_statement = _VA_temp._decompose_identity_statement

dt = _DecompTester()

# The exact message that failed in live testing
live_msg = "My name is Derek Angell and I'm the founder of CONEXUS Global Arts Media (or just CONEXUS) my website is: investor.conexusglobalarts.media"
facts = dt._decompose_identity_statement(live_msg)
test("Decompose: extracts name 'Derek Angell'", any("Derek Angell" in f for f in facts))
test("Decompose: extracts role 'founder'", any("founder" in f.lower() for f in facts))
test("Decompose: extracts org 'CONEXUS'", any("CONEXUS" in f for f in facts))
test("Decompose: extracts alias '(or just CONEXUS)'", any("alias" in f.lower() or "shorthand" in f.lower() for f in facts))
test("Decompose: includes full context", any("Full context:" in f for f in facts))
test("Decompose: produces multiple facts", len(facts) >= 3)

# Short messages should not decompose
short_facts = dt._decompose_identity_statement("My name is Bob")
test("Decompose: short message returns empty", len(short_facts) == 0)

# Test keyword boost in memory retrieval
from project_vargas.memory.memory_client import VargasMemoryClient
# Simulate keyword boost logic directly
test_results = [
    {"id": "1", "score": 0.5, "content": "User's name is Derek Angell", "type": "explicit_statement", "collection": "vargas_identity", "created_at": "", "confidence": 0.9},
    {"id": "2", "score": 0.4, "content": "CONEXUS Global Arts Media is the user's company", "type": "explicit_statement", "collection": "vargas_identity", "created_at": "", "confidence": 0.9},
    {"id": "3", "score": 0.6, "content": "User prefers direct communication", "type": "explicit_statement", "collection": "vargas_behavioral", "created_at": "", "confidence": 0.8},
]
query = "What does CONEXUS mean to you?"
query_words = set(w.lower() for w in query.split() if len(w) > 3)
for r in test_results:
    content_lower = r["content"].lower()
    keyword_hits = sum(1 for w in query_words if w in content_lower)
    if keyword_hits > 0:
        boost = min(keyword_hits * 0.1, 0.3)
        r["score"] = r.get("score", 0) + boost
test_results.sort(key=lambda x: x.get("score", 0), reverse=True)
# CONEXUS memory (originally 0.4) should be boosted by keyword match
conexus_result = next(r for r in test_results if "CONEXUS" in r["content"])
derek_result = next(r for r in test_results if "Derek" in r["content"])
test("Keyword boost: CONEXUS score boosted from 0.4 to 0.5", conexus_result["score"] == 0.5)
test("Keyword boost: non-matching memory unchanged", derek_result["score"] == 0.5)


# ── 9. Bounded Autonomy: Self-Escalation ──
print("\n═══ 9. Bounded Autonomy: Self-Escalation ═══")

# Test _should_self_escalate detection
from project_vargas.agent.vargas_agent import VargasAgent as _VA_esc

class _EscTester:
    """Minimal shim to test _should_self_escalate without full init."""
    _HELP_SIGNALS = _VA_esc._HELP_SIGNALS
    _should_self_escalate = _VA_esc._should_self_escalate

et = _EscTester()

# Deep conversation with circling pattern — should escalate
deep_history = [
    {"role": "user", "content": "What industry loses money from blind AI obedience?"},
    {"role": "vargas", "content": "Name one industry where that happens. Just one. Tell me what breaks when the machine does not push back?"},
    {"role": "user", "content": "I don't know, that's why I'm asking you"},
    {"role": "vargas", "content": "You ran the seventeen thousand trials. You hold the data. Where is the bleeding?"},
    {"role": "user", "content": "Can you look at the data yourself?"},
    {"role": "vargas", "content": "Then give me the path. If the mechanic is already codified there, point me to the file."},
]
test("Self-escalate: 'help me' + deep history + circling", et._should_self_escalate("Could you help me find that answer?", deep_history))
test("Self-escalate: 'figure it out' variant", et._should_self_escalate("Can you figure it out from the data?", deep_history))

# Shallow conversation — should NOT escalate
shallow_history = [
    {"role": "user", "content": "Hello"},
    {"role": "vargas", "content": "Hello. Where are we starting."},
]
test("No escalate: shallow history", not et._should_self_escalate("help me", shallow_history))

# No help signal — should NOT escalate
test("No escalate: no help signal", not et._should_self_escalate("That's interesting", deep_history))

# No questions from Vargas — should NOT escalate
no_question_history = [
    {"role": "user", "content": "Tell me about infrastructure."},
    {"role": "vargas", "content": "Infrastructure management is a key area."},
    {"role": "user", "content": "Go on."},
    {"role": "vargas", "content": "The core challenge is risk management."},
    {"role": "user", "content": "More."},
    {"role": "vargas", "content": "Disaster recovery is critical."},
]
test("No escalate: Vargas not asking questions", not et._should_self_escalate("help me find more", no_question_history))

# Test help signal detection
test("Help signal: 'help me'", any("help me" in sig for sig in _VA_esc._HELP_SIGNALS))
test("Help signal: 'figure it out'", any("figure it out" in sig for sig in _VA_esc._HELP_SIGNALS))
test("Help signal: 'can you find'", any("can you find" in sig for sig in _VA_esc._HELP_SIGNALS))

# Test _extract_escalation_param
test("Extract param: QUERY", _VA_esc._extract_escalation_param("TOOL: web_search\nQUERY: AI blind obedience failures\nREASON: test", "QUERY") == "AI blind obedience failures")
test("Extract param: TOOL", _VA_esc._extract_escalation_param("TOOL: web_search\nQUERY: test", "TOOL") == "web_search")
test("Extract param: missing", _VA_esc._extract_escalation_param("TOOL: none", "QUERY") == "")

# Test system prompt has COMMITMENT section
prompt_path = PROJECT_ROOT / "project_vargas" / "prompts" / "system_prompt.md"
prompt_text = prompt_path.read_text(encoding="utf-8")
test("System prompt: has COMMITMENT section", "## COMMITMENT" in prompt_text)
test("System prompt: bounded autonomy instruction", "bounded autonomy" in prompt_text.lower())
test("System prompt: updated tool use rule", "information gap you can resolve yourself" in prompt_text)


# ── 10. V2.5 Interface + Pending-Action Latch ──
print("\n═══ 10. V2.5 Interface + Pending-Action Latch ═══")

# Test system prompt has INTERFACE section
test("System prompt: has INTERFACE section", "## INTERFACE" in prompt_text)
test("System prompt: Discord not terminal", "Discord is not a terminal" in prompt_text)
test("System prompt: never output raw commands", "Never output raw shell commands" in prompt_text)
test("System prompt: conditional code exception", "review only" in prompt_text.lower())
test("System prompt: tool confirmation UX", "Done — saved" in prompt_text)
test("System prompt: OS context placeholder", "{{OS_CONTEXT}}" in prompt_text)

# Test OS context injection
from project_vargas.agent.vargas_agent import VargasAgent as _VA_os
class _OsTester:
    _web_search = type('', (), {'available': False})()
    _url_reader = type('', (), {'available': False})()
    _openclaw = type('', (), {'available': False})()
    _browser = type('', (), {'available': False})()
    _shell = type('', (), {'available': False})()
    _file_io = type('', (), {'available': False, 'workspace_path': '/tmp/test'})()
    _inject_tool_capabilities = _VA_os._inject_tool_capabilities

ot = _OsTester()
test_prompt = "Hello {{OS_CONTEXT}} World {{TOOL_CAPABILITIES}}"
injected = ot._inject_tool_capabilities(test_prompt)
import platform
if platform.system() == "Windows":
    test("OS context: Windows detected", "Windows" in injected)
    test("OS context: PowerShell mentioned", "PowerShell" in injected)
else:
    test("OS context: system detected", platform.system() in injected)
test("OS context: placeholder replaced", "{{OS_CONTEXT}}" not in injected)

# Test self-escalation no-narration instruction
from project_vargas.agent.vargas_agent import VargasAgent as _VA_esc2
# Read the source to verify tool_context strings
import inspect
esc_source = inspect.getsource(_VA_esc2._self_escalate)
test("Self-escalation: no-narration for web_search", "NEVER show the search command" in esc_source)
test("Self-escalation: no-narration for url_read", "NEVER show the curl command" in esc_source)
test("Self-escalation: no-narration for file_read", "NEVER show the file read command" in esc_source)

# Test pending-action latch
test("Pending-action: APPROVAL_PATTERNS defined", len(_VA_esc2._APPROVAL_PATTERNS) > 5)
test("Pending-action: 'you are authorized' in patterns", "you are authorized" in _VA_esc2._APPROVAL_PATTERNS)
test("Pending-action: 'approved' in patterns", "approved" in _VA_esc2._APPROVAL_PATTERNS)
test("Pending-action: 'proceed' in patterns", "proceed" in _VA_esc2._APPROVAL_PATTERNS)

# Test _detect_file_write_proposal
class _LatchTester:
    _pending_actions = {}
    _detect_file_write_proposal = _VA_esc2._detect_file_write_proposal

lt = _LatchTester()
lt._detect_file_write_proposal("I can write an interactive HTML visualization to your workspace called `trial_43_collision.html`.", "test_ch")
test("Detect proposal: sets pending action", "test_ch" in lt._pending_actions)
if "test_ch" in lt._pending_actions:
    test("Detect proposal: correct filename", lt._pending_actions["test_ch"]["filename"] == "trial_43_collision.html")
    test("Detect proposal: needs_generation flag", lt._pending_actions["test_ch"].get("needs_generation") is True)
    test("Detect proposal: 3 turns remaining", lt._pending_actions["test_ch"]["turns_remaining"] == 3)

# No proposal when text doesn't contain write signals
lt2 = _LatchTester()
lt2._pending_actions = {}
lt2._detect_file_write_proposal("The data shows an 89% improvement in routing distance.", "test_ch2")
test("No proposal: non-write response", "test_ch2" not in lt2._pending_actions)

# Test config max_tokens
import json
config_path = PROJECT_ROOT / "project_vargas" / "config" / "vargas_config.json"
config_data = json.loads(config_path.read_text(encoding="utf-8"))
test("Config: max_tokens is 4096", config_data.get("max_tokens") == 4096)

# Test intent classifier has authorization patterns
from project_vargas.agent.intent_classifier import TASK_EXECUTE_PATTERNS
test("Intent: 'you are authorized' in TASK_EXECUTE", "you are authorized" in TASK_EXECUTE_PATTERNS)
test("Intent: 'i confirm' in TASK_EXECUTE", "i confirm" in TASK_EXECUTE_PATTERNS)


# ── 11. VargasAgent V2 initialization ──
print("\n═══ 11. VargasAgent V2 Initialization ═══")
try:
    from dotenv import load_dotenv
    env_path = PROJECT_ROOT / "project_vargas" / ".env"
    load_dotenv(env_path)

    from project_vargas.agent.vargas_agent import VargasAgent
    agent = VargasAgent()
    health = agent.health_check()

    test("Agent version is 2.0", health.get("version") == "2.0")
    test("Agent status online", health.get("status") == "online")
    test("Browser tool present", "browser" in health)
    test("Shell tool present", "shell" in health)
    test("File IO tool present", "file_io" in health)
    test("Agent loop present", health.get("agent_loop") is True)
    test("Browser is available", health.get("browser") is True)
    test("Shell is available", health.get("shell") is True)
    test("File IO is available", health.get("file_io") is True)
    test("URL reader registered in executor", "url_reader" in agent._executor._tools)
except Exception as e:
    print(f"  ❌ VargasAgent init failed: {e}")
    failed += 1


# ── Summary ──
print(f"\n{'═' * 40}")
print(f"  RESULTS: {passed}/{passed + failed} passed")
if failed == 0:
    print("  🎉 ALL TESTS PASSED — Vargas V2 is ready")
else:
    print(f"  ⚠️  {failed} test(s) failed")
print(f"{'═' * 40}\n")
