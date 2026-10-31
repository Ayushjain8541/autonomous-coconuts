# Autonomous Coconuts

Autonomous SG 2026 — **Airbus #1: Satellite Encounter Console** (working name).

An operator loads encounter reports; a model estimates collision probability for the latest telemetry report, deterministic rules classify encounters, and an LLM explains the computed results. A linked list, timeline, globe/schematic and detail panel help inspect critical events.

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

## Run the integrated console locally

Use Python 3.12+ (the model owner also validated Python 3.13), Node and pnpm. From the repo root:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-full.txt
pnpm install --frozen-lockfile
pnpm run dev:all
```

Open `http://127.0.0.1:5173`. `start.command` launches the same API-plus-UI stack. The launcher uses `.venv/bin/python`, starts the API on port 8000 and proxies the frontend's `/api` calls to it. Ctrl-C stops its own child servers. Existing occupied ports produce an actionable error; use `COCONUTS_PORT` and `COCONUTS_WEB_PORT` for a separate local instance. Keep an existing environment rather than recreating it if already configured.

The root `.env.local` holds the existing Anthropic key. No key is needed for numeric inference. The backend calls P3's frozen predictor on each encounter's latest source report, including lead times shorter than two days. Missing required model columns, unsupported nonnumeric event IDs or a missing runtime remain explicitly unavailable; reported risk is never substituted.

The UI remains P1's pushed implementation. Remaining frontend connections are listed in [the integration review](docs/integration-review.md), including report download and geometry citation handling. The HTTP/PDF endpoints work independently of those pending UI connections.

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

### Current model and cost-sensitive training

The deployed model is an **XGBoost regressor for each report's `risk = log10(Pc)`**.
Its trees learn nonlinear relationships between telemetry and source-reported risk.
A deterministic function maps the estimate and miss distance to **Safe**,
**Elevated risk**, or **Critical**. This estimates the current report's risk;
it does not forecast the final report at TCA or observed collision occurrence.
The current shared product brief also selects this per-report target.

Training uses **162,634 reports from 13,154 events**, with exactly these inputs:

```text
event_id,time_to_tca,miss_distance,relative_speed,relative_position_r,relative_position_t,relative_position_n,c_object_type,c_sigma_r,t_sigma_r,F10,AP
```

Object type is one-hot encoded on the fitting partition only. Unknown categories
use all-zero indicators; numeric missing values use native XGBoost branches.
The target is already logarithmic and is not logged again.

All reports from one event stay in the same partition (fixed seeds 42 and 43):

| Partition | Events | Reports | Use |
| --- | ---: | ---: | --- |
| Fit, approximately 64% of events | 8,418 | 104,230 | Learn encoding, costs and trees |
| Validation, approximately 16% | 2,105 | 26,366 | Select costs and boosting rounds |
| Holdout, approximately 20% | 2,631 | 32,038 | Assessment after selection |

Only **425 fitting reports** have `risk >= -4`. Ordinary squared-error training
largely missed them. The replacement uses **frequency-adaptive sample weights**
with XGBoost's native weighted squared-error objective:

```text
band(y) = Safe if y < -6; Elevated if -6 <= y < -4; Critical if y >= -4
raw_weight(band) = [n / (number_of_present_bands * band_count)] ** power
                   * band_multiplier
weight = raw_weight / mean_fitting_row_weight
loss = 0.5 * sum(weight * (prediction - true_risk) ** 2)
```

Weights depend on fitting labels only. A bounded search compares the unweighted
baseline with nine weighted candidates: Elevated multipliers 5, 20, or 80;
Critical multipliers 1, 4, or 16 times the Elevated multiplier; balance power 1.
Early stopping and candidate selection minimize
`1 - (minimum_band_recall + 0.05 * macro_band_recall) / 1.05`.
These probability-band recalls **ignore distance**, preventing distance overrides
from hiding missed high-Pc cases. A one-class prediction has zero minimum recall.
Candidates must also beat the fit-mean constant's validation RMSE (**10.0719**).
If none pass, training fails explicitly instead of silently exporting a bad model.

