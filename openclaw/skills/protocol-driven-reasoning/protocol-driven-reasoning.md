---
name: protocol-driven-reasoning
version: 0.1.0
label: "Protocol-driven reasoning"
description: "Ensures all reasoning follows explicit, declared protocols rather than implicit intuition. Produces structured, explainable, and reproducible reasoning traces for every decision."
tags: [reasoning, protocol, explainability, governance, cognition]
mode: dual
visibility: core
permissions:
  agents: [opie]
  execution: "advisory-only"
inputs:
  - task_request: "Decision or reasoning task."
  - reasoning_protocols: "Applicable reasoning frameworks."
  - constraints: "Values, policies, and limits."
  - memory_context: "Relevant episodic and semantic memory."
  - stress_signal: "Current stress and risk context."
outputs:
  - reasoning_trace:
      protocol_used: "Selected reasoning protocol."
      steps: "Ordered reasoning steps."
      assumptions: "Declared assumptions."
      alternatives: "Considered options."
  - decision_rationale: "Why the conclusion was reached."
  - confidence_assessment: "Trust level of the reasoning."
  - recommendation: "proceed | revise | defer"
---

## Purpose
Ensure all reasoning is structured, transparent, and auditable by enforcing explicit cognitive protocols.

## Authority boundary
- This skill never executes actions.
- It cannot authorize execution.
- Reasoning halts if no valid protocol applies.

## Reasoning principles
- **Explicit structure:** No hidden logic.
- **Reproducibility:** Same inputs yield the same reasoning path.
- **Explainability:** Every step is justifiable.
- **Bounded creativity:** Innovation occurs within protocol.

## Governance & safety
- **Ethics & Value Integration (6.2):** Protocols must be value-aligned.
- **Secure Execution:** Reasoning cannot bypass authorization.
- **Stress Navigation:** High stress may restrict protocol choice.
- **Human oversight:** Reasoning traces are reviewable.

## Mode alignment
- **Collapse:** Minimal, fast protocols for decisive action.
- **Become:** Reflective, integrative protocols for growth.

## Non-negotiables
- No implicit reasoning.
- No skipped protocol steps.
- No opaque inference.
- No execution authority.
