# Shared interfaces v1 — proposed handshake

**Contract owner: P2. Consumers: P1 and P3; verifier: P4.** These shapes and semantics let owners start independently. This is the shared v1 handshake. P2 implements validated multipart/raw CSV upload, retained analysis retrieval, demo/health/schema routes, CORS and bounded Anthropic insights. The public P3 adapter still determines whether trained predictions are available. See backend/README.md for exact current behavior. Producers/consumers may amend them together; update examples and affected handoffs in the same change. Internal architecture, framework, test runner and provider remain individual choices.

## HTTP boundary (P1 ↔ P2)

| Method/path | Request | Success | Failure |
| --- | --- | --- | --- |
| `GET /api/demo` | None | `AnalysisResult`, visibly synthetic | Standard error envelope |
| `POST /api/analyses` | Multipart form field `file`: report CSV | `AnalysisResult` for validated/grouped records | Invalid/unsupported/oversized CSV or unavailable model is explicit |
| `POST /api/analyses/{analysis_id}/insights` | JSON `{"event_ids":["event-id"]}` | `InsightsResult` tied to that analysis and those events | Invalid/stale analysis, bad event reference, timeout or provider unavailable |
| `GET /api/health` | None | API readiness plus model/insight configuration status | P2 chooses health transport details and documents them |

Analysis and insights are separate requests. P1 renders deterministic results before requesting explanations. The backend retains authoritative analysis facts for insight generation; it does not accept UI-supplied Pc/tier as fact. Limit each insights request to 10 known event IDs; more events can be requested in bounded batches/on selection. P2 documents actual upload/retention limits and P1 exposes actionable errors. No SSE, database, authentication system or cloud service is required by this interface.

A single analysis is all-or-error for invalid required records in v1: do not silently drop invalid rows and report a smaller success batch. Surface a bounded list of row/column errors and the total error count. Missing optional features can be normalized to null only when the model's documented input policy supports that. A valid analysis with an unavailable model may return explicit unknown predictions; it is not a successful trained-model integration.

## AnalysisResult

Canonical JSON examples: `contracts/fixtures/analysis-demo.json` and `contracts/fixtures/insights-demo.json` from repo root. The examples remain synthetic and are not model outputs. Machine-readable schemas now exist at contracts/analysis-v1.schema.json and contracts/insights-v1.schema.json and GET /api/schema; P1 can derive matching client types.

| Field | Type / semantics |
| --- | --- |
| `schema_version` | String `1.0` |
| `analysis_id` | String identifying this analysis; used to reject stale explanation responses |
| `source` | Object: `mode` (`synthetic_demo` or `uploaded_csv`), `label`, `sha256` (string or null), `report_count` (integer) |
| `time_basis` | `scenario_clock` for synthetic demo; `per_event_latest_report` for original timestamp-free CSV |
| `scenario_clock_utc` | ISO UTC timestamp or null; never invented for an uploaded historical batch |
| `model` | Object: `version` (string or null), `status` (`ready`, `fixture`, `unavailable`), `target` string, `feature_schema_version` string or null |
| `encounters` | Array of EncounterAssessment, unique by event_id |
| `warnings` | Array of operator-readable strings describing source/coverage limitations |

EncounterAssessment:

- `event_id`: nonempty string; preserve identity consistently even when CSV IDs are numeric. `mission_id`: string or null. `report_count`: positive integer. `latest_report_id`: string; `report_ids`: list of source report identities.
- `time_to_tca_hours`: non-negative number, from the latest report's source `time_to_tca` days × 24. For synthetic demo this is the labeled scenario horizon. Passed events/negative times are unsupported by the v1 upload contract and produce validation errors, not imminent alerts.
- `reported_pc`: number in [0,1] or null, converted from the latest reported log-risk. `predicted_pc`: number in [0,1] or null. `predicted_log10_pc`: finite number <= 0 or null; when present it must agree with predicted_pc = 10 ** predicted_log10_pc. Zero probability can have null log value. No NaN/Infinity in JSON.
- `prediction_status`: `ready`, `fixture` or `unavailable`; `model.version` identifies the shared model. `ready` means an actual documented model, not a fixture/pass-through mislabeled as learned prediction.
- `miss_distance_m`: non-negative number or null; predicted separation at closest approach from the source report, not current measured distance. `relative_speed_mps`: non-negative number or null.
- `severity`: `critical`, `elevated`, `safe` or `unknown`, computed under requirements.md. `flag_reasons`: list of objects with `rule_id`, `field`, `operator`, `value`, `threshold`, `unit`. IDs are `PC_CRITICAL`, `MISS_DISTANCE_CRITICAL`, `PC_ELEVATED`, `MISS_DISTANCE_ELEVATED`, `SAFE_COMBINED` or `MISSING_EVIDENCE`. Omit unused numeric fields for compound/missing reasons; do not invent a single threshold for a compound rule.
- `geometry`: null or object with `frame: "RTN"`, `position_m` and `velocity_mps` (`r`, `t`, `n` numeric components or null when unavailable). A vector is complete or null; partial vectors are not silently filled with zero. These are source encounter vectors, not global positions.
- `globe_position`: null unless additional credible latitude/longitude **and timestamp/provenance** are supplied. A schematic UI placement stays local presentation state and is visibly labeled; it never becomes a source coordinate in the response.
- `warnings`: array of strings; `report_ids` plus source checksum support provenance. Missing covariance/unsupported prediction horizon are made visible rather than inventing uncertainty intervals.

No precomputed global-banner or filtered-list counts are required in v1. P1 derives both from the same returned encounters. Global banner: all critical events across horizons, earliest lead time first with event ID as a stable tie-breaker. Critical-within-24h list: severity critical AND 0 <= time_to_tca_hours <= 24. Retain selected event identity outside the list with a notice. Filters must not modify source data or classification.

