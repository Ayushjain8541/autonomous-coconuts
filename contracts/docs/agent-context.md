# Shared contract context

P2 owns this boundary; P1/P3 are consumers and P4 verifies examples. Canonical semantics are in .beryl/agent/hackathon/contracts.md. The fixtures directory contains synthetic analysis/insights examples, not trained outputs or a JSON validation schema. Coordinate changes with consumers and update types/examples/checks together.

`GET /api/demo` serves the analysis fixture through the backend and recomputes the tier using the public ML rules. Run `python3 scripts/check.py` and `./.beryl/scripts/check.sh` from root. Keep model/provider/time/geometry provenance explicit. Your schema tooling is the owner's choice.
