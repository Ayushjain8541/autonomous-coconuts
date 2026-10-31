"""Protect benchmark arithmetic, source alignment, and honest denominators."""

import numpy as np
import pandas as pd
import pytest
from pathlib import Path
import subprocess
import sys

from benchmark_predictions import benchmark_frames
from prediction.predict import classify_risk


@pytest.fixture
def paired_reports():
    reference = pd.DataFrame({
        "event_id": [1, 1, 2], "time_to_tca": [3.0, 2.0, 2.5],
        "miss_distance": [6000.0] * 3, "relative_speed": [10000.0] * 3,
        "relative_position_r": [1.0] * 3, "relative_position_t": [2.0] * 3,
        "relative_position_n": [3.0] * 3, "c_object_type": ["DEBRIS"] * 3,
        "c_sigma_r": [10.0] * 3, "t_sigma_r": [5.0] * 3,
        "F10": [80.0] * 3, "AP": [6.0] * 3, "risk": [-7.0, -5.0, -3.0],
    })
    predictions = reference.assign(risk=[-7.0, -7.0, -3.0])
    predictions["class_model"] = classify_risk(predictions.risk, predictions.miss_distance)
    return reference, predictions


def test_known_benchmark_counts_and_regression_errors(paired_reports):
    reference, predictions = paired_reports
    report = benchmark_frames(reference, predictions)
    assert report["rows"] == 3 and report["events"] == 2
    assert report["tier_correct_rows"] == 2
    assert report["tier_accuracy"] == pytest.approx(2 / 3)
    assert report["baselines"]["distance_only"]["accuracy"] == pytest.approx(1 / 3)
    assert report["latest_report_per_event"] == {"rows": 2, "correct_rows": 1, "accuracy": 0.5}
    assert report["regression"]["rmse_log10_pc"] == pytest.approx(np.sqrt(4 / 3))
    assert report["regression"]["mae_log10_pc"] == pytest.approx(2 / 3)
    assert report["regression"]["r2"] == pytest.approx(0.5)
    assert report["regression"]["within_one_log10_unit_rate"] == pytest.approx(2 / 3)
    assert report["confusion_matrix"] == [[1, 0, 0], [1, 0, 0], [0, 0, 1]]


def test_repeated_event_ids_cannot_hide_row_reordering(paired_reports):
    reference, predictions = paired_reports
    reordered = predictions.iloc[[1, 0, 2]].reset_index(drop=True)
    assert reference.event_id.tolist() == reordered.event_id.tolist()
    with pytest.raises(ValueError, match="not aligned"):
        benchmark_frames(reference, reordered)


def test_probability_band_recall_exposes_errors_hidden_by_distance(paired_reports):
    reference, predictions = paired_reports
    reference = reference.assign(miss_distance=500.0)
    predictions = predictions.assign(miss_distance=500.0, class_model="Critical")
    report = benchmark_frames(reference, predictions)
    assert report["tier_accuracy"] == 1.0
    bands = report["probability_bands"]
    assert bands["confusion_matrix"] == [[1, 0, 0], [1, 0, 0], [0, 0, 1]]
    assert bands["macro_recall"] == pytest.approx(2/3)
    assert bands["class_metrics"]["Elevated risk"]["recall"] == 0


def test_unlabelled_upload_cannot_produce_an_accuracy_score(paired_reports):
    reference, predictions = paired_reports
    with pytest.raises(ValueError, match="risk"):
        benchmark_frames(reference.drop(columns="risk"), predictions)


def test_inconsistent_exported_classes_cannot_inflate_accuracy(paired_reports):
    reference, predictions = paired_reports
    changed = predictions.assign(class_model=["Safe", "Elevated risk", "Critical"])
    with pytest.raises(ValueError, match="classes disagree"):
        benchmark_frames(reference, changed)


@pytest.mark.parametrize("frame_index", [0, 1])
@pytest.mark.parametrize("invalid", [np.nan, np.inf, 0.1])
def test_invalid_risk_labels_are_rejected(paired_reports, frame_index, invalid):
    frames = [frame.copy() for frame in paired_reports]
    frames[frame_index].loc[0, "risk"] = invalid
    with pytest.raises(ValueError, match="finite log10"):
        benchmark_frames(*frames)


def test_different_row_counts_are_rejected(paired_reports):
    reference, predictions = paired_reports
    with pytest.raises(ValueError, match="same nonzero"):
        benchmark_frames(reference, predictions.iloc[:2])


def test_constant_reference_has_no_defined_r_squared(paired_reports):
    reference, predictions = paired_reports
    reference = reference.assign(risk=-7.0)
    predictions = predictions.assign(risk=-7.0, class_model="Safe")
    assert benchmark_frames(reference, predictions)["regression"]["r2"] is None


def test_benchmark_cli_cannot_overwrite_reference_csv(tmp_path, paired_reports):
    reference, predictions = paired_reports
    source, output = tmp_path / "reference.csv", tmp_path / "predictions.csv"
    reference.to_csv(source, index=False)
    predictions.to_csv(output, index=False)
    original = source.read_bytes()
    script = Path(__file__).resolve().parents[1] / "benchmark_predictions.py"
    result = subprocess.run([
        sys.executable, str(script), "--reference", str(source),
        "--predictions", str(output), "--output", str(source),
    ], capture_output=True, text=True)
    assert result.returncode != 0
    assert "must not overwrite" in result.stderr
    assert source.read_bytes() == original
