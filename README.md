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

## Run and check the bootstrap

Requires Python 3.9+, Git and Bash. No dependency install or API key needed. Node is optional locally for the JS syntax check; CI includes it.

```sh
python3 backend/server.py --port 8000
```

Open `http://127.0.0.1:8000` and click **Load Demo**. In another terminal from the repo root:

```sh
python3 scripts/check.py
./.beryl/scripts/check.sh
```

Local context: [web](web/docs/agent-context.md), [backend](backend/docs/agent-context.md), [ML](ml/docs/agent-context.md), [P4 docs](docs/agent-context.md), [contracts](contracts/docs/agent-context.md), [tests](tests/docs/agent-context.md). Each development folder also has an AGENTS.md discovery pointer. Source controls/setup are replaceable; preserve the shared contract when changing stacks.

Beryl readiness is lock-backed and reports root AGENTS.md as an intentionally preserved external contract. Hooks are included but not enabled. Its upstream Apache-2.0 LICENSE/NOTICE and the coordinator's MIT attribution are preserved; future product licensing remains a team decision.

## Shared references

- [Product and user journey](.beryl/agent/hackathon/product-brief.md)
- [Requirements and evidence](.beryl/agent/hackathon/requirements.md)
- [Interfaces and data semantics](.beryl/agent/hackathon/contracts.md)
- [Ownership, branches and open-task rules](.beryl/agent/hackathon/team.md)
- [Dependency map and current gaps](.beryl/agent/hackathon/build-plan.md)
- [Evaluation expectations](.beryl/agent/hackathon/evaluation.md)
- [Data/source provenance](.beryl/agent/hackathon/evidence.md)

Beryl standard is installed from pinned upstream source. The replaceable Python/browser fixture is runnable with no package install or API key. It proves connectivity and risk-rule behavior; trained prediction, CSV ingestion, live LLM and the finished console remain role-owned work. No final product framework is imposed.

Original Airbus #2 brainstorming is [archived](.beryl/agent/hackathon/archive/airbus-2-ideas.md). The [coordinator skill](.agents/skills/hackathon-build/SKILL.md) is copied with its license in [third-party notices](THIRD_PARTY_NOTICES.md), subject to the user's workflow-freedom instruction in AGENTS.md. The team's product license remains undecided.
