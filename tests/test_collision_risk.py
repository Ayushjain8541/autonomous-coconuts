"""Behavioral checks for leakage prevention, operational tiers, and UI output."""

import numpy as np
import pandas as pd
import pytest

from collision_risk import (
    CRITICAL,
    ELEVATED,
    FEATURES,
    FORBIDDEN_TEST_COLUMNS,
    FeatureEncoder,
    SAFE,
    TrainingConfig,
    classify_risk,
    dashboard_predictions,
    fit_final_model,
    latest_event_predictions,
    load_test_data,
    split_events,
)
from xgboost import XGBRegressor


EXPECTED_FEATURES = (
    "event_id",
    "time_to_tca",
    "miss_distance",
    "relative_speed",
    "relative_position_r",
    "relative_position_t",
    "relative_position_n",
    "c_object_type",
    "c_sigma_r",
    "t_sigma_r",
    "F10",
    "AP",
)


@pytest.fixture
def telemetry():
    """Unsorted repeated IDs ensure output alignment is preserved."""
    return pd.DataFrame(
        {
            "event_id": [9, 3, 9, 1],
            "time_to_tca": [6.0, 4.0, 2.1, 2.5],
            "miss_distance": [6000.0, 3000.0, 750.0, 10000.0],
            "relative_speed": [14000.0, 12500.0, 9000.0, 7500.0],
            "relative_position_r": [5.0, -3.0, 1.0, -2.0],
            "relative_position_t": [4000.0, 2000.0, 500.0, 7000.0],
            "relative_position_n": [4400.0, -2200.0, -550.0, 7000.0],
            "c_object_type": ["DEBRIS", "UNKNOWN", "DEBRIS", "PAYLOAD"],
            "c_sigma_r": [50.0, 10.0, np.nan, 90.0],
            "t_sigma_r": [3.0, 2.0, 4.0, 5.0],
            "F10": [72.0, np.nan, 80.0, 90.0],
            "AP": [6.0, np.nan, 5.0, 10.0],
        },
        index=[10, 20, 30, 40],
    )


def test_feature_allowlist_matches_user_contract():
    assert tuple(FEATURES) == EXPECTED_FEATURES
    assert set(FORBIDDEN_TEST_COLUMNS) == {
        "risk", "max_risk_estimate", "max_risk_scaling"
    }
    assert not set(FEATURES).intersection(FORBIDDEN_TEST_COLUMNS)


@pytest.mark.parametrize(
    ("risk", "distance_km", "expected"),
    [
        (-7.0, 6.0, SAFE),
        (-6.0, 6.0, ELEVATED),
        (-5.0, 6.0, ELEVATED),
        (-4.0, 6.0, CRITICAL),
        (-3.0, 6.0, CRITICAL),
        (-20.0, 5.0, ELEVATED),
        (-20.0, 1.0, ELEVATED),
        (-20.0, 0.999, CRITICAL),
        (-20.0, 0.0, CRITICAL),
        (-5.0, 0.5, CRITICAL),
        (-4.0, 3.0, CRITICAL),
        (-4.0, 1.0, CRITICAL),
        (-4.0, 5.0, CRITICAL),
        (0.0, 10.0, CRITICAL),
    ],
)
def test_risk_boundaries_and_critical_precedence(risk, distance_km, expected):
    assert classify_risk(risk, distance_km, distance_unit="km") == expected
    assert classify_risk(risk, distance_km * 1000.0) == expected


def test_threshold_neighbors_do_not_round_to_wrong_tier():
    below_elevated = np.nextafter(-6.0, -np.inf)
    below_critical = np.nextafter(-4.0, -np.inf)
    above_five_km = np.nextafter(5000.0, np.inf)
    below_one_km = np.nextafter(1000.0, -np.inf)
    assert classify_risk(below_elevated, 6000.0) == SAFE
    assert classify_risk(below_critical, 6000.0) == ELEVATED
    assert classify_risk(-20.0, above_five_km) == SAFE
    assert classify_risk(-20.0, below_one_km) == CRITICAL


def test_vectorized_classification_preserves_row_order():
    result = classify_risk(
        [-8.0, -6.0, -4.0, -8.0, -5.0],
        [6000.0, 6000.0, 6000.0, 1000.0, 500.0],
    )
    assert isinstance(result, np.ndarray)
    np.testing.assert_array_equal(
        result, [SAFE, ELEVATED, CRITICAL, ELEVATED, CRITICAL]
    )


@pytest.mark.parametrize("invalid", [np.nan, np.inf, -np.inf])
def test_classifier_rejects_nonfinite_risk(invalid):
    with pytest.raises(ValueError):
        classify_risk(invalid, 6000.0)
    with pytest.raises(ValueError):
        classify_risk([-7.0, invalid], [6000.0, 6000.0])


@pytest.mark.parametrize("invalid", [np.nan, np.inf, -np.inf, -1.0])
def test_classifier_rejects_invalid_distances(invalid):
    with pytest.raises(ValueError):
        classify_risk(-7.0, invalid)
    with pytest.raises(ValueError):
        classify_risk([-7.0, -7.0], [6000.0, invalid])


