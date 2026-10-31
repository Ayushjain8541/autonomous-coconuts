# Satellite collision risk evaluator

Open [collision_risk_development.ipynb](collision_risk_development.ipynb) for the
development workflow, data checks, model evaluation, boundary examples, and
dashboard exports. It uses the same functions as the complete command-line
script, [collision_risk.py](collision_risk.py).

## Run the notebook

Use Python 3.10 or newer. The supplied CSVs should remain in this directory.
On macOS, install XGBoost's native OpenMP dependency with `brew install libomp`.
This workspace already includes a checksum-verified project-local runtime under
`.venv/runtime/lib`; the headless runner detects it automatically. To use that
runtime when launching JupyterLab or running the script/tests directly, prefix
the relevant command with `DYLD_LIBRARY_PATH="$PWD/.venv/runtime/lib"`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m jupyterlab collision_risk_development.ipynb
```

Launch immediately in this workspace with:

```bash
DYLD_LIBRARY_PATH="$PWD/.venv/runtime/lib" .venv/bin/python -m jupyterlab collision_risk_development.ipynb
```

Select the `.venv` interpreter in your notebook editor, or launch Jupyter with the
command above. Run all cells in order. The notebook runs the behavioral tests
before training and verifies the saved model and CSV exports at the end.
`requirements-dev.lock.txt` records the exact Python packages used for the
development run; use it instead of `requirements-dev.txt` to reproduce versions.

For a headless notebook run:

```bash
.venv/bin/python execute_notebook.py
```

## Run the script or tests

```bash
.venv/bin/python collision_risk.py --train train_data.csv --test test_data.csv
.venv/bin/python -m pytest -q
```

Training uses CPU histogram boosting, bounded threading, and early stopping.
Use `--max-estimators` and `--n-jobs` to adjust the training budget.

## Data and evaluation contract

- The target is the existing `risk = log10(Pc)` value on each telemetry row.
- The model uses exactly the 12 source features specified in the prompt.
  `c_object_type` is one-hot encoded using training categories; numeric NaNs are
  handled natively by XGBoost. Unknown object types are supported.
- The test loader explicitly drops `risk`, `max_risk_estimate`, and
  `max_risk_scaling`, including when those fields contain values. Inference also
  rejects any frame still containing them. Test labels are never scored or used
  for model selection.
- Fit, early-stopping validation, and untouched assessment use disjoint events
  (approximately 64%, 16%, and 20% of events). Repeated CDMs cannot cross splits.
  Final fitting uses all training rows and the selected boosting-round count.
- Train and test event ID numbering overlaps. IDs are retained as requested,
  without joining the files. No absolute dates are available for a calendar
  backtest, and arbitrary identifiers may limit generalization.

The supplied files match [ESA's dataset documentation](https://kelvins.esa.int/collision-avoidance-challenge/data/):
`miss_distance` is in **metres**. The default classifier converts to kilometres.
Use `--distance-unit km` only for replacement files already in kilometres.

The original ESA task predicts final-event risk from earlier messages. This
implementation follows the requested **row-level target**. The optional event
summary selects the latest available message; it does not change the target
into a forecast of the final risk.

## Tier policy

Rules are evaluated in priority order. Critical takes precedence over Elevated.
These are the prompt's thresholds; the complete policy is not presented as a
universal NASA/ESA standard.

| Tier | Rule, using distance in km |
| --- | --- |
| Critical (Maneuver Required) | `predicted_risk >= -4` OR `distance < 1` |
| Elevated risk | `-6 <= predicted_risk < -4` OR `1 <= distance <= 5` |
| Safe | `predicted_risk < -6` AND `distance > 5` |

Comparisons stay in log space for numerical stability. Predictions are capped at
zero, since `Pc <= 1`. Missing/nonfinite classification inputs and negative
distances raise errors. The probability for display is `10 ** predicted_risk`;
log-space regression alone does not guarantee probability calibration.

## Generated files

The notebook and script write to `artifacts/`, which is ignored by Git:

| File | Contents |
| --- | --- |
| `dashboard_predictions.csv` | Every input test row, preserving input order |
| `dashboard_latest_events.csv` | Latest available row per event, selected by minimum `time_to_tca` |
| `collision_risk_model.ubj` | Final XGBoost model |
| `feature_encoder.json` | Training-fitted encoding vocabulary and schema |
| `evaluation.json` | Configuration, units, grouped holdout metrics, tier diagnostics |

Both dashboard CSVs contain exactly `event_id`, `predicted_risk`, and `risk_tier`.
`predicted_risk` is **log10(Pc)**. The all-row CSV contains repeated event IDs
because events have multiple messages; use the latest-event CSV for one card per
event in a dashboard.

Evaluation includes a constant baseline, RMSE/MAE/R², a tier confusion matrix, and
probability-only precision/recall at `1e-6` and `1e-4`. Distance overrides can
produce correct Critical tiers despite poor probability estimates, so inspect
the probability-only diagnostics. Test targets remain unused.

For inference with saved artifacts:

```python
from xgboost import XGBRegressor
from collision_risk import FeatureEncoder, load_test_data, dashboard_predictions

model = XGBRegressor()
model.load_model("artifacts/collision_risk_model.ubj")
encoder = FeatureEncoder.load("artifacts/feature_encoder.json")
telemetry = load_test_data("test_data.csv")
dashboard = dashboard_predictions(model, encoder, telemetry, distance_unit="m")
```

See [XGBoost's official guide](https://xgboost.readthedocs.io/en/stable/python/sklearn_estimator.html)
for the histogram algorithm, early-stopping interface, and threading behavior.
