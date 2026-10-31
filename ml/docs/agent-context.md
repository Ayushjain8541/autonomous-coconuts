# P3: ML and risk algorithm context

Own model training, inference, feature/label semantics, artifacts and deterministic risk rules. Read root AGENTS.md, product brief, P3 ticket, requirements/contracts/evaluation and source evidence. Choose model family, libraries and work method yourself.

## Current local map

`__init__.py` is the public package boundary. `rules.py` implements the brief's tiers, critical precedence, nulls and numeric validation. `predictor.py` implements the logical batch shape but returns explicit unavailable/null predictions: **no trained model is installed**. Replace that adapter with real inference, preserving output IDs/shape. Backend imports the public package entrypoints.

## Actual checks and data boundary

From repo root: `python3 -m unittest discover -s tests -v`, `python3 scripts/check.py`, `./.beryl/scripts/check.sh`. The tests cover threshold/missing/invalid behavior and an honest unavailable model. Add your actual training/inference/evaluation commands once implemented; none is invented here.

Training data is still outstanding. Source test CSV exists on the coordinator machine only, not in Git. Keep raw data in ignored data/raw/ and publish schema/checksum/access instructions rather than raw records. Publish a model/feature manifest and artifact provisioning with real evaluation evidence. Source units are days, metres, metres/second; normalized API lead time is hours. Final reported-risk target and allowed input window are pinned in contracts.md. Do not count synthetic fixtures as model accuracy. Coordinate packaging/dependencies with P2, geometry semantics with P1, data-acquisition assistance with P4. Handoff: .beryl/agent/hackathon/handoffs/P3.md.
