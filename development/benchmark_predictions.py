"""Evaluate a frozen prediction CSV against supplied same-row risk labels.

This evaluator never deserializes, trains, tunes, or calls the prediction model. It
reads the reference risk only after predictions have been exported separately.
The results measure reported-risk reconstruction, not final-TCA forecasting.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from prediction.predict import FEATURES, classify_risk

CLASSES = ("Safe", "Elevated risk", "Critical")


def _rate(numerator, denominator):
    return float(numerator / denominator) if denominator else 0.0


def _binary_metrics(actual, predicted):
    tp = int(np.sum(actual & predicted))
    fp = int(np.sum(~actual & predicted))
    fn = int(np.sum(actual & ~predicted))
    return {
        "support": int(np.sum(actual)), "true_positives": tp,
        "false_positives": fp, "false_negatives": fn,
        "precision": _rate(tp, tp + fp), "recall": _rate(tp, tp + fn),
        "f1": _rate(2 * tp, 2 * tp + fp + fn),
    }


def benchmark_frames(reference, predictions, *, distance_unit="m"):
    """Require identical row alignment; compare classes and continuous log-risk."""
    for name, frame, extra in (
        ("Reference", reference, ("risk",)),
        ("Predictions", predictions, ("risk", "class_model")),
    ):
        missing = sorted(set((*FEATURES, *extra)).difference(frame.columns))
        if missing:
            raise ValueError(f"{name} CSV is missing required columns: {missing}")
    if len(reference) != len(predictions) or reference.empty:
        raise ValueError("CSV files must contain the same nonzero number of rows.")
    reference, predictions = reference.reset_index(drop=True), predictions.reset_index(drop=True)
    # event_id repeats. Joining on it alone would multiply/misalign the reports.
    try:
        pd.testing.assert_frame_equal(
            reference[list(FEATURES)], predictions[list(FEATURES)],
            check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12,
        )
    except AssertionError as error:
        raise ValueError("CSV telemetry rows are not aligned in the same order.") from error
    actual = pd.to_numeric(reference["risk"], errors="raise").to_numpy(dtype=float)
    predicted = pd.to_numeric(predictions["risk"], errors="raise").to_numpy(dtype=float)
    if any(not np.isfinite(values).all() or (values > 0).any()
           for values in (actual, predicted)):
        raise ValueError("Reference and predicted risk must be finite log10(Pc) values <= 0.")
    distance = pd.to_numeric(reference["miss_distance"], errors="raise").to_numpy(dtype=float)
    truth = classify_risk(actual, distance, distance_unit=distance_unit)
    computed = classify_risk(predicted, distance, distance_unit=distance_unit)
    exported = predictions["class_model"].to_numpy()
    if not np.array_equal(exported, computed):
        raise ValueError("Exported classes disagree with predicted risk and distance rules.")

    correct = truth == exported
    absolute_error = np.abs(actual - predicted)
    squared_error = np.square(actual - predicted)
    variance_sum = np.square(actual - actual.mean()).sum()
    distance_only = classify_risk(np.full(len(actual), -7.0), distance,
                                  distance_unit=distance_unit)
    time = pd.to_numeric(reference["time_to_tca"], errors="raise")
    if not np.isfinite(time).all():
        raise ValueError("Latest-report evaluation requires finite time_to_tca.")
    latest = reference.assign(time_to_tca=time).groupby(
        "event_id", sort=False
    )["time_to_tca"].idxmin().to_numpy()
    confusion = [[int(np.sum((truth == first) & (exported == second)))
                  for second in CLASSES] for first in CLASSES]
    majority = max(CLASSES, key=lambda label: int(np.sum(truth == label)))
    return {
        "target": "same-row reported risk = log10(Pc), not final-TCA risk",
        "distance_unit": distance_unit, "rows": len(reference),
        "events": int(reference["event_id"].nunique()),
        "tier_correct_rows": int(correct.sum()), "tier_accuracy": float(correct.mean()),
        "latest_report_per_event": {
            "rows": len(latest), "correct_rows": int(correct[latest].sum()),
            "accuracy": float(correct[latest].mean()),
        },
        "regression": {
            "rmse_log10_pc": float(np.sqrt(squared_error.mean())),
            "mae_log10_pc": float(absolute_error.mean()),
            "r2": float(1 - squared_error.sum() / variance_sum) if variance_sum else None,
            "within_one_log10_unit_rows": int(np.sum(absolute_error <= 1.0)),
            "within_one_log10_unit_rate": float(np.mean(absolute_error <= 1.0)),
        },
        "class_metrics": {label: _binary_metrics(truth == label, exported == label)
                          for label in CLASSES},
        "confusion_matrix_labels": list(CLASSES), "confusion_matrix": confusion,
        "baselines": {
            "distance_only": {"correct_rows": int(np.sum(distance_only == truth)),
                              "accuracy": float(np.mean(distance_only == truth))},
            "majority_class": {"class": majority,
                               "accuracy": float(np.mean(truth == majority))},
        },
        "probability_only": {
            f"risk_ge_{threshold:g}": _binary_metrics(actual >= threshold, predicted >= threshold)
            for threshold in (-6.0, -4.0)
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path,
                        default=ROOT.parent / "prediction/test_data.csv")
    parser.add_argument("--predictions", type=Path,
                        default=ROOT.parent / "prediction/data_prediction.csv")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "artifacts/prediction_benchmark.json")
    parser.add_argument("--distance-unit", choices=("m", "km"), default="m")
    args = parser.parse_args()
    if args.output.resolve() in {args.reference.resolve(), args.predictions.resolve()}:
        raise ValueError("Benchmark report must not overwrite either input CSV.")
    reference = pd.read_csv(args.reference, usecols=lambda name: name in (*FEATURES, "risk"))
    predictions = pd.read_csv(args.predictions,
                              usecols=lambda name: name in (*FEATURES, "risk", "class_model"))
    report = benchmark_frames(reference, predictions, distance_unit=args.distance_unit)
    report["provenance"] = {
        "reference_sha256": hashlib.sha256(args.reference.read_bytes()).hexdigest(),
        "predictions_sha256": hashlib.sha256(args.predictions.read_bytes()).hexdigest(),
        "evaluation_only": "Reference labels are read only after predictions are frozen.",
    }
    deployed = ROOT.parent / "prediction/artifacts/collision_risk_model.ubj"
    if deployed.is_file():
        report["provenance"]["deployed_model_sha256"] = hashlib.sha256(deployed.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(f"Tier agreement: {report['tier_accuracy']:.2%} "
          f"({report['tier_correct_rows']:,}/{report['rows']:,} rows)")
    print(f"Distance-only baseline: {report['baselines']['distance_only']['accuracy']:.2%}")
    print(f"Within one log10 unit: {report['regression']['within_one_log10_unit_rate']:.2%}")
    print(f"Probability-only critical recall: {report['probability_only']['risk_ge_-4']['recall']:.2%}")
    print(f"Saved evaluation-only report to {args.output}")


if __name__ == "__main__":
    main()
