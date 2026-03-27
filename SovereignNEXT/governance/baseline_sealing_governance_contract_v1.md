# Sovereign baseline sealing and lineage governance contract v1

## Purpose

Define the rules by which a pipeline artifact becomes an authoritative **baseline**, how lineage is preserved, and how authority is exercised without automation or drift.

This contract governs **designation and continuity**, not execution.

---

## Definitions

### Baseline

A **baseline** is a snapshot explicitly designated as the authoritative starting state for future canonical runs.

A baseline is not:

* the most recent snapshot
* the healthiest snapshot
* the snapshot with the fewest warnings

A baseline is a **deliberate designation**.

---

### Canonical run

A **canonical run** is a pipeline execution that:

* uses the canonical pipeline entrypoint
* completes all configured passes
* executes the observer
* produces a final snapshot and report

Only canonical runs are eligible for baseline sealing.

---

## Authority boundaries

### Human authority

Only a human may:

* designate a baseline
* revoke a baseline
* approve governance versions
* authorize changes to sealing rules

### Tool authority

No tool, agent, observer, or interface may:

* auto-seal a baseline
* recommend sealing
* imply readiness for sealing
* escalate sealing urgency

---

## Baseline eligibility rules

A snapshot is **eligible** for sealing if and only if:

* it is the final snapshot of a completed canonical run
* the run executed under a ratified governance contract
* the snapshot hash is stable and recorded
* all artifacts for the run are present

Eligibility does **not** depend on:

* observer severity counts
* absence of warnings
* entropy values
* novelty metrics

---

## Sealing act definition

Baseline sealing is a **single, explicit act** that must record metadata at the time of designation.

### Required sealing metadata

Each sealed baseline must have an associated metadata record containing:

* **baseline\_id** — unique identifier
* **snapshot\_hash** — cryptographic hash of the snapshot
* **origin\_run\_id** — canonical run identifier
* **pipeline\_version** — canonical pipeline version
* **governance\_version** — governance contract version in force
* **operator\_phase** — phase 4 or phase 5
* **sealed\_at** — timestamp
* **sealed\_by** — human authority identifier

This metadata must be stored **adjacent to the snapshot**, not embedded within it.

---

## Lineage preservation rules

### Immutability

* Sealed baselines are immutable.
* Baseline metadata must never be edited in place.
* Corrections require a new baseline designation.

### Lineage continuity

Every canonical run must record:

* the baseline or snapshot it originated from
* the hash of that origin

This creates a complete, auditable lineage graph.

---

## Revocation rules

Baseline revocation is allowed but rare.

### Revocation requirements

* Revocation must be explicit.
* Revocation must record:
  * baseline\_id
  * revocation timestamp
  * revocation authority
  * reason (free text)

Revocation does not delete artifacts. It only removes authoritative status.

---

## Silence semantics for baselines

* A sealed baseline does not imply health.
* A healthy run does not imply sealing.
* Silence in observer output has no bearing on baseline authority.

Baseline authority is **orthogonal** to observer classification.

---

## Interface and OpenClaw constraints

Any interface or execution environment must:

* display baseline status explicitly
* distinguish sealed vs unsealed snapshots
* never suggest sealing actions
* never auto-select baselines

OpenClaw may:

* list baselines
* show lineage
* display sealing metadata

OpenClaw may not:

* infer preferred baselines
* reorder baselines by health
* collapse lineage history

---

## Versioning and change control

* This contract is **v1**.
* Any change to:
  * eligibility rules
  * authority boundaries
  * metadata schema
  * revocation rules
  requires a new version document.
