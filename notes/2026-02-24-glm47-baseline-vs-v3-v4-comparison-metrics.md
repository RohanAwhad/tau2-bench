# 2026-02-24 - Comparison metrics: glm-4.7-flash baseline vs adapter/critic v3/v4

Baseline:
- `glm_4.7_flash_direct`: `experiments/node05_simulation_jsons_all_20260222/glm47flash_baseline_prod_3x50_mc20_temp1_node05_container_hostnet.json`

Compared runs:
- `served_adapter_v3`: `experiments/node09_benchmark_jsons_20260222/SERVER_9daf98ee4cee4653da40421def21f5a7260d41ef_BENCH_58dd82da0df690a95a1512a1cce96b71ac38b396/20260222_054158_prod_01/tau_outputs/data/simulations/served_adapter_prod_3x50_mc6_temp1_v3_glm_flash.json`
- `served_critic_v3`: `experiments/node09_benchmark_jsons_20260222/SERVER_9daf98ee4cee4653da40421def21f5a7260d41ef_BENCH_58dd82da0df690a95a1512a1cce96b71ac38b396/20260222_054158_prod_02/tau_outputs/data/simulations/served_critic_prod_3x50_mc6_temp1_v3_glm_flash.json`
- `served_critic_v4`: `experiments/node09_benchmark_jsons_20260222/SERVER_9daf98ee4cee4653da40421def21f5a7260d41ef_BENCH_58dd82da0df690a95a1512a1cce96b71ac38b396/20260222_054158_prod/tau_outputs/data/simulations/served_critic_prod_3x50_mc6_temp1_v4_glm_flash.json`

McNemar policy:
- `trial == 0` only.

## Summary metrics

| model | mean_win_rate | mean_delta | pct_tasks_improved | pct_tasks_worsened | hard_rescue_rate | hard_full_rescue_rate | easy_regress_rate | easy_collapse_rate | rescue_rate_trial | harm_rate_trial | net_flip | safe_gain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| served_adapter_v3 | 0.4933 | -0.0133 | 0.2800 | 0.2200 | 0.3125 | 0.0625 | 0.3529 | 0.0588 | 0.2432 | 0.2632 | -0.0133 | -0.2831 |
| served_critic_v3 | 0.5267 | +0.0200 | 0.3000 | 0.2600 | 0.4375 | 0.0000 | 0.4706 | 0.0588 | 0.3243 | 0.2763 | +0.0200 | -0.2283 |
| served_critic_v4 | 0.5133 | +0.0067 | 0.2600 | 0.2200 | 0.2500 | 0.0000 | 0.4118 | 0.0000 | 0.2703 | 0.2500 | +0.0067 | -0.2297 |

## McNemar (trial 0)

| model | a | b | c | d | p_value |
|---|---:|---:|---:|---:|---:|
| served_adapter_v3 | 18 | 8 | 6 | 18 | 0.790527343750 |
| served_critic_v3 | 20 | 6 | 9 | 15 | 0.607238769531 |
| served_critic_v4 | 21 | 5 | 6 | 18 | 1.000000000000 |

Interpretation reminder:
- `b`: baseline correct, candidate wrong (regressions).
- `c`: baseline wrong, candidate correct (rescues).

## Hard-set rescued task IDs (`b_i = 0` in baseline)

- served_adapter_v3: `12,15,24,29,30`
- served_critic_v3: `2,9,12,15,24,29,30`
- served_critic_v4: `15,24,29,30`

## Easy-set regressed task IDs (`b_i = 3` in baseline)

- served_adapter_v3: `3,5,22,34,39,48`
- served_critic_v3: `3,5,11,22,34,39,43,49`
- served_critic_v4: `3,5,22,34,39,43,48`

## Quick read

- Relative to the stronger `glm-4.7-flash` baseline, gains are much smaller and no trial-0 McNemar comparison is significant.
