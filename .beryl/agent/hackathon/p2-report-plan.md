# Risk briefing and PDF implementation plan

User direction: expand P2 into an analytical portfolio report and supported advisory actions; keep the website concise and offer detailed PDF export. Maneuver simulation is a separate P3 proposal while the user chooses illustrative versus operational inputs. Existing v1 analysis/insights stay compatible; do not edit web/, ml/, development/ or prediction/ implementations.

Execution: Superpowers inline under the existing user opt-out of repeated approval interviews. Existing isolated role worktree, Python 3.9+, Anthropic access already verified. Main's P3 workflow was merged without changing its row-risk target or claiming adapter compatibility.

## Review Focus
- Unknown/fixture model results and per-report clocks remain explicit in report and PDF.
- Hallucinated references/numbers or unsupported execution recommendations are rejected; free text is not a proof of operational correctness.
- Portfolio counts cover all encounters although prose input is bounded to ten priority encounters.
- PDF escapes source text and preserves source/assumption labels, pagination and evidence.
- Existing endpoints remain compatible; download identifies the exact generated report and does not trigger a paid GET.

### Task 1: Analytical report service
Create backend/reports.py and tests/test_reports.py; extend AnthropicClient with reusable generate_structured(system, content, schema, max_tokens), preserving select behavior. ReportService.generate(analysis) builds whole-portfolio statistics, bounded deterministic priority inputs and a fact catalog, calls Anthropic, validates reference identities/numbers/action eligibility, and caches/stores a uniquely identified report. ReportService.get(analysis_id, report_id) returns isolated retained data. No unsafe exact maneuver instructions; action IDs cover review, tracking, missing prediction/geometry and request flight-dynamics assessment. Tests: counts beyond top ten, free-form supported prose, unsupported refs/numbers/actions, unavailable provider/unknown model, exact report retrieval/cache isolation. RED then minimal implementation then GREEN; commit.

### Task 2: PDF and HTTP delivery
Create backend/report_pdf.py, backend/requirements.txt and tests/test_reports_http.py. POST /api/analyses/{id}/report accepts {}; GET /api/analyses/{id}/reports/{report_id}.pdf downloads the exact report without a new provider call. render_pdf(report) returns ReportLab bytes; absent optional PDF dependency is an actionable 503. Existing numeric API stays dependency-free. Add report schema/examples, precise P1 integration instructions and P2 handoff with P3 simulation proposal. Tests: real HTTP generation/download, unknown IDs, provider unavailability, escaped/multipage text and existing API regression. Install PDF dependency in ignored backend/.venv for actual export; PDF tests skip explicitly in environments without that extra. Generate/render/inspect a labeled demo sample; full checks and one aggregate review; commit/push update existing P2 PR, no merge/deploy.
