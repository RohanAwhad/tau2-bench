from __future__ import annotations

import math
from typing import Any

from tau2.data_model.simulation import Results
from tau2.metrics.agent_metrics import is_successful


TaskTrialSuccess = dict[str, dict[int, int]]


def _task_sort_key(task_id: str) -> tuple[int, int | str]:
    normalized = str(task_id)
    if normalized.lstrip("-").isdigit():
        return (0, int(normalized))
    return (1, normalized)


def _sorted_task_ids(task_ids: set[str]) -> list[str]:
    return sorted(task_ids, key=_task_sort_key)


def _validate_matrix(
    matrix: TaskTrialSuccess,
    *,
    matrix_name: str,
) -> tuple[list[str], list[int]]:
    if not matrix:
        raise ValueError(f"{matrix_name} has no task/trial data")

    task_ids = set(matrix.keys())
    expected_trial_ids: set[int] | None = None

    for task_id in task_ids:
        task_trial_map = matrix[task_id]
        if not task_trial_map:
            raise ValueError(f"{matrix_name} has no trial data for task {task_id}")

        trial_ids = set(task_trial_map.keys())
        if expected_trial_ids is None:
            expected_trial_ids = trial_ids
        elif trial_ids != expected_trial_ids:
            raise ValueError(f"{matrix_name} has inconsistent trial IDs across tasks")

        for trial_id, success in task_trial_map.items():
            if success not in (0, 1):
                raise ValueError(
                    f"{matrix_name} has non-binary success value for task {task_id}, trial {trial_id}: {success}"
                )

    if expected_trial_ids is None:
        raise ValueError(f"{matrix_name} has no trial data")

    return _sorted_task_ids(task_ids), sorted(expected_trial_ids)


def _validate_alignment(
    baseline: TaskTrialSuccess,
    candidate: TaskTrialSuccess,
) -> tuple[list[str], list[int]]:
    baseline_task_ids, baseline_trial_ids = _validate_matrix(
        baseline, matrix_name="baseline"
    )
    candidate_task_ids, candidate_trial_ids = _validate_matrix(
        candidate, matrix_name="candidate"
    )

    if set(baseline_task_ids) != set(candidate_task_ids):
        raise ValueError("Task IDs do not match between baseline and candidate")

    if set(baseline_trial_ids) != set(candidate_trial_ids):
        raise ValueError("Trial IDs do not match between baseline and candidate")

    return baseline_task_ids, baseline_trial_ids


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _binom_tail_probability_half(n: int, k: int) -> float:
    if n == 0:
        return 1.0
    return sum(math.comb(n, i) for i in range(k + 1)) / (2**n)


