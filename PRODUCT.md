# Product context
<!-- impeccable:product-schema 1 -->
## Platform
web

## Stack
Preserved TypeScript/Vite application. CesiumJS renders the existing Earth; Three.js renders the procedural loader and local encounter schematic. No framework migration.

## Confirmed primary journey
Satellite operators load the visibly synthetic API demo or submit CSV to the canonical API, prioritize returned encounters, and open `/encounters/:eventId` for intelligence, source-report facts and interactive conceptual encounter geometry. Backend owns validation/predictions; P3/P2 own authoritative severity. Frontend never recomputes risk tiers. Separate any-file UI preview remains clearly labeled and does not parse/upload the file.

## Data truth
Canonical v1 has predicted/reported Pc, lead hours, miss distance in metres, severity, reasons, model/source/report identities and optional RTN summary vectors. It lacks report creation timestamps, age, disposition, per-report source, object classification, ephemerides and global reference epochs. These appear unavailable rather than invented. Report age requires an explicit valid source timestamp and reference clock; lead time is not age.

## Visual requirements
A restrained mission-control dashboard with neutral rows, compact KPIs, search/sort/risk filtering, persistent global alerts and the original shaded Earth. Selecting an encounter navigates to a separate page; no dashboard details overlay. Local normalized Mode B animation is explicitly illustrative, constrains center separation at TCA to actual miss distance and does not propagate RTN states or claim real trajectories. Null miss distance is unavailable; zero means coincident centers. Models are representative and sizes exaggerated. Magnetic Import, spotlight chooser and one-second procedural satellite preview remain.

## Limits and open dependencies
Actual upload/model and LLM integration remain dependent on P2/P3; current bootstrap returns explicit503 for those operations. Real report timestamps/disposition/source and physical ephemerides require upstream contract additions. Production API routing/root frontend placement needs P4 review. Earth imagery detail and licensing vary. No maneuver is computed, executed, approved or certified by this UI.
