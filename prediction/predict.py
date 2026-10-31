"""Use the saved model to predict CSV risk values and write data_prediction.csv."""

import argparse
import io
import json
import os
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "data_prediction.csv"
FEATURES = (
    "event_id", "time_to_tca", "miss_distance", "relative_speed",
    "relative_position_r", "relative_position_t", "relative_position_n",
    "c_object_type", "c_sigma_r", "t_sigma_r", "F10", "AP",
)
FORBIDDEN_COLUMNS = ("risk", "max_risk_estimate", "max_risk_scaling")


def classify_risk(predicted_risk, miss_distance, *, distance_unit="m"):
    """Classify log10(Pc), with Critical overriding overlapping Elevated rules."""
    if distance_unit not in ("m", "km"):
        raise ValueError("distance_unit must be 'm' or 'km'.")
    risk, distance = np.broadcast_arrays(
        np.asarray(predicted_risk, dtype=float), np.asarray(miss_distance, dtype=float)
    )
    if not np.isfinite(risk).all() or not np.isfinite(distance).all():
        raise ValueError("Risk and miss_distance must contain finite values.")
    if (distance < 0).any():
        raise ValueError("miss_distance must be nonnegative.")
    distance_km = distance / 1000.0 if distance_unit == "m" else distance
    critical = (risk >= -4.0) | (distance_km < 1.0)
    elevated = ((risk >= -6.0) & (risk < -4.0)) | (
        (distance_km >= 1.0) & (distance_km <= 5.0)
    )
    result = np.select([critical, elevated], ["Critical", "Elevated risk"], default="Safe")
    return str(result.item()) if result.ndim == 0 else result


def _encode_features(test_data, metadata):
    """Reproduce the saved numeric/one-hot encoding without fitting anything."""
    if metadata["features"] != list(FEATURES):
        raise ValueError("Saved model metadata does not match the allowed feature schema.")
    missing = sorted(set(FEATURES).difference(test_data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    names = [name for name in FEATURES if name != "c_object_type"]
    numeric = test_data[names].apply(pd.to_numeric, errors="raise")
    numeric = numeric.replace([np.inf, -np.inf], np.nan).astype(np.float32)
    if numeric["event_id"].isna().any():
        raise ValueError("event_id must be a finite numeric identifier.")
    objects = test_data["c_object_type"].fillna("__MISSING__").astype(str)
    categories = metadata["object_type_categories"]
    columns = [*names, *(f"c_object_type_{category}" for category in categories)]
    if columns != metadata["output_columns"]:
        raise ValueError("Saved encoding column order is inconsistent.")
    # Unseen categories produce all-zero indicators, as during development.
    indicators = np.column_stack([
        objects.eq(category).to_numpy(dtype=np.float32) for category in categories
    ])
    values = np.concatenate([numeric.to_numpy(), indicators], axis=1)
    return pd.DataFrame(values, columns=columns, index=test_data.index)


def predict_dataframe(data, *, artifact_dir=None, distance_unit=None):
    """Score telemetry without fitting; return a new frame with risk/class columns.

    Risk columns are optional. Supplied target-derived values are discarded, and
    the caller's frame is never modified. Output retains all telemetry rows in
    their original order, including repeated event IDs.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("Telemetry must be a pandas DataFrame.")
    if data.empty:
        raise ValueError("CSV must contain at least one telemetry row.")
    if data.columns.duplicated().any():
        raise ValueError("Telemetry column names must be unique.")
    directory = Path(artifact_dir) if artifact_dir is not None else ROOT / "artifacts"
    metadata = json.loads((directory / "feature_encoder.json").read_text())
    unit = distance_unit if distance_unit is not None else metadata["distance_unit"]

    # Explicitly discard all target-derived fields BEFORE generating predictions.
    test_data = data.drop(columns=list(FORBIDDEN_COLUMNS), errors="ignore").copy()
    features = _encode_features(test_data, metadata)
    classify_risk(np.full(len(test_data), -7.0), test_data["miss_distance"],
                  distance_unit=unit)

    # Use this project's existing macOS runtime when a system install is absent.
    runtimes = [base / ".venv/runtime/lib/libomp.dylib" for base in (ROOT, ROOT.parent)]
    if sys.platform == "darwin":
        import ctypes
        for runtime in runtimes:
            if runtime.is_file():
                ctypes.CDLL(str(runtime), mode=ctypes.RTLD_GLOBAL)
                break
    from xgboost import Booster, DMatrix

    # Native XGBoost inference does not require training code or scikit-learn.
    model = Booster()
    model.load_model(directory / "collision_risk_model.ubj")
    threads = min(8, os.cpu_count() or 1)
    model.set_param({"nthread": threads})
    risk = model.predict(DMatrix(features, missing=np.nan, nthread=threads)).astype(float)
    if risk.shape != (len(test_data),) or not np.isfinite(risk).all():
        raise ValueError("Model must return one finite risk prediction per row.")
    test_data["risk"] = np.minimum(risk, 0.0)  # log10(Pc) <= 0, since Pc <= 1.
    test_data["class_model"] = classify_risk(
        test_data["risk"], test_data["miss_distance"], distance_unit=unit
    )
    return test_data


def predict_uploaded_csv(csv_content, *, artifact_dir=None, distance_unit=None):
    """Score CSV bytes, text, or an uploaded file stream entirely in memory.

    The backend can pass uploaded bytes or its readable upload stream directly.
    No upload filename is used as a server path, no shared output is overwritten,
    and the saved model is reused. HTTP transport and download responses belong
    to the consuming backend; this helper returns the scored DataFrame.
    """
    if isinstance(csv_content, (bytes, bytearray)):
        source = io.BytesIO(csv_content)
    elif isinstance(csv_content, str):
        source = io.StringIO(csv_content)
    elif hasattr(csv_content, "read"):
        source = csv_content
    else:
        raise TypeError("Upload must be CSV bytes, text, or a readable file stream.")
    try:
        data = pd.read_csv(source, encoding="utf-8")
    except pd.errors.EmptyDataError as error:
        raise ValueError("Uploaded CSV is empty or has no header.") from error
    except pd.errors.ParserError as error:
        raise ValueError("Uploaded CSV could not be parsed.") from error
    except UnicodeDecodeError as error:
        raise ValueError("Uploaded CSV must use UTF-8 encoding.") from error
    return predict_dataframe(data, artifact_dir=artifact_dir, distance_unit=distance_unit)


def create_prediction_csv(
    test_path=None, output_path=None, *, artifact_dir=None, distance_unit=None,
):
    """Score a local CSV and write telemetry + risk/class to a separate file."""
    source = Path(test_path) if test_path is not None else (
        ROOT / "test.csv" if (ROOT / "test.csv").is_file() else ROOT / "test_data.csv"
    )
    destination = Path(output_path) if output_path is not None else DEFAULT_OUTPUT
    if source.resolve() == destination.resolve():
        raise ValueError("Prediction output must differ from the input CSV.")
    test_data = predict_dataframe(
        pd.read_csv(source), artifact_dir=artifact_dir, distance_unit=distance_unit
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    test_data.to_csv(destination, index=False)
    return test_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--artifacts", type=Path, default=ROOT / "artifacts")
    parser.add_argument("--distance-unit", choices=("m", "km"), default=None)
    args = parser.parse_args()
    result = create_prediction_csv(
        args.input, args.output, artifact_dir=args.artifacts,
        distance_unit=args.distance_unit,
    )
    print(f"Saved {len(result):,} predictions to {args.output}")
    print(result["class_model"].value_counts().to_string())


if __name__ == "__main__":
    main()
