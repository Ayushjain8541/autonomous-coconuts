# P1 UI integration

The preserved P1 application remains in root `index.html`, `src/`, `package.json`, and `start.command`; it was built before the shared bootstrap arrived. This is a compatibility exception to the suggested `web/` layout, avoiding an unnecessary move/rebuild. P4 should review the root dependency/setup strategy before merge. Shared README, AGENTS, backend, model and contracts are not changed by this UI integration.

## Run

From repo root: `pnpm install`, `pnpm dev` (or `./start.command`). The UI normally opens at http://127.0.0.1:5173. Separately run the current fixture API: `python3 backend/server.py --port 8000`. `web/vite.config.ts` proxies `/api` to `COCONUTS_API_TARGET` (default http://127.0.0.1:8000). Change the environment variable before starting Vite for another local backend. No backend CORS change is needed. This proxy is a development arrangement; production host routing is a P4 integration decision. Cesium currently expects root-hosted `/cesium/` runtime assets. Vite preview is static UI preview and does not supply API routing.

Checks: `pnpm test` runs existing preview-data tests plus `web/tests/` contract, transport and state tests. It needs Node22.18+ or24+ for TypeScript test stripping; application build supports Vite's Node requirements. `pnpm typecheck` and `pnpm build` check the preserved UI and canonical adapters. Shared Python/Beryl checks remain separate and must not be confused with browser proof.

## Behavior and truth

Load Demo requests GET `/api/demo`. Default CSV selection sends multipart `file` to POST `/api/analyses`; the frontend does not parse the file or compute tiers. API errors remain errors with bounded structured row/column details; explicit unavailable predictions remain unknown/unavailable. A separate recovery button explicitly selects the canonical local fixture; there is no silent fallback. A separately labeled any-file **UI preview only** option preserves the original filename-only one-second satellite animation and35 canned preview rows. That state is not an AnalysisResult and does not add a source.mode to the contract. Real analysis preparation lasts as long as its API request, not a fake timer.

The result UI uses metres, hours, server probabilities/reasons and provenance. Zero Pc is rendered as0, null asUnavailable. Uploaded report-relative hours never become invented UTC dates. The global earliest critical alert is independent of filters; its36h canonical event persists when the exact critical-within24h list is empty. Selection identity survives filters. List, relative timeline and explicitly schematic globe-side controls share one event ID; no globe coordinates or observed orbits are invented.

Numeric details render before a separate insights request. Insights require matching analysis, selection/generation, known event IDs and allowed fact fields. Abort/generation checks reject stale responses. API503 renders unavailable without changing deterministic results. Only explicit local-fixture mode uses the canonical explanation fixture. Native geometry dialog displays supplied RTN vectors or missing geometry. **Trajectory acceptance remains open** pending P3 reference-epoch/relative-motion confirmation; static geometry is not trajectory coverage.

The old image-independent procedural3D satellite, magnetic Import interaction, spotlight chooser, renderer-native globe shading and responsive layout are retained. Source warnings, fixture/model status and source/checksum/report provenance are exposed. Imported strings and insight text are inserted using textContent.

## Dependencies to hand off

P2/P3 real upload/model and provider integration is currently unavailable in the shared bootstrap; successful fixture viewing does not close those outcomes. P3 must clarify trajectory reference epoch/assumptions. P4 must approve root UI placement/dependencies, production routing and deployment setup. Existing large Cesium/Three bundle and imagery service licensing remain explicit limits. No trained prediction, live LLM, certified maneuver or full-orbit claim is made.

## Dedicated visualisation update

The latest P1 brief replaces the dashboard overlay with actual `/encounters/:eventId` history routes. Same-tab refresh revalidates normalized session analysis through the canonical parser; no raw file contents are retained. Direct links without context show an honest missing-analysis page. Back/forward and in-memory dashboard search/risk/sort/horizon/scroll are retained. Production hosting must serve the root SPA entry for these deep links; P4 owns that hosting decision.

The neutral dashboard has actual result-count KPIs, stable search/sort and risk filtering. A dedicated page separates server classification, planning-review recommendation, predictions, reported facts and visualization-only state. Planning text uses returned severity only and is never a calculated maneuver. Age/disposition/timestamp/per-report source remain unavailable in current v1. Numeric facts render independently of insights; requests are aborted/invalidated on route exit, with client-side bounded waiting.

**Mode B is now implemented as explicitly authorized conceptual animation**, not deferred trajectory coverage: normalized approach/TCA/departure with a consistent scale and exact center gap at TCA equal to the returned miss distance. Zero is coincident centers; null is unavailable. RTN summaries are shown as source facts, never treated as ephemerides. The scene's satellite/debris are procedural representative models; no external/licensed model was downloaded. Object sizes are exaggerated and this is not a reconstructed orbit. A single normalized state drives models, line, labels and playback. Rubber-band overshoot is visual only. True Mode A propagation still requires time-indexed positions/epoch data from upstream; no physically reconstructed trajectory claim is made.
