# Repository bootstrap

Companion: https://github.com/Ayushjain8541/hackathon-scaffold-template

## Select a baseline

Inspect existing files before scaffolding. Respect event restrictions on prebuilt code. Use the companion, another approved starter, or a fresh scaffold as appropriate. The companion's Python/browser fixture is replaceable infrastructure, not a required product stack. Choose the product runtime for required capabilities, deployment compatibility, integration access, and time; explain new-service costs in setup time as well as money.

The companion already contains an actual Beryl standard installation. Record its lock revision. For another baseline, use Beryl's real installer from a reviewed pinned checkout or its verified release bootstrap. Follow upstream trust and conflict handling; preserve unknown files. Never manufacture a `.beryl/lock.json` or claim a handwritten approximation is installed Beryl. If obtaining a trusted source is blocked, continue independent planning and state bootstrap is blocked.

For a clone of the companion, create an independent target with:

```sh
python3 scripts/create_project.py --target /path/to/new-product --name "Product name" --team-size 3 --statement /path/to/statement.md
```

It requires a nonexistent target, preserves the source, creates fresh local Git history with no remote, and records original challenge text. It does not approve scope or publish. Replace example context with the selected product facts; remove unused example tickets. An existing repo is adapted in place rather than passed to this generator.

## Choose the product layout before assigning work

Include a concrete proposed repo tree and ownership map in the combined scope/build plan. Derive it from the selected product, framework conventions, runtime/deployment needs, and actual module boundaries. The companion generator copies its example baseline; the agent then adapts that baseline to the approved layout. It is not an arbitrary-stack code generator.

- Prefer one deployable application when it meets the requirements; organize substantial behavior by feature or domain inside it.
- Use separate application directories when different runtimes or deployment lifecycles justify them, for example `apps/web/` and `apps/api/` with shared contracts where useful.
- Add a worker, mobile app, model pipeline, or shared package only when the product needs it. Do not create empty layers for completeness.
- Treat `frontend/`, `backend/`, and `contracts/` as the companion demo's example layout, not required product directories. External provider adapters can live with the feature that owns them; there is no mandatory top-level `integrations/` directory. Integration as a team activity is not a code module.
- Assign tickets to concrete outcomes and file scopes after choosing boundaries. Team size does not determine folder count. A coherent ticket may span UI and server code; shared files still have named owners.

Move or replace the fixture, context pointers, contracts, setup instructions, test adapter, and CI together when adapting the layout. Keep a runnable baseline while doing so.

## Bootstrap deliverable

One initializer sets up the canonical product brief, requirements and rubric evidence map, module ownership, shared API/data contracts and fixtures, environment example, setup commands, checks, team map, approved build plan, demo outline, and initial tickets. Use the companion layout when suitable. A minimal fixture request and result establishes module connectivity while teammates start independent work.

Test the riskiest required integration early, alongside scaffold setup: a representative call with the actual available access, expected data shape, runtime compatibility, observed latency, and known quota/cost constraints. Check selected service facts against current official docs; a catalog does not prove access. Record only redacted results and an allowed fallback in `hackathon/integrations.md`. An unverified capability remains unverified.

Target 30–45 minutes for bootstrap in an eight-hour event, adjusting for time remaining. Deploy a preview early when available and authorized, but do not hold every teammate idle for deployment. Name an owner for deployment and shared configuration.

## Context routing

Root `.beryl/agent/` owns the whole product and common rules. `.beryl/agent/hackathon/` holds requirements, team, plan, integration notes, demo, and tickets. Put concise `docs/agent-context.md` files at substantial application, feature, or domain boundaries with responsibilities, interfaces, local map, commands, and links. Small nested folders inherit relevant parent context; do not create documentation in every directory. Add deeper local design docs only when needed.

Beryl's full module-agent scaffolder requires three declared bounded contexts. Backend and frontend are technical layers, not automatically three domains. Use lightweight local docs unless full module scaffolding fits. Never invent another domain to satisfy its gate.

Keep task scopes in files and live status in GitHub issues; issue bodies link to files. With no issue access, one coordinator owns a local status file. Do not let all agents edit one shared ledger concurrently. Store approval in the canonical build plan and link it from Beryl's design tree. The companion's hackathon context documents its workflow adaptation; it is not an unmodified upstream workflow.

## Distribute

After local bootstrap checks, publish the baseline to the user's authorized GitHub destination. Confirm remote access and preserve concurrent changes; never force-push over them. Teammates clone it and create ticket branches. Give each teammate their ticket path, baseline revision, exact setup commands, and relevant reading. Do not publish secrets, auto-merge work, or contact teammates merely because a guide suggests it.
