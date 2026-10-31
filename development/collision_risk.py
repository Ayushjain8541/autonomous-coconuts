"""Leakage-controlled, row-level conjunction risk regression and dashboard export.

Run ``python collision_risk.py --help`` for the complete training workflow.
The companion notebook explains and exercises each stage interactively.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent
# Load the existing workspace runtime before importing either ML framework.
if sys.platform == "darwin":
    import ctypes
    for base in (ROOT, ROOT.parent):
        runtime = base / ".venv/runtime/lib/libomp.dylib"
        if runtime.is_file():
            ctypes.CDLL(str(runtime), mode=ctypes.RTLD_GLOBAL)
            break

import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_fscore_support,
    r2_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor


FEATURES = (
    "event_id", "time_to_tca", "miss_distance", "relative_speed",
    "relative_position_r", "relative_position_t", "relative_position_n",
    "c_object_type", "c_sigma_r", "t_sigma_r", "F10", "AP",
)
TARGET = "risk"  # log10(Pc); never apply log10 a second time.
FORBIDDEN_TEST_COLUMNS = ("risk", "max_risk_estimate", "max_risk_scaling")
NUMERIC_FEATURES = tuple(name for name in FEATURES if name != "c_object_type")
SAFE = "Safe"
ELEVATED = "Elevated risk"
CRITICAL = "Critical (Maneuver Required)"
TIERS = (SAFE, ELEVATED, CRITICAL)


@dataclass(frozen=True)
class TrainingConfig:
    random_state: int = 42
    holdout_fraction: float = 0.20
    # Of the remaining 80% of events, 20% are used for early stopping.
    validation_fraction: float = 0.20
    max_estimators: int = 1600
    early_stopping_rounds: int = 80
    learning_rate: float = 0.04
    max_depth: int = 7
    n_jobs: int = min(8, os.cpu_count() or 1)
    distance_unit: str = "m"

    def __post_init__(self) -> None:
        if not 0 < self.holdout_fraction < 1:
            raise ValueError("holdout_fraction must be between 0 and 1.")
        if not 0 < self.validation_fraction < 1:
            raise ValueError("validation_fraction must be between 0 and 1.")
        if self.max_estimators < 1 or self.early_stopping_rounds < 1:
            raise ValueError("Boosting rounds and patience must be positive.")
        if self.distance_unit not in ("m", "km"):
            raise ValueError("distance_unit must be 'm' or 'km'.")


def require_columns(frame: pd.DataFrame, columns: tuple[str, ...]) -> None:
    missing = sorted(set(columns).difference(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def load_train_data(path: str | Path) -> pd.DataFrame:
    """Read only approved inputs and the training target; retain all CDM rows."""
    frame = pd.read_csv(path, usecols=lambda name: name in (*FEATURES, TARGET))
    require_columns(frame, (*FEATURES, TARGET))
    return frame.loc[:, [*FEATURES, TARGET]].copy()


def load_test_data(path: str | Path) -> pd.DataFrame:
    """Explicitly remove every forbidden field before returning test inputs.

    Reading only relevant columns reduces memory use for the 103-column CSVs.
    Forbidden columns are read solely so their removal is explicit. Their values
    are never inspected, evaluated, used for fitting, or passed to a predictor.
    ``errors='ignore'`` also permits a genuinely unlabelled future CSV.
    """
    test_data = pd.read_csv(
        path, usecols=lambda name: name in (*FEATURES, *FORBIDDEN_TEST_COLUMNS)
    )
    test_data = test_data.drop(columns=list(FORBIDDEN_TEST_COLUMNS), errors="ignore")
    require_columns(test_data, FEATURES)
    if set(FORBIDDEN_TEST_COLUMNS).intersection(test_data.columns):
        raise ValueError("Forbidden test columns survived sanitization.")
    return test_data.loc[:, list(FEATURES)].copy()


def _numeric_features(frame: pd.DataFrame) -> pd.DataFrame:
    require_columns(frame, FEATURES)
    numeric = frame.loc[:, list(NUMERIC_FEATURES)].apply(pd.to_numeric, errors="raise")
    # XGBoost learns missing-value branches; no imputation fit on test data.
    numeric = numeric.replace([np.inf, -np.inf], np.nan)
    if numeric["event_id"].isna().any():
        raise ValueError("event_id must be a finite, nonmissing numeric identifier.")
    return numeric.astype(np.float32)


def _object_types(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[["c_object_type"]].fillna("__MISSING__").astype(str)


class FeatureEncoder:
    """One-hot encode object type using categories learned from training only.

    Numeric missing values remain NaN for XGBoost's native handling. Novel object
    types are encoded as all zeroes. No extra source telemetry is introduced.
    """

    def fit(self, frame: pd.DataFrame) -> FeatureEncoder:
        _numeric_features(frame)
        self.one_hot_ = OneHotEncoder(
            handle_unknown="ignore", sparse_output=False, dtype=np.float32
        ).fit(_object_types(frame))
        self.output_columns_ = [
            *NUMERIC_FEATURES,
            *self.one_hot_.get_feature_names_out(["c_object_type"]).tolist(),
        ]
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        if not hasattr(self, "one_hot_"):
            raise ValueError("Fit FeatureEncoder before calling transform.")
        numeric = _numeric_features(frame)
        categorical = self.one_hot_.transform(_object_types(frame))
        values = np.concatenate([numeric.to_numpy(), categorical], axis=1)
        return pd.DataFrame(values, index=frame.index, columns=self.output_columns_)

    def fit_transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        return self.fit(frame).transform(frame)

    def save(self, path: str | Path, *, distance_unit: str = "m") -> None:
        """Save portable, inspectable encoding metadata instead of a pickle."""
        Path(path).write_text(json.dumps({
            "features": list(FEATURES),
            "object_type_categories": self.one_hot_.categories_[0].tolist(),
            "output_columns": self.output_columns_,
            "distance_unit": distance_unit,
        }, indent=2) + "\n")

    @classmethod
    def load(cls, path: str | Path) -> FeatureEncoder:
        metadata = json.loads(Path(path).read_text())
        if metadata["features"] != list(FEATURES):
            raise ValueError("Saved feature schema does not match this implementation.")
        instance = cls()
        instance.one_hot_ = OneHotEncoder(
            categories=[metadata["object_type_categories"]],
            handle_unknown="ignore", sparse_output=False, dtype=np.float32,
        ).fit(pd.DataFrame({"c_object_type": metadata["object_type_categories"]}))
        instance.output_columns_ = metadata["output_columns"]
        return instance


def classify_risk(
    predicted_risk: Any, miss_distance: Any, *, distance_unit: str = "m"
) -> str | np.ndarray:
    """Apply the requested policy, with Critical taking highest precedence.

    ``predicted_risk`` is log10(Pc). Comparing it directly to -6 and -4 is
    mathematically equivalent to probability comparisons and avoids underflow.
    Distances 1.0 and 5.0 km are included in Elevated risk. Scalars or broadcast-
    compatible arrays are accepted. Invalid telemetry fails explicitly.
    """
    if distance_unit not in ("m", "km"):
        raise ValueError("distance_unit must be 'm' or 'km'.")
    risk, distance = np.broadcast_arrays(
        np.asarray(predicted_risk, dtype=np.float64),
        np.asarray(miss_distance, dtype=np.float64),
    )
    if not np.isfinite(risk).all() or not np.isfinite(distance).all():
        raise ValueError("Risk and miss_distance must contain only finite values.")
    if (distance < 0).any():
        raise ValueError("miss_distance must be nonnegative.")
    distance_km = distance / 1000.0 if distance_unit == "m" else distance
    critical = (risk >= -4.0) | (distance_km < 1.0)
    elevated = ((risk >= -6.0) & (risk < -4.0)) | (
        (distance_km >= 1.0) & (distance_km <= 5.0)
    )
    safe = (risk < -6.0) & (distance_km > 5.0)
    result = np.select([critical, elevated, safe], list((CRITICAL, ELEVATED, SAFE)),
                       default="Unclassified")
    if np.any(result == "Unclassified"):
        raise ValueError("Inputs do not satisfy any risk tier.")
    return str(result.item()) if result.ndim == 0 else result


def split_events(
    train_data: pd.DataFrame, config: TrainingConfig
) -> dict[str, np.ndarray]:
    """Create fit / early-stopping / untouched assessment partitions by event."""
    require_columns(train_data, (*FEATURES, TARGET))
    groups = train_data["event_id"]
    if groups.isna().any() or groups.nunique() < 5:
        raise ValueError("Need at least five nonmissing events for three partitions.")
    outer = GroupShuffleSplit(
        n_splits=1, test_size=config.holdout_fraction, random_state=config.random_state
    )
    development, holdout = next(outer.split(train_data, groups=groups))
    inner = GroupShuffleSplit(
        n_splits=1, test_size=config.validation_fraction,
        random_state=config.random_state + 1,
    )
    fit_relative, validation_relative = next(
        inner.split(train_data.iloc[development], groups=groups.iloc[development])
    )
    partitions = {
        "fit": development[fit_relative],
        "validation": development[validation_relative],
        "holdout": holdout,
    }
    event_sets = [set(groups.iloc[index]) for index in partitions.values()]
    for index, first in enumerate(event_sets):
        for second in event_sets[index + 1:]:
            if not first.isdisjoint(second):
                raise RuntimeError("An event crossed validation partitions.")
    return partitions


def _target(train_data: pd.DataFrame) -> pd.Series:
    y = pd.to_numeric(train_data[TARGET], errors="raise").astype(np.float64)
    if not np.isfinite(y).all() or (y > 0).any():
        raise ValueError("Training risk must be finite log10(Pc) values <= 0.")
    return y


def _new_model(config: TrainingConfig, rounds: int, *, early_stop: bool) -> XGBRegressor:
    return XGBRegressor(
        objective="reg:squarederror", eval_metric="rmse", tree_method="hist",
        n_estimators=rounds, learning_rate=config.learning_rate,
        max_depth=config.max_depth, min_child_weight=8,
        subsample=0.85, colsample_bytree=0.9, reg_alpha=0.05, reg_lambda=8.0,
        max_bin=256, random_state=config.random_state, n_jobs=config.n_jobs,
        early_stopping_rounds=config.early_stopping_rounds if early_stop else None,
    )


def regression_metrics(y_true: Any, y_pred: Any) -> dict[str, float]:
    return {
        "rmse_log10_pc": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae_log10_pc": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def evaluate_model(train_data: pd.DataFrame, config: TrainingConfig) -> dict[str, Any]:
    """Choose boosting rounds without accessing holdout or test labels."""
    y = _target(train_data)
    partitions = split_events(train_data, config)
    fit_idx, val_idx, holdout_idx = (partitions[key] for key in
                                    ("fit", "validation", "holdout"))
    encoder = FeatureEncoder()
    x_fit = encoder.fit_transform(train_data.iloc[fit_idx])
    x_val = encoder.transform(train_data.iloc[val_idx])
    model = _new_model(config, config.max_estimators, early_stop=True)
    model.fit(x_fit, y.iloc[fit_idx], eval_set=[(x_val, y.iloc[val_idx])], verbose=False)
    best_rounds = int(model.best_iteration + 1)
    holdout = train_data.iloc[holdout_idx]
    prediction = np.minimum(model.predict(encoder.transform(holdout)).astype(float), 0.0)
    actual = y.iloc[holdout_idx].to_numpy()
    baseline = np.full(len(holdout), y.iloc[fit_idx].mean())
    predicted_tiers = classify_risk(prediction, holdout["miss_distance"],
                                    distance_unit=config.distance_unit)
    actual_tiers = classify_risk(actual, holdout["miss_distance"],
                                 distance_unit=config.distance_unit)
    metrics: dict[str, Any] = {
        "selected_boosting_rounds": best_rounds,
        "holdout_xgboost": regression_metrics(actual, prediction),
        "holdout_mean_baseline": regression_metrics(actual, baseline),
        "partitions": {
            name: {"rows": len(idx), "events": int(train_data.iloc[idx]["event_id"].nunique())}
            for name, idx in partitions.items()
        },
        "tier_report": classification_report(
            actual_tiers, predicted_tiers, labels=list(TIERS), output_dict=True,
            zero_division=0,
        ),
        "tier_confusion_matrix": confusion_matrix(
            actual_tiers, predicted_tiers, labels=list(TIERS)
        ).tolist(),
    }
    # Distance-driven Critical classifications can conceal poor Pc recall.
    # Report probability-only performance independently of distance overrides.
    for threshold in (-6.0, -4.0):
        truth, predicted = actual >= threshold, prediction >= threshold
        precision, recall, f1, _ = precision_recall_fscore_support(
            truth, predicted, average="binary", zero_division=0
        )
        metrics[f"probability_only_risk_ge_{threshold:g}"] = {
            "precision": float(precision), "recall": float(recall), "f1": float(f1),
            "actual_positive_rows": int(truth.sum()),
            "predicted_positive_rows": int(predicted.sum()),
        }
    early_mask = holdout["time_to_tca"].to_numpy() > 2.0
    if early_mask.sum() >= 2:
        metrics["holdout_time_to_tca_gt_2_days"] = {
            "rows": int(early_mask.sum()),
            **regression_metrics(actual[early_mask], prediction[early_mask]),
        }
    return {
        "model": model, "encoder": encoder, "partitions": partitions,
        "metrics": metrics, "holdout_actual": actual,
        "holdout_prediction": prediction,
    }


def fit_final_model(
    train_data: pd.DataFrame, config: TrainingConfig, best_rounds: int
) -> tuple[XGBRegressor, FeatureEncoder]:
    """Refit on all labelled training rows at the selected boosting budget."""
    encoder = FeatureEncoder()
    model = _new_model(config, best_rounds, early_stop=False)
    model.fit(encoder.fit_transform(train_data), _target(train_data), verbose=False)
    return model, encoder


def dashboard_predictions(
    model: Any, encoder: FeatureEncoder, test_data: pd.DataFrame, *,
    distance_unit: str = "m",
) -> pd.DataFrame:
    """Predict sanitized rows only, preserving input row order and event IDs."""
    if set(FORBIDDEN_TEST_COLUMNS).intersection(test_data.columns):
        raise ValueError("Drop forbidden test columns before generating predictions.")
    require_columns(test_data, FEATURES)
    # Reject unusable operational distances before invoking the model.
    classify_risk(np.full(len(test_data), -7.0), test_data["miss_distance"],
                  distance_unit=distance_unit)
    prediction = np.asarray(model.predict(encoder.transform(test_data)), dtype=float)
    if prediction.shape != (len(test_data),) or not np.isfinite(prediction).all():
        raise ValueError("Model must return one finite risk prediction per input row.")
    # Squared-error regressors are unconstrained; Pc must not exceed one.
    prediction = np.minimum(prediction, 0.0)
    return pd.DataFrame({
        "event_id": test_data["event_id"].to_numpy(),
        "predicted_risk": prediction,
        "risk_tier": classify_risk(prediction, test_data["miss_distance"],
                                    distance_unit=distance_unit),
    })


def latest_event_predictions(
    dashboard: pd.DataFrame, test_data: pd.DataFrame
) -> pd.DataFrame:
    """Optional event summary: use the latest available CDM (smallest time_to_tca).

    Equal timestamps use the first input row. No future CDM or maximum risk is
    used, and each selected tier comes from the same row as its predicted risk.
    """
    if len(dashboard) != len(test_data):
        raise ValueError("Dashboard and telemetry must contain the same rows.")
    metadata = test_data[["event_id", "time_to_tca"]].reset_index(drop=True)
    if not np.array_equal(dashboard["event_id"].to_numpy(), metadata["event_id"].to_numpy()):
        raise ValueError("Dashboard and telemetry event order must match.")
    time = pd.to_numeric(metadata["time_to_tca"], errors="raise")
    if not np.isfinite(time).all():
        raise ValueError("Latest-event selection requires finite time_to_tca.")
    metadata["time_to_tca"] = time
    selected = metadata.groupby("event_id", sort=False)["time_to_tca"].idxmin()
    return dashboard.iloc[selected.to_numpy()].reset_index(drop=True)


def save_artifacts(
    output_dir: str | Path, model: XGBRegressor, encoder: FeatureEncoder,
    dashboard: pd.DataFrame, latest: pd.DataFrame, metrics: dict[str, Any],
    config: TrainingConfig,
) -> None:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    dashboard.to_csv(directory / "dashboard_predictions.csv", index=False)
    latest.to_csv(directory / "dashboard_latest_events.csv", index=False)
    model.save_model(directory / "collision_risk_model.ubj")
    encoder.save(directory / "feature_encoder.json", distance_unit=config.distance_unit)
    report = {
        "target": "risk = log10(Pc), per telemetry row",
        "distance_unit": config.distance_unit,
        "source_features": list(FEATURES), "config": asdict(config), **metrics,
    }
    (directory / "evaluation.json").write_text(json.dumps(report, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=ROOT / "train_data.csv")
    parser.add_argument("--test", type=Path, default=ROOT.parent / "prediction/test_data.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts")
    parser.add_argument("--distance-unit", choices=("m", "km"), default="m")
    parser.add_argument("--max-estimators", type=int, default=1600)
    parser.add_argument("--n-jobs", type=int, default=min(8, os.cpu_count() or 1))
    args = parser.parse_args()
    config = TrainingConfig(distance_unit=args.distance_unit,
                            max_estimators=args.max_estimators, n_jobs=args.n_jobs)
    train_data = load_train_data(args.train)
    test_data = load_test_data(args.test)  # Forbidden columns removed here.
    print(f"Loaded {len(train_data):,} training and {len(test_data):,} sanitized test rows.")
    evaluation = evaluate_model(train_data, config)
    rounds = evaluation["metrics"]["selected_boosting_rounds"]
    print(f"Selected {rounds} boosting rounds. Refitting on all training rows.")
    model, encoder = fit_final_model(train_data, config, rounds)
    dashboard = dashboard_predictions(model, encoder, test_data,
                                      distance_unit=config.distance_unit)
    latest = latest_event_predictions(dashboard, test_data)
    save_artifacts(args.output_dir, model, encoder, dashboard, latest,
                   evaluation["metrics"], config)
    print(json.dumps(evaluation["metrics"]["holdout_xgboost"], indent=2))
    print(f"Saved {len(dashboard):,} telemetry predictions and {len(latest):,} event summaries to {args.output_dir}.")


if __name__ == "__main__":
    main()
