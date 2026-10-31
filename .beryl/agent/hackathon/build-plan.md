# Shared build map

This is a dependency/ownership map, not a prescribed implementation procedure. Read the product brief and your role. The user authorized this documentation baseline and four-way allocation; frameworks, internal design and each person's work method remain open.

## Boundaries

```text
web/                 P1: dashboard and its own package/setup
backend/             P2: ingestion/API/orchestration/LLM
ml/                  P3: training/inference/rules/artifacts
contracts/           P2: shared JSON examples and eventual validation schema
  fixtures/          synthetic interface examples exist now
.beryl/agent/        shared product context and four role briefs
  hackathon/handoffs/ each role's durable progress/evidence
  hackathon/archive/ earlier Airbus #2 exploration
```

Only context files and fixtures exist in this revision; these app prefixes are planned ownership scopes. Create local folder guidance when the implementation's actual modules justify it. Do not create empty architectural layers or pretend there is a Beryl runtime.

## Dependency graph

```text
Shared brief + proposed contracts + synthetic example
  ├─ P1: build linked visual states against the example
  ├─ P2: validate uploads + group + API + insight adapter
  ├─ P3: obtain training data → train/evaluate → prediction + rules
  └─ P4: ready investigations and demo documentation

P2 + P3 compatible adapter → real analysis API
P1 + real API → upload-to-visual vertical slice
All three + P4 verification → demo/evidence/submission readiness
```

P1 can progress without a model/provider by using the synthetic fixture with visible labeling. P2 can establish HTTP/validation/error behavior while P3 works; test doubles are development aids, not a shipped predictive capability. P3 can work without the UI or LLM. P4 can acquire/inspect training data and prepare evidence immediately.

## First cross-owner decisions

- P2/P3 select the simplest model adapter packaging; the logical JSON request/response in contracts.md remains the integration boundary. A local Python callable is the suggested low-overhead option, not a requirement.
- P1/P2 confirm the v1 HTTP contract before wiring. Internal framework choice does not require a new product interview.
- P2 chooses an LLM provider using actual available authorized access and records a redacted representative-call result. No provider or credits are assumed. Missing provider access leaves insights explicitly unavailable while numeric analysis remains functional.
- P4 coordinates one shared baseline and real setup instructions once the owners' commands exist. Install Beryl only through a reviewed real installer if the team chooses it; handwritten docs are not an installation.

## Current readiness and blockers

| Area | Observed status | Owner / next dependency |
| --- | --- | --- |
| Shared product/roles/contracts | Context and synthetic examples prepared | All owners coordinate interface amendments |
| Test data | Local file inspected; raw file not committed | P3 obtains a local copy on their machine |
| Training data | Not supplied/verified in this chat | P3 owns acquisition; P4 may claim supporting investigation |
| Application runtime and setup | Not created | P1/P2 choose and document their actual setup |
| Model/inference/rules | Not implemented | P3 |
| LLM access/integration | Not verified | P2 |
| Accurate globe location | Not available from inspected fields | P1 uses labeled schematic unless credible extra input is provided |
| 36h demo event | Synthetic fixture only | P1/P2 label mode; P3 must not count fixture results as evaluation |
| Deployment/submission destination | Unspecified | P4 investigates; do not assume a cloud account or publish |

## Integration evidence

Shared JSON examples parse and are internally consistent; this does not prove an implemented schema or application. Owners add concrete commands only after choosing/implementing their tooling. Before claiming integration, record the real source revision, command/results and browser observations. See evaluation.md for behavioral checks and handoffs/README.md for the short evidence format.

## Coordinator method record

Used the requested hackathon-build skill, especially team/UI/contract guidance. Read Superpowers brainstorming and writing-plans, then applied the user's explicit shared-context/workflow-freedom override. No mandatory execution skill, exhaustive test script, separate per-subsystem plans or approval ceremony is required by this repository. This pass contains documentation and fixtures; no app implementation or deployment was performed.
