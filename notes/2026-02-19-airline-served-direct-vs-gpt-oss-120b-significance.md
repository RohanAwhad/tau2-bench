# 2026-02-19 - Airline: gpt-oss-120b variant significance note

- Compared runs:
  - `data/simulations/served_direct_agent_user_120b_airline_full_3trials_20260219.json`
  - `data/simulations/gpt_oss_120b_agent_user_120b_airline_full_3trials_20260219.json`
- Common setup: `airline`, `50` tasks, `3` trials per task.

## Headline metrics

- gpt-oss-120b (`agent=served-direct`, `user=gpt-oss-120b`):
  - `pass^1=0.4600`, `pass^2=0.3600`, `pass^3=0.3200`
  - `pass@1=0.4600`, `pass@2=0.5600`, `pass@3=0.6200`
- gpt-oss-120b (`agent=gpt-oss-120b`, `user=gpt-oss-120b`):
  - `pass^1=0.4267`, `pass^2=0.3200`, `pass^3=0.2600`
  - `pass@1=0.4267`, `pass@2=0.5333`, `pass@3=0.5800`

## Statistical check (paired, task-level)

- Test used: two-sided paired permutation test (sign-flip) over 50 shared tasks.
- CI used: bootstrap 95% CI on mean paired difference (`gpt-oss-120b` baseline minus `gpt-oss-120b`).

- `pass@1`: diff `+0.0333`, `p=0.538`, 95% CI `[-0.0467, 0.1200]`
- `pass@2`: diff `+0.0267`, `p=0.690`, 95% CI `[-0.0667, 0.1267]`
- `pass@3`: diff `+0.0400`, `p=0.753`, 95% CI `[-0.0800, 0.1600]`

Conclusion: no statistically significant difference at typical thresholds (all p-values > 0.05; CIs include 0).

## Update: adapter prod run (b4dbb65)

- Run file:
  - `data/simulations/served_adapter_agent_user_120b_airline_full_3trials_mc50_b4dbb65.json`
- Common setup retained: `airline`, `50` tasks, `3` trials per task.

- adapter (`agent=served-adapter`, `user=gpt-oss-120b`):
  - `pass^1=0.4133`, `pass^2=0.3133`, `pass^3=0.2800`
  - `pass@1=0.4133`, `pass@2=0.5133`, `pass@3=0.5800`

### Delta vs gpt-oss-120b baseline

- `pass^1`: `-0.0467`
- `pass^2`: `-0.0467`
- `pass^3`: `-0.0400`
- `pass@1`: `-0.0467`
- `pass@2`: `-0.0467`
- `pass@3`: `-0.0400`

### Delta vs gpt-oss-120b baseline

- `pass^1`: `-0.0133`
- `pass^2`: `-0.0067`
- `pass^3`: `+0.0200`
- `pass@1`: `-0.0133`
- `pass@2`: `-0.0200`
- `pass@3`: `+0.0000`

## Adapter usefulness analysis (b4dbb65)

- Analysis file: `notes/adapter_usefulness_full_mtall_mc10_b4dbb65.json`
- Judge model: `vertex_ai/claude-opus-4-6@default` (thinking budget 10K tokens)
- Traces analyzed: `150`

- Major API failures identified: `436`
- Adapter attempted fix: `258` (59.2%)
- Adapter not attempted: `178` (40.8%)

- Outcomes when adapter attempted:
  - fixed: `95` (36.8%)
  - partially_fixed: `48` (18.6%)
  - unchanged: `65` (25.2%)
  - worse: `77` (29.8%)

- Root cause attribution:
  - api: `288` (66.1%)
  - mixed: `78` (17.9%)
  - adapter: `67` (15.4%)
  - unknown: `3` (0.7%)

## Update: intervention model swap (v1 gpt-oss-20b vs v3 glm-4.7-flash)

- Context:
  - API model remains `gpt-oss-120b`.
  - v1 intervention model: `gpt-oss-20b`.
  - v3 intervention model: `glm-4.7-flash`.
  - Note: run configs differ (`mc10` in v1 vs `mc6` in v3), so treat as directional comparison.

### Run-level metrics

- gpt-oss-120b baseline:
  - `pass^1=0.4200`, `pass^2=0.3400`, `pass^3=0.3044`
  - `pass@1=0.4200`, `pass@2=0.5000`, `pass@3=0.5444`

- adapter v1 (gpt-oss-20b):
  - `pass^1=0.4400`, `pass^2=0.3600`, `pass^3=0.3200`
  - `pass@1=0.4400`, `pass@2=0.5200`, `pass@3=0.5600`

- adapter v3 (glm-4.7-flash):
  - `pass^1=0.4933`, `pass^2=0.4178`, `pass^3=0.3793`
  - `pass@1=0.4933`, `pass@2=0.5689`, `pass@3=0.6059`

- critic v1 (gpt-oss-20b):
  - `pass^1=0.3933`, `pass^2=0.3222`, `pass^3=0.2926`
  - `pass@1=0.3933`, `pass@2=0.4644`, `pass@3=0.5059`

- critic v3 (glm-4.7-flash):
  - `pass^1=0.5267`, `pass^2=0.4244`, `pass^3=0.3696`
  - `pass@1=0.5267`, `pass@2=0.6289`, `pass@3=0.6763`

### Usefulness analysis deltas (directional)

- Adapter usefulness:
  - v1: `major_failures=519`, `fixed=59`, `partially_fixed=27`, `worse=272`
  - v3: `major_failures=327`, `fixed=80`, `partially_fixed=22`, `worse=51`
  - Direction: v3 shows fewer judged major failures and much lower `worse` count.

- Critic usefulness:
  - v1: `major_failures=377`, `correct=39`, `incorrect=205`, `useless=33`
  - v3: `major_failures=226`, `correct=46`, `incorrect=60`, `useless=14`
  - Direction: v3 has materially better correctness/incorrectness mix.
