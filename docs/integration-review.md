# Integration review — 31 October 2026

User scope: fetch all published work, review integration, then **do not change any UI**. All temporary frontend edits were reverted. This branch has no changes under `src/` or `web/`, and does not change P3's model, predictor, training or classification source.

## Integrated on this branch

- Latest main includes the merged P1 console and P2 API/report work. The separate P3 model-benchmarks branch is merged locally, preserving its authored benchmark documentation and tests.
- The HTTP service now calls P3's frozen per-report predictor through `backend/model_adapter.py`. Previously `backend/analysis.py` defaulted to the explicitly unavailable `ml.predict_batch` stub. Installing the model alone could never make an upload produce learned scores.
- The old >=2-day filter is removed. The user-approved target is the latest report's Pc estimate. Prediction and displayed distance/geometry now use the same report; provenance identifies that report. Reported risk is kept separate and excluded from the feature frame.
- Root `.venv` can host model inference and PDF export together. The launcher starts both existing servers, rejects occupied ports, supports configured local ports, and cleans up only its own children. No frontend appearance or behavior is redesigned.
- Actual-model precision is supported in grounded text. Canonical source briefings use sufficient precision; an explicitly supplied two-decimal hour display is supported without accepting unrelated numbers. A multi-event finding may cite the supplied detailed-cohort count when all its members are already cited. An unsupported numeric key finding is replaced with cited source facts and an explicit warning; invalid identities/references and unsupported executive/assessment/action claims still fail.
- The pinned Beryl markdown checker also traverses ignored dependency folders. CI runs its complete source gate before dependency installation; local source gates are verified from a clean worktree. Full native/frontend checks run separately in the populated development environment; no managed check is weakened.
- CI now exercises the existing frontend tests/build and P3 tests as well as backend checks. Generated Cesium assets are ignored and recreated by the existing postinstall script.

## Remaining P1 connections — deliberately unchanged

| Priority | Source | Concrete issue / reproduction |
| --- | --- | --- |
| Medium | `web/client/contract.ts:9,37` | `geometry` is allowed by the published insight schema and may be cited by review advice, but `factFields` omits it. A valid same-analysis insight citing geometry throws `unsupported insight fact reference`. The page catches this as an error; it cannot display that otherwise valid explanation. |
| Medium | `src/encounter-page.ts:12`; `web/client/api.ts` | The only report control is a disabled **Download Latest Source Report / Coming soon** placeholder. No client calls the analytical-report endpoint. P1 should connect a clearly named analytical PDF control, distinguish it from a source report, allow the backend's report deadline, and surface unavailable narrative/PDF errors. |
| Medium | `web/client/encounter-model.ts:88-91` | `encounterMotion` requires the literal canonical fixture analysis ID. GET /api/demo deliberately gives each copy a fresh ID. Thus API Load Demo shows relative-motion data unavailable and disables playback despite supplying the canonical synthetic RTN vectors. Preserve provenance checks while accepting a content-matching canonical demo with a fresh identity; do not enable orbital playback for uploaded epoch-free records. |
| Medium | `web/client/contract.ts:43` | The parser reads `total_error_count`; backend validation sends `total_errors`. Individual details survive but the true total is lost when the error list is capped. Accept the canonical backend key. |
| Medium | `src/encounter-page.ts:35` | The browser aborts after 25 seconds, equal to the default provider deadline before network/process cleanup. The backend permits up to 60 seconds. Legitimate slow completions can be cancelled by the consumer. |
| Medium | `web/vite.config.ts:2` | Development has an `/api` proxy, preview does not. `pnpm preview` cannot run the API-backed journey through the same origin without additional proxy/hosting configuration. Use the integrated development launcher for the current demo. |

These are separate from model accuracy. P3's existing README discloses that combined tier agreement is dominated by the distance rule, and probability-only critical recall is 16.74% on supplied reports and 3.62% on its event-separated holdout. Wiring the model does not improve those metrics. Training/benchmark code and weights are unchanged.

## Verification

The supplied CSV contains 24,484 reports across 2,167 encounters. The real saved artifact returned ready estimates for all 2,167, producing 181 critical, 465 elevated and 1,521 safe assessments. Native analysis took 1.26 seconds in one local smoke check; HTTP upload took 1.69 seconds in another. These are measured local observations, not performance guarantees or model-accuracy evidence. The P1 analysis parser accepted the actual response.

The original P1 landing → API Load Demo → critical-within-24h filter → global 36-hour critical banner → encounter selection flow was inspected in the browser. The consumer gaps above were recorded rather than changed after the user's scope correction. Backend-only native upload/insight/report/PDF checks and final test totals are recorded in the P2 handoff.

## Review summary

| Severity | Unresolved count | Status |
| --- | ---: | --- |
| Critical | 0 | None found in reviewed application paths |
| High | 0 | Model-wiring and stale-window blockers addressed |
| Medium | 6 | P1 consumer/configuration items above; unchanged by request |
| Low | 0 | No style-only findings included |

Verdict: backend integration is ready for coordinated review; frontend wiring remains with P1. This is a runtime/contract review, not a formal proof of every free-form model statement or an audit of vendored skills/dependencies.
