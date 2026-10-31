# Shared interface examples

Read `.beryl/agent/hackathon/contracts.md` from the repository root for semantics and ownership. P2 owns this folder; consumers coordinate shape changes.

`fixtures/analysis-demo.json` and `fixtures/insights-demo.json` are explicitly **synthetic** response examples. They make the 36h critical-banner / empty 24h critical-list journey concrete. They are not trained predictions, a real upload, an implemented API or JSON validation schemas.

Source report counts, probabilities and geometry here are invented for interface/UX checks. Their presence is never evidence of model accuracy. UI work can consume them while P2/P3 implement the real boundary. Keep the source-mode labels visible. P2 can add a machine-readable schema after selecting runtime tooling; update examples and consumer types together.

Machine-readable schemas are now available as analysis-v1.schema.json and insights-v1.schema.json. GET /api/schema returns them with limits. P2 implements the real transport/CSV/insight paths; a synthetic fixture is still not a trained model output. See backend/README.md for integration details.
