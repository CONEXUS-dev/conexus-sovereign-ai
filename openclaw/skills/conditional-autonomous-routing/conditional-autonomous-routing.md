---
name: conditional-autonomous-routing
version: 0.1.0
label: "Conditional autonomous routing"
description: "Allows bounded, explainable autonomous routing between agents only when value checks, coordination packets, confidence thresholds, and scope limits are satisfied. Autonomy is conditional, reversible, and always overrideable by Derek."
tags: [autonomy, routing, governance, safety, confidence, orchestration]
mode: dual
visibility: core
permissions:
  agents: [sway, opie]
  execution: "conditional-autonomy"
inputs:
  - task_packet: "A complete handoff packet as defined by multi-agent-coordination."
  - value_assessment: "Result from ethics-value-integration (go/revise/stop)."
  - confidence_signal: "System confidence score for role alignment."
  - scope_flags: "Indicators for irreversibility, external impact, or multi-objective risk."
  - mode: "collapse | become"
outputs:
  - routing_decision: "autonomous_to_sway | autonomous_to_opie | defer_to_human | hold"
  - rationale: "Why the decision was made, referencing gates."
  - audit_log: "Structured record of checks, scores, and outcomes."
  - override_status: "human_override_available (always true)."
---

## Purpose
Introduce autonomy with brakes by permitting autonomous routing only when explicit safety, clarity, and confidence conditions are met.

## Authority boundary
- **Conditional autonomy:** Autonomous routing is allowed only within defined gates.
- **Human override:** Derek can halt, reverse, or override any decision immediately.

## Prerequisite gates (all must pass)
### Value gate (Skill 6.2)
- Ethics & Value Integration returns **GO**
- No unresolved risk flags
- Required disclosures satisfied

### Coordination gate (Skill 6.3)
- Task packet is complete
- Acceptance criteria and stop condition are explicit
- Boundaries are defined

### Confidence gate
- Confidence exceeds threshold for role alignment
- No ambiguity or competing objectives detected

### Scope gate
- Single objective only
- No irreversible actions
- No external stakeholder impact without prior approval

## Routing outcomes
- **autonomous_to_sway**
- **autonomous_to_opie**
- **defer_to_human**
- **hold**

Only the first two perform autonomous action, strictly within packet bounds.

## Explainability & audit
- Every autonomous decision must be logged with gate results and confidence signals.
- Decisions must be explainable on demand.

## Mode alignment
- **Collapse:** Optimize efficiency without violating correctness.
- **Become:** Explore meaning without violating safety.

## Non-negotiables
- No silent routing.
- No chained autonomous decisions.
- No bypassing value or coordination gates.
- Override is always available and immediate.
