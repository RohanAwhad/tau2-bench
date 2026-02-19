# Dev Logs

## 2026-02-19
- Metrics terminology: use `pass^k` (a.k.a. `pass_hat_k`), not `pass@k`.
- Source of truth: `src/tau2/metrics/agent_metrics.py` (`pass_hat_k = C(success_count, k) / C(num_trials, k)`).
- Reporting convention for runs: `pass^1`, `pass^2`, `pass^3`.
- Added full LiteLLM completion metadata capture to assistant `raw_data` in `src/tau2/utils/llm_utils.py` under `raw_data.completion_metadata`.
- Verified `adapter_critic.intermediate` is now persisted from `served-adapter` responses via smoke run `served_adapter_agent_user_120b_smoke_1task_metadata_20260219`.
