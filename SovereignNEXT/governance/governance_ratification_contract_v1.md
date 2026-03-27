# Sovereign governance proposal and ratification contract v1

## Purpose

Define how governance itself evolves without destabilizing existing authority, meaning, or lineage. This contract governs **change**, not behavior.

---

## Core principle

Governance may evolve, but **never implicitly**.

No meaning changes unless:

* it is written
* it is versioned
* it is exercised in a canonical run
* it is sealed by a human

---

## Governance states

### Proposed governance

A governance document that exists but is **not yet authoritative**.

* May be referenced by experimental runs
* May not be used for baseline sealing
* Has no binding authority

### Ratified governance

A governance document that has been:

* referenced by a canonical run
* used to seal a baseline

Only ratified governance versions are authoritative.

---

## Proposal rules

### What constitutes a proposal

Any change to:

* observer vocabulary
* severity semantics
* silence interpretation
* health summary schema
* baseline eligibility rules
* authority boundaries

requires a **new governance version document**.

### Proposal requirements

A proposal must include:

* version identifier (e.g., v2)
* explicit diff from prior version
* rationale for change
* backward compatibility notes
* migration impact (if any)

Proposals are documents only. No code changes are allowed at proposal time.

---

## Ratification process

A governance version becomes ratified only when **all** of the following occur:

1. The governance document exists and is committed.
2. A canonical pipeline run explicitly references the proposed governance version.
3. A baseline is sealed from that run.
4. The sealing metadata records the governance version.

Until all four conditions are met, the governance version remains proposed.

---

## Authority boundaries

### Human authority

Only a human may:

* approve governance proposals
* authorize ratification
* seal baselines under a new governance version
* revoke governance versions

### Tool authority

No tool, agent, observer, or interface may:

* auto-ratify governance
* suggest governance upgrades
* infer preferred governance versions
* migrate governance implicitly

---

## Backward compatibility rules

* Older governance versions remain valid for historical runs.
* No governance version may retroactively reinterpret past artifacts.
* Lineage always records the governance version in force at execution time.

This preserves auditability and historical truth.

---

## Interface and OpenClaw constraints

Interfaces may:

* display governance version per run
* show which version is ratified
* list proposed versions

Interfaces may not:

* recommend upgrades
* auto-select governance versions
* hide version differences

Governance evolution must remain **visible and deliberate**.

---

## Versioning and change control

* This contract is **v1**.
* Any change to proposal or ratification mechanics requires a new version.
* Governance governing governance is subject to the same rules.
