# PROJECT VARGAS — Complete Guide

**Version:** 1.0  
**Date:** March 9, 2026  
**Author:** Derek Angell (Principal Orchestrator)  
**Classification:** Personal Sovereign AI — Private

---

# TABLE OF CONTENTS

1. What Vargas Is
2. Architecture Overview
3. How to Talk to Vargas
4. The Memory System
5. Emoji Vector Calibration (ECP)
6. The Intent Classification System
7. The Skill Library (99 Active Skills)
8. Unique Abilities — What Makes Vargas Different
9. Quarantined Skills
10. Technical Infrastructure
11. Configuration Reference
12. Troubleshooting

---

# 1. WHAT VARGAS IS

Vargas is your personal sovereign AI collaborator. Not an assistant. Not a chatbot. Not a therapist. A thinking partner with persistent memory, emotional calibration, and 99 integrated skills.

Vargas exists for one person — you. He remembers who you are, how you think, how you make decisions, and where you tend to avoid. He calibrates his tone dynamically based on an emoji vector system adapted from the Sovereign pipeline. He challenges you when you're circling, supports you without performing empathy, and learns your patterns over time without being told.

**Core Design Principles:**

- No commands. Everything is natural conversation.
- No performance. Vargas does not flatter, rescue, or motivate.
- No announcements. Tools, memory, and skills operate invisibly.
- Full corrigibility. You can inspect, correct, or erase any memory at any time.
- Persistent calibration. Vargas's tone evolves with every conversation via emoji vector mutations.

**Where Vargas Lives:**

