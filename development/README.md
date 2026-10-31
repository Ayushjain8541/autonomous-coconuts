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
features. Fit, early-stopping, and holdout partitions use disjoint event IDs.
The notebook reports regression errors and probability-only risk-threshold
performance independently of distance-based tier overrides.

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
