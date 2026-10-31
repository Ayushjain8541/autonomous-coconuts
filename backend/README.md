# P2 backend

Python 3.9+ standard library for the core numeric API and JSON reports. PDF export uses the optional ReportLab extra below. No OpenAI key is required. This local-development server can be replaced by P2's chosen runtime while preserving the shared HTTP/ML contracts.

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
| ANTHROPIC_REPORT_TIMEOUT_SECONDS | 60; allowed range 1–90; full report generation only |
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
| POST /api/analyses/{id}/report | JSON `{}`; full portfolio briefing, cited priority assessments, advisory actions and hypothetical rule comparisons |
| GET /api/analyses/{id}/reports/{report_id}.pdf | Exact generated report attachment; never starts another paid generation |
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

Error rows and `row-N` report IDs use the physical line where the CSV record ends. Blank lines count; quoted multiline records use their final line.

Reports are grouped by preserved string event_id. Displayed latest report is minimum time_to_tca; ties choose the last CSV record with a visible warning. Source times stay days at the ML boundary and become hours in the API. The P3 input window contains only reports at least 2 days before TCA. Later records remain source evidence but never become forecast inputs. prediction_report_ids identifies the actual earlier window; report_ids/latest_report_id identify the source view.

The source-provided miss_distance is a prediction at TCA, not current measured distance. Reported Pc remains separate from model-predicted Pc. An unavailable model yields null predicted Pc, explicit warnings and `unknown` unless a known critical distance criterion independently triggers. A pass-through of reported risk is never presented as a trained forecast.

Storage is in memory: 32 analyses, one-hour TTL, discarded on restart. Insight cache: 64 successful explanations for ten minutes, isolated by context version/analysis/event selection/model/credential identity. Missing credentials and failures are not cached. At most two provider calls are in flight, ten events per request, 2,048 output tokens and zero automatic retries.

Each provider call runs in a short-lived spawned Python worker with an overall deadline, including connection, headers and body. The backend terminates timed-out work before releasing its concurrency slot (plus at most 0.4 seconds of bounded process cleanup). This prevents slow-drip responses from extending socket timeouts indefinitely. Deployment runtimes must support Python child processes; the documented local CLI does. Truncated/failed transport returns unavailable insights and leaves the analysis retrievable.

## Grounding design

Both LLM paths use backend/llm_context.py: a shared operations brief, actual source/model metadata, time interpretation, warnings, explicit missing-evidence flags and complete classification comparisons (field, operator, observed value, threshold and unit). Example Pc values are distinguished from missing values. Reported-versus-predicted differences are not treated as time trends. The request does not contain risk histories, calibration metrics, feature attributions or maneuver-feasibility evidence; it says so explicitly. Validation bookkeeping stays on the server to keep the provider payload focused.

For short insights, the backend renders the exact assessment and reference-time interpretation. Anthropic chooses one eligible next-review recommendation using the shared context. The backend rejects unknown/duplicate/omitted events, ineligible recommendations, malformed/refused output and unsupported numeric references. This keeps concise explanations consistent with the stored assessment while letting the LLM prioritize useful review advice. The public response shape is unchanged. Numeric analysis remains available when insights are unavailable.

Provider transport follows the official [Messages API](https://platform.claude.com/docs/en/api/messages/create) and [structured output](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) contracts. Live account/model access must be verified after a user adds the key; local provider-double tests are not live Anthropic verification.

## P3 integration

The backend imports only the public `ml.predict_batch` and `ml.classify_encounter` boundary. P3 can replace its placeholder with the real artifact-backed implementation without changing HTTP endpoints. The batch must return exactly one result per requested event and a real model_version for ready predictions. Invalid IDs, non-probabilities or inconsistent log-risk/probability produce a controlled integration error. Do not edit ML internals from P2 to manufacture readiness.

## Analytical report, what-if comparisons and PDF

The full report complements the short-insight endpoint and uses the same context and citation checks. Anthropic writes actual narrative statements with fact references: executive summary, key findings, priority-event assessments, eligible advisory actions with the what-if comparison rendered directly from the classifier results. Numeric claims are checked against cited values and deterministic supporting values. References and these checks do not prove every free-form interpretation; the result remains advisory.

Whole-portfolio counts cover every encounter. Detailed prose is bounded to ten encounters, ordered critical/elevated/unknown/safe and then source-relative lead time. The response states omitted coverage. Original fixture, model target/status and per-report time semantics remain visible. Unknown predictions are never counted as safe. Successful reports cache for ten minutes; at most 32 exact report versions are retained for one hour. Numeric analysis expiry also invalidates download access.

The report context also supplies explicit baseline-to-scenario tier comparisons and any remaining critical triggers. The what-if summary must match a source-rendered comparison for the focus cases; a rewritten LLM version is replaced with that comparison and a warning. The what-if comparison independently assumes Pc x 0.1, miss distance x 2, or both, then invokes P3's unchanged classifier. It is a sensitivity analysis, not an orbital simulation or a prediction that a maneuver can produce those changes. Missing or overflowing assumptions become unavailable. The LLM may suggest review/current tracking/flight-dynamics assessment; it cannot issue an exact burn or safety clearance. Pc is an estimate, not an operator control.

P1's requested minimum is one Generate/download report button, with pending/error handling. Existing views and short-insight consumers stay compatible; no new simulation visualization is required. POST the empty JSON object, inspect status/warnings, then link the returned pdf_url. Even an unavailable AI narrative can export the deterministic statistics/scenarios with an explicit label. Give report requests at least 95 seconds before a UI-side timeout; default provider deadline is 60 seconds, bounded at 90. Report and insight network calls share a global two-call limit; there are no automatic retries.

To enable the optional PDF export in a fresh checkout:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python backend/server.py --port 8000
```

The extra is already installed in Ayush's ignored local backend/.venv. Without it, JSON works and download returns actionable PDF_UNAVAILABLE/503. Restart an older server after installing it. PDF includes source labels, counts, narrative/evidence, action rationale, baseline/what-if tables, coverage and limitations. Test doubles never call a live account; PDF-specific tests skip explicitly if the extra is absent.

## Verification

```sh
python3 scripts/check.py
./.beryl/scripts/update-test-manifest.sh  # only after intentional test changes
./.beryl/scripts/check.sh
```

Tests cover parser errors, ordering/provenance, model contract/unknown behavior, TTL/mutation isolation, local Anthropic HTTP success/failure/refusal/unsupported claims, multipart routes, local CORS and a complete HTTP upload-to-insights path. External provider tests use a local HTTP double and fake credentials, never a developer's key. Real test CSV upload is a separate measured smoke check; P3 model/evaluation and P1's finished dashboard remain independent work.