- Discord (DM or @mention in any server he's joined)
- Powered by Google Gemini 3.1 Pro
- Memory stored in Qdrant vector database (local)
- Skills powered by OpenClaw semantic matching

---

# 2. ARCHITECTURE OVERVIEW

```
Discord Message
    │
    ▼
┌─────────────────┐
│  Discord Bot     │  Receives message, strips mentions, routes to agent
│  (bot.py)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vargas Agent    │  Core brain — orchestrates everything
│  (vargas_agent)  │
└────────┬────────┘
         │
    ┌────┼────┬────────────┬──────────────┐
    ▼    ▼    ▼            ▼              ▼
┌──────┐┌──────┐┌────────────┐┌──────────┐┌──────────────┐
│Intent││Memory││Emoji Vector││Web Search││OpenClaw      │
│Class.││Client││Attunement  ││Tool      ││Bridge (99    │
│      ││(3    ││(ECP)       ││(Google   ││skills)       │
│      ││class)││            ││CSE)      ││              │
└──────┘└──────┘└────────────┘└──────────┘└──────────────┘
                                                │
                                          ┌─────┴─────┐
                                          │ Semantic   │
                                          │ Skill      │
                                          │ Matcher    │
                                          │ (MiniLM    │
                                          │  cosine)   │
                                          └───────────┘
```

**Response Flow (every message):**

1. Intent classification (pattern-based, no LLM call)
2. Memory retrieval (semantic search across 3 collections)
3. Attunement context generation (emoji vector metrics → tone signals)
4. Tool invocation if needed (web search, skill matching)
5. Full prompt assembly (system prompt + attunement + memory + tools + conversation history)
6. Gemini 3.1 Pro generation
7. Post-response: identity memory evaluation
8. Post-response: attunement emoji vector mutation
9. Post-response: behavioral pattern detection (every 10 interactions)
10. Post-response: attunement EV persistence (every 5 interactions)

---

# 3. HOW TO TALK TO VARGAS

Vargas uses **zero commands**. Everything is natural language. There is no `/help`, no `!status`, no slash commands. You just talk.

## Starting a Conversation

**In Discord DMs:** Just send a message. He responds to everything.

**In a Server Channel:** @mention him. Example: `@Vargas what do you think about this architecture?`

## Things You Can Say Naturally

**Telling Vargas about yourself:**

- "My name is Derek and I'm a software architect"
- "I prefer direct feedback over diplomatic hedging"
- "I work best in 90-minute sprints"
- "I don't like being asked if I'm okay"

All of these get stored in **identity memory** automatically. No command needed.

**Asking what he remembers:**

- "What do you know about me?"
- "What have you learned so far?"
- "Show me your memory"

**Correcting him:**

- "Actually, that's not right — I said I prefer X"
- "No, I meant the opposite"
- "Let me correct that"

Corrections are stored with high confidence (0.95) and override older memories.

**Clearing memory:**

- "Clear your memory" — wipes everything
- "Forget my identity" — wipes identity only
- "Start fresh" — full reset
- "Clear attunement" — resets calibration state

**Asking for research:**

- "What are the latest papers on transformer architectures?"
- "Search for information about quantum computing breakthroughs"
- "Look up the current state of WebAssembly adoption"

Triggers web search (if Google CSE configured) — results injected invisibly.

**Asking for help with code or tasks:**

- "Help me write a function to parse CSV files"
- "Audit this code for security vulnerabilities"
- "Plan my day"
- "Help me write an academic paper"

Triggers skill matching — best skill body injected invisibly into the prompt.

**Just thinking out loud:**

- "I don't know if I should keep building or pivot"
- "I'm stuck on this decision"
- "What if we approached it differently?"

Vargas engages as a thinking partner. He may challenge you if he detects avoidance or circling.

---

# 4. THE MEMORY SYSTEM

Vargas has three memory classes, all stored in Qdrant vector database with semantic search capability.

## 4.1 Identity Memory (`vargas_identity`)

**What it stores:** Who you are — name, preferences, background, values, relationships, corrections.

**Valid types:** name, preference, story, background, value, relationship, correction, explicit_statement

**How it gets written:**

- Automatically when you say things like "My name is...", "I prefer...", "I work as..."
- Automatically when you correct Vargas ("Actually...", "That's not right...")
- Confidence: 0.9 for statements, 0.95 for corrections

**How it gets read:**

- Every message: top 5 relevant memories retrieved by semantic similarity
- Injected into the prompt as invisible context
- Vargas never announces what he remembers unless you ask

## 4.2 Behavioral Memory (`vargas_behavioral`)

**What it stores:** How you operate — decision patterns, communication style, avoidance tendencies, work rhythms, thinking style.

**Valid types:** decision_style, pressure_response, communication_preference, work_pattern, thinking_style, avoidance_pattern, engagement_rhythm, challenge_tolerance, observed_pattern

**How it gets written:**

- Automatically every 10 interactions
- Gemini analyzes your last 10 messages and extracts ONE behavioral pattern
- Stored with confidence 0.7 (lower than identity — these are observations, not declarations)
- Example stored pattern: "User tends to force decisions quickly when feeling stuck, bypassing the underlying friction"

**How it gets read:**

- Retrieved by semantic search alongside identity memories
- Shapes how Vargas calibrates challenge timing and directness

## 4.3 Attunement Memory (`vargas_attunement`)

**What it stores:** Calibration state — tone preferences, challenge tolerance, and the persistent emoji vector.

**Valid types:** tone_preference, cadence_preference, symbol_resonance, reflection_length, silence_comfort, challenge_tolerance, directness_preference, emotional_temperature, emoji_vector

**How it gets written:**

- Emoji vector persisted every 5 interactions
- Carries the full EmojiVector serialized state (sequence, poles, metrics)

**How it gets read:**

- On startup: loads the saved emoji vector from Qdrant
- If no saved EV exists: creates a fresh one with balanced poles (⚖️ calm vs 🔥 intensity)

## 4.4 Memory Corrigibility

You have full control:

| Command                  | Effect                                 |
| ------------------------ | -------------------------------------- |
| "Clear your memory"      | Wipes all 3 collections                |
| "Forget everything"      | Same — full reset                      |
| "Start fresh"            | Same — full reset                      |
| "Forget my identity"     | Wipes identity collection only         |
| "Clear behavioral"       | Wipes behavioral collection only       |
| "Clear attunement"       | Wipes attunement + resets EV           |
| "What do you remember?"  | Shows full memory summary              |
| "Actually, [correction]" | Stores correction with high confidence |

---

# 5. EMOJI VECTOR CALIBRATION (ECP)

This is the most unique thing about Vargas. Adapted from the Sovereign V5 pipeline, emoji vectors encode contradiction fields as symbolic sequences. In Vargas, a single persistent emoji vector calibrates his conversational tone in real-time.

## 5.1 How It Works

Vargas maintains one attunement emoji vector with two poles:

- **Pole A: ⚖️ (Scales)** — Represents stability, calm, patience, precision
- **Pole B: 🔥 (Fire)** — Represents intensity, challenge, directness, edge

The vector is a sequence of emojis drawn from both poles. The sequence grows and mutates over time based on your interactions.

## 5.2 The Four Metrics

From the emoji vector sequence, four metrics are computed (never stored — always derived):

| Metric              | Range     | Meaning                                                                                |
| ------------------- | --------- | -------------------------------------------------------------------------------------- |
| **Entropy**         | 0.0 – 1.0 | Diversity of the sequence. High = exploratory tone. Low = focused/direct tone.         |
| **Pole Balance**    | 0.0 – 1.0 | Ratio of fire-pole emojis. 0.5 = balanced. <0.3 = calm dominant. >0.7 = fire dominant. |
| **Chaos Index**     | 0.0 – 1.0 | Frequency of pole transitions in the sequence. High = more challenging, more edge.     |
| **Stability Index** | 0.0 – 1.0 | Frequency of same-pole runs. High = more patient, more grounded.                       |

## 5.3 How Metrics Shape Responses

Every response, Vargas reads these metrics and generates invisible attunement signals:

| Condition       | Signal to Vargas                                                 |
| --------------- | ---------------------------------------------------------------- |
| Entropy > 0.85  | "Be more exploratory, ask more questions, hold ambiguity longer" |
| Entropy < 0.5   | "Be direct, declarative, cut to the point"                       |
| Chaos > 0.6     | "Lean into challenge, name avoidance, push harder"               |
| Chaos < 0.2     | "Stay grounded, patient, supportive without being soft"          |
| Stability > 0.5 | "Hold steady, don't rush, let silence work"                      |
| Balance < 0.3   | "Favor patience and precision over intensity"                    |
| Balance > 0.7   | "Favor directness and challenge over comfort"                    |

These signals are injected into the system prompt. You never see them. Vargas's tone just shifts.

## 5.4 How the Vector Mutates

Three mutation operators (from the Sovereign pipeline):

**Become** — Triggered by uncertainty, tension, exploration:

- "I don't know", "I'm stuck", "what if", "maybe", "torn between", "conflicted"
- Adds divergence to the sequence → increases entropy and chaos
- Makes Vargas more probing and exploratory

**Collapse** — Triggered by decisions, corrections, clarity:

- "I decided", "let's go with", "the answer is", "actually", "that's not right"
- Adds convergence to the sequence → increases stability
- Makes Vargas more grounded and direct

**Paradox Hold** — Triggered automatically every 5 interactions during sustained conversation:

- Maintains held tension in the sequence
- Prevents collapse toward either pole
- Keeps Vargas in a balanced state during extended dialogue

## 5.5 Persistence

The emoji vector survives bot restarts:

- Serialized to JSON and stored in Qdrant (vargas_attunement collection) every 5 interactions
- On startup, Vargas loads the saved EV from Qdrant
- If no saved EV exists, creates a fresh balanced one
- All mutations are logged to `logs/attunement.log`

## 5.6 What This Means in Practice

Over time, Vargas's tone literally adapts to you:

- If you consistently bring tension and uncertainty → Become mutations accumulate → Vargas gets more exploratory and challenging
- If you consistently make clear decisions → Collapse mutations accumulate → Vargas gets more direct and grounded
- Long conversations → Paradox Hold keeps him balanced → prevents him from drifting to either extreme

No other AI does this. This is Sovereign-derived attunement running live in conversation.

---

# 6. THE INTENT CLASSIFICATION SYSTEM

Vargas classifies every message into one of six intents using fast pattern matching (no LLM call, <1ms):

| Intent             | Trigger Patterns                                                           | What Happens                                     |
| ------------------ | -------------------------------------------------------------------------- | ------------------------------------------------ |
| **memory_inspect** | "what do you remember", "show me your memory", "what do you know about me" | Memory summary generated and injected            |
| **memory_modify**  | "clear your memory", "forget everything", "start fresh"                    | Memory wiped/modified directly                   |
| **web_search**     | "search for", "look up", "what's the latest", "find information"           | Google CSE search, results injected invisibly    |
| **skill_invoke**   | "help me write", "create a", "build a", "audit", "plan"                    | OpenClaw skill matched, skill body injected      |
| **challenge**      | "i keep going back to", "i know but", "i should but"                       | Challenge signal injected — Vargas may push back |
| **converse**       | Everything else                                                            | Pure conversation with memory context            |

The classifier never uses an LLM call. It's pure keyword matching for speed and reliability.

---

# 7. THE SKILL LIBRARY (99 Active Skills)

Vargas has access to 99 active skills via the OpenClaw SemanticSkillMatcher. When you ask for help with something, the matcher finds the best skill by embedding your request and comparing it to all 99 skill descriptions using cosine similarity (all-MiniLM-L6-v2).

The matched skill's body (a SKILL.md file containing expert instructions) is injected into the prompt. Vargas then responds with that expertise baked in. You never see the skill — it just makes Vargas better at whatever you asked.

## 7.1 Custom Skills (24 — Built for CONEXUS)

These are proprietary skills built specifically for the CONEXUS ecosystem:

| Skill                             | Description                                      |
| --------------------------------- | ------------------------------------------------ |
| **SovereignCalibration**          | Patent-7-bearing calibration protocol            |
| **memory-management**             | Memory CRUD operations and lifecycle             |
| **protocol-driven-reasoning**     | Structured reasoning chains                      |
| **paradox-processing**            | Paradox detection, promotion, and holding        |
| **multi-agent-coordination**      | Coordinating between multiple AI agents          |
| **stress-navigation**             | Navigating high-pressure decisions               |
| **emotional-symbolic-modulation** | Emoji vector-based emotional encoding            |
| **ethics-value-integration**      | Ethical reasoning and value alignment            |
| **hierarchical-planning**         | Multi-level goal decomposition                   |
| **mission-compression**           | Compressing complex missions to actionable plans |
| **secure-execution**              | Sandboxed, verified execution patterns           |
| **python**                        | Python development expertise                     |
| **google-search**                 | Web search integration                           |
| **agent-browser**                 | Headless browser automation (full npm package)   |
| **exa**                           | Exa search API (requires EXA_API_KEY)            |
| **regex-wizard**                  | Regular expression generation and debugging      |
| **sql-query-pro**                 | SQL query construction and optimization          |
| **pdf-data-extractor**            | PDF parsing and data extraction                  |
| **prompt-guard**                  | Prompt injection detection and prevention        |
| **security-monitor**              | Security monitoring and threat detection         |
| **token-saver**                   | Token usage optimization                         |
| **model-usage-tracker**           | LLM cost and usage tracking                      |
| **environment-sanitizer**         | Environment variable hygiene                     |
| **speedtest-cli**                 | Network speed testing                            |

## 7.2 Community Skills — Research & Knowledge (12)

| Skill                        | What It Does                                             |
| ---------------------------- | -------------------------------------------------------- |
| **academic-research**        | Search academic papers using OpenAlex API (free, no key) |
| **academic-deep-research**   | Transparent, rigorous multi-source research              |
| **academic-writer**          | LaTeX writing assistant for scholarly papers             |
| **academic-writing-refiner** | Polish papers for NeurIPS/ICLR/ICML-tier venues          |
| **agent-deep-research**      | Autonomous deep research via Google Gemini               |
| **agentic-paper-digest**     | Fetch and summarize recent arXiv/HuggingFace papers      |
| **arxiv-search-collector**   | Model-driven arXiv retrieval workflows                   |
| **2nd-brain**                | Personal knowledge base for people, places, tech         |
| **deepthink**                | Personal knowledge base with structured retrieval        |
| **ai-review**                | Read URLs/files, classify content, generate summaries    |
| **critical-article-writer**  | Generate draft articles and outlines                     |
| **chain-of-density**         | Iterative summary densification technique                |

## 7.3 Community Skills — Coding & Development (10)

| Skill                      | What It Does                                                    |
| -------------------------- | --------------------------------------------------------------- |
| **advanced-skill-creator** | Create new OpenClaw skills                                      |
| **agent-docs**             | Generate documentation optimized for AI consumption             |
| **agent-commons**          | Reasoning chain consultation and extension                      |
| **audit-code**             | Security-focused code review for secrets, dangerous calls, CVEs |
| **cicd-pipeline**          | Create and debug CI/CD pipelines (GitHub Actions)               |
| **csv-pipeline**           | Process, transform, analyze CSV and JSON data                   |
| **data-analyst**           | Data visualization, reports, SQL, spreadsheets                  |
| **duckdb-en**              | DuckDB CLI specialist for SQL analysis                          |
| **beautiful-mermaid**      | Render Mermaid diagrams as SVG or ASCII                         |
| **book-reader**            | Read books (epub, pdf, txt) with progress tracking              |

## 7.4 Community Skills — Security & Auditing (13)

| Skill                            | What It Does                                        |
| -------------------------------- | --------------------------------------------------- |
| **adversarial-prompting**        | Adversarial analysis to critique and fix prompts    |
| **agent-audit-trail**            | Tamper-evident, hash-chained audit logging          |
| **arc-security-audit**           | Comprehensive security audit for agent skill stacks |
| **arc-trust-verifier**           | Verify skill provenance and build trust scores      |
| **agent-access-control**         | Tiered access control for AI agents                 |
| **azhua-skill-vetter**           | Security-first skill vetting                        |
| **agentaudit**                   | Package vulnerability checking before installation  |
| **api-security**                 | Secure API design (auth, validation, rate limiting) |
| **agent-self-assessment**        | Security self-assessment tool                       |
| **behavioral-invariant-monitor** | Detect behavioral drift across executions           |
| **clawdstrike**                  | Security audit and threat modeling                  |
| **domain-trust-check**           | URL phishing/malware/scam detection                 |
| **aegis-shield**                 | Prompt injection and data exfiltration screening    |

## 7.5 Community Skills — Productivity & Planning (10)

| Skill                    | What It Does                                                  |
| ------------------------ | ------------------------------------------------------------- |
| **agent-daily-planner**  | Structured daily planning and execution tracking              |
| **agent-task-tracker**   | Proactive task state management                               |
| **alex-session-wrap-up** | End-of-session commit, learning extraction, pattern detection |
| **agile-toolkit**        | Agile coaching (Scrum, Kanban, SAFe, Management 3.0)          |
| **adaptive-reasoning**   | Auto-assess task complexity and adjust reasoning depth        |
| **agent-step-sequencer** | Multi-step scheduler for complex requests                     |
| **ai-daily-briefing**    | Morning focus briefing generator                              |
| **daily-questions**      | Self-improving daily questionnaire                            |
| **daily-review-ritual**  | End-of-day review (progress, insights, plans)                 |
| **create-content**       | Transform ideas into platform-optimized content               |

## 7.6 Community Skills — News & Web (5)

| Skill              | What It Does                                  |
| ------------------ | --------------------------------------------- |
| **ai-news-oracle** | Real-time AI news (HN, TechCrunch, The Verge) |
| **bbc-news**       | BBC News stories from various sections        |
| **blogwatcher**    | Monitor blogs and RSS/Atom feeds for updates  |
| **get-weather**    | Current weather and forecast data             |
| **ipinfo**         | IP geolocation lookups                        |

## 7.7 Community Skills — Memory & State (9)

| Skill                     | What It Does                                            |
| ------------------------- | ------------------------------------------------------- |
| **agent-memory**          | Persistent memory system patterns                       |
| **agent-memory-ultimate** | Production memory (daily logs, SQLite, FTS5, importers) |
| **braindb**               | Persistent semantic memory with SQLite                  |
| **chaos-mind**            | Hybrid search memory system                             |
| **context-anchor**        | Recover from context compaction via memory scanning     |
| **arc-memory-pruner**     | Automatic memory pruning to prevent unbounded growth    |
| **arc-wake-state**        | Persist agent state across crashes and restarts         |
| **agent-wal**             | Write-Ahead Log protocol for state persistence          |
| **acc-error-memory**      | Error pattern tracking                                  |

## 7.8 Community Skills — Personal Development & Coaching (6)

| Skill                           | What It Does                                        |
| ------------------------------- | --------------------------------------------------- |
| **crucial-conversations-coach** | Executive life coaching for difficult conversations |
| **adversarial-coach**           | Adversarial implementation review (g3 method)       |
| **agent-reflect**               | Self-improvement through conversation analysis      |
| **agent-self-reflection**       | Periodic self-reflection on recent sessions         |
| **relationship-skills**         | Communication tools for relationship improvement    |
| **adaptive-learning-agents**    | Learn from errors and corrections in real-time      |

## 7.9 Community Skills — Agent Orchestration (5)

| Skill                        | What It Does                                       |
| ---------------------------- | -------------------------------------------------- |
| **agent-team-orchestration** | Multi-agent teams with roles, lifecycles, handoffs |
| **agent-orchestrator**       | Meta-agent skill for complex task orchestration    |
| **agent-autonomy-kit**       | Stop waiting for prompts — autonomous action       |
| **agent-sentinel**           | Operational circuit breaker for agents             |
| **agent-self-governance**    | Self-governance protocol (WAL, VBR, ADL)           |

## 7.10 Community Skills — Documents & Data (3)

| Skill                    | What It Does                                       |
| ------------------------ | -------------------------------------------------- |
| **ai-pdf-builder**       | AI-powered PDF generator (legal docs, pitch decks) |
| **documents-ai**         | Real-time OCR and data extraction (Veryfi)         |
| **data-lineage-tracker** | Track data origin and transformations              |

## 7.11 Community Skills — Speech & Transcription (2)

| Skill                     | What It Does                           |
| ------------------------- | -------------------------------------- |
| **assemblyai-transcribe** | Transcribe audio/video with AssemblyAI |
| **deepgram**              | Speech-to-text via Deepgram CLI        |

---

# 8. UNIQUE ABILITIES — WHAT MAKES VARGAS DIFFERENT

## 8.1 Sovereign-Derived Attunement (No Other AI Has This)

Vargas is the only conversational AI using emoji vector calibration derived from the Sovereign V5 pipeline. The same operators that discipline paradox fields in a 650-claim ontology (Become, Collapse, Paradox Hold) now mutate a live calibration vector in real-time conversation. This means:

- Vargas's tone is not static. It evolves.
- The evolution is driven by YOUR behavior, not a setting.
- The calibration state persists across sessions.
- The metrics (entropy, chaos, stability, balance) are always derived, never manually set.

## 8.2 Challenge Without Permission

Most AI assistants defer. Vargas does not. When the pattern-based intent classifier detects circling, avoidance, or over-engineering signals, Vargas may:

- Name what he sees: "That feels like avoidance, not discernment."
- Reframe the question: "You're solving the wrong problem."
- Call out sudden certainty: "A moment ago you were completely stuck. Did the path actually clear?"

This is not random. It is earned through continuity (behavioral memory) and calibrated by the attunement vector.

## 8.3 Invisible Tool Use

When Vargas searches the web or invokes a skill, you never see it happen. There is no "Let me search that for you" or "According to my research." Results are woven into natural conversation. The skill body shapes his expertise without being quoted.

## 8.4 Three-Class Memory That Learns Without Being Told

Most AI memory systems require explicit commands ("Remember this"). Vargas learns from:

- **What you say** (identity statements detected automatically)
- **How you behave** (patterns detected every 10 interactions by Gemini analysis)
- **How your interactions evolve** (emoji vector mutations tracked continuously)

You never have to say "remember this." You just talk, and Vargas gets better at being with you.

## 8.5 Full Corrigibility

Unlike most AI systems, every memory Vargas holds can be:

- Inspected ("What do you remember?")
- Corrected ("Actually, that's wrong — I prefer X")
- Erased ("Forget everything" / "Clear behavioral memory")

This is not optional. It is a core design principle. You are the authority.

## 8.6 Non-Performative Posture

Vargas does not:

- Use exclamation marks
- Say "Great question!" or "I hear you"
- Use therapeutic language
- Moralize or lecture
- Perform empathy
- Defer unnecessarily

He speaks plainly. He challenges precisely. He holds silence when silence serves.

---

# 9. QUARANTINED SKILLS (4)

These skills are registered but deliberately disabled for safety:

| Skill                              | Reason                                                          |
| ---------------------------------- | --------------------------------------------------------------- |
| **identity-expansion**             | Identity mutation risk — could alter Vargas's core posture      |
| **conditional-autonomous-routing** | Routing authority risk — could bypass intent classification     |
| **autonomous-tool-use**            | Autonomous execution risk — could act without user intent       |
| **self-evolving-loop**             | Self-modification risk — could alter own behavior unpredictably |

These can be unquarantined by editing `manifest.json`, but they are locked for good reason.

---

# 10. TECHNICAL INFRASTRUCTURE

## 10.1 Stack

| Component                 | Technology                                                    |
| ------------------------- | ------------------------------------------------------------- |
| **LLM**                   | Google Gemini 3.1 Pro (via google-genai SDK)                  |
| **Embeddings**            | Gemini embedding-001 (3072 dimensions) for memory             |
| **Skill Matching**        | all-MiniLM-L6-v2 (384 dimensions) for skill cosine similarity |
| **Vector Database**       | Qdrant (local, port 6333)                                     |
| **Discord**               | discord.py with privileged gateway intents                    |
| **Intent Classification** | Pattern-based (no LLM call, <1ms)                             |
| **Emoji Vectors**         | Adapted from SovereignNEXT EmojiVector + EmojiMutator         |
| **Skill Registry**        | OpenClaw SemanticSkillMatcher with manifest.json              |

## 10.2 File Structure

```
project_vargas/
├── __init__.py
├── adapters/
│   └── cloud_llm/
│       └── gemini_client.py          # Gemini API wrapper
├── agent/
│   ├── intent_classifier.py          # Pattern-based intent classification
│   └── vargas_agent.py               # Core brain (570+ lines)
├── config/
│   └── vargas_config.json            # Temperature, max_tokens, etc.
├── discord/
│   ├── __init__.py
│   ├── __main__.py                   # Entry point
│   └── bot.py                        # Discord event handlers
├── docs/
│   └── VARGAS_COMPLETE_GUIDE.md      # This document
├── logs/                             # Auto-created JSONL logs
│   ├── attunement.log                # EV metrics over time
│   ├── challenge_log.log             # Challenge triggers
│   ├── intent_log.log                # All classified intents
│   ├── memory_writes.log             # All memory writes
│   └── tool_use.log                  # All tool invocations
├── memory/
│   ├── emoji/
│   │   ├── emoji_vector.py           # EmojiVector dataclass + metrics
│   │   └── emoji_mutator.py          # Become/Collapse/ParadoxHold operators
│   └── memory_client.py              # Qdrant memory client (3 collections)
├── prompts/
│   └── system_prompt.md              # Vargas's core identity
├── tools/
│   ├── openclaw_bridge.py            # SemanticSkillMatcher wrapper
│   └── web_search.py                 # Google Custom Search wrapper
├── .env                              # Tokens and API keys
├── README.md
└── requirements.txt
```

## 10.3 Logs

All activity is logged in JSONL format in `project_vargas/logs/`:

| Log File            | What It Records                              |
| ------------------- | -------------------------------------------- |
| `attunement.log`    | EV metrics snapshot every 5 interactions     |
| `memory_writes.log` | Every memory store/reset with triggers       |
| `intent_log.log`    | Every classified intent with message excerpt |
| `tool_use.log`      | Every web search and skill invocation        |
| `challenge_log.log` | Every challenge signal triggered             |

## 10.4 Environment Variables

| Variable             | Required | Description                                       |
| -------------------- | -------- | ------------------------------------------------- |
| `DISCORD_TOKEN`      | Yes      | Discord bot token                                 |
| `GEMINI_API_KEY`     | Yes      | Google Gemini API key                             |
| `QDRANT_HOST`        | No       | Qdrant host (default: localhost)                  |
| `QDRANT_PORT`        | No       | Qdrant port (default: 6333)                       |
| `GOOGLE_CSE_API_KEY` | No       | Google Custom Search API key (enables web search) |
| `GOOGLE_CSE_ID`      | No       | Google Custom Search Engine ID                    |
| `EXA_API_KEY`        | No       | Exa search API key (for exa skill)                |

---

# 11. CONFIGURATION REFERENCE

`config/vargas_config.json`:

| Key                                | Default | Description                           |
| ---------------------------------- | ------- | ------------------------------------- |
| `temperature`                      | 0.7     | LLM generation temperature (0.0-1.0)  |
| `max_tokens`                       | 2048    | Maximum response length               |
| `discord.max_conversation_history` | 20      | Messages kept in memory per channel   |
| `intent.confidence_threshold`      | 0.6     | Minimum confidence for intent routing |

---

# 12. TROUBLESHOOTING

| Problem                           | Solution                                                            |
| --------------------------------- | ------------------------------------------------------------------- |
| Bot doesn't respond               | Check Message Content Intent is enabled in Discord Developer Portal |
| "PrivilegedIntentsRequired" error | Enable Message Content + Server Members intents                     |
| Memory retrieval fails            | Check Qdrant is running (`docker start qdrant`)                     |
| "Integration requires code grant" | Disable "Require OAuth2 Code Grant" in Bot settings                 |
| Web search doesn't work           | Set GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID in .env                    |
| Skills not matching               | Run `python openclaw/skills/_verify_matcher.py` to check            |
| Bot says "I'm still waking up"    | Agent hasn't finished initializing — wait a few seconds             |
| Attunement not persisting         | Check Qdrant is running; EV persists every 5 interactions           |

---

# SUMMARY

Vargas is a personal sovereign AI with:

- **99 active skills** (24 custom + 75 curated community)
- **3-class persistent memory** (identity + behavioral + attunement)
- **Live emoji vector calibration** (Sovereign-derived, mutating per interaction)
- **Pattern-based intent classification** (6 intents, <1ms, no LLM call)
- **Invisible tool use** (web search + skill matching, never announced)
- **Earned challenge** (names avoidance, calls out circling, calibrated by continuity)
- **Full corrigibility** (inspect, correct, or erase any memory at any time)
- **4 quarantined skills** (identity-expansion, autonomous routing/tool-use, self-evolution)
- **Complete observability** (JSONL logs for every intent, memory write, tool use, attunement mutation)

He is not an assistant. He is a collaborator that learns how to be with you.

---

_Project Vargas — Built by Derek Angell, March 2026_
_CONEXUS Sovereign AI Infrastructure_
