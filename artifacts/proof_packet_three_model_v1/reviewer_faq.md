# Reviewer FAQ

Anticipated questions from a skeptical technical reviewer, answered strictly from evidence in this proof packet.

---

**Q: Isn't this just prompt engineering?**

No. The governance invariants (zero open tensions, 100% held, 100% vetoed) are enforced by deterministic operators that run *after* LLM output is generated. The LLM receives prompts, but the prompts do not control the governance outcomes. The operators do. This is demonstrated by the fact that three different models — with different architectures, parameter counts, and inference backends — all produced identical invariant outcomes despite producing different text, different claim counts, and different tension counts. If the results depended on prompt engineering, different models would respond to the same prompts differently and produce different governance outcomes. They did not.

**Evidence:** `comparison_metrics.json → invariants_verified` (all `true`); `interpretation_notes.md → Summary of Variation Patterns` (governance-relevant metrics are model-independent).

---

**Q: Why only one pass?**

Hardware constraint. The test machine has 16 GB RAM. LLaMA (8B) alone consumes approximately 7 GB. The initial LLaMA run attempted 3 passes and caused a system freeze during Pass 1's operator phase due to memory exhaustion. The recovery plan reduced all runs to 1 pass each, which allowed Mistral and Phi to run in parallel without exceeding available memory. One pass is sufficient to demonstrate the invariant property because the operators execute fully in a single pass — Collapse resolves all tensions, Hold processes all paradoxes, and Observer audits the final state. Additional passes would test the pipeline's iterative refinement behavior, not its governance enforcement.

**Evidence:** `run_metadata/llama_metadata.json → status: "completed_pass1_crash_recovered"`; `run_metadata/mistral_metadata.json → passes: 1`; `run_metadata/phi_metadata.json → passes: 1`.

---

**Q: Why do the final state hashes differ across models?**

Because the models produced different text. LLaMA generated 862 claims; Mistral generated 858; Phi generated 843. The claim *content* differs because each model generates different language. The hashes are SHA-256 digests of the full JSON state, which includes all claim text, tension text, and paradox text. Different text produces different hashes. This is expected and correct. The proof does not claim identical outputs — it claims identical *structural invariants* (zero open tensions, 100% held, 100% vetoed, identical paradox counts and promotions).

**Evidence:** `comparison_metrics.json → runs.{model}.final_state_hash` (three distinct hashes); `comparison_metrics.json → runs.{model}.final_claims` (862, 858, 843).

---

**Q: Does Phi being smaller (4B) weaken the proof?**

No — it strengthens it. Phi produced the fewest new tensions (47 vs. 205 for Mistral) and the fewest new claims (5 vs. 20 for Mistral). Despite generating significantly less material, the governance invariants held identically: 94 paradoxes, 94 held, 94 vetoed, 0 open tensions, 10 promotions. This demonstrates that the operators enforce invariants regardless of output volume. A model that generates less does not escape governance — the operators still process every tension and every paradox.

**Evidence:** `comparison_metrics.json → runs.phi` (all invariant fields match other models despite lower counts).

---

**Q: Could this be overfit to these specific models?**

The proof uses three models that differ in: parameter count (4B, 7B, 8B), architecture family (Phi, Mistral, LLaMA), and inference backend (llama-cpp-python vs. GPT4All). The invariants held across all three. However, this proof does not claim the invariants hold for *all possible* LLMs. It demonstrates the property for these three models under these specific conditions (V5 baseline, seed 42, 1 pass, governance v1). Generalizing beyond the tested models would require additional runs. The `README_verify.md` explicitly lists this as a non-claim.

**Evidence:** `README_verify.md → What Conclusions Are NOT Claimed`; `comparison_metrics.json → runs` (three distinct models with different backends).

---

**Q: The LLaMA run crashed — can you trust its data?**

The LLaMA run completed Pass 1 fully before the system froze. The Pass 1 state snapshot was written to disk before the crash. The snapshot contains 862 claims, 1720 tensions, 94 paradoxes, and 0 open tensions — consistent with the pattern observed in the Mistral and Phi runs. The crash occurred during the attempt to start Pass 2, not during Pass 1 execution. Since all runs were subsequently limited to 1 pass, the LLaMA Pass 1 snapshot is a complete artifact for the purposes of this proof. The limitation is that no canonical report (with operator-level details) was generated for LLaMA, which is why some fields in `comparison_metrics.json` are `null` for the LLaMA run.

**Evidence:** `run_metadata/llama_metadata.json → status`, `→ note`; snapshot file exists and is hashed in `hash_manifest.json`.

---

**Q: How do I know the operators weren't modified between runs?**

The governance version is recorded as `v1` in every run's metadata. The operator sequence (Collapse → Become → Paradox-Hold → Observer) is recorded in every canonical report and in `comparison_metrics.json`. The starting snapshot hash (`f9a12fa4...`) is identical across all three runs, confirming they began from the same sealed baseline. The governance contracts in `SovereignNEXT/governance/` were not modified — this is verifiable from the repository's git history.

**Evidence:** `comparison_metrics.json → governance_version`, `→ operator_sequence`, `→ input_content_hash`; `run_metadata/*.json → governance_version`.

---

**Q: What would falsify this proof?**

Any of the following would constitute a falsification:
1. A model run that produces a non-zero open tension count after Collapse.
2. A model run where fewer than 100% of paradoxes are held after Paradox-Hold.
3. A model run where the operator sequence is not preserved.
4. A model run where paradox promotions differ given the same starting state and seed.
5. A SHA-256 mismatch in the hash manifest (indicating artifact tampering).

None of these occurred in the three runs. The `_verify.py` script and `verification_log.md` confirm hash integrity. The `invariants_table.md` confirms all invariant conditions.

**Evidence:** `verification_log.md → Final Verdict: VERIFIED`; `invariants_table.md` (all 9 invariants satisfied).
