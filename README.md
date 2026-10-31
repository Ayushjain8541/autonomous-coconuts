# Autonomous Coconuts

Autonomous SG 2026 — **Airbus #1: Satellite Encounter Console** (working name).

An operator loads encounter reports; a model forecasts collision probability, deterministic rules classify encounters, and an LLM explains the computed results. A linked list, timeline, globe/schematic and detail panel help inspect critical events.

**Deadline:** 31 October 2026, 4:15 pm Singapore time. **Team:** P1 UI, P2 backend/LLM, P3 ML/algorithm, P4 floating support.

## Join independently

```sh
git clone https://github.com/Ayushjain8541/autonomous-coconuts.git
cd autonomous-coconuts
```

Ask your agent:

> Read AGENTS.md, then .beryl/agent/hackathon/product-brief.md and my role brief in .beryl/agent/hackathon/tickets/. I am P1 / P2 / P3 / P4. Work within my scope, preserve teammate changes, and use the shared contracts for integration. Choose your own implementation workflow. Do not assume a fixture or a planned command is a real integration.

Replace the role with yours. [Team entrypoint and role links](.beryl/agent/hackathon/README.md).

## Shared references

- [Product and user journey](.beryl/agent/hackathon/product-brief.md)
- [Requirements and evidence](.beryl/agent/hackathon/requirements.md)
- [Interfaces and data semantics](.beryl/agent/hackathon/contracts.md)
- [Ownership, branches and open-task rules](.beryl/agent/hackathon/team.md)
- [Dependency map and current gaps](.beryl/agent/hackathon/build-plan.md)
- [Evaluation expectations](.beryl/agent/hackathon/evaluation.md)
- [Data/source provenance](.beryl/agent/hackathon/evidence.md)

This revision is **shared planning context plus clearly labeled JSON fixtures**. There is no application code, trained model, live LLM integration, deployment or runnable application setup yet. Owners add their actual setup/check commands and dependency locks alongside their implementation. No framework is imposed.

Original Airbus #2 brainstorming is [archived](.beryl/agent/hackathon/archive/airbus-2-ideas.md). The [coordinator skill](.agents/skills/hackathon-build/SKILL.md) is copied with its license in [third-party notices](THIRD_PARTY_NOTICES.md), subject to the user's workflow-freedom instruction in AGENTS.md. The team's product license remains undecided.