The selected multipliers are **Safe 1, Elevated 20, Critical 320**, with power 1.
After frequency correction and normalization, fitting row weights are
**0.003122, 1.034732, and 230.143868** respectively. The same squared error on
a true Critical report therefore costs approximately **73,711 times** the error
on a true Safe report. This heavily penalizes missed Critical cases, while also
weighting other errors on true Critical rows; it is a class-weighted objective,
not an implementation that changes inference thresholds.

Histogram boosting retains learning rate 0.04, depth 7, minimum child weight 8,
row/column sampling 0.85/0.90, L1 0.05 and L2 8.0. The budget is 1,600 rounds,
with patience 80. Validation selected **125 rounds**, minimum band recall
**66.57%**, macro recall **72.80%**, and log-risk RMSE **9.8092**.

The final model refits all training reports at the selected costs and round count,
recomputing frequency weights on that final fitting set. Upload inference needs
only the saved model and encoder, with no training or label-dependent weighting.
Before any prediction, **`risk`, `max_risk_estimate`, and `max_risk_scaling` are
explicitly removed**. Only the twelve allowed features enter inference.
Distances remain in metres, Critical takes precedence, and log-risk is capped at zero.

Implementation: [development/collision_risk.py](development/collision_risk.py).
The [XGBoost fit API](https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBRegressor.fit)
documents sample weighting; its
[estimator guide](https://xgboost.readthedocs.io/en/stable/python/sklearn_estimator.html)
documents callable validation costs and early stopping.

### Did Critical detection improve?

Recall means **correct detections / reference reports in that class**. Overall
accuracy is different: it is matching classes / all reports. The table below
isolates the model's probability bands, without applying distance overrides,
on the same event-separated holdout used for the original baseline:

| Probability band | Reference reports | Unweighted recall | Weighted recall | Weighted precision |
| --- | ---: | ---: | ---: | ---: |
| Safe | 30,007 | 99.30% | **86.33%** | 98.59% |
| Elevated risk | 1,893 | 15.06% | **64.82%** | 23.78% |
| Critical | 138 | 3.62% | **60.14%** | 13.79% |

Critical detections rise from **5/138 to 83/138**; false negatives fall from
**133 to 55** (58.65% fewer). Macro recall rises from **39.33% to 70.43%**.
The gap between the highest and lowest band recall falls from **95.68 to 26.19
percentage points**. This is much more balanced; probability-band recalls are
still unequal, and the prototype still misses 55 of 138 high-Pc reports.

With the operational distance rules applied, holdout recalls are **91.32% Safe,
92.28% Elevated, and 99.15% Critical**. Combined-tier agreement is **92.12%**,
versus 97.32% for the old model. Log-risk RMSE rises from **5.7234 to 9.5750**;
the constant-mean holdout baseline is 10.0084. These are real costs of prioritizing
sensitivity. Higher class costs bias estimates toward higher-risk outcomes;
exponentiating them does **not** establish calibrated collision probabilities.

The assessment model fits only the fit partition. The deployed model subsequently
refits all training data, so that final refit cannot be independently scored on
these training holdout rows.

### Simple accuracy: current data_prediction.csv versus test_data.csv

The benchmark compares the frozen export with same-row reference risk in the
supplied test CSV, checking row order and all twelve inputs. It does not join
on repeated `event_id` alone, train, tune, or invoke the model. Reference tiers
are calculated from the source risk and miss distance using the same rules.

```text
current tier agreement = 21,514 / 24,484 * 100 = 87.87%
```

This is a **retrospective comparison** of 24,484 reports from 2,167 events. Test
labels were previously inspected for baseline benchmarking; this is not a fresh
blind test. They did not select these costs or rounds, and the model was not
retuned after this comparison. It evaluates reported risk, not actual collisions.

| Metric | Prior unweighted export | Current weighted export |
| --- | ---: | ---: |
| Probability-only Critical recall | 16.74% (39/233) | **53.65% (125/233)** |
| Probability-only Critical false negatives | 194 | **108** |
| Probability-only Critical false positives | 114 | **518** |
| Probability-only Critical precision | 25.49% | **19.44%** |
| Overall combined-tier agreement | 95.45% | **87.87%** |
| Log-risk RMSE | 6.0391 | **9.4602** |
| Numerical risk within ±1 log10 unit | 18.84% | **21.77%** |

Current combined-tier precision/recall, including distance:

| Tier | Reference reports | Prior recall | Current recall | Current precision |
| --- | ---: | ---: | ---: | ---: |
| Safe | 15,756 | 99.63% | **85.41%** | 97.84% |
| Elevated risk | 6,501 | 85.09% | **90.57%** | 71.41% |
| Critical | 2,227 | 96.09% | **97.40%** | 87.28% |

The weighted model's probability-only Safe/Elevated/Critical recalls are
**79.44% / 74.95% / 53.65%**. The higher Critical sensitivity comes with more
false alerts and worse numerical RMSE. Distance alone yields **95.44%** combined
tier agreement, higher than this sensitivity-focused model's 87.87%. The new
objective improves rare-case detection and class balance, **not overall accuracy**.
Latest-report-per-event agreement is **95.52%** (2,070/2,167), using the smallest
available `time_to_tca`; this is not final-TCA truth.

### Explaining the evidence to judges

> We train on separated events and explicitly remove risk fields before inference.
> Frequency-adaptive costs make missed high-risk reports expensive. On the event
> holdout, Critical probability recall improves from 3.62% to 60.14%, and average
> recall across probability bands improves from 39.33% to 70.43%. We disclose the
> additional false alerts, higher regression error, and the remaining missed cases.
> The model is a reproducible decision-support prototype, not a calibrated
> operational collision predictor.

Reports within an event are correlated, and this is not a chronological backtest.
`event_id` is retained because it is explicitly requested, but is an arbitrary
identifier; identifier ablation and fresh grouped/chronological validation remain
future work. Further tuning needs fresh evaluation events rather than repeated
optimization against this holdout/test comparison. Software-test pass rates do
not measure predictive accuracy.

### Reproduce and inspect

With the local training/test CSVs present, execute the notebook or training script:

```bash
development/.venv/bin/python development/execute_notebook.py
# Equivalent training workflow:
development/.venv/bin/python development/collision_risk.py
# Reproduce the original RMSE-only baseline in a separate output directory:
development/.venv/bin/python development/collision_risk.py --unweighted --output-dir development/artifacts/unweighted
```

Training saves to `development/artifacts/`; it does not automatically replace the
deployed model. After reviewing results, promote the model and encoder together
as described in [development/README.md](development/README.md). This update has
promoted the weighted model and regenerated the local canonical CSV.

```bash
.venv/bin/python prediction/predict.py --input prediction/test_data.csv --output prediction/data_prediction.csv
.venv/bin/python development/benchmark_predictions.py
development/.venv/bin/python -m pytest -q development/tests
```

The benchmark writes `development/artifacts/prediction_benchmark.json`; training
writes `development/artifacts/evaluation.json`. A small, committed aggregate
snapshot with baseline comparisons, cost-search results and hashes is available
at [development/reports/cost_sensitive_evaluation.json](development/reports/cost_sensitive_evaluation.json).
Raw data and generated prediction CSVs remain excluded from Git.
The deployed model SHA-256 is:

```text
e68b5d62bd0d674b4be277881b496d837eb42809d7abd024b8aec5c582807d9c
```

New uploads without reference risk can be scored, but their accuracy requires
independent labels. The upload helper and output columns (`risk`, `class_model`)
remain compatible with the existing prediction workflow.
