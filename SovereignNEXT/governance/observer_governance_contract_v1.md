# Sovereign observer governance contract v1

## Purpose

Define a stable, non-ambiguous contract for what the **Sovereign Observer** is, what it is allowed to say, what it must never imply, and how its outputs are interpreted by humans and tooling (including OpenClaw). This contract governs **language and meaning**, not engine behavior.

---

## Definitions

### System layers

* **Pipeline:** Executes passes and produces state transitions and artifacts.
* **Operators:** Deterministic enforcement mechanisms (Phase 5) that constrain expansion and preserve boundedness.
* **Observer:** A reporting layer that inspects state and histories and emits classifications and summaries.
* **Governance:** The semantic contract that constrains observer language, severity, and interpretation.
* **Interface:** Any presentation layer (OpenClaw, CLI, UI) that displays governance-approved outputs.

### Authority boundaries

* **Observer has zero execution authority.**

  * It cannot mutate state.
  * It cannot trigger operators.
  * It cannot decide next actions.
  * It cannot block or approve runs.
* **Observer has descriptive authority only.**

  * It may classify and summarize.
  * It may explain why a classification occurred.
  * It may surface evidence references (counts, deltas, event windows).

---

## Observer output contract

### Output types

The observer emits **anomaly records**. Each record has:

* **type:** One of `stuck`, `saturated`, `oscillating`, `drifting`, `regulated`
* **severity:** One of `info`, `warning`
* **message:** Human-readable explanation constrained by vocabulary rules
* **evidence:** Minimal structured evidence fields (see below)

### Severity mapping

* **info**

  * `regulated`
* **warning**

  * `stuck`
  * `saturated`
  * `oscillating`
  * `drifting`

No other severities exist in v1.

---

## Semantic definitions

### regulated (info)

**Meaning:** A healthy expand-hold cycle is present and stable. Alternation alone is not pathological.

**Required evidence signals (minimum):**

* **cycle evidence:** At least one expand-hold alternation window exists
* **boundedness evidence:** Entropy remains within configured band or shows stabilization
* **veto continuity:** Veto state is stable or behaves as expected under hold

**Forbidden implications:**

* Must not imply a need for intervention.
* Must not imply instability.

---

### oscillating (warning)

**Meaning:** Alternation is present **and** at least one pathological signal is detected.

**Pathological signals (examples, not necessarily exhaustive):**

* entropy drift exceeds threshold within a hold-to-hold window
* repeated veto flips inconsistent with stable holding
* repeated status churn without convergence

**Required evidence:**

* **alternation window:** show the event indices or count window used
* **pathological signal:** name the signal and include the measured value and threshold

---

### drifting (warning)

**Meaning:** Monotonic entropy trend across multiple hold events indicates directional instability.

**Required evidence:**

* at least 3 hold events
* monotonic trend direction and magnitude

---

### stuck (warning)

**Meaning:** A paradox is held without sufficient history or without meaningful progression.

**Required evidence:**

* history length and relevant missing signals

---

### saturated (warning)

**Meaning:** Expansion is no longer producing meaningful novelty or is repeatedly hitting constraints.

**Required evidence:**

* repeated collapse outcomes or repeated low-novelty expansions (as defined by existing logic)

---

## Evidence schema v1

Each anomaly record must include a minimal `evidence` object with only what is needed to justify the classification.

### Required fields

* **paradox\_id:** string
* **window:** object
  * **events\_considered:** integer
  * **holds\_considered:** integer
* **entropy:** object
  * **latest:** number or null
  * **delta:** number or null
  * **threshold:** number or null
* **veto:** object
  * **latest\_state:** string or null
  * **flip\_count:** integer or null
* **status:** object
  * **latest:** string or null

No extra fields unless explicitly added in a version bump.

---

## Vocabulary and phrasing constraints

### Forbidden words

Observer messages must not include:

* `should`
* `recommend`
* `consider`
* `next`
* `optimize`
* `trigger`

### Forbidden speech acts

Observer messages must not:

* instruct actions
* propose plans
* assign blame
* imply urgency
* imply authority over execution

### Allowed speech acts

Observer messages may:

* describe what was detected
* cite evidence values and thresholds
* state classification and severity
* state uncertainty only if evidence is incomplete

---

## Silence semantics

### Definition of silence

**Silence** means: no warnings were emitted for the inspected scope.

### Interpretation

* Silence is a **positive health signal** when:

  * the observer ran successfully
  * artifacts were produced
  * the report indicates zero warnings
* Silence is **not** interpreted as health when:

  * the observer did not run
  * the report is missing
  * the run failed before observation

### Required interface behavior

Any interface must distinguish:

* **healthy silence:** observer ran, zero warnings
* **missing observation:** observer did not run or report missing

---

## Canonical health summary v1

A run must produce a single summary object derived from anomaly records.

### Summary fields

* **run\_id**
* **snapshot\_hash\_start**
* **snapshot\_hash\_end**
* **passes\_completed**
* **anomalies\_total**
* **warnings\_total**
* **regulated\_total**
* **warnings\_by\_type:** map of type → count
* **regulated\_by\_pass:** map of pass → count (if available)
* **warnings\_by\_pass:** map of pass → count (if available)

### Health statement rule

* If `warnings_total == 0`:
  * health\_statement = "healthy: no warnings"
* Else:
  * health\_statement = "warnings present: review anomalies"

No other health statements in v1.

---

## OpenClaw integration rules

OpenClaw must treat the observer as:

* **a reporter, not a controller**
* **a source of governance-approved summaries**
* **non-binding**

### Allowed OpenClaw actions in v1

* run pipeline with args
* detect completion/failure
* load and display canonical health summary
* list anomalies and filter by type/severity
* show evidence fields

### Forbidden OpenClaw actions in v1

* auto-rerun based on warnings
* auto-modify thresholds
* auto-seal baselines
* auto-escalate or notify without explicit human instruction

---

## Versioning and change control

* This contract is **v1**.
* Any change to:
  * anomaly types
  * severity mapping
  * evidence schema
  * vocabulary constraints
  * silence semantics
  * health summary fields
  requires a **v2** document and explicit approval.
