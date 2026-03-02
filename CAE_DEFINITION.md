# Complexity Amplification Effect — Formal Definition

**Context:** Experiment FE-3D-PF-SCALING-2026-02-23 | Patent ref: US 63/898,911

---

## Definition

The **Complexity Amplification Effect (CAE)** is the empirically observed property whereby an elimination-based search algorithm with paradox retention (Forgetting Engine) gains increasing relative advantage over standard Monte Carlo optimization as combinatorial problem complexity grows, under equal computational budgets and locked parameters. In a controlled experiment comprising 28,000 main-phase trials (2,000 per algorithm per length) on 3D HP lattice protein folding across seven sequence lengths (L = 20, 25, 30, 35, 40, 45, 50), the success-rate gap Δ(L) = FE% − MC% was fitted by ordinary least squares as Δ(L) = −2.20 + 0.1046·L, with a positive slope confirmed by one-sided permutation test (b = 0.1046, p = 0.007, 10,000 permutations, R² = 0.531). At every length tested, the Forgetting Engine produced significantly lower energy conformations than Monte Carlo (Cohen's d = −3.36 to −3.86, Mann-Whitney p < 10⁻⁶ at all lengths), with the gap widening from Δ = 0.6 percentage points at L = 20 to Δ = 4.9 percentage points at L = 50. All algorithm parameters were locked across lengths, no per-length tuning was applied, and success thresholds E*(L) were pre-declared in a separate pilot phase (2,800 trials) before main data collection.

---

## Supporting Data

| L  | MC%  | FE%  | Δ(L) pp | Cohen's d | FE mean energy | MC mean energy |
|----|------|------|---------|-----------|----------------|----------------|
| 20 | 0.0  | 0.6  | +0.6    | −3.86     | −8.55          | −3.73          |
| 25 | 0.0  | 0.6  | +0.6    | −3.76     | −8.72          | −3.55          |
| 30 | 0.0  | 0.7  | +0.7    | −3.51     | −8.23          | −3.63          |
| 35 | 0.0  | 1.2  | +1.2    | −3.60     | −9.80          | −4.64          |
| 40 | 0.0  | 0.8  | +0.8    | −3.50     | −9.69          | −4.61          |
| 45 | 0.0  | 1.4  | +1.4    | −3.85     | −19.42         | −10.31         |
| 50 | 0.1  | 5.0  | +4.9    | −3.36     | −23.77         | −14.00         |

**Trend:** Δ(L) = −2.20 + 0.1046·L (R² = 0.531, p_perm = 0.007)

---

*Source: `fe_pf_replication_2026/manuscript_outputs/stats_summary.json`*
