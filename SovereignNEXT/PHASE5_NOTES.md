# Phase 5 Implementation Notes

## Paradox-Hold: `nudge_entropy_down` uses duplication, not removal

**Operator:** `paradox_hold_operator.py` → `_reduce_entropy_by_duplication()`

The Phase 5 plan specified reducing entropy by "removing redundant duplicates" from the emoji vector. During implementation, this was found to be mathematically incorrect for near-uniform distributions.

**The problem:** Normalized Shannon entropy measures how uniform a distribution is. Removing a duplicate from a high-entropy (near-uniform) sequence makes the remaining distribution *more* uniform, which *increases* entropy — the opposite of the intended effect.

**The fix:** `nudge_entropy_down` appends copies of the most common non-pole emoji already present in the sequence. This skews the frequency distribution away from uniformity, mechanically lowering normalized Shannon entropy without introducing any new emoji types.

**Why this matters:**
- Paradox-Hold must never introduce collapse-aligned (stable) symbols — that would violate Phase 5 constraints.
- Paradox-Hold must never shorten the vector below minimum length — removal risks this.
- Duplication is monotonically entropy-reducing for any non-degenerate sequence, making the operator's behavior predictable.

**Verified:** Entropy 0.9625 → 0.875 after appending 2 duplicates of the most common non-pole emoji (seed=42).

This is a Phase 5 implementation clarification. No Phase 4 behavior is affected.
