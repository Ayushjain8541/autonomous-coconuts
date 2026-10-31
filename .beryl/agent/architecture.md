# Architecture and ownership

| Area | Owner | Responsibility | Public boundary |
| --- | --- | --- | --- |
| web | P1 | Browser shell, future operator views | HTTP contract; web/docs/agent-context.md |
| backend | P2 | Local fixture transport, future CSV/API/LLM | GET /api/health, GET /api/demo; backend/docs/agent-context.md |
| ml | P3 | Authoritative tiers, unavailable prediction adapter, future model | ml.predict_batch and ml.classify_encounter exported by ml/__init__.py |
| contracts | P2 with consumers | Shared semantics/examples | hackathon/contracts.md and JSON fixtures |
| docs/tests/shared setup | P4 coordinates | Scoped supporting tasks and integration evidence | Local instructions and role handoff |

These are technical ownership areas, not three invented domain bounded contexts. Lightweight local docs are used; full module-agent generation is unnecessary. No third-party package, provider account, database or production deployment is required for this baseline. P1/P2/P3 may replace internal frameworks while coordinating interfaces.

The backend serves only three allowlisted browser assets. Demo Pc values remain synthetic; the real rule function recomputes their tiers. The predictor returns unavailable rather than a fabricated learned result. CSV analysis/live insights endpoints are explicit unavailable responses. Browser and API are same-origin in this local server. No source data or credentials are served as static files.
