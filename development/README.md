# Model development and training

Raw input CSVs are local files excluded from Git. Supply `development/train_data.csv`
and `prediction/test_data.csv` at those paths before running their workflows.

This folder contains the recovered training data, development notebook, reusable
training code, and behavioral tests. The prediction workflow is in `../prediction/`.

From the repository root, install the separate development environment:

```bash
python3 -m venv development/.venv
development/.venv/bin/python -m pip install -r development/requirements-dev.lock.txt
```

The lock file reproduces the recovered development dependencies. Alternatively,
install `development/requirements-dev.txt` for the declared compatible ranges.

Open JupyterLab or execute the entire notebook:

```bash
development/.venv/bin/python development/execute_notebook.py --lab
development/.venv/bin/python development/execute_notebook.py
```

Train directly, or run the tests:

```bash
development/.venv/bin/python development/collision_risk.py
development/.venv/bin/python -m pytest -q development/tests
```

Defaults use this folder's `train_data.csv`, `../prediction/test_data.csv`, and
this folder's `artifacts/` output directory. There is one shared copy of the test
CSV. All three forbidden test fields are dropped before prediction.

The model predicts per-row `risk = log10(Pc)` using exactly the requested 12 source
features. Fit, validation, and holdout partitions use disjoint event IDs.
Frequency-adaptive sample weights make rare high-risk errors expensive. Weights
are computed from fitting labels only and normalized to mean one. Validation
selects among nine weighted candidates and the unweighted baseline by worst-band
recall plus a small macro-recall term; candidates must also beat a fit-mean
constant's validation RMSE. The holdout/test labels never select the costs.

The notebook reports probability-band recall/precision separately from the
distance-based operational tiers, with the unweighted baseline and numerical
error tradeoffs. It refits using `evaluation["selected_config"]` and the selected
round count, recomputing frequency weights on all training rows. The current
selection uses balance power 1, Elevated multiplier 20, Critical multiplier 320,
and 125 rounds. Reproduce the original baseline separately with:

```bash
development/.venv/bin/python development/collision_risk.py --unweighted --output-dir development/artifacts/unweighted
```

The committed aggregate run is [reports/cost_sensitive_evaluation.json](reports/cost_sensitive_evaluation.json).
Cost-sensitive risk estimates prioritize sensitivity and are not calibrated
collision probabilities. See the root README for increased recall, false alerts,
and regression error; equal probability-band recall is not guaranteed.

## Benchmark an existing prediction export

```bash
.venv/bin/python development/benchmark_predictions.py
```

Run this from the repository root using the lightweight prediction environment.
It compares the frozen `prediction/data_prediction.csv` with same-row reference
labels in `prediction/test_data.csv`; no model is loaded for inference or trained.
The report is written to `development/artifacts/prediction_benchmark.json`, with
row alignment checks, class agreement, regression errors, a distance-only
baseline, critical-probability recall, and provenance hashes. It does not modify
the input CSVs or saved model. Unlabelled uploads cannot supply accuracy labels.

See the root README's ML benchmark section for the measured results and the
distinction between class agreement, probability quality, and final-risk forecasting.

Generated model files, encoders, evaluation reports, and dashboard CSVs remain
in `development/artifacts/`. Encoding metadata records distance units so reviewed
artifacts can be used directly by the prediction workflow. To update its model:

```bash
cp development/artifacts/collision_risk_model.ubj prediction/artifacts/collision_risk_model.ubj
cp development/artifacts/feature_encoder.json prediction/artifacts/feature_encoder.json
```

Copy both files together after reviewing validation results. Then run:

```bash
.venv/bin/python prediction/predict.py
```

On this Mac, the module and notebook runner use the existing OpenMP library in
`../.venv/runtime/lib/`. On a fresh Mac install `libomp` with Homebrew.
