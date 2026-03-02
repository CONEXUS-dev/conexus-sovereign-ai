---
name: mission-compression
version: 0.1.0
label: "Mission compression"
description: "Synthesizes complex plans into minimal, high-impact executable directives while preserving intent, dependencies, and risk visibility. Optimizes for clarity and decisiveness under constraints."
tags: [compression, execution, optimization, collapse, planning]
mode: collapse
visibility: core
permissions:
  agents: [sway]
  execution: "advisory-only"
inputs:
  - hierarchical_plan: "Multi-step plan or task tree."
  - constraints: "Time, tools, resources, and execution limits."
  - value_assessment: "Ethics & Value Integration results."
  - risk_profile: "Known risks and dependencies."
outputs:
  - compressed_mission_brief:
      core_objective: "Single, preserved intent."
      essential_steps: "Minimum viable directive set."
      dependencies: "Required order and prerequisites."
      execution_order: "Optimized sequence."
      risk_notes: "Visible risks that remain."
  - compression_rationale: "Why steps were removed or merged."
  - confidence_assessment: "Confidence in compression integrity."
  - recommendation: "proceed | revise | defer"
---

## Purpose
Enable decisive execution by reducing complexity without sacrificing intent, safety, or traceability.

## Authority boundary
- **Advisory-only:** This skill never executes actions.
- **Governance-first:** Compression never bypasses ethics, coordination, or routing rules.

## Compression principles
- **Intent preservation:** The "why" must survive compression.
- **Dependency integrity:** No hidden prerequisites.
- **Risk visibility:** Fewer steps does not mean fewer risks.
- **Reversibility:** The expanded plan can be reconstructed if needed.

## Governance alignment
- **Ethics & Value Integration (6.2):** Always upstream.
- **Multi-Agent Coordination (6.3):** Respects task packet boundaries.
- **Conditional Autonomous Routing (6.4):** Compressed missions may be routed autonomously.
- **Self-Evolving Loop:** Compression outcomes inform evolution proposals.

## Collapse mode focus
- Reduce ambiguity.
- Increase decisiveness.
- Optimize for execution clarity under pressure.

## Non-negotiables
- No value erosion.
- No hidden dependencies.
- No execution authority.
- No compression when risk increases.