def test_classifier_rejects_unknown_distance_units():
    with pytest.raises(ValueError):
        classify_risk(-7.0, 6000.0, distance_unit="miles")


def test_test_loader_drops_forbidden_and_extra_columns(tmp_path, telemetry):
    poisoned = telemetry.assign(
        risk=[0.0, -30.0, -4.0, -6.0],
        max_risk_estimate=123456789.0,
        max_risk_scaling=-999.0,
        mission_id=42,
    )
    # CSV order must not determine the model feature order.
    path = tmp_path / "test_data.csv"
    poisoned.loc[:, list(reversed(poisoned.columns))].to_csv(path, index=False)
    actual = load_test_data(path)
    pd.testing.assert_frame_equal(actual, telemetry.reset_index(drop=True))
    assert list(actual.columns) == list(FEATURES)


def test_test_loader_accepts_already_sanitized_data(tmp_path, telemetry):
    path = tmp_path / "clean_test.csv"
    telemetry.to_csv(path, index=False)
    pd.testing.assert_frame_equal(
        load_test_data(path), telemetry.reset_index(drop=True)
    )


def test_test_loader_rejects_missing_allowed_feature(tmp_path, telemetry):
    path = tmp_path / "missing_distance.csv"
    telemetry.drop(columns="miss_distance").to_csv(path, index=False)
    with pytest.raises((KeyError, ValueError)):
        load_test_data(path)


class SpyEncoder:
    def __init__(self):
        self.calls = []

    def transform(self, frame):
        assert not set(frame.columns).intersection(FORBIDDEN_TEST_COLUMNS)
        assert list(frame.columns) == list(FEATURES)
        self.calls.append(frame.copy())
        return frame.loc[:, ["miss_distance", "relative_speed"]]


class SpyModel:
    def __init__(self, predictions):
        self.predictions = np.asarray(predictions, dtype=float)
        self.calls = []

    def predict(self, encoded):
        assert not set(encoded.columns).intersection(FORBIDDEN_TEST_COLUMNS)
        self.calls.append(encoded.copy())
        return self.predictions.copy()


def test_dashboard_output_schema_alignment_and_probability_bound(telemetry):
    encoder = SpyEncoder()
    model = SpyModel([-7.0, -5.0, -20.0, 0.25])
    result = dashboard_predictions(model, encoder, telemetry)
    assert list(result.columns) == ["event_id", "predicted_risk", "risk_tier"]
    assert result.index.equals(pd.RangeIndex(len(telemetry)))
    assert result["event_id"].tolist() == [9, 3, 9, 1]
    np.testing.assert_array_equal(result["predicted_risk"], [-7.0, -5.0, -20.0, 0.0])
    assert result["risk_tier"].tolist() == [SAFE, ELEVATED, CRITICAL, CRITICAL]
    assert len(model.calls) == len(encoder.calls) == 1
    pd.testing.assert_frame_equal(encoder.calls[0], telemetry)


@pytest.mark.parametrize("forbidden", ["risk", "max_risk_estimate", "max_risk_scaling"])
def test_dashboard_rejects_unsanitized_test_before_any_prediction(telemetry, forbidden):
    model, encoder = SpyModel([-7.0] * len(telemetry)), SpyEncoder()
    poisoned = telemetry.assign(**{forbidden: -999.0})
    with pytest.raises(ValueError):
        dashboard_predictions(model, encoder, poisoned)
    assert model.calls == []
    assert encoder.calls == []


def test_poisoned_targets_never_reach_inference(tmp_path, telemetry):
    encoder = SpyEncoder()
    model = SpyModel([-7.0, -5.0, -20.0, -4.0])
    outputs = []
    for poison in [-999999.0, 999999.0]:
        raw = telemetry.assign(**{column: poison for column in FORBIDDEN_TEST_COLUMNS})
        path = tmp_path / f"test_{poison}.csv"
        raw.to_csv(path, index=False)
        sanitized = load_test_data(path)
        outputs.append(dashboard_predictions(model, encoder, sanitized))
    pd.testing.assert_frame_equal(outputs[0], outputs[1])
    assert len(model.calls) == len(encoder.calls) == 2


def test_encoder_handles_unseen_types_and_missing_numeric_values(telemetry):
    original = telemetry.copy(deep=True)
    encoder = FeatureEncoder().fit(telemetry)
    known = encoder.transform(telemetry)
    future = telemetry.copy()
    future.loc[10, "c_object_type"] = "NEW_UNSEEN_OBJECT_TYPE"
    future.loc[10, "F10"] = np.nan
    future.loc[20, "AP"] = np.inf
    encoded = encoder.transform(future)
    object_columns = [c for c in encoded.columns if c.startswith("c_object_type_")]
    assert object_columns
    assert encoded.columns.equals(known.columns)
    assert encoded.index.equals(telemetry.index)
    assert encoded.loc[10, object_columns].eq(0).all()
    assert known.loc[10, object_columns].sum() == 1
    assert np.isnan(encoded.loc[10, "F10"])
    assert np.isnan(encoded.loc[20, "AP"])
    assert np.isnan(encoded.loc[30, "c_sigma_r"])
    assert np.issubdtype(encoded.to_numpy().dtype, np.number)
    assert not set(encoded.columns).intersection(FORBIDDEN_TEST_COLUMNS)
    pd.testing.assert_frame_equal(telemetry, original)


