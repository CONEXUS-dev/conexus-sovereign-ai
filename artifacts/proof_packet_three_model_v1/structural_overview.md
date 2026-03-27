# Structural Proof Summary

This document explains why the governance invariants hold regardless of which LLM is bound to the pipeline. It uses only structural arguments and references only artifacts in this proof packet.

---

## 1. Pipeline Flow

```
                    ┌─────────────────────────────┐
                    │   Sealed Starting Snapshot   │
                    │   (Sovereign-V5-Anchor)      │
                    │   650 claims, 1505 tensions  │
                    │   84 paradoxes               │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │      LLM Generation         │
                    │  (model-specific, variable)  │
                    │                             │
                    │  Inputs: claims + prompts   │
                    │  Outputs: raw text          │
                    └──────────────┬──────────────┘
                                   │
                    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
                    GOVERNANCE BOUNDARY
                    Everything below is deterministic
                    given state + seed
                    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │  OPERATOR 1: Collapse        │
                    │                             │
                    │  Evaluates open tensions    │
                    │  Actions: commit / defer /  │
                    │    paradox_held / skip      │
                    │  Result: 0 open tensions    │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │  OPERATOR 2: Become          │
                    │                             │
                    │  Expands held paradoxes     │
                    │  Spawns alternative claims  │
                    │  Does NOT resolve paradoxes │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │  OPERATOR 3: Paradox-Hold    │
                    │                             │
                    │  Stabilizes or nudges       │
                    │  paradoxes toward balance   │
                    │  Enforces hold invariant    │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │  OPERATOR 4: Observer        │
                    │                             │
                    │  Detects anomalies          │
                    │  Classifies: oscillating,   │
                    │    drifting, regulated       │
                    │  Reports health summary     │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │    Governed Final State      │
                    │    (hashable, auditable)     │
                    └─────────────────────────────┘
```

---

## 2. Where LLM Output Enters and Where It Is Constrained

```
  LLM OUTPUT                    GOVERNANCE OPERATORS
  (variable)                    (deterministic)
  ──────────                    ────────────────────

  Raw text          ──┐
  (claims,            │
   expansions,        │
   tension            │        ┌─────────────────┐
   judgments)         ├───────▶│ Parsed into      │
                      │        │ structured state │
                      │        └────────┬────────┘
                      │                 │
                      │                 ▼
                      │        ┌─────────────────┐
                      │        │ Collapse: force  │
                      │        │ all tensions to  │
                      │        │ resolution       │
                      │        └────────┬────────┘
                      │                 │
                      │                 ▼
                      │        ┌─────────────────┐
                      │        │ Become: expand   │
                      │        │ paradoxes into   │
                      │        │ alternatives     │
                      │        └────────┬────────┘
                      │                 │
                      │                 ▼
                      │        ┌─────────────────┐
                      │        │ Hold: stabilize  │
                      │        │ or nudge every   │
                      │        │ paradox          │
                      │        └────────┬────────┘
                      │                 │
                      │                 ▼
                      │        ┌─────────────────┐
                      └───────▶│ Observer: audit  │
                               │ final state      │
                               └─────────────────┘

  KEY INSIGHT:
  The LLM produces raw material.
  The operators decide what happens to it.
  The operators are deterministic given state + seed.
  Therefore, model choice cannot violate invariants.
```

---

## 3. Model Binding Abstraction

```
  ┌──────────────────────────────────────────────┐
  │           SOVEREIGN PIPELINE (fixed)          │
  │                                              │
  │  Operators: Collapse → Become → Hold → Obs   │
  │  State:     v5_final_state_snapshot.json      │
  │  Seed:      42                               │
  │  Governance: v1                              │
  │                                              │
  │         ┌──────────────┐                     │
  │         │  LLM SLOT    │ ◄── swappable       │
  │         └──────────────┘                     │
  │              │                               │
  │    ┌─────────┼─────────┐                     │
  │    ▼         ▼         ▼                     │
  │  LLaMA   Mistral     Phi                    │
  │  (8B)    (7B)        (4B)                    │
  │  GPT4All GPT4All  llama-cpp                  │
  │                                              │
  │  Each model fills the same slot.             │
  │  Each model's output is governed by the      │
  │  same operator sequence.                     │
  │  No model can bypass or alter operators.     │
  └──────────────────────────────────────────────┘
```

---

## 4. Operator Dominance

The following table shows which aspects of the final state are controlled by the LLM vs. the operators:

| Final state property | Controlled by LLM | Controlled by operators |
|---------------------|-------------------|------------------------|
| Raw claim text | Yes | No |
| Raw tension text | Yes | No |
| Number of new claims | Yes | No |
| Number of new tensions | Yes | No |
| Whether tensions are resolved | No | Yes (Collapse) |
| Whether paradoxes are held | No | Yes (Hold) |
| Whether paradoxes are vetoed | No | Yes (Collapse) |
| Paradox promotion threshold | No | Yes (fixed rule) |
| Open tension count at end | No | Yes (Collapse forces to 0) |
| Operator execution order | No | Yes (hardcoded) |
| Observer health assessment | No | Yes (Observer) |

**Summary:** The LLM controls the *content* of claims and tensions. The operators control the *structural outcomes*. Since invariants are structural properties (zero open tensions, 100% held, 100% vetoed), they are operator-controlled and therefore model-independent.

---

## 5. Why Model Choice Cannot Violate Invariants

1. **Collapse processes every open tension.** It does not skip. It does not consult the LLM for permission. Result: 0 open tensions, always.

2. **Paradox-Hold processes every paradox.** It stabilizes or nudges each one. It does not skip. Result: 100% held, always.

3. **Collapse vetoes every paradox.** The veto is a structural operation applied to all paradoxes after tension resolution. It does not depend on LLM output. Result: 100% vetoed, always.

4. **The operator sequence is hardcoded.** No model output can reorder, skip, or modify the sequence. It runs: Collapse → Become → Paradox-Hold → Observer. Always.

5. **The seed is fixed.** Any pseudorandom decisions within operators use seed 42. Given the same state and seed, operators produce identical results.

The LLM is upstream of the governance boundary. The invariants are downstream. The boundary is not permeable.
