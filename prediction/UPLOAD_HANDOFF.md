# Teammate handoff: CSV upload prediction

The generated export for this handoff is `prediction/data_prediction.csv`.
It contains one prediction per input telemetry row, with original telemetry plus:

| Column | Meaning |
| --- | --- |
| `risk` | Predicted **log10(Pc)**; convert to probability with `10 ** risk` |
| `class_model` | Exactly `Safe`, `Elevated risk`, or `Critical` |

The exported risk is a model estimate for that telemetry row. It is not an
original reported score or a forecast of the final report at TCA. A file can
contain several reports for the same `event_id`; select the smallest
`time_to_tca` if the UI needs one latest-report card per event.

## Generate the export locally

From the repository root, with the prediction dependencies installed:

```bash
.venv/bin/python prediction/predict.py --input prediction/test_data.csv --output prediction/data_prediction.csv
```

Generated CSVs and supplied raw inputs are excluded from Git. Regenerate the
export from your local input file, or obtain the generated file from its owner.
The CLI's existing default output remains `prediction/prediction_data.csv`.

## Connect your upload endpoint

The prediction helper is implemented. P1/P2 still own the upload screen, HTTP
route, and download response. No backend route or shared v1 adapter is changed
by this helper. Use the uploaded file's bytes or readable stream directly:

```python
from prediction.predict import predict_uploaded_csv

scored = predict_uploaded_csv(uploaded_csv_bytes)
download_bytes = scored.to_csv(index=False).encode("utf-8")
```

For asynchronous uploads, await the file read in the endpoint and pass the
resulting bytes to the helper.

Return `download_bytes` as `text/csv; charset=utf-8` with a download filename of
`data_prediction.csv`. The helper scores in memory and does not overwrite a
shared CSV, so each request can receive its own output. It reuses the saved model
and does not train on the upload. Existing parsed pandas frames can use
`predict_dataframe(frame)`, which returns a new frame and leaves its caller
unchanged.

The upload needs these twelve feature columns:

```text
event_id,time_to_tca,miss_distance,relative_speed,relative_position_r,relative_position_t,relative_position_n,c_object_type,c_sigma_r,t_sigma_r,F10,AP
```

`risk`, `max_risk_estimate`, and `max_risk_scaling` are **not required**. If they
are supplied, they are discarded before prediction. Other telemetry columns and
all input rows are preserved. Event IDs must be numeric for this trained model.
`time_to_tca` is in days, distances are metres, and `relative_speed` is metres/second.
The model metadata records the classification distance unit. Missing numeric
predictors are supported, but event IDs and
classification distances must be usable; negative or nonfinite distances fail.

Apply the endpoint's upload limit before passing content to the helper. Empty,
unparseable, non-UTF-8, or incomplete CSVs raise `ValueError`; adapt these to the
backend's existing `INVALID_CSV` response. Handle unavailable model artifacts as
an unavailable dependency rather than returning fabricated scores.

Install `prediction/requirements.txt` in the backend's Python environment before
importing the helper. Python 3.13 is the validated environment for these pinned
dependencies. The helper does not require notebook or training dependencies.

For a UI using the shared lowercase severity enum, the display mapping is
`Safe -> safe`, `Elevated risk -> elevated`, and `Critical -> critical`. The
helper already applies the deterministic thresholds; display its computed class.
