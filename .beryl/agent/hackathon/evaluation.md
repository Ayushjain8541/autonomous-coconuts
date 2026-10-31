# Evaluation and acceptance outcomes

Owners choose the tools and checks appropriate to their implementation. This file states observable outcomes and evidence to preserve; it does not mandate TDD, a test framework or commands that do not exist yet.

## Product/contract checks

- Valid CSV groups reports by event_id; arbitrary row order does not change the latest report. Duplicate event IDs are expected updates, not automatically duplicates to discard. Latest means smallest valid non-negative time_to_tca; conflicting records at the same event/time produce an explicit warning or rejection policy rather than an arbitrary winner.
- Units remain days in raw time_to_tca, seconds/metres in their documented raw fields, and hours/metres in the v1 normalized response. Risk log values become probabilities before threshold checks. Invalid inputs identify affected row/column; no NaN/Infinity reaches JSON.
- Tier checks cover Pc at/below/above 1e-6 and 1e-4; distance at/below/above 1000 m and 5000 m; critical precedence; nulls and invalid values. The UI consumes server reasons, not a second rule engine.
- Selection by event ID synchronizes views. A 36h critical synthetic event remains in the global banner when the critical-within-24h list is empty. Detail/geometry selection remains visible with an outside-filter notice. Missing geometry is explicit.
- Corrupt CSV, missing columns, no valid events and prediction unavailable yield usable error/unknown states. No LLM failure blocks deterministic results; a late insights response for a previous analysis is discarded.
- CSV text is untrusted. LLM output may reference only known event/fact IDs; unknown references, provider failure, timeout or unavailable credentials leave an explicit unavailable explanation. Numeric values are rendered from analysis facts, not trusted from model prose.

## ML evidence (P3)

Use the shared v1 target in contracts.md: final available reported log-risk per encounter, with input reports at least 2 days before closest approach and training/evaluation labels from final reports within 1 day. Later reported risk supplies labels only; count excluded events and do not imply this target is observed collision occurrence. Keep event IDs disjoint between train and validation. Fit preprocessing only on training data. Do not randomly split individual reports from the same event across sets. Describe excluded/incomplete events and missingness rather than hiding them.

Compare against an honest baseline, such as latest available reported log-risk. Report the event counts, split/seed, log-risk regression error and critical-risk recall/false negatives where labels support them. Separate probability-only prediction evaluation from the combined distance-plus-Pc operational tier. Test-set earlier risk is not the withheld final target; do not claim final-risk test accuracy without final labels.

A row-level current-risk reconstruction is a different task from forecasting final encounter risk; if chosen as an experiment, label it accordingly and do not substitute it silently. If no training data is accessible, record the block. Precomputed fixtures or a pass-through of reported risk do not complete A1-05.

## Integrated evidence (P4)

Verify the real upload → backend → model/rules → UI → insight-status path on the integrated revision. Exercise the supplied test CSV, the synthetic demo, one malformed file and one model/LLM unavailable case. Record actual runtimes and call counts instead of promising performance. Preserve browser observations plus exact commands/results from the owners. A clean diff, passing local tests, working fixture and deployed behavior are different evidence categories.

## Limits to disclose

Historical data, unaligned report clocks, synthetic 36h demo, schematic globe, forecast horizon, model limitations, unverified real-world calibration and any missing live integration. No operational maneuver recommendation is validated by this hackathon prototype.
