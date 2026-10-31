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

A replaceable Python/browser baseline now exists in these scopes, with local agent instructions. Beryl standard is actually installed. Read integrations.md and handoffs/bootstrap.md for observed evidence. Product ML/CSV/LLM/full-UI work remains separate.

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
- P4 maintains the verified bootstrap setup instructions. Real Beryl standard is installed via reviewed pinned upstream installer; future updates preserve project context and use its lifecycle.

## Current readiness and blockers

| Area | Observed status | Owner / next dependency |
| --- | --- | --- |
| Shared product/roles/contracts | Context and synthetic examples prepared | All owners coordinate interface amendments |
| Test data | Local file inspected; raw file not committed | P3 obtains a local copy on their machine |
| Training data | Not supplied/verified in this chat | P3 owns acquisition; P4 may claim supporting investigation |
| Application runtime and setup | Python/browser fixture runnable; local instructions and real checks present | P1/P2 may replace stack while preserving shared boundaries |
| Model/inference/rules | Authoritative tier function implemented/tested; prediction adapter explicitly unavailable | P3 trains and integrates the real model |
| LLM access/integration | Not verified | P2 |
| Accurate globe location | Not available from inspected fields | P1 uses labeled schematic unless credible extra input is provided |
| 36h demo event | Synthetic fixture only | P1/P2 label mode; P3 must not count fixture results as evaluation |
| Deployment/submission destination | Unspecified | P4 investigates; do not assume a cloud account or publish |

## Integration evidence

Shared JSON examples parse and are internally consistent; this does not prove an implemented schema or application. Owners add concrete commands only after choosing/implementing their tooling. Before claiming integration, record the real source revision, command/results and browser observations. See evaluation.md for behavioral checks and handoffs/README.md for the short evidence format.

## Coordinator method record

Used the requested hackathon-build skill, especially team/UI/contract guidance. Read Superpowers brainstorming and writing-plans, then applied the user's explicit shared-context/workflow-freedom override. No mandatory execution skill, exhaustive test script, separate per-subsystem plans or approval ceremony is required by this repository. The original context pass contained documentation/fixtures. A subsequent user-authorized bootstrap adds a runnable connectivity shell, genuine Beryl and checks; it does not complete product model/LLM work or deploy.
