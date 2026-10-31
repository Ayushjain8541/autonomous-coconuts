# Encounter console design
<!-- impeccable:design-schema 1 -->

## Authority and mode
Operate. Latest P1 dashboard/Encounter Visualisation brief supersedes prior whole-row severity tints and globe details overlay. The existing realistic shaded Earth and Import kinetics are retained. No approved Figma design was supplied. Parent researched official Linear, Vercel, shadcn, Grafana and Carbon references; implementation follows their restrained hierarchy/table clarity rather than cloning a template.

## Tokens
Background #0B0F14; primary #121923; secondary #1A2430; border #263241; primary text #E7EDF5; secondary #A7B5C6; accent #4C9AFF; focus #86BAFF. Risk red/amber/green is reserved for compact textual badges and actionable critical alerts. Neutral rows have distinct hover/focus. UI sans stack with Inter when available, tabular measurements, 4/8-based spacing. Main panels16px, cards12px, controls8–10px, severity pills.

## Dashboard
Semantic application header with identity, source/model indicator, timeframe, Load Demo and Import. Compact KPIs derive from returned encounters; no risk engine. Search, risk selector and stable sort operate on existing horizon filter. Main table and original Cesium context remain balanced desktop panels. Relative-horizon and explicitly schematic selection links navigate by event ID. Global critical alert is independent of list filters. The canonical36h alert persists beside the exact empty critical24h message.

## Encounter page
Dedicated history route with Back, event identity, source and risk. Compact intelligence answers severity, operator-planning review, relative lead time, predicted Pc and miss distance first. Report card separates reported Pc from predictions; age/timestamp/disposition/per-report source are Not provided. Progressive technical details expose provenance, server reasons and RTN values without an excessive raw panel. Insights remain independent and explicitly pending/fixture/ready/unavailable. Validated normalized analysis is retained in session storage for same-tab refresh; raw CSV is not stored. Missing deep-link context is explicit.

## Mode B scene and controls
Procedural representative satellite and generic debris share one deterministic normalized parameter. Local center separation at exact TCA equals actual miss_distance_m under a single displayed scale; zero is not padded, null disables the schematic. The mandatory illustrative/not-reconstructed disclosure and exaggerated-size note remain visible. RTN summary data is not silently propagated. Camera orbit/zoom/reset is separate from Play/Pause/Restart/Jump-to-TCA/speed. Rubber-band drag clamps logical phase0–1 while only the thumb overshoots visually; release preserves phase. Pointer/touch/keyboard and reduced-motion spring handling are supported. No autonomous playback, camera movement or unrelated CSS object motion. RAF, observers, controls, geometry/materials, renderer and insight requests are cleaned on route exit. Earth is a separately labeled complementary context viewport, not an inferred encounter location.

## Layout and limits
Desktop intelligence scrolls beside a scene fitted to the viewport so playback remains accessible. Narrow screens stack assessment, full-width scene, reports and explanations; Earth context is omitted in the narrow encounter page to prioritize the local scene, while dashboard Earth stays. Source/imagery credits remain preserved. Renderer/load failures leave numeric facts usable. API waiting is bounded with explicit retryable failure; existing deterministic results survive failed loads.
