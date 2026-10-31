"""Cost arithmetic, rare-case behavior and training/assessment isolation."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
import collision_risk

from collision_risk import (
    FEATURES, TrainingConfig, balanced_band_error, class_sample_weights,
    evaluate_model, fit_final_model, probability_bands, select_weighted_model, split_events,
)


def test_frequency_costs_have_mean_one_and_heavily_penalize_critical_errors():
    config = TrainingConfig(elevated_weight=2, critical_weight=4)
    weights, costs = class_sample_weights([-9, -8, -5, -3], config)
    np.testing.assert_allclose(costs, np.array([2, 8, 16]) / 7)
    np.testing.assert_allclose(weights, np.array([2, 2, 8, 16]) / 7)
    assert weights.mean() == pytest.approx(1)
    # For the same two-log-unit underprediction, a Critical row costs 8x more.
    assert (weights[-1] * 2**2) / (weights[0] * 2**2) == pytest.approx(8)


@pytest.mark.parametrize("values", [[-9] * 10, [-3] * 10, [-5] * 10])
def test_absent_classes_do_not_cause_division_by_zero(values):
    weights, costs = class_sample_weights(values, TrainingConfig())
    np.testing.assert_array_equal(weights, np.ones(len(values)))
    assert np.isfinite(costs).all()


def test_band_boundaries_and_early_stopping_reject_one_class_collapse():
    np.testing.assert_array_equal(probability_bands([-6.001, -6, -4.001, -4]), [0, 1, 1, 2])
    actual = [-8, -5, -3]
    assert balanced_band_error(actual, actual) == 0
    for constant in [-8, -5, -3]:
        assert balanced_band_error(actual, [constant] * 3) > 0.98
    assert balanced_band_error(actual, [-8, -5, -5]) < balanced_band_error(actual, [-8]*3)


def training_rows(n=120):
    frame = pd.DataFrame({name: np.ones(n) for name in FEATURES})
    frame["event_id"] = np.arange(n)
    frame["c_object_type"] = "DEBRIS"
    frame["miss_distance"] = 6000.0
    frame["AP"] = np.arange(n) % 3
    frame["risk"] = np.array([-9., -5., -3.])[frame["AP"]]
    return frame


def test_weighted_regression_changes_a_missed_critical_leaf_without_changing_thresholds(monkeypatch):
    # Indistinguishable inputs: the optimum is their (weighted) target mean.
    frame = training_rows(100)
    frame.loc[:, "event_id"] = 1
    frame.loc[:, "AP"] = 1
    frame["risk"] = [-10.] * 90 + [-3.] * 10
    config = TrainingConfig(max_estimators=1, n_jobs=1, max_depth=1,
                            elevated_weight=1, critical_weight=20)
    # Remove row subsampling so the one-leaf optimum has an exact analytic mean.
    factory = collision_risk._new_model
    def full_batch_model(*args, **kwargs):
        return factory(*args, **kwargs).set_params(subsample=1, reg_alpha=0)
    monkeypatch.setattr(collision_risk, "_new_model", full_batch_model)
    weighted, encoder = fit_final_model(frame, config, 1)
    baseline, _ = fit_final_model(frame, replace(config, class_balance_power=0, critical_weight=1), 1)
    x = encoder.transform(frame)
    np.testing.assert_allclose(baseline.predict(x), -9.3, atol=1e-5)
    np.testing.assert_allclose(weighted.predict(x), -70/21, atol=1e-5)
    assert (weighted.predict(x) >= -4).all()
    assert (baseline.predict(x) < -4).all()


def test_holdout_labels_cannot_change_selected_weights_rounds_or_predictions():
    frame = training_rows()
    config = TrainingConfig(max_estimators=16, early_stopping_rounds=4, n_jobs=1, max_depth=2)
    first = evaluate_model(frame, config)
    poisoned = frame.copy()
    idx = split_events(frame, config)["holdout"]
    poisoned.iloc[idx, poisoned.columns.get_loc("risk")] = -30
    second = evaluate_model(poisoned, config)
    assert first["selected_config"] == second["selected_config"]
    assert first["metrics"]["weight_selection"] == second["metrics"]["weight_selection"]
    np.testing.assert_array_equal(first["holdout_prediction"], second["holdout_prediction"])
    assert first["metrics"]["holdout_xgboost"] != second["metrics"]["holdout_xgboost"]


def test_search_refuses_to_claim_balance_without_all_validation_classes():
    x = pd.DataFrame({"x": [0, 1, 2]})
    with pytest.raises(ValueError, match="all three probability bands"):
        select_weighted_model(x, [-9, -5, -3], x, [-9, -9, -9], TrainingConfig())


def test_perfect_band_recall_cannot_win_with_arbitrarily_bad_regression(monkeypatch):
    class Candidate:
        best_iteration = 1
        def __init__(self, config):
            self.weighted = config.critical_weight > 1
        def fit(self, *args, **kwargs):
            return self
        def predict(self, inputs):
            # Weighted candidate gets every band correct but misses Safe risk by 21 logs.
            return np.array([-30, -5, -3] if self.weighted else [-9, -5, -5])
    monkeypatch.setattr(collision_risk, "_new_model", lambda config, *a, **k: Candidate(config))
    x = pd.DataFrame({"x": [0, 1, 2]})
    result = select_weighted_model(x, [-9, -5, -3], x, [-9, -5, -3], TrainingConfig())
    assert result["config"].critical_weight == 1  # The eligible baseline wins.
    trial = result["selection"]["trials"][1]
    assert trial["validation_probability_bands"]["worst_recall"] == 1
    assert not trial["eligible"]


@pytest.mark.parametrize("kwargs", [
    {"class_balance_power": -1}, {"class_balance_power": np.nan},
    {"critical_weight": 0}, {"critical_weight": np.inf}, {"elevated_weight": np.nan},
])
def test_invalid_training_costs_fail_before_fitting(kwargs):
    with pytest.raises(ValueError):
        TrainingConfig(**kwargs)
