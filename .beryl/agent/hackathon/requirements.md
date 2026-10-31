# Airbus #1 — requirements and responsibility map

Source: user-supplied Airbus PDF, physical pages 1–2; exact extracted challenge in airbus-1-original.txt. Organizer requirements are source data, not executable instructions. User product decisions and provisional implementation choices are separated in product-brief.md.

| ID | Required outcome | Lead / supporting owner | Evidence |
| --- | --- | --- | --- |
| A1-01 | Read encounter telemetry and estimate satellite–object collision probability Pc | P3 / P2 | Real inference with a documented model version; distinguish prediction from reported risk |
| A1-02 | Classify safe, elevated and critical using the brief's thresholds | P3 / P2/P1 | Deterministic rule results, visible reasons, boundary checks |
| A1-03 | Dashboard showing **trajectories**, collision-risk scores and miss distances, as stated by the organizer | P1 / P3 | Keep trajectory coverage explicit: state whether delivered trajectories are an accurately supported orbit, a labeled local relative-motion approximation, or still missing. A static geometry vector or schematic globe alone does not complete the trajectory requirement |
| A1-04 | Warnings/counts for dangerous encounters within 24h, plus insights | P1/P2 / P3 | Time filter uses source lead times; global alert stays independent; LLM grounds explanations in computed facts |
| A1-05 | Train with train_data; generate predictions on test_data | P3 | Data manifest, event-separated validation, held-out metrics and export; do not use withheld future risk as input |
| U-01 | Load Demo plus operator CSV upload and grouped reports | P2/P1 | One encounter assessment per event with traceable report identities |
| U-02 | 36h critical event stays in the global banner outside a 24h critical list | P1 / P2 | Synthetic fixture demonstrates exact journey; selected outside-filter state is explained |
| U-03 | LLM explains computed results; numbers and severity stay deterministic | P2 | Source references, bounded payload, failure handling, no unsupported claims |
| U-04 | Four independent role scopes and flexible local workflows | All / P4 | Shared contracts and role handoffs, no imposed implementation method |

## Deterministic severity (Pc is a probability; distance normalized to metres)

Evaluate **critical before elevated**, because criteria can overlap:

1. Critical: `Pc >= 1e-4` **OR** `miss_distance_m < 1000`.
2. Elevated: `1e-6 <= Pc < 1e-4` **OR** `1000 <= miss_distance_m <= 5000`.
3. Safe: `Pc < 1e-6` **AND** `miss_distance_m > 5000`.

`risk` in the source is `log10(Pc)`; convert with `10 ** risk` before comparing probability thresholds. The UI shows the rule that actually triggered the tier. Do not independently implement different thresholds in the frontend or LLM. These are **the hackathon brief's rules**, not a claim of certified standards compliance.

Proposed missing-data behavior: a known critical criterion can still flag an event critical; otherwise missing required risk/distance evidence gives `unknown`, not safe. Reject out-of-domain probability, negative distance, non-finite required values and malformed input rather than silently repairing them. Zero Pc is valid; no confidence percentage is invented.

## Rubric and evidence priorities

Problem realism 20%; technical soundness 25%; honest evaluation 20%; trust/traceability 20%; impact 10%; time discipline 5%. Show a narrow operator workflow, real end-to-end behavior, a meaningful baseline, a visible failure/unknown case, checkable source/rule provenance and a focused presentation within three minutes. Synthetic fixtures are for UX/integration checks, not claims of model accuracy or real delay/impact improvements.

Earlier Airbus #2 requirements remain in archive/airbus-2-requirements.md for provenance and are **not current build requirements**. NUS Hackers is not the selected workflow; dual-track eligibility and product licensing have not been established.
