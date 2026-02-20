# 2026-02-19 - Airline: served-direct vs gpt-oss-120b significance note

- Compared runs:
  - `data/simulations/served_direct_agent_user_120b_airline_full_3trials_20260219.json`
  - `data/simulations/gpt_oss_120b_agent_user_120b_airline_full_3trials_20260219.json`
- Common setup: `airline`, `50` tasks, `3` trials per task.

## Headline metrics

- served-direct (`agent=served-direct`, `user=gpt-oss-120b`):
  - `pass^1=0.4600`, `pass^2=0.3600`, `pass^3=0.3200`
  - `pass@1=0.4600`, `pass@2=0.5600`, `pass@3=0.6200`
- gpt-oss-120b (`agent=gpt-oss-120b`, `user=gpt-oss-120b`):
  - `pass^1=0.4267`, `pass^2=0.3200`, `pass^3=0.2600`
  - `pass@1=0.4267`, `pass@2=0.5333`, `pass@3=0.5800`

## Statistical check (paired, task-level)

- Test used: two-sided paired permutation test (sign-flip) over 50 shared tasks.
- CI used: bootstrap 95% CI on mean paired difference (served-direct minus gpt-oss-120b).

- `pass@1`: diff `+0.0333`, `p=0.538`, 95% CI `[-0.0467, 0.1200]`
- `pass@2`: diff `+0.0267`, `p=0.690`, 95% CI `[-0.0667, 0.1267]`
- `pass@3`: diff `+0.0400`, `p=0.753`, 95% CI `[-0.0800, 0.1600]`

Conclusion: no statistically significant difference at typical thresholds (all p-values > 0.05; CIs include 0).

## Update: served-adapter prod run (latest)

- New run:
  - `data/simulations/served_adapter_agent_user_120b_airline_full_3trials_20260219_prod_mc50_99262e9f3c35e9ba77804451bddd8746f3fd2541.json`
- Common setup retained: `airline`, `50` tasks, `3` trials per task.

- served-adapter (`agent=served-adapter`, `user=gpt-oss-120b`):
  - `pass^1=0.4200`, `pass^2=0.3200`, `pass^3=0.2800`
  - `pass@1=0.4200`, `pass@2=0.5200`, `pass@3=0.5800`

### Delta vs served-direct baseline

- `pass^1`: `-0.0400`
- `pass^2`: `-0.0400`
- `pass^3`: `-0.0400`
- `pass@1`: `-0.0400`
- `pass@2`: `-0.0400`
- `pass@3`: `-0.0400`

### Delta vs gpt-oss-120b baseline

- `pass^1`: `-0.0067`
- `pass^2`: `+0.0000`
- `pass^3`: `+0.0200`
- `pass@1`: `-0.0067`
- `pass@2`: `-0.0133`
- `pass@3`: `+0.0000`