def _mcnemar_exact_p_value(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = _binom_tail_probability_half(n=n, k=min(b, c))
    return min(1.0, 2 * tail)


def build_task_trial_success(results: Results) -> TaskTrialSuccess:
    matrix: TaskTrialSuccess = {}

    for simulation in results.simulations:
        if simulation.trial is None:
            raise ValueError(
                f"Simulation {simulation.id} has no trial index; cannot compute comparison metrics"
            )
        if simulation.reward_info is None:
            raise ValueError(
                f"Simulation {simulation.id} has no reward_info; cannot compute comparison metrics"
            )

        task_id = str(simulation.task_id)
        trial_id = int(simulation.trial)
        success = 1 if is_successful(simulation.reward_info.reward) else 0

        if task_id not in matrix:
            matrix[task_id] = {}

        if trial_id in matrix[task_id]:
            raise ValueError(
                f"Duplicate simulation found for task {task_id}, trial {trial_id}"
            )

        matrix[task_id][trial_id] = success

    _validate_matrix(matrix, matrix_name="results")
    return matrix


def compute_comparison_metrics(
    baseline: TaskTrialSuccess,
    candidate: TaskTrialSuccess,
    *,
    mcnemar_trial: int = 0,
) -> dict[str, Any]:
    task_ids, trial_ids = _validate_alignment(baseline, candidate)

    if mcnemar_trial not in trial_ids:
        raise ValueError(
            f"McNemar trial {mcnemar_trial} is not present in trial IDs: {trial_ids}"
        )

    num_tasks = len(task_ids)
    num_trials = len(trial_ids)

    per_task: list[dict[str, Any]] = []
    total_candidate_win_rate = 0.0
    total_delta = 0.0
    tasks_improved = 0
    tasks_worsened = 0

    hard_task_ids: list[str] = []
    easy_task_ids: list[str] = []
    hard_rescued_task_ids: list[str] = []
    hard_fully_rescued_task_ids: list[str] = []
    easy_regressed_task_ids: list[str] = []
    easy_collapsed_task_ids: list[str] = []

    for task_id in task_ids:
        baseline_by_trial = baseline[task_id]
        candidate_by_trial = candidate[task_id]

        baseline_successes = sum(baseline_by_trial[t] for t in trial_ids)
        candidate_successes = sum(candidate_by_trial[t] for t in trial_ids)

        baseline_win_rate = baseline_successes / num_trials
        candidate_win_rate = candidate_successes / num_trials
        delta_win_rate = (candidate_successes - baseline_successes) / num_trials

        total_candidate_win_rate += candidate_win_rate
        total_delta += delta_win_rate

        if delta_win_rate > 0:
            tasks_improved += 1
        elif delta_win_rate < 0:
            tasks_worsened += 1

        if baseline_successes == 0:
            hard_task_ids.append(task_id)
            if candidate_successes > 0:
                hard_rescued_task_ids.append(task_id)
            if candidate_successes == num_trials:
                hard_fully_rescued_task_ids.append(task_id)

        if baseline_successes == num_trials:
            easy_task_ids.append(task_id)
            if candidate_successes < num_trials:
                easy_regressed_task_ids.append(task_id)
            if candidate_successes == 0:
                easy_collapsed_task_ids.append(task_id)

        per_task.append(
            {
                "task_id": task_id,
                "baseline_successes": baseline_successes,
                "candidate_successes": candidate_successes,
                "baseline_win_rate": baseline_win_rate,
                "candidate_win_rate": candidate_win_rate,
                "delta_win_rate": delta_win_rate,
            }
        )

    baseline_fails = 0
    baseline_passes = 0
    rescues = 0
    regressions = 0

    for task_id in task_ids:
        for trial_id in trial_ids:
            baseline_success = baseline[task_id][trial_id]
            candidate_success = candidate[task_id][trial_id]

            if baseline_success == 0:
                baseline_fails += 1
            else:
                baseline_passes += 1

            if baseline_success == 0 and candidate_success == 1:
                rescues += 1
            elif baseline_success == 1 and candidate_success == 0:
                regressions += 1

    total_pairs = baseline_fails + baseline_passes
    rescue_rate_trial = _rate(rescues, baseline_fails)
    harm_rate_trial = _rate(regressions, baseline_passes)
    net_flip = _rate(rescues - regressions, total_pairs)
    safe_gain = rescue_rate_trial - (2 * harm_rate_trial)

    mcnemar_a = 0
    mcnemar_b = 0
    mcnemar_c = 0
    mcnemar_d = 0
    for task_id in task_ids:
        baseline_success = baseline[task_id][mcnemar_trial]
        candidate_success = candidate[task_id][mcnemar_trial]

        if baseline_success == 1 and candidate_success == 1:
            mcnemar_a += 1
        elif baseline_success == 1 and candidate_success == 0:
            mcnemar_b += 1
        elif baseline_success == 0 and candidate_success == 1:
            mcnemar_c += 1
        else:
            mcnemar_d += 1

    return {
        "num_tasks": num_tasks,
        "num_trials": num_trials,
        "trial_ids": trial_ids,
        "mean_win_rate": total_candidate_win_rate / num_tasks,
        "mean_delta": total_delta / num_tasks,
        "pct_tasks_improved": _rate(tasks_improved, num_tasks),
        "pct_tasks_worsened": _rate(tasks_worsened, num_tasks),
        "pct_tasks_unchanged": _rate(
            num_tasks - tasks_improved - tasks_worsened,
            num_tasks,
        ),
        "hard_task_ids": hard_task_ids,
        "easy_task_ids": easy_task_ids,
        "hard_rescue_rate": _rate(len(hard_rescued_task_ids), len(hard_task_ids)),
        "hard_full_rescue_rate": _rate(
            len(hard_fully_rescued_task_ids), len(hard_task_ids)
        ),
        "easy_regress_rate": _rate(len(easy_regressed_task_ids), len(easy_task_ids)),
        "easy_collapse_rate": _rate(len(easy_collapsed_task_ids), len(easy_task_ids)),
        "hard_rescued_task_ids": hard_rescued_task_ids,
        "hard_fully_rescued_task_ids": hard_fully_rescued_task_ids,
        "easy_regressed_task_ids": easy_regressed_task_ids,
        "easy_collapsed_task_ids": easy_collapsed_task_ids,
        "trial_flip_counts": {
            "rescues": rescues,
            "regressions": regressions,
            "baseline_fails": baseline_fails,
            "baseline_passes": baseline_passes,
            "total_pairs": total_pairs,
        },
        "rescue_rate_trial": rescue_rate_trial,
        "harm_rate_trial": harm_rate_trial,
        "net_flip": net_flip,
        "safe_gain": safe_gain,
        "mcnemar_trial": {
            "trial": mcnemar_trial,
            "a": mcnemar_a,
            "b": mcnemar_b,
            "c": mcnemar_c,
            "d": mcnemar_d,
            "p_value": _mcnemar_exact_p_value(mcnemar_b, mcnemar_c),
        },
        "per_task": per_task,
    }


def compute_results_comparison_metrics(
    baseline_results: Results,
    candidate_results: Results,
    *,
    mcnemar_trial: int = 0,
) -> dict[str, Any]:
    baseline = build_task_trial_success(baseline_results)
    candidate = build_task_trial_success(candidate_results)
    return compute_comparison_metrics(
        baseline,
        candidate,
        mcnemar_trial=mcnemar_trial,
    )
