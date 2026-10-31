# Integration readiness

## Beryl and local baseline

Installed using upstream install.sh from a clean Git checkout pinned to c2d2c6c86d2bf0ffe0647883c0ccd2bdd69791ab, standard profile. Genuine installer-generated lock records the ref, managed surface and root-conflict decisions. Existing project context was backed up and restored; root AGENTS.md is an explicitly preserved external contract. Tool shims are generated from the adapted template and point to the same project policy. Hooks were not enabled. No handwritten lock or fake installation was used.

The companion scaffold ea5111ff8d9cc54c8bf6e8c972462ff21b659eee was reviewed for its baseline pattern; this existing repository was adapted in place, not passed to its new-project generator. Python 3.9+ and the standard library are enough to run the local browser/API fixture. No packages/accounts/provider credits are required. Development server is local infrastructure, not a production-hosting decision.

## Boundaries actually exercised

Baseline checks exercise real local HTTP GET /api/health and GET /api/demo, source labeling and shared risk rules. The browser Load Demo action calls the same API. Exact verification observations and remaining gaps are recorded in handoffs/bootstrap.md. Fixture connectivity does not establish trained inference, CSV ingestion or live LLM access.

## Still role-owned/unverified

- P3: training data, trained artifact, genuine prediction/evaluation and supported horizons.
- P2: CSV validation/grouping, model adapter integration, provider selection/access, representative structured output, grounding and observed latency/quota/cost.
- P1: finished linked views/trajectory coverage/accessibility beyond the bootstrap shell.
- P4: deployment/submission access and final real-product end-to-end verification.

Keep raw source data and secrets local. Missing provider/model returns explicit unavailable; it does not silently become a fixture success. No deployment or external messaging performed by this bootstrap.
