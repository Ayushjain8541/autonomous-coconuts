# CSV risk prediction

Run from the repository root:

```bash
.venv/bin/python prediction/predict.py
```

Or from this folder:

```bash
../.venv/bin/python predict.py
```

The script reads this folder's `test.csv` if present, otherwise `test_data.csv`,
and writes this folder's `prediction_data.csv`. Its default model files are in
this folder's `artifacts/`, regardless of the current working directory.
For explicit paths, run from the repository root:

```bash
.venv/bin/python prediction/predict.py --input prediction/test.csv --output prediction/prediction_data.csv
```

The output preserves all input rows and telemetry, replaces `risk` with predicted
**log10(Pc)**, and adds `class_model`: **Safe**, **Elevated risk**, or **Critical**.
Input `risk`, `max_risk_estimate`, and `max_risk_scaling` are dropped before
prediction; the source CSV is never overwritten.

The supplied distances are in metres. Critical takes precedence:

| Class | Rule, using distance in km |
| --- | --- |
| Critical | `risk >= -4` OR `distance < 1` |
| Elevated risk | `-6 <= risk < -4` OR `1 <= distance <= 5` |
| Safe | `risk < -6` AND `distance > 5` |

Required model files:

- `artifacts/collision_risk_model.ubj`: deployed XGBoost model.
- `artifacts/feature_encoder.json`: feature order, categories, and distance units.

The root `.venv` is the lightweight prediction environment. It remains separate
from `../development/.venv`. To install prediction dependencies from the root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r prediction/requirements.txt
```

The script loads a project-local macOS OpenMP runtime from either this folder's
`.venv/runtime/lib/` or the root `.venv/runtime/lib/`. On a fresh Mac install
`libomp` with Homebrew.
