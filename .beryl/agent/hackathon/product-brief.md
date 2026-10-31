# Satellite Encounter Console — shared product brief

## Intent and settled user direction

Build a console for a satellite operator to load a CSV of encounter reports, obtain model-predicted collision probabilities (Pc), classify encounters with deterministic rules, and inspect algorithm-grounded LLM insights visually. This is the user's proposed product direction for Airbus #1, replacing the earlier Airbus #2 exploration.

The user requested four independent roles: **P1 UI; P2 backend and LLM; P3 model and algorithm; P4 floating support whose agent can take suitable open tasks**. The user then explicitly clarified that documentation should provide shared context while leaving individuals free to choose how they work. This is not authorization for this chat to build the whole application or dispatch implementation agents.

## Core journey

1. Operator chooses **Load Demo** or uploads a compatible report CSV.
2. The backend validates records, groups by `event_id`, invokes prediction and deterministic classification, and returns one assessment per encounter with source provenance.
3. A global critical-alert banner can announce a critical encounter **in 36 hours** in the labeled synthetic demo.
4. **View encounter** synchronizes selection across the list, timeline, globe/schematic and right-hand detail panel.
5. The detail panel explains predicted Pc, reported Pc when available, predicted miss distance, lead time, rule reasons, source reports and model identity. The LLM adds explanation without changing numbers or classification.
6. **Encounter geometry** opens the relative position/velocity view with units and uncertainty where supported.
7. **Critical within 24h** filters the encounter list; the global critical banner still includes the 36-hour critical event. The detail panel retains the selection and indicates when it is outside the current filter.

In the supplied synthetic fixture, the 24-hour critical list is empty; show **No critical encounters within 24 hours**. Do not silently clear the global alert. The banner should say it covers all horizons. A selected event outside the filter remains inspectable.

## Data truth and important limits

The supplied test CSV has 24,484 rows and 2,167 encounters, with repeated reports per event. `t_*` describes the target, `c_*` the other object, and relative fields describe their encounter. It already includes earlier reported log-risk values. The shared v1 objective is the final available reported encounter log-risk forecast from reports at least two days before closest approach, with evaluation labels limited to final reports within one day. It predicts a later source-reported risk estimate, not observed collision occurrence. See contracts.md for the exact shared target and unsupported-input behavior.

All observed test rows have `time_to_tca > 2` days. A 36-hour demo cannot come directly from those horizons. **Load Demo uses clearly labeled synthetic interface data** until a genuine data-backed demo can satisfy the scenario; any precomputed fixture prediction remains marked fixture. CSV upload preserves source horizons. A successful demo-fixture view does not prove upload, ML or LLM integration.

Original rows lack a common absolute report timestamp. Real batch mode uses **hours remaining as of each encounter's latest report**, not a claim that unrelated historical events share today's clock. A calendar timeline requires additional timestamped input; the MVP can use a labeled relative timeline. Do not shift source times to make a 24-hour alert appear.

The test columns do not specify complete epoch-tagged global state/orbit data. The globe can be a **schematic selection aid**; do not present invented latitude/longitude or full trajectories as observed. The precise data-backed view is relative encounter geometry. Accurate global orbital propagation and maneuver planning are outside the MVP. The organizer separately asks for trajectory visualization: P1/P3 should provide an explicitly labeled local relative-motion illustration where data supports it, document its assumptions, and retain the distinction from full orbits. A static geometry view or schematic globe alone must not be reported as satisfying trajectory coverage.

## Functional structure and states

One dashboard: load/upload actions, source-mode label, global critical banner, list, relative timeline, globe/schematic selection aid, details and an encounter-geometry view. P1 chooses layout, styling, components and visual tools. No mandatory screenshot, library or 3D implementation is prescribed.

Essential states: initial/empty, parsing/analyzing, validation error with actionable row/column details, results, unknown prediction, no filter matches, selection outside filter, insights pending/ready/unavailable, and geometry unavailable. Numeric results remain usable when the LLM fails or is unconfigured. Filters and selection must work by keyboard as well as pointer; color is never the only risk indicator. Aim for a usable desktop demo and a narrow-screen stacked layout.

## Scope boundaries

Must have: real CSV validation/grouping; trained-model inference on supplied-format inputs; deterministic, explainable tiers; labeled source/fixture modes; linked views; bounded grounded LLM explanation; negative-case handling and honest evaluation evidence.

Do not spend core time on accounts, billing, live debris feeds, certified operational clearances, automatic maneuvers, arbitrary coordinate-based encounter discovery, photorealistic Earth rendering or unsupported confidence percentages. These are not required for this journey.

## Decisions left to owners

Frameworks, language/tooling within owned areas, visual design, model family, internal modules, provider choice using existing authorized access, dependency management, testing procedure and deployment arrangement. P2/P3 should prefer a simple local model adapter when feasible; Python is a practical suggestion, not a mandate. Shared interface changes require producer/consumer coordination. The contracts document states the proposed v1 handshake; owners can revise it together before dependent integration.

## Evidence of completion

The real upload → grouped inference → classification → visual details journey works beyond a canned fixture. The LLM's status and provenance are visible. One failure/missing-data case is demonstrated. Evaluation reports compare a model with a stated baseline on separated events and make no unsupported real-world benefit claims. See requirements/evaluation for ownership and evidence.


## User-directed report extension

Add a full LLM analytical report: whole-portfolio statistics, cited priority assessments, supported advisory actions and what-if interpretation. Keep the website concise; P1 only needs generate/download report access, not a new simulation view. P2 owns JSON/PDF production. What-if detail stays in the report and tests independently assumed Pc/miss-distance changes through P3's existing rule function. These sensitivity cases are not actual maneuver planning or achievable risk-reduction predictions. True orbital/burn optimization still requires additional input and is not claimed.
