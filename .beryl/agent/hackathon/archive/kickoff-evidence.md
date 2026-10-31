# Evidence and integration readiness

## Sources actually consulted

- User-provided `Autonomous SG 2026_Airbus Track.pdf`: 8 physical pages. Challenge #2 occupies physical pages 2–3; weighted rubric physical pages 7–8. Read text and visually inspected these relevant pages. File fingerprints below identify the exact local originals; originals are not committed.
- User-provided `Autonomous SG 2026_NUS Hackers.pdf`: 3 physical pages; text read for the alternative track and rubric.
- [hackathon-coordinator](https://github.com/Ayushjain8541/hackathon-coordinator), revision `4e28870e3cd11808607e9751be574ea7465b7aeb`: README, installer source, skill entrypoint, kickoff/ideation/bootstrap/UI/capability references and idea-card template. The installer was reviewed before use. MIT license preserved in root notices.
- Installed `superpowers:brainstorming`, plugin 7.0.1: read directly for product discovery; full source locator and stage status in kickoff.
- [BTS explanation of on-time performance and delay causes](https://www.bts.gov/explore-topics-and-geography/topics/airline-time-performance-and-causes-flight-delays): verifies that delay causes are reported categories and distinguishes late-arriving aircraft, weather and NAS. This is contextual evidence, not the organizer's exact CSV schema or a source of operational fuel/gate limits.

No external idea catalogs, market/pricing claims, current provider quotas, flight safety standard thresholds, or claimed production deployments were used.

## Organizer dataset

Folder printed in the Airbus brief: [organizer Drive folder](https://drive.google.com/drive/u/1/folders/13h0JZnSqhYTX3rV8dGDGy5AiwaADQvJR).

- Expected path from source: `Challenge #2/DATA`; 2015 US DOT flight delays/cancellations.
- Required predicate: `WEATHER_DELAY > 15 OR LATE_AIRCRAFT_DELAY > 20`.
- Access attempted: connected Drive fetch returned 404 for the folder; web open also inaccessible. This does not prove the folder is absent; current access is insufficient or the link may need checking.
- Actual files, columns, row counts, file size, units, license and qualifying rows: **unverified**. No dataset file or representative real row was downloaded. Do not substitute another dataset silently.
- Next evidence: accessible folder/file, checksum, header/units, one qualifying raw row and row identifier, malformed/missing-value handling, timezone/date handling. Preserve raw source fields and transformation notes.
- Gate availability, runway separation rules, taxiway topology, reserves, turbulence, crew windows and passenger itineraries: **not verified**. Treat separately supplied demo inputs as simulations with explicit provenance. Never label assumed thresholds as certified safety logic.

## Model, runtime and deployment

Not selected or tested. No API keys created, copied or printed; no provider account configured; no model call made; no hosting resources created. The planning stage must verify a representative structured message using actual access, schema validity, latency, budget and timeout behavior before the team builds around it. A deterministic fallback cannot prove that independent AI negotiation works.

## Repository connection and preparation checks

Local authenticated `gh` verified `viewerPermission=ADMIN` and `isPrivate=true`. The repository had no commits/refs before preparation. The GitHub connector returned 404; local `gh`/Git provides working access. No visibility or account settings changed.

Preparation verification is limited to copied skill integrity, document/source consistency, local links, Git diff checks and remote readback after publication. No runtime behavior, tests, benchmarks, real agent negotiation, operational feasibility or delay reductions are claimed.

## Original file fingerprints (SHA-256)

- `Autonomous SG 2026_Airbus Track.pdf`: `540ac5bc79d8ed9906c00da11a5bc215362f4d2e9f9be50590931e1397875a6c`
- `Autonomous SG 2026_NUS Hackers.pdf`: `142d28993847cde79ee4f4cbc34fcb58dea2eb6547898ef4007029ed798dd506`
