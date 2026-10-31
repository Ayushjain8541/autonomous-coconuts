# CSV risk prediction

Raw input CSVs are local files excluded from Git. Supply `development/train_data.csv`
and `prediction/test_data.csv` at those paths before running their workflows.

Run from the repository root:

```bash
.venv/bin/python prediction/predict.py
```

Or from this folder:

```bash
../.venv/bin/python predict.py
```

The script reads this folder's `test.csv` if present, otherwise `test_data.csv`,
and writes this folder's `data_prediction.csv`. Its default model files are in
this folder's `artifacts/`, regardless of the current working directory.
For explicit paths, run from the repository root:

```bash
.venv/bin/python prediction/predict.py --input prediction/test.csv --output prediction/data_prediction.csv
```

The output preserves all input rows and telemetry, replaces `risk` with predicted
**log10(Pc)**, and adds `class_model`: **Safe**, **Elevated risk**, or **Critical**.
Input `risk`, `max_risk_estimate`, and `max_risk_scaling` are dropped before
prediction; the source CSV is never overwritten.

The deployed model now uses class-frequency weighting during training to improve
rare Critical detection. Uploads use the saved model directly; no labels,
retraining, new dependencies, or inference-time weights are needed. Risk thresholds
and output columns are unchanged. This sensitivity-focused model produces more
false alerts and higher regression RMSE than the earlier model; its numerical
outputs must not be described as calibrated collision probabilities. See the
[training and benchmark evidence](../README.md#ml-training-and-benchmark-evidence)
for measured recall, class balance, and tradeoffs.

## Uploaded CSV helper

CSV uploads can omit all three risk-related input columns. Backend code can
score uploaded bytes, CSV text, or a readable stream without a temporary file:

```python
from prediction.predict import predict_uploaded_csv

scored = predict_uploaded_csv(upload_bytes)
csv_download = scored.to_csv(index=False).encode("utf-8")
```

Use `predict_dataframe(frame)` for an already parsed pandas frame. Neither helper
mutates the caller's input or trains a model. The helpers return all input rows
and telemetry with predicted `risk` and `class_model` added.

For the teammate handoff filename:

```bash
.venv/bin/python prediction/predict.py --input prediction/test_data.csv --output prediction/data_prediction.csv
```

See [UPLOAD_HANDOFF.md](UPLOAD_HANDOFF.md) for the required columns, error handling,
and the upload/download integration instructions for P1/P2.

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
