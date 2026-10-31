"""Leakage-controlled, row-level conjunction risk regression and dashboard export.

Run ``python collision_risk.py --help`` for the complete training workflow.
The companion notebook explains and exercises each stage interactively.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
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
    class_balance_power: float = 1.0
    elevated_weight: float = 20.0
    critical_weight: float = 320.0

    def __post_init__(self) -> None:
        if not 0 < self.holdout_fraction < 1:
            raise ValueError("holdout_fraction must be between 0 and 1.")
        if not 0 < self.validation_fraction < 1:
            raise ValueError("validation_fraction must be between 0 and 1.")
        if self.max_estimators < 1 or self.early_stopping_rounds < 1:
            raise ValueError("Boosting rounds and patience must be positive.")
        if self.distance_unit not in ("m", "km"):
            raise ValueError("distance_unit must be 'm' or 'km'.")
        if not np.isfinite(self.class_balance_power) or not 0 <= self.class_balance_power <= 1:
            raise ValueError("class_balance_power must be between zero and one.")
        if any(not np.isfinite(w) or w < 1 for w in
               (self.elevated_weight, self.critical_weight)):
            raise ValueError("Class cost multipliers must be finite and at least one.")


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


def probability_bands(risk: Any) -> np.ndarray:
    """0=Safe, 1=Elevated, 2=Critical, without distance overrides."""
    values = np.asarray(risk, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("Risk bands require a nonempty finite one-dimensional array.")
    return np.digitize(values, [-6.0, -4.0])


def class_sample_weights(y_fit: Any, config: TrainingConfig) -> tuple[np.ndarray, np.ndarray]:
    """Learn frequency-adaptive costs from fitting labels only, normalized to mean 1.

    Per-band cost = (n / (k * count))**power * multiplier. Critical errors
    therefore contribute much more to squared loss, including false negatives.
    Missing bands receive no rows/weight; constant-target refits remain valid.
    Never call this on validation, holdout, or uploaded/test labels.
    """
    bands = probability_bands(y_fit)
    counts = np.bincount(bands, minlength=3)
    present = counts > 0
    costs = np.zeros(3, dtype=float)
    costs[present] = (len(bands) / (present.sum() * counts[present])) ** config.class_balance_power
    costs *= [1.0, config.elevated_weight, config.critical_weight]
    costs /= np.average(costs, weights=counts)
    return costs[bands], costs


def balanced_band_error(y_true: Any, y_pred: Any) -> float:
    """Minimize worst-band error, with macro recall providing a small secondary term.

    This validation cost is used for early stopping, never for gradients.
    A one-class prediction has zero worst recall when all three bands exist.
    """
    actual, predicted = probability_bands(y_true), probability_bands(y_pred)
    counts = np.bincount(actual, minlength=3)
    correct = np.bincount(actual[actual == predicted], minlength=3)
    recall = correct[counts > 0] / counts[counts > 0]
    return float(1.0 - (recall.min() + 0.05 * recall.mean()) / 1.05)


def probability_band_metrics(actual: Any, prediction: Any) -> dict[str, Any]:
    truth, predicted = probability_bands(actual), probability_bands(prediction)
    report = classification_report(truth, predicted, labels=[0, 1, 2],
                                   target_names=list(TIERS), output_dict=True, zero_division=0)
    recalls = [report[tier]["recall"] for tier in TIERS]
    return {
        "report": report, "confusion_matrix": confusion_matrix(truth, predicted, labels=[0, 1, 2]).tolist(),
        "macro_recall": float(np.mean(recalls)), "worst_recall": float(min(recalls)),
        "recall_gap": float(max(recalls) - min(recalls)),
        "balanced_band_error": balanced_band_error(actual, prediction),
    }


def _is_unweighted(config: TrainingConfig) -> bool:
    return (config.class_balance_power, config.elevated_weight, config.critical_weight) == (0, 1, 1)


def _new_model(config: TrainingConfig, rounds: int, *, early_stop: bool) -> XGBRegressor:
    return XGBRegressor(
        objective="reg:squarederror",
        eval_metric="rmse" if _is_unweighted(config) else balanced_band_error,
        tree_method="hist",
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


def select_weighted_model(
    x_fit: pd.DataFrame, y_fit: Any, x_validation: pd.DataFrame, y_validation: Any,
    config: TrainingConfig, *, tune_weights: bool = True,
) -> dict[str, Any]:
    """Fit and select costs using fit/validation ONLY; no holdout/test argument.

    Search a bounded 3x3 grid, plus the original unweighted RMSE baseline.
    Maximize the worst probability-band recall, with a 5% macro-recall tie-break,
    subject to validation RMSE beating a fit-mean constant. Thus neither an
    all-Critical model nor arbitrarily poor numeric predictions win the search.
    """
    y_fit, y_validation = np.asarray(y_fit), np.asarray(y_validation)
    if tune_weights and any(len(np.unique(probability_bands(y))) != 3
                            for y in (y_fit, y_validation)):
        raise ValueError("Weight search needs all three probability bands in fit and validation; "
                         "use more events or explicitly select fixed weights.")
    baseline_config = replace(config, class_balance_power=0, elevated_weight=1, critical_weight=1)
    candidates = [baseline_config, config]
    if tune_weights:
        candidates += [replace(config, class_balance_power=1, elevated_weight=e, critical_weight=e*r)
                       for e in (5, 20, 80) for r in (1, 4, 16)]
    candidates = list(dict.fromkeys(candidates))
    constant_rmse = regression_metrics(y_validation, np.full(len(y_validation), y_fit.mean()))["rmse_log10_pc"]
    trials = []
    selected = None
    baseline_model = None
    for candidate in candidates:
        model = _new_model(candidate, config.max_estimators, early_stop=True)
        sample_weight, class_costs = class_sample_weights(y_fit, candidate)
        model.fit(x_fit, y_fit, sample_weight=sample_weight,
                  eval_set=[(x_validation, y_validation)], verbose=False)
        prediction = np.minimum(model.predict(x_validation).astype(float), 0.0)
        bands = probability_band_metrics(y_validation, prediction)
        rmse = regression_metrics(y_validation, prediction)["rmse_log10_pc"]
        eligible = rmse < constant_rmse
        trial = {
            "class_balance_power": candidate.class_balance_power,
            "elevated_weight": candidate.elevated_weight, "critical_weight": candidate.critical_weight,
            "fit_class_counts": np.bincount(probability_bands(y_fit), minlength=3).tolist(),
            "fit_class_costs": class_costs.tolist(), "rounds": int(model.best_iteration + 1),
            "validation_probability_bands": bands, "validation_rmse_log10_pc": rmse,
            "eligible": bool(eligible),
        }
        trials.append(trial)
        if _is_unweighted(candidate):
            baseline_model = model
        # In fixed mode the requested costs are used, and the guard is still reported.
        if not tune_weights:
            if candidate == config:
                selected = (model, candidate, trial)
        elif eligible and (selected is None or
                           bands["balanced_band_error"] < selected[2]["validation_probability_bands"]["balanced_band_error"]):
            selected = (model, candidate, trial)
    if selected is None:
        raise ValueError("No candidate beat the fit-mean validation RMSE baseline; no model selected.")
    return {
        "model": selected[0], "config": selected[1], "baseline_model": baseline_model,
        "selection": {
            "protocol": "fit/validation event partitions only; probability bands ignore distance",
            "criterion": "minimize 1 - (worst recall + 0.05 * macro recall) / 1.05",
            "rmse_guard_constant_mean": constant_rmse, "tuned": tune_weights,
            "selected": selected[2], "trials": trials,
        },
    }


def evaluate_model(
    train_data: pd.DataFrame, config: TrainingConfig, *, tune_weights: bool = True,
) -> dict[str, Any]:
    """Select costs/rounds on validation, then assess once on held-out events."""
    y = _target(train_data)
    partitions = split_events(train_data, config)
    fit_idx, val_idx, holdout_idx = (partitions[key] for key in
                                    ("fit", "validation", "holdout"))
    encoder = FeatureEncoder()
    x_fit = encoder.fit_transform(train_data.iloc[fit_idx])
    x_val = encoder.transform(train_data.iloc[val_idx])
    selection = select_weighted_model(x_fit, y.iloc[fit_idx], x_val, y.iloc[val_idx],
                                      config, tune_weights=tune_weights)
    model, selected_config = selection["model"], selection["config"]
    best_rounds = int(model.best_iteration + 1)
    holdout = train_data.iloc[holdout_idx]
    prediction = np.minimum(model.predict(encoder.transform(holdout)).astype(float), 0.0)
    actual = y.iloc[holdout_idx].to_numpy()
    baseline = np.full(len(holdout), y.iloc[fit_idx].mean())
    baseline_prediction = np.minimum(selection["baseline_model"].predict(encoder.transform(holdout)).astype(float), 0.0)
    predicted_tiers = classify_risk(prediction, holdout["miss_distance"],
                                    distance_unit=config.distance_unit)
    actual_tiers = classify_risk(actual, holdout["miss_distance"],
                                 distance_unit=config.distance_unit)
    metrics: dict[str, Any] = {
        "selected_boosting_rounds": best_rounds,
        "holdout_xgboost": regression_metrics(actual, prediction),
        "holdout_mean_baseline": regression_metrics(actual, baseline),
        "weight_selection": selection["selection"],
        "selected_config": asdict(selected_config),
        "holdout_probability_bands": probability_band_metrics(actual, prediction),
        "holdout_unweighted_xgboost": {
            **regression_metrics(actual, baseline_prediction),
            "probability_bands": probability_band_metrics(actual, baseline_prediction),
        },
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
        "selected_config": selected_config,
    }


def fit_final_model(
    train_data: pd.DataFrame, config: TrainingConfig, best_rounds: int
) -> tuple[XGBRegressor, FeatureEncoder]:
    """Refit on all labelled training rows at the selected boosting budget."""
    encoder = FeatureEncoder()
    model = _new_model(config, best_rounds, early_stop=False)
    y = _target(train_data)
    weights, _ = class_sample_weights(y, config)  # Recompute on the final fitting data.
    model.fit(encoder.fit_transform(train_data), y, sample_weight=weights, verbose=False)
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
    parser.add_argument("--unweighted", action="store_true", help="Reproduce the original RMSE-only baseline.")
    args = parser.parse_args()
    config = TrainingConfig(distance_unit=args.distance_unit,
                            max_estimators=args.max_estimators, n_jobs=args.n_jobs)
    if args.unweighted:
        config = replace(config, class_balance_power=0, elevated_weight=1, critical_weight=1)
    train_data = load_train_data(args.train)
    test_data = load_test_data(args.test)  # Forbidden columns removed here.
    print(f"Loaded {len(train_data):,} training and {len(test_data):,} sanitized test rows.")
    evaluation = evaluate_model(train_data, config, tune_weights=not args.unweighted)
    config = evaluation["selected_config"]
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
