# P2 — Backend and grounded LLM insights

**Owner:** P2. **Suggested branch:** `p2/backend-llm`. **Scope:** `backend/`, shared `contracts/`, canonical contracts.md, backend dependencies/setup/checks and handoffs/P2.md. **Requirements:** A1-01/04, U-01/03; integration of P3's A1-02/05. Full role outcome remains open; a replaceable bootstrap exists with local folder instructions and verified setup/check commands.

## Read

Root AGENTS.md → [product brief](../product-brief.md) → this file → [contracts](../contracts.md)/examples → relevant source. Consult P3 only for the actual adapter and manifest, P1 for consumed response shape. Choose your framework, provider adapter, architecture and working method; the shared contract is the coordination boundary. Python with a local P3 adapter is a suggestion, not a mandated stack.

## Outcome you own

Validate/upload reports, normalize source types without changing meaning, group by event, invoke P3's predictor and authoritative classifier, and return traceable analysis. One assessment per event, complete ID coverage, preserved source units/provenance and explicit unknown/error states. No final-risk target leakage or silent substitution of reported Pc for a model result.

Implement bounded LLM insights over stored authoritative analysis facts, separate from the numeric analysis response. Validate shape/references and guard against CSV text being treated as instructions. Missing access, unsupported claims, timeout and provider failure yield explicit unavailable insights while numeric results remain usable. Do not fabricate a successful live call or create accounts/keys without authorization.

## Interfaces and dependencies

Own proposed HTTP routes, examples and eventual machine-readable validation schema. Coordinate revisions with P1/P3; do not change field names independently. The model boundary in contracts.md is logical; agree actual local-call/service packaging with P3 and record it. Model artifacts/manifests belong to P3. A development stub can unblock transport checks but must be labeled and replaced before claiming inference integration. The synthetic Load Demo response is a distinct mode from uploaded analysis.

## Acceptance outcomes

- The supplied-format CSV parses; required input errors identify row/column and are not silently dropped. Source values, units, event IDs and report counts are preserved.
- Responses match the agreed contract, with one result per event and no non-finite JSON numbers. Duplicate/missing model output IDs are detected.
- A real P3 adapter is invoked for uploaded analysis; model unavailable is explicit. API health distinguishes dependency configuration from product success.
- Insight generation is bounded, grounded in known event/fact references, and isolated by analysis ID. Provider failure leaves the deterministic result available.
- P1 can use the real API with its documented origin/proxy configuration. Upload/retention limits and exact setup/check commands are recorded.

Choose meaningful parser/contract/integration checks and preserve actual results in your handoff. P4 can help test/upload/error behavior after a scoped claim; they do not own your API/schema decisions. Do not deploy or modify shared hosting/configuration without coordinating with P4.
