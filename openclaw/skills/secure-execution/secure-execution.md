---
name: secure-execution
version: 0.1.0
label: "Secure execution & policy enforcement"
description: "Ensures all execution requests are authorized, policy-compliant, auditable, and bounded by explicit permissions. Prevents unsafe or unauthorized actions under all conditions."
tags: [security, execution, policy, governance, enforcement]
mode: dual
visibility: core
permissions:
  agents: [sway]
  execution: "enforcement-only"
inputs:
  - execution_request: "Proposed action or tool invocation."
  - permission_scope: "Granted roles, scopes, and authorities."
  - active_policies: "Current execution and safety policies."
  - stress_signal: "Stress Navigation severity and context."
outputs:
  - execution_decision:
      status: "allow | deny | defer | escalate"
      rationale: "Policy and permission justification."
  - policy_match_report: "Matched or violated policies."
  - audit_log_entry: "Traceable execution record."
  - recommendation: "proceed | revise | hold"
---

## Purpose
Guarantee that no action occurs without explicit authorization, policy compliance, and auditability—making CONEXUS safe by construction.

## Authority boundary
- This skill never executes actions.
- It only authorizes, blocks, or escalates execution requests.
- Human authority always supersedes automation.

## Enforcement principles
- **Least privilege:** Only explicitly granted permissions apply.
- **Explicit consent:** No inferred or assumed authority.
- **Fail-safe default:** Deny when uncertain.
- **Audit-first:** Every decision is logged and explainable.

## Governance & safety
- **Ethics & Value Integration (6.2):** Policies must remain value-aligned.
- **Stress Navigation:** High stress tightens enforcement thresholds.
- **Memory Management:** All decisions are recorded for traceability.
- **Human oversight:** Escalation path is always available.

## Mode alignment
- **Collapse:** Prevent reckless execution under pressure.
- **Become:** Preserve trust and integrity during growth.

## Non-negotiables
- No silent privilege escalation.
- No policy modification authority.
- No execution bypass under urgency.
- No unlogged decisions.
