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


## Compact dashboard follow-up

Dashboard horizon stops are 24 hours, 3 days, 7 days and All. Their logical values snap to valid stops; pointer overshoot moves the thumb at 32% resistance only. Default risk order is Critical, Elevated, Safe, Unknown with lead-time and event-ID tie-breakers. Global alerts do not use filtered membership. Repeated relative-horizon and schematic globe-selection lists are removed. Full-row subdued tint always accompanies risk text.

Encounter pages use one compact intelligence panel, once-per-entry count-up metrics, collapsed source report and on-demand expandable canonical Insights. No freeform chatbot endpoint is invented. The satellite is fixed at the conceptual local origin; a generic debris model moves on a deterministic 3D illustrative template. Current v1 RTN geometry has no validated at-TCA epoch/permission, so **Relative-motion data unavailable** remains visible; neither vectors nor scalar relative_speed drive claimed physical motion. `miss_distance_m` constrains exact illustrative TCA separation only. Actual propagation awaits P2/P3 confirmation and permitted-data rules. Raw CSV is never parsed by the UI or committed.


## Final refinement routing and 3D scope

- `/` is the landing page; Launch Dashboard opens `/dashboard`. Successful demo/upload/local-fixture/filename-preview flows open the dashboard. Encounter links remain `/encounters/:eventId`; back returns to `/dashboard`. Session-retained normalized analyses resolve refreshes; no unknown event is fabricated.
- Dashboard satellite/debris loops use Cesium-native entities and a procedural Canvas satellite billboard. These are decorative geocentric loops, never encounter telemetry; reduced motion freezes them and navigation/hidden tabs stop their animation resources.
- Encounter Earth is hidden and inert. Local axes label X→R, Y→T, Z→N as schematic orientation. Cyan position arrows follow the illustrative current position; a validated velocity arrow is unavailable. Source geometry is retained separately in technical details without propagation.
- Playback pauses its actual phase clock at exact TCA for 1.75 seconds once per automatic pass; manual seeking does not trigger hold loops. Jump to TCA pauses and retains line/annotation. Minimum predicted distance remains visible throughout.
- Debris is an original procedural smooth perturbed icosphere, not a downloaded NASA asset. No external asset attribution or additional license is required. Generic shape does not assert object identity.
- Browser visual verification for this refinement is unavailable while local-browser access is disabled; source-level responsive checks do not establish rendered fidelity.

## Consolidated refinement (supersedes earlier scene/report descriptions)
Landing and dashboard open the exact same reparented nonmodal Import panel and canonical API file input. File cancellation and failures retain current route/analysis; errors render inside the shared panel. Escape/Close return focus to its current invoker. Upload success alone navigates to dashboard; the separately labelled UI preview remains filename-only. One shared surface supplies identical dimensions, entrance/exit, validation, spotlight and busy state.

The selected Encounter and AnalysisResult now reach playback, fixing the dropped-geometry boundary. Only the canonical synthetic fixture, fixture model/prediction status, complete finite RTN vectors with positive speed, r·v≈0 and |r|≈miss distance enable a short synthetic local linear approximation r(t)=r0+v·dt. The explicit at-TCA assumption and ±seconds interval are in optional Scene information; they are not added to contracts. Uploaded/unconfirmed/missing geometry never obtains fake event vectors/motion. Source metadata remains available in optional Data and scene information. Persistent predicted miss distance and current simulated separation stay distinct; TCA line/label and1750ms hold share the existing clock.

The viewport retains one small Illustrative encounter label; camera controls and optional information use normal flex layout outside the canvas. Download Latest Source Report is a disabled future control with icon/Coming soon and no URL or fabricated download. Layered severity-gradient pseudo-elements animate the risk word with a Pause effects control; severity-specific text/icons use authoritative server severity. Every alert text pulses once700ms per page mount. Reduced motion shows final metrics without animation. No browser-observed fidelity is claimed while local browser access is disabled.


## Integrated analytical PDF and consumer connections

The encounter page has a **Download Analytical PDF** control for the full analysis. It is separate from the disabled latest-source-report placeholder. It posts `{}` to the existing singular `/api/analyses/{analysis_id}/report` endpoint, validates analysis/source/model identity and the exact relative PDF route, then fetches the export before starting a native blob download. Unavailable narrative can still produce a deterministic analysis PDF; `PDF_UNAVAILABLE`, provider warnings and connection/timeout errors remain explicit. Local UI previews cannot request backend reports. Navigation aborts pending generation/export and releases object URLs.

Insight waiting is bounded at 75 seconds; report generation and PDF retrieval each have a separate 100-second client limit, beyond the backend's permitted 90-second provider deadline. The UI accepts same-event `geometry` fact references and canonical `total_errors` validation counts (legacy `total_error_count` remains a fallback). Demo motion now matches the canonical synthetic content and provenance rather than its original analysis ID, allowing fresh API demo identities while rejecting changed geometry, provenance and uploaded epoch-free states. No telemetry or risk rules change.

Both Vite development and preview proxy `/api` to `COCONUTS_API_TARGET` (default `http://127.0.0.1:8000`). This is local development/preview configuration, not production hosting.
