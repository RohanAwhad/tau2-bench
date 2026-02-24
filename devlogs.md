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

## 2026-02-24
- Added comparison-metrics module at `src/tau2/metrics/comparison_metrics.py` for baseline-vs-candidate analysis on aligned `(task_id, trial)` pairs.
- Implemented new metric set: per-task win-rate deltas, hard/easy anchor rescue/regress rates, trial-level flip counts/rates, and `safe_gain`.
- Added exact McNemar test support with current policy `trial == 0` only (`mcnemar_trial` payload in outputs).
- Added executable script `scripts/compute_comparison_metrics.py` to compute and export JSON reports for one baseline and multiple candidates.
- Added tests in `tests/test_comparison_metrics.py` and followed red-green cycle (initial missing-module failure -> implementation -> passing tests).
- Updated docs at `docs/adapter_critic_improvement_metrics.md` with finalized metric definitions, McNemar trial-0 policy, future inference upgrades, and CLI usage example.
- Added `notes/qwen_results_report.html` with embedded pass^k/pass@k PNGs and qwen-focused intervention metric tables.
- Updated `notes/qwen_results_report.html` to render pass charts with Chart.js (interactive hover + legend toggles) and replaced wide intervention table with compact `% improved`/`% worsened` summary plus side-by-side improved/worsened task examples per comparison.
- Refined `notes/qwen_results_report.html` again: switched intervention summary to absolute task counts (`improved_questions`, `worsened_questions`, `hard_rescue_number`, `easy_harm_number`) and removed McNemar mentions for a simpler reader-facing view.
- Rebased the intervention section in `notes/qwen_results_report.html` to use `served_direct_v1_gpt-oss-120b` as baseline for counts/examples in the compact table and comparison cards.
- Renamed report-facing run labels in `notes/qwen_results_report.html` to clearer names (`gpt-oss-120b (baseline)`, `qwen3-30b-a3b (baseline)`, `adapter-mode`, `critic-mode`, `critic-mode [UCB MAST style]`) including Chart.js legend labels.
