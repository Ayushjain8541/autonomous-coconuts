# Shared context index

Read **AGENTS.md → product brief → your role → contracts → relevant current code**. Expand context only when your boundary changes.

| Role | Start here | Main responsibility |
| --- | --- | --- |
| P1 | [UI](tickets/P1-ui.md) | Operator experience and linked visual views |
| P2 | [Backend and LLM](tickets/P2-backend-llm.md) | Ingestion, API, orchestration and grounded explanations; Ayush also owns team coordination |
| P3 | [ML and algorithm](tickets/P3-ml-algorithm.md) | Training, inference, deterministic risk rules and model evidence |
| P4 | [Floating support](tickets/P4-floating.md) | Claim appropriate open tasks; assist Ayush with verification and submission evidence |

Shared documents: [product](product-brief.md), [requirements](requirements.md), [contracts](contracts.md), [team](team.md), [dependency map](build-plan.md), [evaluation](evaluation.md), [sources](evidence.md), [demo](demo.md). P4's [open-task queue](open-tasks.md) names ready investigations and blocked work. Each role writes its own file under [handoffs](handoffs/README.md).

The user chose the roles and requested lightweight shared context, not prescribed implementation procedures. No app framework, UI aesthetic, provider or internal module design is mandatory. The response examples are synthetic interface fixtures, not trained predictions. A replaceable Python/browser baseline and real Beryl standard installation are now present. Start with the relevant local agent-context.md under web/docs/, backend/docs/, or ml/docs/. Current setup/check commands are in root README.md.
