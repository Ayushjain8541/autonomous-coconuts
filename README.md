# Satellite collision risk evaluator

The workspace has separate development and prediction workflows:

```text
development/
  collision_risk_development.ipynb  # Experiments and evaluation
  collision_risk.py                 # Model training
  execute_notebook.py               # Notebook runner / JupyterLab launcher
  train_data.csv
  tests/
  artifacts/                       # Experimental training outputs
  .venv/                           # Notebook/training dependencies
prediction/
  predict.py                       # Saved-model inference
  test_data.csv                    # Input (test.csv is also supported)
  prediction_data.csv              # Output
  artifacts/                       # Deployed model + encoding metadata
  requirements.txt
.venv/                             # Lightweight prediction environment
```

Generate predictions from the repository root:

```bash
.venv/bin/python prediction/predict.py
```

The default input, output, and model paths resolve inside `prediction/`, including
when running from another directory. Explicit paths are relative to the current
working directory:

```bash
.venv/bin/python prediction/predict.py --input prediction/test.csv --output prediction/prediction_data.csv
```

Run development tests or open the notebook:

```bash
development/.venv/bin/python -m pytest -q development/tests
development/.venv/bin/python development/execute_notebook.py --lab
```

For a complete headless training and evaluation run:

```bash
development/.venv/bin/python development/execute_notebook.py
```

Training writes only to `development/artifacts/`. The deployed prediction model is
updated by explicitly copying a reviewed model and its encoder into
`prediction/artifacts/`; training never replaces it automatically.

See [development/README.md](development/README.md) and
[prediction/README.md](prediction/README.md) for setup and workflow details.
