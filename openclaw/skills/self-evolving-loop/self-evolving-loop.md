---
name: self-evolving-loop
version: 0.1.0
label: "Self-evolving loop"
description: "Enables controlled system evolution through observation, reflection, and proposal. Generates bounded evolution proposals that require governance checks and explicit human approval. No silent mutation."
tags: [evolution, learning, governance, lineage, reflection]
mode: dual
visibility: core
permissions:
  agents: [sway, opie]
  execution: "proposal-only"
inputs:
  - execution_logs: "Tool usage, task outcomes, errors, and completions."
  - routing_history: "Autonomous and manual routing decisions with overrides."
  - value_outcomes: "Ethics & Value Integration results."
  - human_feedback: "Approvals, rejections, and corrections."
  - mode: "collapse | become"
outputs:
  - evolution_proposal:
      target: "Skill, routing rule, protocol, or memory behavior."
      change: "Proposed modification or addition."
      rationale: "Why the change improves the system."
      risks: "Potential downsides or failure modes."
      rollback_plan: "How to revert safely."
      expected_benefit: "Measurable or qualitative gain."
  - confidence_assessment: "System confidence in the proposal."
  - recommendation: "propose | defer | discard"
---

## Purpose
Allow CONEXUS to improve itself without losing values, lineage, or human authority by proposing changes rather than applying them.

## Authority boundary
- **Proposal-only:** This skill never applies changes.
- **Human approval required:** Derek explicitly approves or rejects every proposal.

## Governance gates (all required)
### Ethics & value gate (Skill 6.2)
- No value violations
- No hidden tradeoffs
- Transparency preserved

### Lineage gate
- Changes are additive or versioned
- No destructive edits
- Full audit trail maintained

### Scope gate
- One change per proposal
- No cascading or self-referential evolution

### Human approval gate
- Approval or rejection is logged
- Rejections recalibrate proposal confidence

## Learning behavior
- Approved proposals increase confidence
- Rejected proposals reduce aggressiveness
- Overrides refine future proposal thresholds
- The system learns how to propose, not how to bypass

## Mode alignment
- **Collapse:** Improve efficiency, reliability, and execution quality
- **Become:** Refine meaning, coherence, and identity

## Non-negotiables
- No silent mutation
- No recursive self-modification
- No deletion of lineage
- No execution authority