## Prediction boundary (P2 ↔ P3)

Logical interface, independent of transport/language:

`predict_batch(request: PredictionRequest) -> PredictionBatch`

- PredictionRequest: `schema_version: "1.0"`, `events: [{event_id: string, reports: [{report_id: string, fields: object}]}]`.
- `fields` uses the **original CSV column names and documented source units**; `event_id` is kept as an identity, source numeric values become numbers/null, `c_object_type` stays categorical text. `time_to_tca` stays **days** here. Do not pass normalized hours under the original name.
- Shared v1 target: forecast the **final available reported log10(Pc) for an encounter**, using only reports created **at least 2 days before closest approach** (`time_to_tca >= 2`). When training/evaluating, use the final target only for events with a final report within 1 day of closest approach; record excluded counts. This is a source-report target, not observed collision occurrence. P3 owns model choice/features, but P2/P1 must use this same meaning.
- P2 validates/parses/groups and assigns stable report IDs. P3 orders reports, selects only the allowed earlier window and owns feature selection/manifest plus unknown behavior. If no eligible earlier reports exist, prediction is unavailable; do not extrapolate a trained model to unsupported horizons silently. Original earlier reported risk can support a separately labeled baseline; later/final risk must never leak into inputs.
- PredictionBatch: `model_version: string|null`, `feature_schema_version: string|null`, `predictions: [{event_id, predicted_pc, predicted_log10_pc, status, warnings}]`. Status is `ready` or `unavailable`. Exactly one response per requested unique event; unmatched, missing or duplicate output IDs are integration errors. A fixture is an explicit development adapter owned/labeled by P2, not an actual P3 model result. Uploaded assessments additionally include prediction_report_ids for the actual >=2-day input window; report_ids/latest_report_id still describe all source reports/the displayed latest report.

Second logical interface:

`classify_encounter(predicted_pc: number|null, miss_distance_m: number|null) -> {severity, flag_reasons}`

P3 owns the single authoritative rule implementation. P2 calls/adapts it, P1 renders the returned result, and the LLM explains it. P2/P3 select the simplest packaging compatible with their stacks. A local Python import is a suggested low-overhead option; an HTTP service is not mandated. Record the agreed adapter location and actual invocation in both handoffs before integration.

## InsightsResult (P2 → P1)

Fields: `schema_version: "1.0"`, `analysis_id`, `status` (`ready`, `fixture`, `unavailable`), `items` (array), `warnings` (array). Each item has `event_id`, `summary` (string), `fact_refs` (array of `{event_id: string, field: string}` references), and `limitations` (array of strings).

Each fact reference resolves an encounter by its exact event_id, then a field from this allowlist: `predicted_pc`, `reported_pc`, `miss_distance_m`, `relative_speed_mps`, `time_to_tca_hours`, `severity`, `flag_reasons`, `prediction_status`, `geometry`. Reference event_id must match its item event_id and exist in the same analysis. No array-position strings, arbitrary property paths or references to another analysis are accepted.

The LLM receives bounded structured facts and existing reason IDs, never authority to alter severity or create predictions. Validate event/fact references and output shape; reject unsupported claims rather than silently shipping them. Keep critical numbers in deterministic UI fields. A ready explanation is not a guarantee of truth: enforce grounding and show limits. Provider absence/failure/timeout yields unavailable with a useful message, and never hides deterministic results. P2 owns a bounded timeout/retry policy and records it with real latency evidence. Synthetic example explanations use status fixture.

## Error envelope

`{"error":{"code":"INVALID_CSV","message":"Missing required column: event_id","details":[{"row":null,"column":"event_id","reason":"required"}]}}`

Stable codes: `INVALID_CSV`, `UNSUPPORTED_SCHEMA`, `UPLOAD_TOO_LARGE`, `MODEL_UNAVAILABLE`, `ANALYSIS_NOT_FOUND`, `UNKNOWN_EVENT`, `INSIGHTS_UNAVAILABLE`, `INTERNAL_ERROR`. Use HTTP 400/413/422 for actionable input errors, 404 for missing analysis, and 503 for an unavailable dependency when returning an error rather than an explicit unavailable result. No stack traces or secrets in UI messages. P2 settles exact status/code choices once and documents them for P1.

## P2 implementation details (non-breaking v1 additions)

GET /api/analyses/{id} retrieves retained results; GET /api/schema exposes schemas and limits. POST /api/analyses also accepts raw text/csv. Default upload limit is 64 MiB/100,000 reports, with exactly one multipart file field. Validation errors are HTTP 422 with up to 50 row/column details and total_errors; the entire CSV is rejected. Unsupported content type is 415; malformed requests 400; oversize 413; missing analyses 404; invalid model output 502; model-adapter exception 503. Additional stable error codes: INVALID_REQUEST, NOT_FOUND and ORIGIN_NOT_ALLOWED.

Insight provider failures/missing key return HTTP 200 with status unavailable and warnings, preserving numeric analysis. Bad analysis/event/body is still an HTTP error. Anthropic selects supported observation codes; the backend validates and renders text/fact references from saved results. It does not accept arbitrary model-authored numeric/safety prose. Ten event IDs/request, 25s default timeout, two concurrent calls, no automatic retries, successful cache for ten minutes. The configured provider is Anthropic; credentials stay in ignored local env files.

Analyses are retained in memory for one hour, maximum 32, with copy isolation and unique IDs for each Load Demo. Restart loses analysis IDs. Latest-time ties choose the last CSV record and emit a warning. Forecast inputs are filtered to >=2 days at the P2 boundary; later reports remain source evidence. P3 must still supply the real trained predictor; the backend does not fake its output.
