# Experiment Progress — COMPLETE

## Phase A (Pilot) — COMPLETE

All 7 thresholds locked:

| L   | E\*(L) | Time |
| --- | ------ | ---- |
| 20  | -12    | 97s  |
| 25  | -13    | 110s |
| 30  | -12    | 119s |
| 35  | -14    | 169s |
| 40  | -14    | 168s |
| 45  | -24    | 443s |
| 50  | -28    | 604s |

## Phase B (Main) — COMPLETE

| L   | Status   | Trials | Time  |
| --- | -------- | ------ | ----- |
| 20  | COMPLETE | 4000   | 947s  |
| 25  | COMPLETE | 4000   | 1080s |
| 30  | COMPLETE | 4000   | 1193s |
| 35  | COMPLETE | 4000   | 1703s |
| 40  | COMPLETE | 4000   | 2325s |
| 45  | COMPLETE | 4000   | 5558s |
| 50  | COMPLETE | 4000   | 6615s |

## Analysis — COMPLETE

### Manuscript Table

```
   L |     MC% |     FE% |    Δ(L) |    R(L) |       d |          p
----------------------------------------------------------------------
  20 |    0.0% |    0.6% |    0.6% |     inf |  -3.860 |   0.000000
  25 |    0.0% |    0.6% |    0.6% |     inf |  -3.764 |   0.000000
  30 |    0.0% |    0.7% |    0.7% |     inf |  -3.506 |   0.000000
  35 |    0.0% |    1.2% |    1.2% |     inf |  -3.595 |   0.000000
  40 |    0.0% |    0.8% |    0.8% |     inf |  -3.495 |   0.000000
  45 |    0.0% |    1.4% |    1.4% |     inf |  -3.854 |   0.000000
  50 |    0.1% |    5.0% |    4.9% |    50.0 |  -3.356 |   0.000000
```

### Trend Test

```
Δ(L) = -2.20 + 0.1046·L  (R²=0.531, p_perm=0.0070)
b > 0 is SIGNIFICANT (p_perm = 0.0070)
```

### Key Findings

- FE outperforms MC at every length (Cohen's d = -3.3 to -3.9, all p < 0.000001)
- MC success rate is essentially 0% across all lengths (thresholds are very strict)
- FE success rate increases with length, especially at L=50 (5.0%)
- The trend slope b = 0.1046 is statistically significant (p = 0.007)
- **The Complexity Amplification Effect is confirmed**: Δ(L) increases with L

## Outputs

- `manuscript_outputs/scaling_table.csv`
- `manuscript_outputs/scaling_plot.png`
- `manuscript_outputs/stats_summary.json`

## Total Trials

- Phase A: 2,800 pilot trials (7 lengths × 400)
- Phase B: 28,000 main trials (7 lengths × 4,000)
- Grand total: 30,800 trials
