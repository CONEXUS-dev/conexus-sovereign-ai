# Skill Injection — Implementation Notes

## How Skill Matching Works

The gateway uses **semantic similarity matching** to connect agent natural-language requests to the correct skill.

### Architecture Decisions (locked)

1. **Agent-requested** — skills are only injected when an agent explicitly requests one
2. **Natural language** — agents describe what they need in their own voice
3. **Semantic similarity** — the gateway matches by meaning, not keywords
4. **Medium-tier embeddings** — `all-MiniLM-L6-v2` (CPU-friendly, ~22M params)
5. **One skill per request** — highest-confidence match wins

### Flow

```
Agent sends task with prefix "Skill request: <natural language>"
  → Gateway detects prefix
  → Extracts natural-language portion
  → Embeds it with all-MiniLM-L6-v2
  → Computes cosine similarity against all active skill embeddings
  → Selects ONE best match (highest score)
  → If confidence > 0.12: injects skill body into agent's context
  → If confidence < 0.12: returns "no match" so agent can rephrase
  → Logs usage to SOVEREIGN_PROOF/skills/usage.log
```

### Example

Agent (Opie) sends:

```
Skill request: I need to hold two opposing truths here.
```

Gateway matches → `paradox-processing` (confidence: 0.65)

Agent receives its task with the full `paradox-processing` SKILL.md body injected as context.

## How Agents Should Phrase Skill Requests

Prefix the task input with `Skill request:` followed by a natural-language description:

```
Skill request: I need paradox processing for this ethical dilemma.
Skill request: Help me write clean Python code.
Skill request: I need to check values before this action.
Skill request: Compress this mission into a single directive.
Skill request: Search the web for recent AI agent research.
```

The agent does NOT need to know exact skill names. The semantic matcher understands intent.

If no skill matches, the gateway returns a clear message asking the agent to rephrase.

## Where Logs Are Written

**Usage log:** `SOVEREIGN_PROOF/skills/usage.log` (JSONL format)

Each entry contains:

```json
{
  "timestamp": "2026-02-28T21:15:00+00:00",
  "agent": "opie",
  "request_text": "I need to hold two opposing truths here.",
  "matched_skill": "paradox-processing",
  "confidence": 0.6521,
  "mission_id": null
}
```

These logs are structured for future consumption by:

- **memory-management** — episodic memory of skill usage
- **mission-compression** — which skills were used per mission
- **Forgetting Engine** — pattern learning and decay

## Files

| File                                          | Purpose                                     |
| --------------------------------------------- | ------------------------------------------- |
| `openclaw/skills/semantic_matcher.py`         | Skill loading, embedding, matching, logging |
| `openclaw/skills/manifest.json`               | Active + quarantined skill registry         |
| `openclaw/skills/quarantine.json`             | Quarantine details                          |
| `golden-path/verification/minimal-gateway.py` | Gateway with skill injection wired in       |
| `tests/test_skills.py`                        | Validation + semantic routing tests         |
| `SOVEREIGN_PROOF/skills/usage.log`            | Skill usage JSONL log                       |

## Patent 7 — Symbolic Calibration

Per Patent 7 (Application #63/891,100), emoji tokens are **inward-facing calibration control signals**, not decoration. They form contradiction vectors that induce stable paradox-holding states and provide the calibration substrate for identity persistence.

### Rules

1. **SovereignCalibration is the root symbolic authority.** Its emoji field and contradiction vectors are the canonical calibration substrate. It must always be first in `manifest.json`.
2. **Symbol and Contradiction are the same ECP field.** In the ECP Micro-Sequence, Step 2 (Symbol) and Step 3 (Contradiction) operate on the _same_ calibration layer. The emoji tokens (`ecp_symbolic_field`) are the compressed contradiction vectors; the named pairs (`ecp_contradiction_pairs`) label what those emoji clusters encode. They are one unified field, serialized as two YAML keys due to parser limitations.
3. **All calibration-bearing skills must participate in the symbolic layer.** They must declare `calibration_type: "patent-7-bearing"` and include a non-empty `ecp_symbolic_field` and `ecp_contradiction_pairs` in their YAML frontmatter.
4. **Structural skills are explicitly exempt.** Skills like `python`, `regex-wizard`, `sql-query-pro`, etc. do not participate in paradox induction and must NOT have calibration fields.
5. **Named pairs are embedded; emoji tokens are stored.** The semantic matcher appends `ecp_contradiction_pairs` text to the embedding blob. The emoji field (`ecp_symbolic_field`) is preserved in metadata for compliance and Sovereign enforcement but does not enter the blob — raw emoji codepoints are noise to text embedding models.
6. **Contradiction pairs must use inline `[...]` format** in YAML frontmatter — the `_parse_frontmatter()` parser does not support multi-line YAML lists.

### Calibration Skills

| Skill                         | Symbolic Domain                           |
| ----------------------------- | ----------------------------------------- |
| SovereignCalibration          | Root authority (business-art-sovereignty) |
| paradox-processing            | Duality, tension, transformation          |
| emotional-symbolic-modulation | Emotion, resonance, identity expansion    |
| stress-navigation             | Pressure, resilience, stability           |
| ethics-value-integration      | Justice, truth, boundaries                |
| memory-management             | Memory, time, continuity, forgetting      |

### Emoji Inheritance Rules

- **SovereignCalibration defines the canonical calibration substrate.** Its emoji field and contradiction pairs are the root reference.
- **Each calibration skill defines its own domain-specific emoji field** that reflects its symbolic domain (e.g., stress uses ⚡🌪️🔥, ethics uses ⚖️📜🔍). Skills do not copy Sovereign's emojis — they extend the symbolic layer into their domain.
- **Structural skills never inherit or define emoji fields.** They are exempt from the calibration layer entirely.

### Deterministic Emoji Ordering

`_normalize_symbolic_field()` in `semantic_matcher.py` guarantees reproducible emoji representations:

1. Strip Unicode variation selectors (U+FE0E, U+FE0F)
2. Sort remaining characters by Unicode codepoint
3. Return as space-separated tokens

This ensures the same emoji field always produces the same normalized output regardless of input order.

### Weighting Rule

> _Embed full contradiction pairs text (`ecp_contradiction_pairs`) into the skill embedding blob. Store the emoji field (`ecp_symbolic_field`) in metadata only. Do not embed the full emoji field — raw emoji codepoints are noise to text embedding models._

### Enforcement

- `semantic_matcher.py` validates that every `patent-7-bearing` skill has an `ecp_symbolic_field` at load time
- `test_skills.py` includes `test_patent7_compliance` which asserts type correctness of all ECP fields and detects YAML drift
- `test_sovereign_verification` asserts correct routing for all 5 calibration skills and checks for emoji leakage in text blobs
- Removing emoji fields from a calibration skill will break tests

## Safety

- Only skills in `manifest.json` (active) are eligible for matching
- Quarantined skills are never loaded or matched
- The gateway does NOT modify calibration, identity, or routing logic
- No tools are executed autonomously
- All skill injections are logged
