# Adapter/Critic Improvement Metrics

This doc defines a metric set to measure whether adapter/critic variants improve hard cases without harming easy cases.

## Setup and notation

- Trials per task: `T = 3`
- Binary reward per trial: `reward(i, t, m) in {0, 1}`
  - `i`: task id
  - `t`: trial index in `{0, 1, 2}`
  - `m`: model/run key
- Task success count for model `m`:
  - `s_i(m) = sum_{t=0..2} reward(i, t, m)` (so `s_i(m) in {0,1,2,3}`)
- Baseline is served-direct:
  - `b_i = s_i(served_direct)`

## Primary per-task metric

- Per-task win rate:
  - `win_rate_i(m) = s_i(m) / 3`
- Per-task delta vs baseline:
  - `delta_i(m) = (s_i(m) - b_i) / 3`

Aggregate reporting:

- `mean_win_rate(m) = mean_i win_rate_i(m)`
- `mean_delta(m) = mean_i delta_i(m)`
- `%tasks_improved = mean_i[delta_i(m) > 0]`
- `%tasks_worsened = mean_i[delta_i(m) < 0]`

## Hard/easy anchor sets (key diagnostics)

- Hard tasks (baseline always wrong):
  - `H = { i | b_i = 0 }`
- Easy tasks (baseline always right):
  - `E = { i | b_i = 3 }`

Rescue metrics on hard set:

- `hard_rescue_rate(m) = |{i in H : s_i(m) > 0}| / |H|`
- `hard_full_rescue_rate(m) = |{i in H : s_i(m) = 3}| / |H|`

Degradation metrics on easy set:

- `easy_regress_rate(m) = |{i in E : s_i(m) < 3}| / |E|`
- `easy_collapse_rate(m) = |{i in E : s_i(m) = 0}| / |E|`

These four metrics are the cleanest signal for "fix hard, do not break easy".

## Trial-level paired flip metrics

Compute over all paired `(task, trial)` against baseline:

- Rescue flips: `R = count(reward_baseline = 0 and reward_model = 1)`
- Regression flips: `G = count(reward_baseline = 1 and reward_model = 0)`
- Baseline fails: `F = count(reward_baseline = 0)`
- Baseline passes: `P = count(reward_baseline = 1)`
- Total pairs: `N = F + P`

Directional rates:

- `rescue_rate_trial = R / F`
- `harm_rate_trial = G / P`
- `net_flip = (R - G) / N`

Optional safety-weighted scalar:

- `safe_gain = rescue_rate_trial - 2 * harm_rate_trial`

## Significance check (McNemar)

Use McNemar on paired binary outcomes from baseline vs candidate model.

Current policy:

- McNemar is computed on `trial == 0` only (one paired outcome per task, `N = 50`).
- Rationale: avoids within-task correlation from using 3 trials from the same task in the same test.
- Point metrics (win-rate, rescue/regress rates) can still use all 3 trials.

2x2 table:

- `a`: both correct
- `b`: baseline correct, model wrong (regressions)
- `c`: baseline wrong, model correct (rescues)
- `d`: both wrong

Only `b` and `c` matter for directional change.

- Null: `b` and `c` are equally likely.
- If `c >> b` with low p-value, improvement is directional and statistically supported.

## Future inference upgrades

Potential next steps to better use all 3 trials while respecting within-task dependence:

- Task-cluster permutation test on `D_i = c_i - b_i` per task (permute labels at task level).
- Task-block bootstrap confidence intervals (resample tasks, keep all trials inside each task).
- Sensitivity checks with task-level binarizations (e.g., any-success, all-success).
- Cluster-robust modeling (e.g., GEE logistic with `cluster=task`) as a confirmatory analysis.

## Recommended dashboard/report block

Per model include:

- `mean_win_rate`, `mean_delta`
- `hard_rescue_rate`, `hard_full_rescue_rate`
- `easy_regress_rate`, `easy_collapse_rate`
- `rescue_rate_trial`, `harm_rate_trial`, `net_flip`
- `mcnemar_p_value_trial0`

And list example task ids for:

- Hard tasks rescued
- Hard tasks fully rescued
- Easy tasks regressed
- Easy tasks collapsed

## Script usage

Use `scripts/compute_comparison_metrics.py`.

Example:

```bash
python scripts/compute_comparison_metrics.py \
  --baseline /path/to/served_direct.json \
  --candidate served_adapter=/path/to/served_adapter.json \
  --candidate served_critic=/path/to/served_critic.json \
  --mcnemar-trial 0 \
  --out comparison_metrics.json
```

Notes:

- `--candidate` accepts either `label=path` or just `path`.
- McNemar is reported under `mcnemar_trial` and uses `trial == 0` by default.
