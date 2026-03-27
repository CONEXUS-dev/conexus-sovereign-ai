# VARGAS V2 — Comprehensive Guide

**Version:** 2.1  
**Build Date:** 2026-03-10  
**Test Status:** 171/171 passed (full verification), 75/75 (unit tests)  
**Author:** Derek Angell + Cascade

---

## Table of Contents

1. [What Vargas Is](#1-what-vargas-is)
2. [Architecture Overview](#2-architecture-overview)
3. [V1 Capabilities (Preserved)](#3-v1-capabilities-preserved)
4. [V2 Capabilities (New)](#4-v2-capabilities-new)
5. [Safety Model](#5-safety-model)
6. [Tool Reference](#6-tool-reference)
7. [Agent Loop — How Multi-Step Tasks Work](#7-agent-loop)
8. [Intent Classification — How Vargas Decides What to Do](#8-intent-classification)
9. [Attunement System — How Vargas Calibrates Tone](#9-attunement-system)
10. [Memory System](#10-memory-system)
11. [Discord Integration](#11-discord-integration)
12. [File Map](#12-file-map)
13. [Configuration Reference](#13-configuration-reference)
14. [What Vargas CAN Do Right Now](#14-what-vargas-can-do-right-now)
15. [What Vargas CANNOT Do Right Now](#15-what-vargas-cannot-do-right-now)
16. [Known Limitations and Edge Cases](#16-known-limitations-and-edge-cases)
17. [How to Test](#17-how-to-test)
18. [Troubleshooting](#18-troubleshooting)

---

## 1. What Vargas Is

Vargas is a personal collaborator AI built for one person. Not a chatbot. Not a virtual assistant. A thinking partner with memory, continuity, calibrated tone, and now — autonomous execution capability.

**V1** was the mind: conversation, memory, web search, URL reading, OpenClaw skills, attunement calibration.

**V2** is the body: browser automation, shell command execution, file I/O, multi-step task planning with human approval gates.

The calibration is the mind. V2 is the body. V2 is purely additive — nothing from V1 was removed or degraded.

---

## 2. Architecture Overview

```
Discord Message
    │
    ▼
┌─────────────────────────────────────────────┐
│  on_message (discord/bot.py)                │
│  ├─ Downloads image attachments             │
│  ├─ Strips mentions                         │
│  └─ Calls vargas.respond()                  │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  VargasAgent.respond() (vargas_agent.py)    │
│  ├─ 1. Classify intent (pattern matching)   │
│  ├─ 2a. Memory modify? → handle directly    │
│  ├─ 2b. Active plan? → approve/cancel       │
│  ├─ 2c. V2 intent? → Agent Loop             │
│  ├─ 3. Build memory + tool context          │
│  ├─ 4. Handle V1 tools (search, URL, etc.)  │
│  ├─ 5. Build attunement context             │
│  ├─ 6. Generate LLM response (Gemini)       │
│  ├─ 7. Post-response memory evaluation      │
│  └─ 8. Attunement mutation                  │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Discord Reply (split into 2000-char chunks)│
└─────────────────────────────────────────────┘

V2 ADDITIONS:

┌─────────────────────────────────────────────┐
│  Agent Loop (agent_loop.py)                 │
│  ├─ Analyze complexity (LLM decides)        │
│  ├─ Create plan (draft)                     │
│  ├─ Present plan to user                    │
│  ├─ User approves (yes) or cancels (no)     │
│  ├─ Execute steps sequentially              │
│  │   └─ Each step → ToolExecutor            │
│  ├─ Observe results, retry on failure       │
│  └─ Build results context for LLM summary   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Tool Executor (executor.py)                │
│  ├─ Routes by SafetyLevel (AUTO/GATED/BLOCKED)
│  ├─ AUTO → execute immediately              │
│  ├─ GATED → request approval via Discord    │
│  │   ├─ User reacts ✅ → execute            │
│  │   └─ User reacts ❌ → reject             │
│  ├─ BLOCKED → always rejected               │
│  └─ Timeout: 120 seconds per approval       │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┼──────┐
        ▼      ▼      ▼
   Browser   Shell   FileIO
```

---

## 3. V1 Capabilities (Preserved)

All of these work exactly as before.

### Conversation

- Natural language conversation via Discord
- 20-message conversation history per channel
- Multimodal: accepts image attachments (PNG, JPEG, GIF, WebP)
- Intent-driven routing (pattern matching, no LLM call for classification)
- Attunement-calibrated tone (entropy, chaos, stability, pole balance)

### Memory (3 classes)

- **Identity:** Who you are, what you care about, explicit statements ("my name is...", "I prefer...")
- **Behavioral:** Observed patterns detected every 10 interactions (decision style, communication preferences, avoidance patterns)
- **Attunement:** Persistent emoji vector that calibrates Vargas's tone across sessions

### Web Search

- Google Custom Search integration
- Triggered by patterns: "search for", "look up", "what's the latest", "google", etc.
- Results injected as context — Vargas never says "I searched for..."

### URL Reading

- Reads public web pages when given a link
- Follows links from previously read pages ("click the link to...", "read more")
- Stores last page read per channel for link following

### OpenClaw Skills

- 99 active skills loaded from manifest
- Semantic matching (all-MiniLM-L6-v2 embeddings)
- Skill context injected into LLM prompt when matched

### Challenge System

- Challenges suppressed for first 5 interactions per channel
- Earned through continuity, not triggered by keywords
- Attunement chaos index influences challenge intensity

---

## 4. V2 Capabilities (New)

### Browser Automation

**Binary:** `openclaw/skills/agent-browser/bin/agent-browser-win32-x64.exe`

Vargas can control a headless Chromium browser. Actions:

| Action                  | What It Does                             | Safety |
| ----------------------- | ---------------------------------------- | ------ |
| `open`                  | Navigate to a URL                        | AUTO   |
| `snapshot`              | Get accessibility tree with element refs | AUTO   |
| `get_text`              | Extract text from an element             | AUTO   |
| `get_url`               | Get current page URL                     | AUTO   |
| `get_title`             | Get current page title                   | AUTO   |
| `screenshot`            | Take a screenshot (optional full-page)   | AUTO   |
| `back`                  | Navigate back                            | AUTO   |
| `forward`               | Navigate forward                         | AUTO   |
| `reload`                | Reload current page                      | AUTO   |
| `wait`                  | Wait for element, text, or time          | AUTO   |
| `click`                 | Click an element by ref                  | GATED  |
| `dblclick`              | Double-click an element                  | GATED  |
| `fill`                  | Clear and fill an input field            | GATED  |
| `type`                  | Type text into an element                | GATED  |
| `press`                 | Press a keyboard key                     | GATED  |
| `select`                | Select a dropdown option                 | GATED  |
| `check` / `uncheck`     | Toggle checkboxes                        | GATED  |
| `hover`                 | Hover over an element                    | GATED  |
| `scroll`                | Scroll the page (direction + pixels)     | GATED  |
| `upload`                | Upload a file                            | GATED  |
| `eval`                  | Execute JavaScript on page               | GATED  |
| `tab_new` / `tab_close` | Manage tabs                              | GATED  |

**Timeouts:** 30s for commands, 45s for page loads.  
**Session:** All browser actions share a single session named "vargas".

### Shell Command Execution

**Working Directory:** `project_vargas/workspace/`

Vargas can run shell commands as subprocesses.

**Auto-approved (read-only):**

```
dir, ls, type, cat, echo, pwd, cd
git status, git log, git diff, git branch
python --version, python3 --version
node --version, npm --version
where, which, whoami, hostname
pip list, pip show
```

**Gated (requires approval):**
Everything else — `python script.py`, `npm install`, `pip install`, etc.

**Always blocked:**

```
rm -rf, rm -r /, del /s /q
format, shutdown, reboot, restart-computer
taskkill, kill -9
mkfs, fdisk, diskpart
reg delete, reg add
net user, net localgroup
> /dev/null, | rm
curl | bash, curl | sh, wget | bash, wget | sh
| bash, | sh
powershell -enc, powershell -encodedcommand
invoke-expression, iex(
```

**Timeouts:** 30 seconds per command.  
**Output limits:** stdout truncated at 4000 chars, stderr at 2000 chars.

### File I/O

**Workspace:** `project_vargas/workspace/`

| Action        | What It Does                    | Safety |
| ------------- | ------------------------------- | ------ |
| `read_file`   | Read any file in the repo       | AUTO   |
| `list_dir`    | List directory contents         | AUTO   |
| `file_exists` | Check if a file exists          | AUTO   |
| `write_file`  | Write a file to workspace       | GATED  |
| `append_file` | Append to a file in workspace   | GATED  |
| `delete_file` | Delete a file in workspace      | GATED  |
| `create_dir`  | Create a directory in workspace | GATED  |

**Sandbox enforcement:**

- **Reads:** Allowed anywhere within `CONEXUS_REPO/` (the repo root)
- **Writes:** Only allowed within `project_vargas/workspace/` — attempts to write outside are rejected
- **Read size limit:** 100KB (truncated with notice)
- **Write size limit:** 50KB (rejected if exceeded)
- `.` and `__pycache__` directories are hidden from `list_dir`

### Multi-Step Task Execution (Agent Loop)

When Vargas detects a complex task (via intent classification), it:

1. **Analyzes complexity** — asks the LLM whether this needs a multi-step plan
2. **Creates a plan** — draft with numbered steps, each describing a tool + action
3. **Presents the plan** — shows you the steps and asks for approval
4. **Executes on approval** — runs each step sequentially through the ToolExecutor
5. **Handles failures** — retries each failed step once, then continues to next step
6. **Summarizes results** — feeds all step results back to the LLM for a natural summary

**Limits:**

- Max 10 steps per plan
- Max 15 loop iterations (prevents infinite retries)
- One active plan per channel at a time
- Plans start as "draft" — must be approved before execution

**Plan approval words:** `yes`, `approve`, `do it`, `go ahead`, `proceed`, `y`, `go`  
**Plan cancellation words:** `no`, `cancel`, `stop`, `nevermind`, `n`

---

## 5. Safety Model

Three tiers. No exceptions.

### AUTO (read-only)

- Executes immediately without asking
- Examples: `git status`, `read_file`, `snapshot`, `screenshot`, web search, URL read

### GATED (write operations)

- Sends a Discord message with description
- Adds ✅ and ❌ reactions
- Waits up to **120 seconds** for user reaction
- ✅ = approved, ❌ = rejected
- Timeout = auto-rejected
- Examples: `click`, `fill`, `write_file`, `python script.py`, `npm install`

### BLOCKED (dangerous operations)

- Always rejected. No override. No approval path.
- Examples: `rm -rf`, `format`, `shutdown`, `| bash`, `powershell -enc`

### Blanket Approval

The executor supports "blanket approval" per channel — if granted, all GATED operations auto-approve for that session. This is NOT currently exposed via Discord (no command to grant it). It exists in the code for future use or manual testing.

---

## 6. Tool Reference

### Browser Tool

**File:** `project_vargas/tools/browser.py`  
**Binary:** `openclaw/skills/agent-browser/bin/agent-browser-win32-x64.exe`  
**Fallback:** `openclaw/skills/agent-browser/bin/agent-browser.js` (via Node.js)  
**Session:** `vargas` (shared across all actions)  
**Output format:** JSON (parsed automatically)  
**Snapshot truncation:** 6000 chars max

### Shell Tool

**File:** `project_vargas/tools/shell.py`  
**Working directory:** `project_vargas/workspace/`  
**Subprocess:** `asyncio.create_subprocess_shell`  
**Classification:** Pattern match against `AUTO_COMMANDS` (exact prefix match), `BLOCKED_PATTERNS` (substring match), everything else is GATED

### File I/O Tool

**File:** `project_vargas/tools/file_io.py`  
**Read root:** `CONEXUS_REPO/` (entire repo)  
**Write root:** `project_vargas/workspace/` only  
**Path resolution:** Relative paths resolve from workspace. Absolute paths must be within boundary.

### Tool Executor

**File:** `project_vargas/tools/executor.py`  
**Registered tools:** `browser`, `shell`, `file`  
**Approval callback:** Set by `discord/bot.py` on startup  
**Call IDs:** Auto-incremented `tc_1`, `tc_2`, etc.  
**Per-channel state:** Each Discord channel has independent approval state

---

## 7. Agent Loop

**File:** `agent_loop.py`

### Flow

```
User message ("go to example.com and screenshot the homepage")
    │
    ▼
Intent classifier → "browser_interact"
    │
    ▼
AgentLoop.analyze_complexity()
    │  (LLM decides: needs_plan=true, plan=[...])
    │
    ▼
AgentLoop.create_plan() → TaskPlan (status=draft)
    │
    ▼
Vargas presents plan to user:
    "Here's what I'll do:
     ⏳ Step 1: Navigate to example.com
     ⏳ Step 2: Take a screenshot
     Say yes to proceed or no to cancel."
    │
    ▼
User says "yes"
    │
    ▼
AgentLoop.approve_plan() → status=approved
    │
    ▼
AgentLoop.execute_plan()
    ├─ Step 1: ToolExecutor.execute(browser.open, {url: "example.com"}) → AUTO → runs
    ├─ Progress: "⚙️ Step 1/2: Navigate to example.com"
    ├─ Step 2: ToolExecutor.execute(browser.screenshot, {}) → AUTO → runs
    └─ Progress: "⚙️ Step 2/2: Take a screenshot"
    │
    ▼
AgentLoop.build_results_context() → "[TASK EXECUTION RESULTS...]"
    │
    ▼
LLM generates natural summary of results
    │
    ▼
Discord reply
```

### Data Structures

**TaskStep:**

```python
id: int
description: str
tool_name: str | None      # "browser", "shell", "file"
tool_action: str | None     # "open", "run", "write_file"
tool_params: dict | None    # {"url": "https://..."}
status: str                 # pending → running → completed|failed|skipped
result: Any                 # Tool output
error: str | None
retry_count: int            # Max 1 retry
```

**TaskPlan:**

```python
goal: str                   # Original user request
steps: list[TaskStep]       # Max 10 steps
status: str                 # draft → approved → running → completed|failed
current_step: int
observations: list[str]     # Running log of what happened
```

### Safety Level Determination (in Agent Loop)

The agent loop determines safety level based on tool+action:

- **Browser read actions** (open, snapshot, screenshot, etc.) → AUTO
- **File read actions** (read_file, list_dir, file_exists) → AUTO
- **Web search and URL reader** → AUTO
- **Shell commands** → GATED (ShellTool does its own blocklist check internally)
- **Everything else** → GATED

### Failure Handling

- Each step gets **one retry** on failure
- After retry failure, step is marked failed and execution **continues** to next step
- Partial success counts as "completed" (e.g., 3/5 steps succeeded)
- Total failure (0 steps succeeded) marks plan as "failed"

---

## 8. Intent Classification

**File:** `agent/intent_classifier.py`

Pattern-based. No LLM call. Runs in microseconds.

### Priority Order (first match wins)

| Priority | Intent             | Example Triggers                                             |
| -------- | ------------------ | ------------------------------------------------------------ |
| 1        | `memory_modify`    | "forget that", "remember this", "start fresh"                |
| 2        | `memory_inspect`   | "what do you remember", "what do you know about me"          |
| 3        | `url_read`         | Any URL in message, or "read this page", "go to the"         |
| 4        | `web_search`       | "search for", "look up", "google", "what's the latest"       |
| 5        | `skill_list`       | "what skills do you have", "list your capabilities"          |
| 6        | `skill_invoke`     | "write code", "analyze this", "debug this"                   |
| 7        | `browser_interact` | "open the website", "take a screenshot", "fill out the form" |
| 8        | `code_execute`     | "run this command", "pip install", "git clone"               |
| 9        | `task_execute`     | "i need you to", "save this to a file", "download", "deploy" |
| 10       | `converse`         | Everything else (default)                                    |

**Important:** Priority order matters. "go to the website" matches `url_read` ("go to the") before `browser_interact` ("go to the website"). This is by design — V1 URL reading takes precedence for simple navigation. `browser_interact` catches browser-specific patterns like "fill out the form", "click the button", "take a screenshot".

### V2 Intents → Agent Loop

When intent is `task_execute`, `browser_interact`, or `code_execute`:

1. Message goes to `AgentLoop.analyze_complexity()`
2. LLM decides if it needs a multi-step plan
3. If yes → plan is created and presented
4. If no → falls through to normal single-shot response

---

## 9. Attunement System

**Purpose:** Calibrates Vargas's tone dynamically based on interaction patterns. Uses the SovereignNEXT emoji vector system.

### The Emoji Vector

```
Pole A: ⚖️ (scales — stability, calm, patience)
Pole B: 🔥 (fire — challenge, intensity, directness)
```

### Metrics That Shape Tone

| Metric              | Range   | Effect on Vargas                                                                                                     |
| ------------------- | ------- | -------------------------------------------------------------------------------------------------------------------- |
| **Entropy**         | 0.0–1.0 | High (>0.85): exploratory, asks more questions, holds ambiguity. Low (<0.5): direct, declarative, cuts to the point. |
| **Chaos Index**     | 0.0–1.0 | High (>0.6): leans into challenge, names avoidance, pushes harder. Low (<0.2): grounded, patient, supportive.        |
| **Stability Index** | 0.0–1.0 | High (>0.5): holds steady, doesn't rush, lets silence work.                                                          |
| **Pole Balance**    | 0.0–1.0 | <0.3: favors patience and precision. >0.7: favors directness and challenge. 0.5: balanced.                           |

### Mutation Rules

The attunement EV mutates after every response:

- **Collapse** (convergence): triggered by decisions, corrections, clarity  
  Signals: "i decided", "let's go with", "the answer is", "actually", "that's not right"  
  Also triggered by `memory_modify` intent.

- **Become** (divergence): triggered by tension, exploration, being stuck  
  Signals: "i don't know", "i'm stuck", "what if", "torn between", "conflicted"  
  Also triggered by `challenge` intent.

- **Paradox Hold** (sustained tension): every 5th interaction  
  Keeps the vector in held tension — neither converging nor diverging.

### Persistence

The attunement EV is saved to Qdrant every 5 interactions. On restart, it loads the last saved state. If no state exists, it creates a fresh vector with `initial_chaos=2, seed=42`.

### Challenge Gating

Challenges are suppressed for the first 5 interactions per channel. After that, the attunement system influences whether and how hard Vargas challenges.

---

## 10. Memory System

**Backend:** Qdrant (vector database at `localhost:6333`)  
**Embeddings:** all-MiniLM-L6-v2 (sentence-transformers)

### Collections

| Collection          | What It Stores                                               | Max Entries |
| ------------------- | ------------------------------------------------------------ | ----------- |
| `vargas_identity`   | Who you are: name, preferences, beliefs, explicit statements | 100         |
| `vargas_behavioral` | Observed patterns: decision style, communication preferences | 100         |
| `vargas_attunement` | Persistent emoji vector state                                | 100         |

### How Memories Are Created

**Identity memories** — stored immediately when Vargas detects:

- Strong triggers (always store): "my name is", "call me", "i prefer", "i work as", "i like", "i don't like", "i hate", "i believe"
- Weak triggers (store if message starts with and > 20 chars): "i am", "i'm", "i do"
- Negative prefixes that block weak triggers: "i'm not", "i'm just", "i'm having", "i'm going", etc.

**Behavioral memories** — detected every 10 interactions:

- Vargas sends last 10 user messages to Gemini
- Gemini identifies ONE behavioral pattern (or "NONE")
- Stored with confidence 0.7

**Attunement** — saved every 5 interactions

### How Memories Are Retrieved

On every message, Vargas does a semantic search against all collections with the user's message as query, retrieves top 5 results, and injects them as invisible context:

```
[MEMORY CONTEXT — do not surface unless asked]
- [vargas_identity|explicit_statement] My name is Derek
- [vargas_behavioral|observed_pattern] Tends to deep-dive into technical details
[END MEMORY CONTEXT]
```

### Memory Corrigibility

- "forget everything" / "clear your memory" / "start fresh" → wipes all collections
- "forget my identity" / "clear identity" → wipes specific collection
- "remember this" / "actually my name is" → triggers memory_modify intent
- Memory decay: half-life of 30 days (configurable)

---

## 11. Discord Integration

**File:** `discord/bot.py`

### Message Flow

1. Every non-bot message in channels Vargas can see goes to `on_message`
2. Bot mentions are stripped from content
3. Image attachments are downloaded and passed as multimodal parts
4. `vargas.respond(content, channel_id)` is called
5. Response is split at paragraph boundaries into ≤2000-char chunks
6. First chunk is a reply; subsequent chunks are channel sends
7. Typing indicator shown during processing

### V2 Approval Flow

1. When ToolExecutor needs approval, it calls `_approval_callback`
2. Bot sends a message: "🔒 **Approval required:** [description]. React ✅ to approve or ❌ to reject."
3. Bot adds both reactions to the message
4. `on_raw_reaction_add` watches for user reactions on tracked messages
5. ✅ → `executor.resolve_approval(approved=True)` → tool executes
6. ❌ → `executor.resolve_approval(approved=False)` → tool rejected
7. Timeout (120s) → auto-rejected

### V2 Progress Updates

During plan execution, each step sends a progress message:

```
⚙️ Step 1/3: Navigate to example.com
⚙️ Step 2/3: Take accessibility snapshot
⚙️ Step 3/3: Extract main content text
```

---

## 12. File Map

```
project_vargas/
├── agent/
│   ├── vargas_agent.py        # Core agent — respond(), memory, attunement, V2 routing
│   ├── agent_loop.py          # V2: Plan→Execute→Observe→Iterate cycle
│   └── intent_classifier.py   # Pattern-based intent classification (10 intents)
├── tools/
│   ├── executor.py            # V2: Central dispatcher with AUTO/GATED/BLOCKED safety
│   ├── browser.py             # V2: Headless browser via agent-browser binary
│   ├── shell.py               # V2: Sandboxed shell command execution
│   ├── file_io.py             # V2: Sandboxed file I/O (reads repo, writes workspace)
│   ├── web_search.py          # V1: Google Custom Search
│   ├── url_reader.py          # V1: Public URL reader
│   └── openclaw_bridge.py     # V1: OpenClaw skill matching
├── memory/
│   └── memory_client.py       # Qdrant-backed semantic memory
├── llm/
│   └── gemini_client.py       # Gemini 3.1 Pro Preview LLM client
├── discord/
│   ├── bot.py                 # Discord interface + V2 approval reactions
│   └── __main__.py            # Entry point: python -m project_vargas.discord
├── prompts/
│   └── system_prompt.md       # System prompt with {{TOOL_CAPABILITIES}} placeholder
├── config/
│   └── vargas_config.json     # Model, memory, intent, OpenClaw, Discord config
├── workspace/                 # V2: Sandboxed write directory for file_io
└── logs/                      # JSONL event logs (tool_use, memory_writes, challenges)
```

---

## 13. Configuration Reference

**File:** `config/vargas_config.json`

```json
{
  "model": "gemini-3.1-pro-preview",
  "embedding_model": "gemini-embedding-001",
  "temperature": 0.7,
  "max_tokens": 2048,
  "memory": {
    "collections": [
      "vargas_identity",
      "vargas_behavioral",
      "vargas_attunement"
    ],
    "max_memories_per_class": 100,
    "retrieval_top_k": 5,
    "decay_enabled": true,
    "decay_half_life_days": 30
  },
  "intent": {
    "confidence_threshold": 0.6,
    "default_intent": "converse"
  },
  "openclaw": {
    "skills_path": "../openclaw/skills",
    "manifest_path": "../openclaw/skills/manifest.json",
    "confidence_threshold": 0.12
  },
  "discord": {
    "max_response_length": 2000,
    "typing_indicator": true,
    "max_conversation_history": 20
  }
}
```

### Environment Variables (project_vargas/.env)

| Variable                  | Purpose                                                |
| ------------------------- | ------------------------------------------------------ |
| `DISCORD_TOKEN`           | Discord bot token                                      |
| `GOOGLE_API_KEY`          | Gemini API key                                         |
| `GEMINI_API_KEY`          | Alternate Gemini key (GOOGLE_API_KEY takes precedence) |
| `GOOGLE_SEARCH_API_KEY`   | Google Custom Search API key                           |
| `GOOGLE_SEARCH_ENGINE_ID` | Custom Search engine ID                                |
| `QDRANT_HOST`             | Qdrant host (default: localhost)                       |
| `QDRANT_PORT`             | Qdrant port (default: 6333)                            |

### Hardcoded Limits

| Constant                    | Value                        | Location             |
| --------------------------- | ---------------------------- | -------------------- |
| Browser command timeout     | 30s                          | `browser.py`         |
| Browser navigation timeout  | 45s                          | `browser.py`         |
| Browser snapshot truncation | 6000 chars                   | `browser.py`         |
| Shell command timeout       | 30s                          | `shell.py`           |
| Shell stdout truncation     | 4000 chars                   | `shell.py`           |
| Shell stderr truncation     | 2000 chars                   | `shell.py`           |
| File read max size          | 100KB                        | `file_io.py`         |
| File write max size         | 50KB                         | `file_io.py`         |
| Approval timeout            | 120s                         | `executor.py`        |
| Max plan steps              | 10                           | `agent_loop.py`      |
| Max loop iterations         | 15                           | `agent_loop.py`      |
| Max conversation history    | 20 messages                  | `vargas_config.json` |
| Max memories per class      | 100                          | `vargas_config.json` |
| Memory retrieval top-k      | 5                            | `vargas_config.json` |
| Memory decay half-life      | 30 days                      | `vargas_config.json` |
| Behavioral eval interval    | Every 10 interactions        | `vargas_agent.py`    |
| Attunement persist interval | Every 5 interactions         | `vargas_agent.py`    |
| Challenge suppression       | First 5 interactions/channel | `vargas_agent.py`    |

---

## 14. What Vargas CAN Do Right Now

### Conversation

- ✅ Multi-turn conversation with memory and context
- ✅ Multimodal input (images via Discord attachments)
- ✅ Tone calibration via attunement system
- ✅ Challenge behavior earned through continuity
- ✅ Memory inspection, correction, and erasure

### Information Retrieval

- ✅ Google web search (live internet results)
- ✅ Read any public URL and follow links from it
- ✅ Bare domain URLs detected automatically (e.g., `investor.conexusglobalarts.media` — no `https://` required)
- ✅ Site crawl: read homepage → extract internal links → build approval plan → read all pages (capped at 10)
- ✅ Read any file within the CONEXUS_REPO repository

### Browser Automation

- ✅ Navigate to websites
- ✅ Take accessibility snapshots (see interactive elements)
- ✅ Click buttons, fill forms, type text, press keys
- ✅ Take screenshots
- ✅ Scroll, navigate back/forward, reload
- ✅ Wait for elements or text to appear

### Shell Execution

- ✅ Run read-only commands automatically (git status, ls, dir, echo, etc.)
- ✅ Run gated commands with approval (python, npm, pip, etc.)
- ✅ Block dangerous commands (rm -rf, format, shutdown, etc.)

### File Operations

- ✅ Read any file in the repository
- ✅ List directory contents
- ✅ Write files to the workspace directory
- ✅ Append to files, create directories, delete files in workspace

### Task Planning

- ✅ Analyze task complexity (LLM-driven)
- ✅ Create multi-step execution plans
- ✅ Present plans for human approval before executing
- ✅ Execute plans with progress updates
- ✅ Retry failed steps once, continue on failure
- ✅ Summarize results naturally

### OpenClaw Skills

- ✅ 99 skills loaded from manifest
- ✅ Semantic matching for skill invocation
- ✅ Skill context injection into prompts

---

## 15. What Vargas CANNOT Do Right Now

### Structural Limitations

- ❌ **No persistent browser session across messages.** Each browser command runs independently. There is no long-lived Chromium process. Each `_run_cmd` spawns a new subprocess. The "session" flag persists state on the agent-browser side, but if the binary doesn't support persistent sessions, each command may start fresh.
- ❌ **No file writes outside workspace.** Cannot modify source code, config files, or anything outside `project_vargas/workspace/`. This is a security boundary, not a bug.
- ❌ **No network requests from shell.** The shell tool doesn't block `curl` or `wget` outright (only piped-to-shell patterns), but Vargas doesn't proactively use them. The browser tool is the intended way to interact with the web.
- ❌ **No simultaneous plans.** Only one active plan per channel. A new task request while a plan is active will be ignored or treated as conversation.
- ❌ **No plan modification mid-execution.** Once a plan is approved and running, it runs all steps. You can't add, remove, or reorder steps mid-flight.
- ❌ **No blanket approval via Discord.** The `grant_blanket_approval()` method exists in code but there is no Discord command or pattern to trigger it. Every gated action requires individual reaction approval.
- ❌ **No parallel step execution.** All plan steps run sequentially. Step 2 waits for Step 1 to complete.
- ❌ **No streaming output.** Long shell commands output nothing until they complete (or timeout at 30s). No real-time stdout streaming.

### Missing Features (Not Yet Built)

- ❌ **No scheduled/recurring tasks.** Vargas cannot set timers or cron jobs.
- ❌ **No multi-channel plan awareness.** Plans are per-channel only. Vargas in channel A doesn't know about a plan in channel B.
- ❌ **No audit log viewer.** Logs exist in `project_vargas/logs/` as JSONL but there's no Discord command to view them.
- ❌ **No tool result caching.** Each tool call is independent. No deduplication.
- ❌ **No dynamic tool discovery.** Tools are hardcoded at init. Adding a new tool requires code changes.
- ❌ **No rollback on plan failure.** If Step 3 of 5 writes a file and Step 4 fails, the file from Step 3 remains. No transactional semantics.
- ❌ **No image output to Discord.** Browser screenshots are taken but not sent as Discord attachments. The path is returned in the result but not uploaded.
- ❌ **No voice/audio support.**
- ❌ **No DM support.** Only works in server channels (due to how `channel.id` is used).

### LLM Limitations

- ❌ **Single LLM.** Only Gemini 3.1 Pro Preview. No model fallback, no local models for Vargas (SovereignNEXT uses local GGUF models but Vargas does not).
- ❌ **No function calling.** The LLM generates text, not structured tool calls. The agent loop asks the LLM for JSON plans, but this is prompt engineering, not native function calling. JSON parsing can fail.
- ❌ **No context window management.** If conversation history + memory + tool results + system prompt exceeds the model's context window, behavior is undefined (likely truncation by the API).

---

## 16. Known Limitations and Edge Cases

### Intent Classification Collisions

- "go to the website" matches `url_read` (pattern: "go to the") before `browser_interact` (pattern: "go to the website"). This means URL read takes priority for navigation phrases.
- "navigate to X" matches `url_read` (pattern: "navigate to") before `browser_interact` (pattern: "navigate to the").
- Workaround: Use browser-specific language like "open the website and click...", "fill out the form", "take a screenshot".

### Agent Loop JSON Parsing

- The complexity analyzer asks the LLM to output JSON. If the LLM wraps it in markdown code blocks (```json), the parser strips them. If the LLM produces malformed JSON, the analyzer defaults to `needs_plan: false` (single-shot response).

### Approval Race Conditions

- If two gated operations fire simultaneously in the same channel, each gets its own approval message. The user must react to each one individually.
- If Vargas's bot adds reactions and the user's reaction comes before the bot finishes adding both reactions, it still works (reaction handler doesn't check for both reactions).

### Browser Binary Availability

- The browser tool checks for `agent-browser-win32-x64.exe` at startup. If the binary is missing or the OpenClaw skills directory structure changes, browser capability silently degrades (available=false, actions return error).

### Shell on Windows

- `asyncio.create_subprocess_shell` uses the default shell (PowerShell on Windows). Commands like `ls` work because PowerShell aliases them. Pure Unix commands may not work.
- The `cd` command is in AUTO_COMMANDS but doesn't actually change the working directory for subsequent commands (each command runs in its own subprocess).

---

## 17. How to Test

### Unit Tests

```bash
python test_vargas_v2.py
```

Runs 75 tests across all 7 subsystems + V2.1 additions. Expected: 75/75 passed.

### Full Capability Verification

```bash
python verify_vargas_v2_full.py
```

Runs 171 tests across 10 categories covering every capability in this guide. Expected: 171/171 passed (1 skip if network unavailable).

### Start Vargas

```bash
python -m project_vargas.discord
```

Requires: Discord token, Gemini API key, Qdrant running on localhost:6333.

### Health Check (in code)

```python
from project_vargas.agent.vargas_agent import VargasAgent
agent = VargasAgent()
print(agent.health_check())
```

Expected output includes:

```json
{
  "agent": "vargas",
  "version": "2.1",
  "status": "online",
  "browser": true,
  "shell": true,
  "file_io": true,
  "agent_loop": true,
  ...
}
```

### Test Individual Tools

```python
import asyncio
from project_vargas.tools.shell import ShellTool
shell = ShellTool()
print(asyncio.run(shell.run("echo hello")))
# {'success': True, 'stdout': 'hello', 'stderr': '', 'exit_code': 0, 'error': None}
```

```python
from project_vargas.tools.file_io import FileIOTool
fio = FileIOTool()
print(asyncio.run(fio.write_file("test.txt", "hello world")))
print(asyncio.run(fio.read_file("project_vargas/workspace/test.txt")))
```

---

## 18. Troubleshooting

| Symptom                                | Cause                              | Fix                                                                             |
| -------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------- |
| Browser actions return "not available" | Binary not found at expected path  | Check `openclaw/skills/agent-browser/bin/` exists with the `.exe`               |
| Approval never completes               | Reaction not detected              | Ensure Discord Intents include reactions; check `on_raw_reaction_add` is firing |
| Plan never executes                    | Plan stuck in "draft"              | User must say "yes"/"approve"/"go ahead" to approve                             |
| Shell command hangs                    | Command doesn't terminate          | Will timeout after 30s; check if command expects stdin                          |
| File write fails "outside workspace"   | Path resolves outside sandbox      | Use relative paths (e.g., `report.md` not `C:\Users\...`)                       |
| JSON parse error in agent loop         | LLM returned malformed JSON        | Falls back to single-shot response; check logs for raw output                   |
| "Something broke on my end"            | LLM generation failed twice        | Check Gemini API key, rate limits, network                                      |
| Intent misclassified                   | Pattern collision (priority order) | Use more specific language or adjust patterns in `intent_classifier.py`         |
| Attunement feels "off"                 | EV drifted to extreme values       | Say "start fresh" to reset, or wait for paradox_hold to stabilize               |
| Memory not retrieving                  | Qdrant down or empty               | Check `localhost:6333` is running; check collection exists                      |

---

## Summary

Vargas V2 is a fully wired autonomous agent with:

- **5 tools** (browser, shell, file I/O, web search, URL reader) + OpenClaw skills
- **3-tier safety model** (AUTO/GATED/BLOCKED) with Discord reaction approval
- **Multi-step task execution** with plan/approve/execute/observe cycle
- **10 intents** driving routing (3 new for V2)
- **Attunement calibration** via SovereignNEXT emoji vectors
- **3-class semantic memory** with decay and corrigibility
- **64/64 integration tests** passing

The mind was V1. The body is V2. Both are live.
