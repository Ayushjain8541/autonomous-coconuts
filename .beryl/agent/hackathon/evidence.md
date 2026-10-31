# Sources and observed readiness

## Supplied files

- `Autonomous SG 2026_Airbus Track.pdf`: 8 physical pages; Challenge #1 pages 1–2, weighted Airbus rubric pages 7–8. Exact challenge extraction in airbus-1-original.txt. Relevant #1 text read; rubric pages visually verified. Original PDF not committed. SHA-256 `540ac5bc79d8ed9906c00da11a5bc215362f4d2e9f9be50590931e1397875a6c`.
- `test_data.csv`: directly inspected from the user's supplied local file. **24,484 reports, 2,167 unique event IDs, 103 columns**. `risk` is populated; repeated IDs are report updates. `time_to_tca` minimum `2.000213078703704`, maximum `6.993168715277778` days; no supplied row is within 24h or 36h. Actual data/hash recorded, not hypothetical. SHA-256 `fc4110e979e7d569cb8aa819d450d29311e799115b2fe5b519b8a18eafa37323`. Raw file (~35.3 MB) is not committed; P3/P2 need local copies.
- `Autonomous SG 2026_NUS Hackers.pdf`: previously read for alternative-track context, not current build requirements. Historical source notes are in archive/kickoff-evidence.md.

## Dataset interpretation

[ESA data documentation](https://live.kelvins.esa.int/collision-avoidance-challenge/data/) matches the supplied schema and counts. Each row is a report for a target/chaser encounter; event_id groups a series. Source time is days; miss distance metres; relative speed metres/second. Earlier reported risk is not the withheld final target. The original competition forecasts final risk from earlier available reports; do not confuse reconstruction of a provided risk value with that forecast.

The organizer's [Drive folder](https://drive.google.com/drive/u/1/folders/13h0JZnSqhYTX3rV8dGDGy5AiwaADQvJR) returned 404 with the connected account and was inaccessible to the web tool. Direct user delivery resolved access to the test file on this machine only. **Training data is still not supplied/verified.** P3 owns target/data decisions and P4 can investigate the official training download from the ESA page. Verify the source and schema before substituting a different archive.

The CSV has no common absolute report timestamp and lacks complete epoch-tagged global states/orbital elements for faithful full-orbit placement. Use per-event report horizons and relative geometry; label synthetic time and schematic globe positions explicitly. Do not infer common current timestamps from event ordering or place an encounter using geocentric latitude alone.

## Context/skill provenance

[Hackathon coordinator](https://github.com/Ayushjain8541/hackathon-coordinator) revision `4e28870e3cd11808607e9751be574ea7465b7aeb`; complete skill copied locally, MIT attribution in THIRD_PARTY_NOTICES.md. Relevant ideation, team, execution, UI, bootstrap, capabilities and templates were read. No source utilities were run without inspection. No Beryl runtime/lock or companion scaffold has been installed.

Superpowers brainstorming and writing-plans instructions were read directly from installed plugin 7.0.1. The user then explicitly requested shared context without prescribing individuals' working methods. Team.md records that user-directed override; no strict compliance with overridden workflow gates is claimed. Each person may choose useful local skills.

Official implementation references consulted while considering optional stack choices: [Vite guide](https://vite.dev/guide/), [FastAPI file uploads](https://fastapi.tiangolo.com/tutorial/request-files/), [scikit-learn regressor reference](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html). These do not establish the team's chosen framework, installed dependency version or provider access. No stack/provider is imposed.

## Actual integrations

Authenticated local gh/Git works; repository is private at observed kickoff. GitHub connector returned 404. No visibility/account settings changed. Preparation revisions were pushed/read back on main; actual current revision is obtained from Git, not assumed from this document.

No model trained, provider call made, API key configured, application runtime created, deployment performed or live UI verified in this context-only pass. JSON examples are synthetic fixtures. Document/fixture consistency checks establish preparation quality only; owners must record actual implementation evidence in handoffs.
