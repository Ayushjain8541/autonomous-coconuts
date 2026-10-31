# P2 backend and Anthropic implementation plan

User authorization: P2 implementation requested in chat, with Anthropic key to be entered manually and the last hour reserved for presentation. Execute inline; no new whole-product planning gate. Scope: backend/, shared schema/examples/docs as needed, P2 tests/handoff. Preserve web/ and ml/ ownership. Existing spec: product-brief.md, contracts.md and tickets/P2-backend-llm.md.

Architecture: extend the existing local Python boundary, keeping dependencies at zero unless integration requires otherwise. CSV parsing/grouping feeds the public P3 predictor/classifier; normalized results are retained in a bounded expiring local store. Anthropic selects fact-grounded observations in structured output; backend validates them and renders deterministic factual explanations. HTTP routes preserve v1 shapes, with local-development CORS and helpful errors.

Global constraints: no secret in Git/logs; no fabricated model/LLM success; 64 MiB upload limit; no silent row drops; source times remain days until response conversion to hours; model output IDs/probabilities are validated; insights use stored facts, max 10 selected events and a bounded provider call; source synthetic flags remain visible. The public P3 placeholder is a dependency, not permission to train/replace their model.

Review focus: malformed CSV/non-finite values; wrong model IDs or non-probability outputs; mixed report horizons/ambiguous latest report; stale analysis and concurrent requests; provider failure/unsupported observation claims. Tests below pin these at real consumer boundaries.

### Task 1: CSV ingestion and validation

Create backend/ingestion.py and tests/test_ingestion.py. Interface: parse_csv(raw: bytes) -> {events, source_sha256, report_count}; events use the original-field PredictionRequest shape. CSVError carries code/message/details/total_errors. Cover BOM, unsorted reports, blank IDs, missing/duplicate headers, extra/missing cells, invalid/negative/non-finite values, all-or-error and row caps. Write/run failing behavior tests, implement, run green, commit.

### Task 2: Analysis pipeline and bounded store

Create backend/analysis.py and tests/test_analysis.py. Interface: AnalysisService.analyze(raw)->AnalysisResult, demo()->AnalysisResult, get(id)->AnalysisResult; injected prediction/classification boundary defaults to public ml functions. Preserve latest-report provenance and normalize geometry/units, validate exact model ID coverage and probability/log consistency, handle unavailable predictor honestly. Bounded TTL store; source checksums, unique IDs, missing values and synthetic demo preserved. Red/green tests, then commit.

### Task 3: Anthropic configuration and grounded insights

Create backend/config.py, backend/insights.py, tests/test_insights.py and machine-readable schemas in contracts/. Load ignored .env.local/.env without overwriting process environment. Never print keys. Use the official Messages endpoint with structured JSON output, bounded timeout/output and no autonomous retry loop. LLM can select only valid observation codes for stored facts; render those facts server-side with citations and validate requested IDs. Missing key/provider error/refusal/malformed/unsupported claims return explicit unavailable. Test via a real local HTTP provider double and deterministic clock/analysis data; no live call without a user-entered key. Red/green, commit.

### Task 4: HTTP integration, real-file smoke and handoff

Extend backend/server.py; add tests/test_p2_http.py and update superseded bootstrap assertions intentionally. Routes: health/demo; multipart CSV POST /api/analyses (also text/csv convenience); stored analysis GET; insights POST; schema GET; CORS OPTIONS for configured development origins. Upload limits, consistent errors and no secret-bearing static files. Red/green HTTP tests; exercise the actual supplied test CSV through the pipeline and real HTTP endpoint. Update backend context/setup, ignored env example, exact contract details and P2 handoff. Run Python/JS/Beryl gates, fresh final review, push role branch and open/attach PR. No auto-merge or deployment.
