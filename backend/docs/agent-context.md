# P2 backend and LLM context

Read root AGENTS.md, the product brief, P2 role brief and shared contracts. P2 owns backend/, shared API schemas and its tests; leave web/ and ml/ changes with P1/P3. Choose implementation tools freely. This P2 pass uses Superpowers inline execution, focused red/green tests and verification under direct user authorization.

## Actual map

- server.py: real local HTTP routes, bounded multipart/raw CSV uploads, retained result retrieval, insights requests, schemas and development CORS.
- ingestion.py: strict all-or-error CSV parsing into the public P3 request shape; source units/types/provenance preserved.
- analysis.py: invokes public ml functions, validates model outputs, selects latest source report, normalizes response/geometry and stores bounded TTL results.
- config.py: reads ignored .env/.env.local plus process environment, without executing or logging secrets.
- insights.py: bounded Anthropic Messages structured-output call; validates supported observation selection and renders grounded explanations/citations; explicit unavailable state on failure.
- reports.py: full LLM narrative, portfolio counts, cited priority assessments, advisory actions and deterministic P3 rule-sensitivity what-ifs; exact report retention/cache.
- report_pdf.py: optional ReportLab export with provenance, action rationale and comparison tables. Install backend/requirements.txt in the server environment.
- README.md: exact setup, API recipe, limits and P1/P3 integration details. No external runtime dependency or API key is required for upload/numeric paths.

## Commands from repo root

`python3 backend/server.py --port 8000`; `python3 scripts/check.py`; `./.beryl/scripts/check.sh`. Local manual configuration is ANTHROPIC_API_KEY in ignored .env.local. Key changes are read without restart; Python code/model adapter changes need restart. No key file is distributed via Git.

## Boundaries and truth

HTTP keeps the shared v1 contract; schemas are in contracts/*.schema.json. prediction_report_ids is additive provenance for the restricted >=48h model input window. Fact references may include geometry. Public ml.predict_batch and ml.classify_encounter remain P3-owned. The current P3 adapter returns unavailable, so do not label null predictions or reported Pc as learned inference. The synthetic demo remains labeled. No global orbit coordinates are invented.

The old insight endpoint selects supported observations. The additive report endpoint writes actual narrative with validated references/numeric membership, eligible actions and explicit interpretation limits. What-if inputs are assumptions, not a maneuver optimizer or model-predicted improvements. Missing key, provider failure, refusal, unknown references or invalid output never blocks numeric analysis. Full reports use a separate 60s default deadline (maximum 90s); all provider calls share two global slots. API/retention limits, status codes and origin configuration are documented in backend/README.md. The server remains local development infrastructure, not a production deployment.

Handoff and actual check evidence: .beryl/agent/hackathon/handoffs/P2.md. Update test manifest intentionally when adding tests. Preserve teammate changes; coordinate contract changes and PR integration.
