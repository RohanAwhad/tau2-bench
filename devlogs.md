# Dev Logs

## 2026-02-19
- Metrics terminology: use `pass^k` (a.k.a. `pass_hat_k`), not `pass@k`.
- Source of truth: `src/tau2/metrics/agent_metrics.py` (`pass_hat_k = C(success_count, k) / C(num_trials, k)`).
- Reporting convention for runs: `pass^1`, `pass^2`, `pass^3`.
- Added full LiteLLM completion metadata capture to assistant `raw_data` in `src/tau2/utils/llm_utils.py` under `raw_data.completion_metadata`.
- Verified `adapter_critic.intermediate` is now persisted from `served-adapter` responses via smoke run `served_adapter_agent_user_120b_smoke_1task_metadata_20260219`.
- Added `scripts/analyze_adapter_usefulness.py` to score major API failures vs adapter repair outcomes per trace via LLM judge.
- Default judge model set to Vertex Anthropic `vertex_ai/claude-opus-4-6@default`; smoke run passed with `--vertex-location us-east5`.
- Renamed latest served-adapter prod simulation to include commit hash: `served_adapter_agent_user_120b_airline_full_3trials_20260219_prod_mc50_99262e9f3c35e9ba77804451bddd8746f3fd2541.json`.
- Added async concurrency to analyzer using `asyncio.Semaphore` + `litellm.acompletion` with CLI arg `--max-concurrency`.
- Added `tqdm` progress bar for analyzer runs (`Analyzing traces`) while keeping async concurrency.
- Updated `run_tasks()` failure handling in `src/tau2/run.py` to continue batch execution on task-trial exceptions.
- Failed task-trials are now persisted as `SimulationRun` with `termination_reason=agent_error`, `reward=0.0`, and error taxonomy in `reward_info.info` (`error_type`, `retryable`, `error_class`, `error_message`).
- Added regression test `test_run_tasks_continues_after_task_failure` in `tests/test_run.py`.
