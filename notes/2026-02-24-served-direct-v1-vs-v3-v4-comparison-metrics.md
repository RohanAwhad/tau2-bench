# 2026-02-24 - Comparison metrics: served-direct v1 vs adapter/critic v3/v4

Baseline:
- `served_direct_v1`: `experiments/node09_benchmark_jsons_20260222/SERVER_31e8ea6f7b9be2bb101867819082b673b9a72f9f_BENCH_58dd82da0df690a95a1512a1cce96b71ac38b396/20260221_191706_prod/tau_outputs/data/simulations/served_direct_prod_3x50_mc1_temp1_default_tauref_ra_benchmarking.json`

Compared runs:
- `served_adapter_v3`: `experiments/node09_benchmark_jsons_20260222/SERVER_9daf98ee4cee4653da40421def21f5a7260d41ef_BENCH_58dd82da0df690a95a1512a1cce96b71ac38b396/20260222_054158_prod_01/tau_outputs/data/simulations/served_adapter_prod_3x50_mc6_temp1_v3_glm_flash.json`
- `served_critic_v3`: `experiments/node09_benchmark_jsons_20260222/SERVER_9daf98ee4cee4653da40421def21f5a7260d41ef_BENCH_58dd82da0df690a95a1512a1cce96b71ac38b396/20260222_054158_prod_02/tau_outputs/data/simulations/served_critic_prod_3x50_mc6_temp1_v3_glm_flash.json`
- `served_critic_v4`: `experiments/node09_benchmark_jsons_20260222/SERVER_9daf98ee4cee4653da40421def21f5a7260d41ef_BENCH_58dd82da0df690a95a1512a1cce96b71ac38b396/20260222_054158_prod/tau_outputs/data/simulations/served_critic_prod_3x50_mc6_temp1_v4_glm_flash.json`

McNemar policy:
- `trial == 0` only.

## Summary metrics

| model | mean_win_rate | mean_delta | pct_tasks_improved | pct_tasks_worsened | hard_rescue_rate | hard_full_rescue_rate | easy_regress_rate | easy_collapse_rate | rescue_rate_trial | harm_rate_trial | net_flip | safe_gain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| served_adapter_v3 | 0.4933 | +0.0733 | 0.3000 | 0.1600 | 0.3684 | 0.0000 | 0.2308 | 0.0000 | 0.2874 | 0.2222 | +0.0733 | -0.1571 |
| served_critic_v3 | 0.5267 | +0.1067 | 0.2800 | 0.1000 | 0.3684 | 0.0526 | 0.2308 | 0.0000 | 0.3333 | 0.2063 | +0.1067 | -0.0794 |
| served_critic_v4 | 0.5133 | +0.0933 | 0.3200 | 0.1200 | 0.3158 | 0.0000 | 0.3077 | 0.0000 | 0.3333 | 0.2381 | +0.0933 | -0.1429 |

## McNemar (trial 0)

| model | a | b | c | d | p_value |
|---|---:|---:|---:|---:|---:|
| served_adapter_v3 | 12 | 8 | 12 | 18 | 0.503444671631 |
| served_critic_v3 | 18 | 2 | 11 | 19 | 0.022460937500 |
| served_critic_v4 | 16 | 4 | 11 | 19 | 0.118469238281 |

Interpretation reminder:
- `b`: baseline correct, candidate wrong (regressions).
- `c`: baseline wrong, candidate correct (rescues).

## Hard-set rescued task IDs (`b_i = 0` in baseline)

- served_adapter_v3: `12,17,20,24,27,39,40`
- served_critic_v3: `2,10,12,18,20,24,40`
- served_critic_v4: `10,17,18,20,24,39`

## Easy-set regressed task IDs (`b_i = 3` in baseline)

- served_adapter_v3: `5,6,16`
- served_critic_v3: `5,16,43`
- served_critic_v4: `5,6,16,43`

## Quick read

- By this metric set, `served_critic_v3` is strongest overall: highest `mean_delta`, highest `net_flip`, best `safe_gain` (least negative), and the only run with trial-0 McNemar p-value below 0.05.
