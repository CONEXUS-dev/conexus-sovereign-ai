# CONEXUS SovereignNEXT — Architectural Specification (Frozen v1)

**Date:** 2026-03-03
**Authors:** Derek Angell + Pylo (architecture), Opie/Cascade (implementation)
**Status:** FROZEN — This is the non-negotiable frame for implementation.
**Patent:** US 63/898,911

---

## Origin

This architecture was designed in response to forensic analysis by Incognito Claude,
which identified **mode-sycophancy** in the original 6-mission proof run:

- Collapse always resolved contradictions using the same template (always picking pole_a)
- Become always produced the same proto-moments (20x repetition of meta-description)
- Only 2 unique breakthroughs across 6 missions
- Confidence scores measured structural completion, not cognitive depth
- The system was sycophantic to its own design imperatives, not to the user

The core diagnosis: **"prompted roles + rigid pipeline = structural sycophancy."**

SovereignNEXT replaces this with: **"algorithmic operators + flexible pipeline = genuine cognitive tension."**

---

## 1. System State (Center of Gravity)

Everything revolves around a shared, structured, inspectable internal state:

```
SystemState S = {
    Claims C,
    Tensions T,
    Paradoxes P,
    EmojiFields E,
    MemoryRefs M
}
```

- **Claims (C):** `{ id, text, confidence, source, tags, timestamp }`
- **Tensions (T):** `{ id, pole_a, pole_b, relation_type, status, metrics }`
- **Paradoxes (P):** Paradox objects with emoji vectors, metrics, history, links
- **EmojiFields (E):** Contradiction fields / mode-bias vectors
- **MemoryRefs (M):** Pointers + hashes into episodic/semantic memory

**Key principle:** LLM output = proposals. System state = structured object.
The LLM no longer _is_ the system — it _feeds_ the system.

---

## 2. Operators (Not Personas)

### Collapse(S) -> S'

- Scores tensions using 4-dimension rubric (evidence, consistency, goal_fit, memory_support)
- Commits when margin > 0.25, defers to ParadoxHold when margin < 0.10, defers open otherwise
- Mutates emoji vectors toward stability (entropy decreases, pole_balance shifts)
- Updates claims and tension statuses

### Become(S) -> S'

- Expands around tensions: implications, scenarios, edge cases, reframings
- Creates new claims with low-medium confidence
- Increases entropy, keeps pole_balance near 0.5
- Optionally creates new tensions from conflicting expansions

### ParadoxHold(S) -> S'

- Activates when entropy > 0.7 + pole_balance ~0.5 + agent_divergence high
- Creates or updates paradox objects with status `paradox_held`
- Stabilizes entropy (high but not increasing), reorganizes emoji vector
- Adds superposition emojis (♾️🔀🧬)

### Sovereign(S) -> (Output, S')

- Reads entire state: accepted claims, active paradoxes, open tensions
- Asks LLM to draft synthesis, constrained by: "do not erase paradox_held states"
- Post-processes draft against state to ensure fidelity
- Updates memory with hash chain

---

## 3. Emoji Vectors (Contradiction Substrate)

Each tension or paradox has an emoji vector:

```json
{
  "id": "ev_0017",
  "role": "paradox_field",
  "core": {
    "length": 12,
    "sequence": [
      "🧭",
      "🛡️",
      "🌫️",
      "🌀",
      "✨",
      "⚖️",
      "🎭",
      "🌪️",
      "🧩",
      "🧬",
      "🔀",
      "♾️"
    ],
    "poles": { "a": "🧭", "b": "🛡️" }
  },
  "metrics": {
    "entropy": 0.78,
    "pole_balance": 0.52,
    "chaos_index": 0.71,
    "stability_index": 0.29
  },
  "links": {
    "paradox_id": "paradox_17",
    "related_claims": ["claim_102", "claim_119"],
    "origin": "Become_expansion_M3",
    "last_updated": "2026-03-03T06:15:00Z"
  }
}
```

### Emoji Sets

- **CHAOS:** 🌪️ 🌀 🌫️ ⚡ 🔥 💥 🌊 ⚫ 🕳️
- **STABLE:** ⚖️ 🧱 🏛️ 🔒 🛡️ 📐 🧮 ⚓
- **SUPERPOSITION:** ♾️ 🔀 🧬 ☯️ 🪞 🎭

### Entropy Computation

Normalized Shannon entropy over emoji category distribution:

- 0.0 = all same emoji
- 1.0 = all unique
- Chaos/stability indices = fraction of emojis from curated sets

### Mutation Rules

| Operator    | Entropy                   | Pole Balance      | Chaos Index | Sequence Length |
| ----------- | ------------------------- | ----------------- | ----------- | --------------- |
| Collapse    | ↓                         | → 0 or 1          | ↓           | ↓               |
| Become      | ↑                         | → 0.5             | ↑           | ↑               |
| ParadoxHold | stable high               | ~0.5              | oscillates  | reorder         |
| Sovereign   | slight ↓                  | evidence-weighted | ↓           | simplify        |
| Memory      | decays unless reactivated | drifts            | decays      | stable          |

---

## 4. Paradox Objects (Computational Heart)

