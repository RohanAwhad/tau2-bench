import pytest

from tau2.metrics.comparison_metrics import compute_comparison_metrics


def test_compute_comparison_metrics_basic_case() -> None:
    baseline = {
        "1": {0: 0, 1: 0, 2: 0},
        "2": {0: 1, 1: 1, 2: 1},
        "3": {0: 1, 1: 0, 2: 1},
        "4": {0: 0, 1: 1, 2: 0},
    }
    candidate = {
        "1": {0: 1, 1: 0, 2: 0},
        "2": {0: 1, 1: 0, 2: 1},
        "3": {0: 1, 1: 0, 2: 1},
        "4": {0: 0, 1: 1, 2: 1},
    }

    metrics = compute_comparison_metrics(baseline, candidate, mcnemar_trial=0)

    assert metrics["num_tasks"] == 4
    assert metrics["num_trials"] == 3

    assert metrics["mean_win_rate"] == pytest.approx(7 / 12)
    assert metrics["mean_delta"] == pytest.approx(1 / 12)
    assert metrics["pct_tasks_improved"] == pytest.approx(0.5)
    assert metrics["pct_tasks_worsened"] == pytest.approx(0.25)

    assert metrics["hard_task_ids"] == ["1"]
    assert metrics["easy_task_ids"] == ["2"]
    assert metrics["hard_rescue_rate"] == pytest.approx(1.0)
    assert metrics["hard_full_rescue_rate"] == pytest.approx(0.0)
    assert metrics["easy_regress_rate"] == pytest.approx(1.0)
    assert metrics["easy_collapse_rate"] == pytest.approx(0.0)

    assert metrics["trial_flip_counts"]["rescues"] == 2
    assert metrics["trial_flip_counts"]["regressions"] == 1
    assert metrics["rescue_rate_trial"] == pytest.approx(2 / 6)
    assert metrics["harm_rate_trial"] == pytest.approx(1 / 6)
    assert metrics["net_flip"] == pytest.approx(1 / 12)
    assert metrics["safe_gain"] == pytest.approx(0.0)

    assert metrics["mcnemar_trial"]["trial"] == 0
    assert metrics["mcnemar_trial"]["a"] == 2
    assert metrics["mcnemar_trial"]["b"] == 0
    assert metrics["mcnemar_trial"]["c"] == 1
    assert metrics["mcnemar_trial"]["d"] == 1
    assert metrics["mcnemar_trial"]["p_value"] == pytest.approx(1.0)


def test_compute_comparison_metrics_rejects_task_mismatch() -> None:
    baseline = {
        "1": {0: 1, 1: 0, 2: 1},
        "2": {0: 0, 1: 0, 2: 0},
    }
    candidate = {
        "1": {0: 1, 1: 0, 2: 1},
    }

    with pytest.raises(ValueError, match="Task IDs do not match"):
        compute_comparison_metrics(baseline, candidate)


def test_compute_comparison_metrics_rejects_trial_mismatch() -> None:
    baseline = {
        "1": {0: 1, 1: 0, 2: 1},
    }
    candidate = {
        "1": {0: 1, 1: 0},
    }

    with pytest.raises(ValueError, match="Trial IDs do not match"):
        compute_comparison_metrics(baseline, candidate)


def test_compute_comparison_metrics_mcnemar_exact_small_p_value() -> None:
    baseline = {str(task_id): {0: 0} for task_id in range(10)}
    candidate = {str(task_id): {0: 1} for task_id in range(10)}

    metrics = compute_comparison_metrics(baseline, candidate, mcnemar_trial=0)

    assert metrics["mcnemar_trial"]["a"] == 0
    assert metrics["mcnemar_trial"]["b"] == 0
    assert metrics["mcnemar_trial"]["c"] == 10
    assert metrics["mcnemar_trial"]["d"] == 0
    assert metrics["mcnemar_trial"]["p_value"] == pytest.approx(0.001953125)
