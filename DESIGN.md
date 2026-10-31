# Encounter console design
<!-- impeccable:design-schema 1 -->

## Authority and mode
Operate. Latest P1 dashboard/Encounter Visualisation brief supersedes prior neutral rows, repeated selection aids and verbose intelligence. The existing realistic shaded Earth and Import kinetics are retained. No approved Figma design was supplied. Parent researched official Linear, Vercel, shadcn, Grafana and Carbon references; implementation follows their restrained hierarchy/table clarity rather than cloning a template.

## Tokens
Background #0B0F14; primary #121923; secondary #1A2430; border #263241; primary text #E7EDF5; secondary #A7B5C6; accent #4C9AFF; focus #86BAFF. Risk red/amber/green appears as subdued whole-row tint plus readable status text and actionable alerts. Rows have distinct hover/focus. UI sans stack with Inter when available, tabular measurements, 4/8-based spacing. Main panels16px, cards12px, controls8–10px, severity pills.

## Dashboard
Semantic application header with identity, source/model indicator, timeframe, Load Demo and Import. Compact KPIs derive from returned encounters; no risk engine. Search, risk selector and stable sort operate on existing horizon filter. Main table and original Cesium context remain balanced desktop panels. The redundant Relative horizon and schematic globe-selection lists are removed. A discrete 24h / 3d / 7d / All rubber-band slider filters membership, never classification. Whole rows and event links navigate by event ID. Default order is Critical, Elevated, Safe, Unknown; lead time and event ID break ties. Global critical alert is independent of list filters. The canonical36h alert persists beside the exact empty critical24h message.

## Encounter page
Dedicated history route with Back, event identity, compact source indicator. Option B intelligence contains a planning alert, prominent risk class and three metric values. Risk is not repeated in the header. Metrics count up once with ease-out-cubic, stable Pc exponent, exact final formatting and reduced-motion bypass. Disabled Download Latest Source Report control includes Coming soon; optional data disclosure separates reported Pc from predictions; age/timestamp/disposition/per-report source are Not provided. Progressive technical details expose provenance, server reasons and RTN values without an excessive raw panel. Expandable AI Insights requests a canonical grounded explanation on demand, without a fake chat input. Insights remain independent and explicitly pending/fixture/ready/unavailable. Validated normalized analysis is retained in session storage for same-tab refresh; raw CSV is not stored. Missing deep-link context is explicit.

## Scene and controls
A compact dedicated camera toolbar sits outside the canvas. Only “Illustrative encounter” remains as a scene label; detailed source/scientific safeguards are available in optional Scene information and Data and scene information. The canonical synthetic fixture may show a short linear local approximation from its returned complete RTN vectors, explicitly assuming that fixture state is at TCA. Provenance, finite-vector, positive-speed, perpendicularity and miss-distance consistency guards prevent this mode for unknown states or imported analyses. No backend contract epoch or orbital trajectory is inferred. Missing/unconfirmed geometry gets no fabricated event motion. Primary remains local origin; cyan position and amber velocity, TCA annotation and current separation all share the same state. Persistent predicted miss distance is independent of current separation. Jump to TCA pauses; automatic passes hold 1750ms. Camera and resource cleanup retain existing behavior.

## Layout and limits
Desktop intelligence scrolls beside a scene fitted to the viewport so playback remains accessible. Narrow screens stack compact intelligence with collapsed reports/explanations, then full-width scene, keeping DOM and keyboard order aligned; Earth context is omitted in the narrow encounter page to prioritize the local scene, while dashboard Earth stays. Source/imagery credits remain preserved. Renderer/load failures leave numeric facts usable. API waiting is bounded with explicit retryable failure; existing deterministic results survive failed loads.


## Final P1 refinement

The default `/` surface uses the existing photographic Earth beside a restrained product hero. `/dashboard` retains the risk-monitoring layout, with muted blue/red/amber KPI treatments and an explicitly illustrative orbital animation. Encounter pages hide the Earth section completely and use a compact dark glass-inspired intelligence widget, bordered 14px/26px metrics and a dominant local scene. All severity alerts emphasize once for 700ms; layered gradient-clipped risk-word sweeps have Pause effects, and all effects/count-ups honor reduced motion. XYZ labels map to RTN for schematic orientation only.

The Cesium orbit is a presentation-only loop independent of analysis. The canonical synthetic fixture illustrates actual response RTN vectors under an explicit synthetic at-TCA assumption; uploaded geometry remains unpropagated pending P2/P3 epoch confirmation.

## Shared import refinement
Landing and dashboard invoke the same DOM panel, file input, API handler and error area. The panel anchors to its current invoker with identical bounded width, entrance/exit and spotlight selection. Escape/Close restore the invoker; outside click closes. It is nonmodal and normal Tab navigation remains available. Cancel/failure preserve route/data; successful API import opens dashboard. Landing copy uses the user’s exact simplified wording.
