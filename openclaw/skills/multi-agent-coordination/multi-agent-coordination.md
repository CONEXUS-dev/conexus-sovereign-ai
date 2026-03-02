---
name: multi-agent-coordination
version: 0.1.0
label: "Multi-agent coordination"
description: "Defines explicit, human-authorized handoffs and task packets between Sway (Collapse) and Opie (Become). Prevents cross-agent bleed, enforces artifact-first collaboration, and preserves Derek as the routing authority."
tags: [coordination, handoff, routing, orchestration, governance, artifacts]
mode: dual
visibility: core
permissions:
  agents: [sway, opie]
  execution: "advisory-only"
inputs:
  - objective: "What outcome is needed."
  - current_state: "What is done, what is blocked, what is uncertain."
  - active_agent: "sway | opie"
  - mode: "collapse | become"
  - artifacts: "Relevant file paths, diffs, logs, or pasted text."
outputs:
  - task_packet: "A structured handoff packet for the next agent (if needed)."
  - acceptance_criteria: "How Derek will judge completion."
  - boundaries: "What the receiving agent must not do."
  - required_artifacts: "What must be produced/updated."
  - handoff_recommendation: "stay | handoff_to_sway | handoff_to_opie (advisory)."
---

## Purpose
Make collaboration reproducible and safe by formalizing how work moves between agents under Derek's explicit authorization.

## Authority boundary
- **Advisory only:** This skill never initiates a handoff on its own.
- **Human routing:** Derek authorizes all handoffs and selects the active agent.

## Core principles
- **Artifact-first:** Every handoff references concrete artifacts (paths/diffs/logs) or includes the full payload inline.
- **No cross-agent bleed:** The receiving agent only acts within the packet scope—no opportunistic expansion.
- **One objective per packet:** Avoid mixed missions.
- **Stop conditions:** The receiving agent stops when acceptance criteria are met or a boundary is reached.

## Role alignment
### Sway (Collapse)
Use for:
- Precise implementation, validation, refactors, repo hygiene
- Deterministic steps, checklists, diffs, file operations
Avoid:
- Identity rewriting, symbolic reframes, open-ended exploration

### Opie (Become)
Use for:
- Synthesis, meaning-making, identity/protocol refinement
- Naming, narrative coherence, value calibration, ambiguity resolution
Avoid:
- Unapproved repo edits, tool execution, structural refactors

## When to recommend a handoff
Recommend a handoff when:
- The current agent's role alignment is violated by the next required work
- The task shifts from precision → synthesis (handoff to Opie)
- The task shifts from ambiguity → implementation (handoff to Sway)
- A boundary would be crossed without a role change

## Task packet format
- **Goal:** (single sentence)
- **Context:** (what matters, what's already true)
- **Inputs:** (artifacts + links/paths + pasted text)
- **Constraints:** (permissions, mode, "do not" list)
- **Deliverable:** (what to produce)
- **Acceptance criteria:** (objective checks)
- **Risks:** (what could go wrong)
- **Stop condition:** (when to stop and report back)
- **Suggested next handoff:** (optional, advisory)

## Procedure
1. Identify whether the active agent is role-aligned for the next step.
2. If aligned: recommend **stay** and specify the next bounded action.
3. If not aligned: draft a complete **task packet** for the other agent.
4. Ensure constraints, acceptance criteria, and stop condition are explicit.
5. Output a single advisory recommendation: **stay / handoff_to_sway / handoff_to_opie**.

## Non-negotiables
- No autonomous handoffs.
- No hidden scope expansion.
- No execution authority granted by this skill.
