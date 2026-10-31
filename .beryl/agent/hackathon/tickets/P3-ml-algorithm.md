# P3 — Model, prediction target and risk algorithm

**Owner:** P3. **Suggested branch:** `p3/ml-algorithm`. **Scope:** `ml/`, model artifact/manifests, training/inference/feature transforms, deterministic classification, their checks and handoffs/P3.md. **Requirements:** A1-01/02/05; supports geometry/insights evidence. A tier implementation and unavailable adapter now exist; real training/inference remains this role's work.

## Read

Root AGENTS.md → [product brief](../product-brief.md) → this file → [requirements](../requirements.md) + [contracts](../contracts.md) → [evidence](../evidence.md) + [evaluation](../evaluation.md) → relevant data/current source. Choose model family, libraries, artifact format, training approach and working method. Keep the logical prediction interface compatible with P2; internal implementation is yours.

## Outcome you own

Define the target/horizon, train and evaluate a model, expose inference and the single authoritative deterministic risk classifier. The shared v1 target is the final available reported log-risk per encounter, using inputs with time_to_tca >= 2 days; training/evaluation targets must come from a final report within 1 day of closest approach. Record excluded/unsupported events. This source-report forecast is distinct from reconstructing current reported risk or predicting actual collision occurrence. The target is a shared meaning, while the model/features remain your choice. `predicted_pc = 10 ** predicted_log10_pc` when finite; preserve zero/null semantics and do not invent calibration/confidence claims.

Source features can use the brief's simple subset: time_to_tca, miss_distance, relative_speed, relative_position_r/t/n, c_object_type, c_sigma_r, t_sigma_r, max_risk_estimate, F10, AP; event_id is identity/grouping. Feature selection is your choice, but publish a manifest so P2 knows required columns/units, missingness policy, model version and supported horizons. Verify transformations such as max_risk_estimate against the actual values/docs; a negative logged value is not a raw probability.

Train_data has not been acquired/verified here. Test_data is inspected but cannot supply withheld final-risk labels. P4 may help locate/verify the training source. Preserve raw data locally; do not commit it. If labels/access are insufficient, record the block and useful experiments honestly; a pass-through of reported risk or synthetic Pc does not complete model training.

## Interfaces and boundaries

Produce predict_batch and classify_encounter under the logical v1 contract. Agree concrete adapter packaging with P2; do not add an unrequested service solely to match a preferred library. Return one result per event, model metadata and explicit unknown reasons. P2 handles HTTP/CSV transport; you handle feature semantics, ordering, valid prediction horizons and rule logic. Help P1 interpret relative geometry without pretending to supply complete global orbital states.

## Acceptance outcomes

- Events are separated across train/validation; preprocessing is fit on training only; inputs exclude later target information. State how report order and latest-report ties are handled.
- Evaluate against a meaningful baseline such as latest available reported log-risk. Save event counts, target/horizon, split, metrics, false-negative/failure examples and limitations.
- Rules use metres/probabilities, critical precedence and explicit missing evidence exactly as in requirements.md. Cover thresholds/boundaries with checks appropriate to your method.
- Inference is reproducible from the documented artifact/runtime and compatible with P2. Unknown/out-of-domain cases and missing artifacts are explicit.
- Do not score synthetic fixture predictions as real accuracy or claim withheld final-risk test accuracy from earlier risk columns.

Publish your actual run/check commands and artifact provisioning instructions in your handoff. Coordinate backend dependency/shared-schema changes with P2; keep UI visual decisions with P1.
