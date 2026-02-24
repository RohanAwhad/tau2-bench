# Node09 Benchmark Comparison (Temp=1)

Generated on `2026-02-24` from node09 run artifacts (`50 tasks x 3 trials` each).

Interactive chart: `NODE09_RESULTS_20260224_plot.html`

## Metrics

| Variant | Avg reward | pass^1 | pass^2 | pass^3 | pass@1 | pass@2 | pass@3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v1 served-direct temp1 | 0.4200 | 0.4200 | 0.3000 | 0.2600 | 0.4200 | 0.5400 | 0.6200 |
| v9 served-direct temp1 | 0.3800 | 0.3800 | 0.3600 | 0.3400 | 0.3800 | 0.4000 | 0.4000 |
| v5 served-adapter | 0.4533 | 0.4533 | 0.3400 | 0.2800 | 0.4533 | 0.5667 | 0.6200 |
| v5 served-critic | 0.3800 | 0.3800 | 0.2733 | 0.2200 | 0.3800 | 0.4867 | 0.5400 |
| v6 served-critic | 0.3667 | 0.3667 | 0.2933 | 0.2600 | 0.3667 | 0.4400 | 0.4800 |
| v3 served-adapter | 0.4933 | 0.4933 | 0.3800 | 0.3200 | 0.4933 | 0.6067 | 0.6600 |
| v3 served-critic | 0.5267 | 0.5267 | 0.3733 | 0.2800 | 0.5267 | 0.6800 | 0.7400 |
| v4 served-critic | 0.5133 | 0.5133 | 0.3733 | 0.2800 | 0.5133 | 0.6533 | 0.7000 |

## Notes

- `v3`, `v4`, `v5`, and `v6` runs all use `temperature=1` for both agent and user.
- `v9` in this table is the rerun with `temperature=1` (`served_direct_prod_3x50_mc20_temp1_v9_39379bb`).
- pass^k and pass@k are computed task-wise from 3 trials and averaged over 50 tasks.
