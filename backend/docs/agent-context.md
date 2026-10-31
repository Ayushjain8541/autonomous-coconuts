# P2: backend and LLM context

Own transport, CSV validation/grouping, API/schema decisions, orchestration and grounded insights. Read root AGENTS.md, product brief, P2 ticket and contracts.md. Framework, provider and internal design are yours; coordinate shared boundaries with P1/P3.

## Current local map

`server.py` is a local Python 3.9+ standard-library fixture server; no packages or API keys required. It serves only web/index.html, app.js and styles.css. `GET /api/health` reports model unavailable and insights unconfigured. `GET /api/demo` loads the synthetic fixture and calls P3's public risk-rule entrypoint. Upload/model and live-insights POST routes explicitly return 503 until implemented. No CSV parser, retained analysis store or live LLM exists yet. This server is not a production-hosting choice.

## Commands and boundaries

From repo root: `python3 backend/server.py --port 8000`; `python3 -m unittest discover -s tests -v`; `python3 scripts/check.py`; `./.beryl/scripts/check.sh`.

Optional shell settings: COCONUTS_HOST/COCONUTS_PORT, or CLI flags. `.env.example` is documentation; the baseline does not load .env automatically. Do not print credentials. No provider is chosen or configured by the scaffold.

Use the public `ml` package boundary and shared contract, not training internals. A classifier does not imply a trained model. If replacing the runtime, preserve endpoints/types/error semantics or coordinate amendments with P1/P3; update actual setup commands, test adapter and CI together. Provider access and real representative-call latency remain your integration investigation. Handoff: .beryl/agent/hackathon/handoffs/P2.md.