```json
{
    "id": "paradox_17",
    "poles": {
        "a": { "id": "autonomy", "emoji": "🧭" },
        "b": { "id": "control", "emoji": "🛡️" }
    },
    "status": "paradox_held",
    "emoji_vector": { "..." },
    "metrics": {
        "tension_strength": 0.84,
        "resolution_pressure": 0.31,
        "paradox_stability": 0.72,
        "agent_divergence": 0.66
    },
    "history": [
        { "event": "created", "operator": "Sovereign", "entropy": 0.62, "timestamp": "..." },
        { "event": "expanded", "operator": "Become", "entropy": 0.74, "timestamp": "..." },
        { "event": "paradox_held", "operator": "ParadoxHold", "entropy": 0.78, "timestamp": "..." }
    ],
    "links": {
        "claims": ["claim_102", "claim_119"],
        "missions": ["M3", "M4"],
        "memory_hash": "a8f3c9...",
        "related_paradoxes": ["paradox_12", "paradox_21"]
    }
}
```

### Status Values

- `open` — tension identified but not processed
- `collapsed_to_a` — Collapse committed to pole A
- `collapsed_to_b` — Collapse committed to pole B
- `paradox_held` — ParadoxHold is active
- `integrated` — Sovereign resolved at a higher level

### Lifecycle

1. **Creation** — Triggered by Collapse detecting contradiction, Become generating conflicts, or Sovereign identifying tension
2. **Expansion (Become)** — Increases entropy, chaos, pole balance symmetry
3. **Evaluation (Collapse)** — May collapse to A, collapse to B, defer, or trigger paradox-hold
4. **ParadoxHold** — Activated when entropy > 0.7, pole_balance ~0.5, agent_divergence high
5. **Integration (Sovereign)** — May resolve at higher level, maintain, or archive

---

## 5. Sycophancy-Resistant Loop (The Engine)

**Principle:** The next action is chosen by the state, not by the script.

### Pipeline (Non-Linear)

1. **Foundation:** Ingest task + context → initialize S
2. **Gravity_Well:** Detect tensions → populate T (and maybe P)
3. **Release_Forge:** Iteratively apply Collapse / Become / ParadoxHold until stopping conditions
4. **Seal:** Sovereign reads S and produces final answer + updated memory

### Routing Function (Heart of Sycophancy Resistance)

| Condition                            | Route to                   |
| ------------------------------------ | -------------------------- |
| High evidence + low entropy          | Collapse                   |
| High uncertainty + low evidence      | Become                     |
| High entropy + balanced poles        | ParadoxHold                |
| Low tension strength                 | Skip                       |
| Previously collapsed but unstable    | Reopen → Become            |
| Previously paradox-held but drifting | Re-stabilize → ParadoxHold |

### Entropy-Based Control

- Entropy < 0.4 → Collapse favored
- Entropy 0.4–0.7 → Become favored
- Entropy > 0.7 → ParadoxHold favored

### Stopping Conditions (3-Gate)

| Gate          | Default                                          |
| ------------- | ------------------------------------------------ |
| Iteration cap | 5 iterations                                     |
| Token budget  | 8,000 output tokens                              |
| Tension drain | No tension with strength > 0.3 and status = open |

---

## 6. Engineering Decisions (Locked v1)

### Decision 1: Claim Extraction

- LLM-as-parser with strict JSON schema + post-processing rules
- Dedup threshold: 0.9 cosine similarity
- **Hard cap: max 10 claims per extraction** (prevents pathological verbosity from inflating state)
- 1 extra LLM call per operator (~15-30s CPU)

### Decision 2: Tension Detection

- Embedding similarity band (0.3–0.7) for candidate pairs
- LLM-as-judge for confirmation (AGREEMENT/CONTRADICTION/TRADEOFF/POLARITY/UNRELATED)
- 5-15 judge calls per iteration

### Decision 3: Emoji Entropy

- Normalized Shannon entropy over emoji category distribution
- Chaos/Stable sets are hand-curated, tunable
- Zero compute cost (pure math)
- **INVARIANT: Emoji metrics are pure functions.** No operator may override entropy, chaos, or stability directly — only via mutation rules. This keeps the substrate honest.

### Decision 4: Stopping Conditions

- 3-gate system: 5 iterations, 8K tokens, no tensions > 0.3
- Paradox-held states do NOT count as unresolved for stopping
- **If iteration cap is hit, Sovereign must explicitly surface remaining open tensions** rather than silently integrating. Epistemic honesty is non-negotiable.

### Decision 5: Collapse Scoring

- 4-dimension rubric: evidence (0.3), consistency (0.25), goal_fit (0.25), memory_support (0.2)
- LLM fills scores in structured JSON
- Algorithm decides: margin > 0.25 = commit, < 0.10 = paradox-hold, else defer
- **Raw rubric scores are logged into paradox/tension history** for forensic auditability

---

## 7. Memory as Active Constraint

Memory stores Claims, Paradoxes, EmojiFields with hashes. It pushes back:

- Previously collapsed and failed → increase divergence_pressure for opposite pole
- Paradox stable across 3+ missions → bias toward ParadoxHold
- Pole repeatedly chosen → reduce its score to avoid drift

---

## 8. What This Architecture Achieves

- **Not** "LLM with fancy prompts" — operators transform structured state
- **Not** a rigid 9-gear script — tension-driven dynamic decision process
- **Not** mode-sycophancy — entropy-based routing the LLM cannot game
- **Not** fake paradox-holding — paradox is a computational object with behavioral consequences
- **Not** passive memory — memory is an active force that shapes operator behavior

---

_This spec is FROZEN. Implementation proceeds from here._
_Patent reference: US 63/898,911_
_Collapse-Become Unified Protocol v1.1 → SovereignNEXT_
