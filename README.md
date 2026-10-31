# Autonomous Coconuts

Autonomous SG 2026 — **Airbus #1: Satellite Encounter Console** (working name).

An operator loads encounter reports; a model forecasts collision probability, deterministic rules classify encounters, and an LLM explains the computed results. A linked list, timeline, globe/schematic and detail panel help inspect critical events.

**Deadline:** 31 October 2026, 4:15 pm Singapore time. **Team:** P1 UI, P2 backend/LLM, P3 ML/algorithm, P4 floating support.


**Measured ML benchmark:** 95.45% agreement with the supplied same-row risk tiers
(23,369/24,484 reports). The distance-only baseline is
95.44%, so this is primarily a policy-agreement metric, not a claim of
precise collision-probability prediction. [Training method and full evidence](#ml-training-and-benchmark-evidence).

## Join independently

```sh
git clone https://github.com/Ayushjain8541/autonomous-coconuts.git
cd autonomous-coconuts
```

Ask your agent:

> Read AGENTS.md, then .beryl/agent/hackathon/product-brief.md and my role brief in .beryl/agent/hackathon/tickets/. I am P1 / P2 / P3 / P4. Work within my scope, preserve teammate changes, and use the shared contracts for integration. Choose your own implementation workflow. Do not assume a fixture or a planned command is a real integration.

Replace the role with yours. [Team entrypoint and role links](.beryl/agent/hackathon/README.md).

## Run and check the bootstrap

Requires Python 3.9+, Git and Bash. No dependency install or API key needed. Node is optional locally for the JS syntax check; CI includes it.

```sh
python3 backend/server.py --port 8000
```

Open `http://127.0.0.1:8000` and click **Load Demo**. In another terminal from the repo root:

```sh
python3 scripts/check.py
./.beryl/scripts/check.sh
```

Local context: [web](web/docs/agent-context.md), [backend](backend/docs/agent-context.md), [ML](ml/docs/agent-context.md), [P4 docs](docs/agent-context.md), [contracts](contracts/docs/agent-context.md), [tests](tests/docs/agent-context.md). Each development folder also has an AGENTS.md discovery pointer. Source controls/setup are replaceable; preserve the shared contract when changing stacks.

Beryl readiness is lock-backed and reports root AGENTS.md as an intentionally preserved external contract. Hooks are included but not enabled. Its upstream Apache-2.0 LICENSE/NOTICE and the coordinator's MIT attribution are preserved; future product licensing remains a team decision.

## Shared references

- [Product and user journey](.beryl/agent/hackathon/product-brief.md)
- [Requirements and evidence](.beryl/agent/hackathon/requirements.md)
- [Interfaces and data semantics](.beryl/agent/hackathon/contracts.md)
- [Ownership, branches and open-task rules](.beryl/agent/hackathon/team.md)
- [Dependency map and current gaps](.beryl/agent/hackathon/build-plan.md)
- [Evaluation expectations](.beryl/agent/hackathon/evaluation.md)
- [Data/source provenance](.beryl/agent/hackathon/evidence.md)

Beryl standard is installed from pinned upstream source. The replaceable Python/browser fixture is runnable with no package install or API key. It proves connectivity and risk-rule behavior; trained prediction, CSV ingestion, live LLM and the finished console remain role-owned work. No final product framework is imposed.

Original Airbus #2 brainstorming is [archived](.beryl/agent/hackathon/archive/airbus-2-ideas.md). The [coordinator skill](.agents/skills/hackathon-build/SKILL.md) is copied with its license in [third-party notices](THIRD_PARTY_NOTICES.md), subject to the user's workflow-freedom instruction in AGENTS.md. The team's product license remains undecided.

## Model development and CSV prediction


The model workflow below estimates the risk on each telemetry row. It remains
separate from the bootstrap HTTP adapter and does not implement the shared
final-report forecasting target described in the team contracts.

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
  data_prediction.csv              # Output
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
.venv/bin/python prediction/predict.py --input prediction/test.csv --output prediction/data_prediction.csv
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

### Local datasets

Raw CSVs are excluded from Git and remain on the local machine. Before training,
place the supplied training CSV at `development/train_data.csv`; before
prediction, place the supplied test CSV at `prediction/test_data.csv` (or
`prediction/test.csv`). See [ESA's dataset documentation](https://kelvins.esa.int/collision-avoidance-challenge/data/)
for the original source, schema, and units. The model and encoder remain tracked.

## ML training and benchmark evidence

### What the model learns

The saved model is an **XGBoost regression model** that predicts the existing
`risk = log10(Pc)` associated with each telemetry report. It learns nonlinear
relationships by adding decision trees that reduce the remaining regression
error. A separate deterministic function turns the estimate and miss distance
into **Safe**, **Elevated risk**, or **Critical**. This is a per-report risk
estimate; it does not forecast the final report at TCA or actual collision
occurrence. The shared final-report forecasting task remains separate.

Training uses **162,634 reports from 13,154 events** in `train_data.csv` and exactly
these twelve source features:

```text
event_id,time_to_tca,miss_distance,relative_speed,relative_position_r,relative_position_t,relative_position_n,c_object_type,c_sigma_r,t_sigma_r,F10,AP
```

1. The target is already logarithmic; it is not logged a second time. Object type
   is one-hot encoded using categories learned from the training partition.
   Numeric missing values use XGBoost's learned missing-value branches, and
   unseen object types use all-zero category indicators.
2. Reports are split **by event**, using fixed seeds 42 and 43. Every report for
   an event stays in one partition, preventing the same encounter's updates from
   appearing in both fitting and assessment sets.

| Partition | Events | Reports | Purpose |
| --- | ---: | ---: | --- |
| Fit, approximately 64% of events | 8,418 | 104,230 | Learn trees and initial encoding |
| Validation, approximately 16% | 2,105 | 26,366 | Select boosting rounds with early stopping |
| Holdout, approximately 20% | 2,631 | 32,038 | Assess unseen events; no fitting or early stopping |

3. Histogram boosting uses squared-error loss, learning rate **0.04**, maximum
   tree depth **7**, row subsampling **0.85**, column subsampling **0.90**, minimum
   child weight **8**, L1 penalty **0.05**, and L2 penalty **8.0**. These constrain
   complexity and reduce overfitting; they do not prove generalization by
   themselves. The budget is 1,600 rounds with patience 80; this run selected
   **356 rounds**.
4. After evaluation, the final model is refitted on all training reports using
   that fixed round count. The model and encoder are saved for inference;
   uploading a new CSV does not retrain them.
5. Before any test prediction, `risk`, `max_risk_estimate`, and `max_risk_scaling`
   are explicitly removed. Only the twelve allowed features enter the model.
   Prediction/classification uses metres and Critical precedence. The model
   output is capped at log-risk zero, since Pc cannot exceed one.

The implementation is [development/collision_risk.py](development/collision_risk.py).
[XGBoost's estimator guide](https://xgboost.readthedocs.io/en/stable/python/sklearn_estimator.html)
explains early stopping. Numeric errors and class metrics follow the standard
[regression and classification metric definitions](https://scikit-learn.org/stable/modules/model_evaluation.html).

### Simple accuracy rate: data_prediction.csv versus test_data.csv

The provided `test_data.csv` contains same-report reference risk values. The
benchmark reads those values **only after `data_prediction.csv` is frozen**.
It never trains, tunes, or invokes the model. Since events have multiple reports,
it verifies the row order and all twelve source feature values rather than
joining on `event_id` alone.

The test CSV has no reference `class_model` column. Reference tiers are therefore
computed from its `risk` and `miss_distance` using the exact same policy as the
prediction workflow. Classification accuracy means:

```text
tier agreement = matching predicted/reference tiers / all compared reports × 100
               = 23,369 / 24,484 × 100
               = 95.45%
```

There are **24,484 reports and 2,167 events** in this comparison.
This measures agreement with the supplied reported-risk estimates, not verified
physical collision outcomes or withheld final-event labels.

| Benchmark | Result | Interpretation |
| --- | ---: | --- |
| Combined risk-tier agreement, every report | **95.45%** | 23,369 correct; 1,115 disagree |
| Latest report per event | 97.74% | 2,118/2,167; smallest `time_to_tca`, not final-TCA truth |
| Always predict the majority class, Safe | 64.35% | Simple class-frequency reference |
| Distance-only rule, ignoring predicted Pc | **95.44%** | 23,368 correct using the supplied distance alone |
| Numerical risk within ±1 log10 unit | 18.84% | 4,613/24,484; estimated Pc within a factor of 10 of the reference |

**Important interpretation:** the model improves the combined tier count by only
**1 report** over the distance-only baseline, a gain of approximately
**0.0041 percentage points**. Both sides use the same supplied miss
distance, and many tiers are fixed by the distance override. Therefore the
95.45% tier score must not be presented as 95.45% accurate probability estimates.

Combined-tier precision and recall on the supplied test reports:

| Class | Reference reports | Precision | Recall |
| --- | ---: | ---: | ---: |
| Safe | 15,756 | 94.39% | 99.63% |
| Elevated risk | 6,501 | 97.58% | 85.09% |
| Critical | 2,227 | 97.94% | 96.09% |

### Numerical prediction quality and critical-risk detection

Regression does not have a universal percentage accuracy score. **RMSE** gives
larger errors more weight; **MAE** is average absolute error. Both below are in
log10(Pc) units, so lower is better. **R²** measures explained reference-label
variance; it is not a classification accuracy percentage.

| Metric | Event-separated training holdout, 32,038 reports | Frozen supplied-test comparison, 24,484 reports |
| --- | ---: | ---: |
| Log-risk RMSE | 5.7234 | 6.0391 |
| Log-risk MAE | 4.0281 | 4.4235 |
| R² | 0.6730 | 0.6238 |
| Combined-tier agreement | 97.32% | 95.45% |

The holdout column describes the assessment model before the final refit. The
deployed model is subsequently trained on all training reports; those holdout
rows are not an independent test of that final refitted model.

On the event-separated holdout, a constant fit-partition-mean predictor has RMSE
**10.0084**, compared with **5.7234** for XGBoost:
**42.81% lower log-risk RMSE**. This establishes learning beyond that
baseline, while the numerical errors remain substantial.

Probability-only critical detection, using Pc >= 1e-4 and **ignoring distance
for this diagnostic**, is much weaker than the combined-tier score:

- Supplied-test recall: **16.74%** (39/233 reference high-Pc reports detected;
  **194 missed**). Precision is **25.49%**, with 114 false positives.
- Event-separated holdout recall: **3.62%**.

These are different datasets and protocols; the difference is not evidence of a
model improvement. High combined Critical recall is largely provided by the
close-distance rule. Rare high-probability detection and probability calibration
remain important model limitations.

### What we can responsibly tell judges

> We trained a gradient-boosted regression model with event-separated evaluation,
> training-only preprocessing, early stopping, and explicit leakage protection.
> Our exported reports agree with reference operational tiers 95.45% of the time.
> We also disclose the 95.44% distance-only baseline and low probability-only
> critical recall. The evidence supports a reproducible prototype and controlled
> evaluation, rather than a validated operational collision predictor.

The event split is not a chronological backtest. Repeated reports are correlated,
so report-level and latest-event rates are shown separately. `event_id` is
retained as requested, but is an arbitrary identifier; identifier ablation is a
future validation step. Same-row reported risk is distinct from the shared
final-report forecasting objective. Do not tune the model on this retrospective
test comparison, or treat software-test pass rates as predictive accuracy.

### Reproduce the measurements

With the local reference CSV and frozen prediction export present:

```bash
.venv/bin/python development/benchmark_predictions.py
```

This writes `development/artifacts/prediction_benchmark.json` with the counts,
confusion matrix, regression metrics, baselines, and input/export/model SHA-256
hashes. It reads the supplied risk labels for evaluation only and does not change
model artifacts or CSVs. A newly uploaded CSV without reference risk can be
scored, but its accuracy cannot be calculated until independent labels exist.

The saved training holdout results are in
`development/artifacts/evaluation.json`; regenerate them with the development
notebook. The current deployed model and the training run's saved model have the
same SHA-256:

```text
d4f2035c9b01c44a93073267cf215d594934c2359bdffe28784aaa12fd05a289
```

The benchmark source is [development/benchmark_predictions.py](development/benchmark_predictions.py).
Its checks cover hand-calculated metrics, duplicate-event row alignment, missing
labels, invalid risks, and inconsistent exported classes, in addition to the
model/upload regression suite. Those are software robustness checks, not a
claim about real-world collision-prediction accuracy.
