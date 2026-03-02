# Metrics Definitions — Manuscript Block

## Per-Length Metrics

**Success Rate** (MC%, FE%):
Fraction of trials where final energy ≤ E*(L), where E*(L) is the pre-declared
threshold locked during Phase A (pilot). Reported as percentage with Wilson score
95% confidence intervals.

**Success Rate Gap** Δ(L):
```
Δ(L) = FE_success_rate(L) − MC_success_rate(L)
```
Primary metric. Positive values indicate FE advantage. Reported as percentage points.

**Relative Advantage Ratio** R(L):
```
R(L) = FE_success_rate(L) / MC_success_rate(L)
```
Supplementary metric. WARNING: If MC_success_rate → 0, R(L) → ∞. Always report
absolute rates alongside ratios.

**Cohen's d** (energy distributions):
```
d = (mean_FE_energy − mean_MC_energy) / pooled_SD
```
Pooled standard deviation: √[((n₁−1)s₁² + (n₂−1)s₂²) / (n₁+n₂−2)]
Interpretation: |d| < 0.2 negligible, 0.2–0.5 small, 0.5–0.8 medium, > 0.8 large.

**Mann-Whitney U test**:
Non-parametric test comparing MC and FE energy distributions.
Alternative hypothesis: MC energies are stochastically greater (worse) than FE energies.
Significance level: α = 0.001 (pre-committed).

## Trend Metrics

**Linear Trend**:
```
Δ(L) = a + b·L
```
Fitted via ordinary least squares across all 7 lengths.

**Slope Significance**:
One-sided permutation test (10,000 permutations) for b > 0.
If p < 0.05: "The success-rate gap Δ(L) increases significantly with sequence length L
under equal evaluation budgets."

## Pre-Committed Thresholds

| Parameter | Value | Justification |
|-----------|-------|---------------|
| MC max_steps | 10,000 | Matches validated study |
| FE pop_size | 50 | Matches validated study |
| FE forget_rate | 0.3 | Matches validated study |
| FE max_gen | 100 | Matches validated study |
| Trials per algorithm | 2,000 | Statistical power |
| Pilot trials | 200 | Threshold estimation |
| Significance α | 0.001 | Pre-committed |
| CI level | 95% | Wilson score |

## Claim Structure

**Strongest safe claim**:
"The success-rate gap Δ(L) increases with length L under equal evaluation budgets."

**Supporting evidence**:
- Table: L | MC% | FE% | Δ(L) | R(L) | d | p
- Plot: Δ(L) vs L with fitted trend line
- Slope b with permutation p-value

**What we are NOT claiming**:
- "FE is universally better" (we test one domain)
- "FE scales infinitely" (we test L=20–50)
- "MC is broken" (MC works, FE works better at scale)
