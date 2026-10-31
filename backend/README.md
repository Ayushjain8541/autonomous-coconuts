# P2 backend

Python 3.9+ standard library only. No package install or OpenAI key is required. This local-development server can be replaced by P2's chosen runtime while preserving the shared HTTP/ML contracts.

## Start

From the repository root:

```sh
python3 backend/server.py --port 8000
```

The browser shell and API share http://127.0.0.1:8000. The shell remains P1's replaceable bootstrap; P2 adds the real upload/analysis/insight endpoints beneath it.

## Anthropic setup (the only key entry needed)

Create `.env.local` from `.env.example` if it does not already exist. Enter your own key after `ANTHROPIC_API_KEY=`. Keep it local; `.env.local` and `.env` are ignored by Git. Do not paste credentials into chat, commits or test output. An empty ignored file was created on the coordinator's P2 machine; Git intentionally does not distribute it.

Provider settings are read on each request, so adding a key does not require restarting the server. Process environment takes precedence over local files. Restart after changing Python code or merging P3's implementation.

| Setting | Default / meaning |
| --- | --- |
| ANTHROPIC_API_KEY | Blank; required only for live insights |
| ANTHROPIC_MODEL | claude-haiku-4-5-20251001; change to an available model if your account requires it |
| ANTHROPIC_TIMEOUT_SECONDS | 25; allowed range 1–60 |
| COCONUTS_CORS_ORIGINS | localhost/127.0.0.1 on ports 5173 and 3000; comma-separated override |

Host/port can be set by CLI flags or process environment COCONUTS_HOST/COCONUTS_PORT. The local env-file reader loads provider/CORS settings without executing shell expressions. No provider error includes the credential or raw provider response.

## Routes for P1

| Route | Behavior |
| --- | --- |
| GET /api/health | API status, last observed model status, Anthropic configured/unconfigured; configured does not prove a live call |
| GET /api/demo | New retained analysis ID for the labeled synthetic fixture |
| POST /api/analyses | Multipart field `file`, or raw text/csv; validates/groups and invokes public P3 prediction/rule functions |
| GET /api/analyses/{id} | Retained analysis; missing/expired IDs return 404 |
| POST /api/analyses/{id}/insights | JSON `{"event_ids":["id"]}`; bounded grounded Anthropic explanation for saved facts |
| GET /api/schema | Machine-readable result schemas plus current request/retention limits |
| OPTIONS /api/... | Development CORS preflight for allowed origins |

Load/upload first, render numeric results, then request insights using the returned analysis_id and selected event IDs. Insights return HTTP 200 with status `ready` or `unavailable`; inspect that status, not HTTP status alone. Unknown analysis/event or malformed input is an actionable HTTP error. A synthetic demo remains synthetic even when a live LLM explains it.

Example upload:

```sh
curl -F 'file=@/absolute/path/to/test_data.csv' http://127.0.0.1:8000/api/analyses
```

Vite-style development clients can use http://127.0.0.1:8000 as API base, or proxy `/api` to it. Production origins/deployment/authentication are a coordinated P4 decision; this server defaults to loopback local development.

## Limits and data semantics

64 MiB CSV; 100,000 reports; exactly one multipart file. UTF-8 (BOM supported), unique headers, finite/range-checked numbers and required event_id/time_to_tca/miss_distance. Invalid required input rejects the entire CSV with up to 50 row/column errors and total_errors; no silent row drops. Empty optional numbers are null. Extra/missing cells and ambiguous headers are rejected.

Reports are grouped by preserved string event_id. Displayed latest report is minimum time_to_tca; ties choose the last CSV record with a visible warning. Source times stay days at the ML boundary and become hours in the API. The P3 input window contains only reports at least 2 days before TCA. Later records remain source evidence but never become forecast inputs. prediction_report_ids identifies the actual earlier window; report_ids/latest_report_id identify the source view.

The source-provided miss_distance is a prediction at TCA, not current measured distance. Reported Pc remains separate from model-predicted Pc. An unavailable model yields null predicted Pc, explicit warnings and `unknown` unless a known critical distance criterion independently triggers. A pass-through of reported risk is never presented as a trained forecast.

Storage is in memory: 32 analyses, one-hour TTL, discarded on restart. Insight cache: 64 successful selections for ten minutes, isolated by analysis/event selection/model/credential identity. Missing credentials and failures are not cached. At most two provider calls are in flight, ten events per request, 2,048 output tokens and zero automatic retries.

## Grounding design

Anthropic receives only a bounded catalog of observations supported by saved numeric results and rule reasons. It selects useful observation codes and their order. The backend rejects unknown events, duplicates, unsupported codes, incomplete/refused output and malformed JSON, then renders source-backed sentences/citations itself. This is intentionally bounded insight generation: the LLM cannot invent a new probability, severity, maneuver or numeric claim. Numeric analysis remains available when insights are unavailable.

Provider transport follows the official [Messages API](https://platform.claude.com/docs/en/api/messages/create) and [structured output](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) contracts. Live account/model access must be verified after a user adds the key; local provider-double tests are not live Anthropic verification.

## P3 integration

The backend imports only the public `ml.predict_batch` and `ml.classify_encounter` boundary. P3 can replace its placeholder with the real artifact-backed implementation without changing HTTP endpoints. The batch must return exactly one result per requested event and a real model_version for ready predictions. Invalid IDs, non-probabilities or inconsistent log-risk/probability produce a controlled integration error. Do not edit ML internals from P2 to manufacture readiness.

## Verification

```sh
python3 scripts/check.py
./.beryl/scripts/update-test-manifest.sh  # only after intentional test changes
./.beryl/scripts/check.sh
```

Tests cover parser errors, ordering/provenance, model contract/unknown behavior, TTL/mutation isolation, local Anthropic HTTP success/failure/refusal/unsupported claims, multipart routes, local CORS and a complete HTTP upload-to-insights path. External provider tests use a local HTTP double and fake credentials, never a developer's key. Real test CSV upload is a separate measured smoke check; P3 model/evaluation and P1's finished dashboard remain independent work.
