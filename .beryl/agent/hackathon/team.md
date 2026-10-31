# Team and independent working agreement

Roles are **P1, P2, P3, P4**, as requested by the user. Do not invent names or demand a name mapping before starting.

| Owner | Primary scope | Files requiring coordination |
| --- | --- | --- |
| P1 | `web/` including its dependencies, UI state, visualizations and component tests | Shared API/types with P2; source/geometry semantics with P3 |
| P2 | `backend/`, API adapters, input validation, orchestration, LLM integration, backend dependencies | Owns `contracts/` and canonical contracts.md; changes require affected consumers to agree |
| P3 | `ml/`, model artifacts/manifests, training/data transforms, prediction adapter, deterministic tiers and ML/rule tests | Rule semantics in requirements.md with P2/P1; integration packaging with P2 |
| P4 | `docs/`, root README/setup integration, `tests/e2e/`, optional CI/deployment config, open-task queue and integration ledger | May assist an owned area only through a scoped claim agreed with its owner |

These are ownership boundaries, not mandatory final frameworks or internal folder trees. A replaceable browser/server baseline now exists, with local context in each development area. Owners may agree a different boundary; update the contract and affected role briefs together. P4 coordinates integration and root/shared setup; P2 remains the API contract owner. Each role owns its handoff at `.beryl/agent/hackathon/handoffs/Pn.md`.

## Branches and handoffs

Suggested branches: `p1/ui`, `p2/backend-llm`, `p3/ml-algorithm`, `p4/<small-task>`. Start from fetched `origin/main`; inspect current files and open PRs before writing. Never reset another person's work or force-push shared main. Submit a focused branch/PR with actual checks, limitations and setup changes. P4 reviews contract compatibility and coordinates merges; no automatic merge or publishing is authorized merely by these docs.

If you open a PR, include its canonical role/ticket link. If your agent has Codex artifact tools, attach the PR to its chat. Do not message teammates or other chats unless the human authorizes that communication.

## How P4 takes open work

P4 reads open-tasks.md, current handoffs, branches/PRs and current source. It can claim **one suitable unclaimed task at a time** when its prerequisites exist and its files do not overlap active ownership. Record the task ID, P4, scope/branch and status before working; re-read shared status to avoid duplicate work. The queue is maintained by P4, not edited concurrently by every agent. Others propose tasks in their own handoff or PR.

A P4 agent may investigate missing data, inspect/test fixtures, improve the demo documentation or verify integrated behavior without taking over the model/UI/backend. Assistance inside `web/`, `backend/`, or `ml/` needs the owner's agreed scope. Changing contracts, safety/risk rules, root dependency strategy or deployment access is not an opportunistic open task. Do not silently downgrade mandatory scope when a dependency is blocked.

## Workflow freedom — user-directed override

The user's latest instruction is the primary rule: shared context for independent work and freedom in how individuals work. This is **Fallback — user-directed override** of the coordinator's mandatory Superpowers/ECC routing and rigid planning/approval procedure. The replacement is outcome/contract-based coordination with role-local checks and evidence. Installed skills are optional aids, not project gates. No claim of strict compliance with the overridden workflow is made.

The coordinator used ideation/team references and read Superpowers brainstorming/writing-plans for context, but deliberately does not copy their step-by-step execution plans, blanket TDD rules or repeated approval gates into role briefs. P1 chooses the UI workflow. Other owners choose theirs. Tests/checks should establish the contract and real user behavior, not mirror implementation or test trivial prose edits.

## Deadline

31 October 2026 **16:15 Asia/Singapore**. Reserve a practical buffer for integration, evaluation evidence, a three-minute presentation and submission. Intermediate milestones and effort allocation are team decisions; no fictitious eight-hour schedule or fixed per-role timing is imposed.