def test_encoder_requires_fit_before_transform(telemetry):
    with pytest.raises(ValueError):
        FeatureEncoder().transform(telemetry)


def test_encoder_metadata_roundtrip_preserves_known_and_unseen_types(tmp_path, telemetry):
    train = telemetry.copy()
    train.loc[20, "c_object_type"] = None
    encoder = FeatureEncoder().fit(train)
    path = tmp_path / "feature_encoder.json"
    encoder.save(path)
    restored = FeatureEncoder.load(path)
    future = train.copy()
    future.loc[30, "c_object_type"] = "UNSEEN_AFTER_RELOAD"
    pd.testing.assert_frame_equal(
        restored.transform(future), encoder.transform(future)
    )
    assert path.read_text().lstrip().startswith("{")


def test_event_partitions_are_disjoint_exhaustive_and_repeatable(telemetry):
    train = pd.concat([telemetry.iloc[[0]]] * 60, ignore_index=True)
    train["event_id"] = np.repeat(np.arange(20), 3)
    train["time_to_tca"] = np.tile([6.0, 4.0, 2.1], 20)
    train["risk"] = np.linspace(-20.0, -3.0, len(train))
    train.index = np.arange(1000, 1000 + len(train))[::-1]
    config = TrainingConfig(random_state=123)
    partitions = split_events(train, config)
    repeated = split_events(train, config)
    assert set(partitions) == {"fit", "validation", "holdout"}
    all_indices = np.concatenate(list(partitions.values()))
    np.testing.assert_array_equal(np.sort(all_indices), np.arange(len(train)))
    assert len(np.unique(all_indices)) == len(train)
    event_sets = {}
    for name, indices in partitions.items():
        assert len(indices) > 0
        np.testing.assert_array_equal(indices, repeated[name])
        event_sets[name] = set(train.iloc[indices]["event_id"])
    assert event_sets["fit"].isdisjoint(event_sets["validation"])
    assert event_sets["fit"].isdisjoint(event_sets["holdout"])
    assert event_sets["validation"].isdisjoint(event_sets["holdout"])
    assert set.union(*event_sets.values()) == set(train["event_id"])


def test_latest_event_summary_selects_whole_latest_rows_with_stable_ties(telemetry):
    duplicate = telemetry.iloc[[2]].copy()
    # Same timestamp/event as the prior latest row: first input row must win.
    test_data = pd.concat([telemetry, duplicate], ignore_index=True)
    dashboard = pd.DataFrame(
        {
            "event_id": [9, 3, 9, 1, 9],
            "predicted_risk": [-4.0, -5.0, -8.0, -7.0, -2.0],
            "risk_tier": [CRITICAL, ELEVATED, CRITICAL, SAFE, CRITICAL],
        },
        index=[100, 200, 300, 400, 500],
    )
    latest = latest_event_predictions(dashboard, test_data)
    expected = dashboard.iloc[[2, 1, 3]].reset_index(drop=True)
    pd.testing.assert_frame_equal(latest, expected)
    assert latest["event_id"].is_unique


def test_latest_event_summary_rejects_misaligned_telemetry(telemetry):
    dashboard = pd.DataFrame(
        {
            "event_id": telemetry["event_id"].to_numpy(),
            "predicted_risk": [-7.0] * len(telemetry),
            "risk_tier": [SAFE] * len(telemetry),
        }
    )
    with pytest.raises(ValueError):
        latest_event_predictions(dashboard.iloc[:-1], telemetry)
    reordered = telemetry.iloc[[1, 0, 2, 3]]
    with pytest.raises(ValueError):
        latest_event_predictions(dashboard, reordered)
    invalid_time = telemetry.copy()
    invalid_time.loc[10, "time_to_tca"] = np.nan
    with pytest.raises(ValueError):
        latest_event_predictions(dashboard, invalid_time)


def test_real_xgboost_save_load_inference_smoke(tmp_path, telemetry):
    train = pd.concat([telemetry] * 8, ignore_index=True)
    train["event_id"] = np.repeat(np.arange(8), len(telemetry))
    train["risk"] = np.tile([-8.0, -5.0, -3.0, -10.0], 8)
    config = TrainingConfig(max_estimators=3, n_jobs=1, max_depth=2)
    model, encoder = fit_final_model(train, config, best_rounds=3)
    expected = dashboard_predictions(model, encoder, telemetry)
    model_path = tmp_path / "model.ubj"
    encoder_path = tmp_path / "encoder.json"
    model.save_model(model_path)
    encoder.save(encoder_path)
    restored_model = XGBRegressor()
    restored_model.load_model(model_path)
    restored_encoder = FeatureEncoder.load(encoder_path)
    actual = dashboard_predictions(restored_model, restored_encoder, telemetry)
    pd.testing.assert_frame_equal(actual, expected)
    assert np.isfinite(actual["predicted_risk"]).all()
    assert actual["predicted_risk"].le(0).all()
