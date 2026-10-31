# Execution and integration

## Execute a ticket

Read its context and the approved plan and inspect current code. For UI/UX and frontend work, follow [UI/UX ownership](ui-ux.md): the owner's workflow is primary, with agreed product structure, interfaces, and acceptance evidence. For other engineering work, apply [Required engineering workflow routing](capabilities.md) before implementation. Announce and record the actual locally selected Superpowers or ECC workflow, or the explicit fallback and reason. Follow the selected implementation, testing, and verification instructions within the owned scope; retain red–green evidence when TDD is required. Repository conventions supplement that engineering workflow rather than replace a usable one.

State the checks that prove success, protect critical behavior with focused tests, and run the configured checks. In fallback, derive checks from ticket acceptance criteria before coding, reproduce bugs with a failing check, implement the scoped change, and run narrow then project checks. Do not weaken tests or change the acceptance criteria just to pass. New behavior needs real verification; documentation is checked for factual accuracy and usable handoff links. Handoffs name steps actually followed, exact check results, and any skipped or blocked gates; never claim a workflow or TDD was followed from installation or passing tests alone.

Use agreed schemas and representative fixtures to avoid waiting for other implementations. Replace fixtures at integration. Do not present a stub as a mandatory live capability. Update durable architecture or folder docs when behavior or boundaries change. Shared-interface changes go through the owner so dependent tickets and fixtures change together.

## Inspect progress and replan

Fetch actual work state when access allows. Report what the observed revision proves, not what an agent previously claimed. Compare against milestones and remaining time. Proposed eight-hour targets: bootstrap by 45 minutes, real core journey around hour 3, required scope integrated around hour 5.5, freeze around hour 6, then verification, recording, rehearsal, and submission. Adapt these to the deadline and evidence.

When behind, cut optional features, simplify secondary interactions, and unblock the critical dependency. Name a short investigation budget for the blocker and choose help, a compatible alternative, or reduced allowed scope when it expires. Escalate any loss of mandatory requirements; do not silently redefine success. Avoid multi-hour pivot rules copied from longer events.

Reserve owners and time for UX, evidence, README, recording, and pitch in parallel with coding. A noncoding teammate can own those deliverables. Keep optional extensions as a roadmap unless the required journey is already verified.

## Integrate continuously

One integrator reviews the diff, ticket acceptance evidence, recorded workflow or fallback, and schema compatibility. Fixes retain the same UI versus other engineering workflow boundary. Combine branches in dependency order using authorized Git operations. Resolve overlapping writes with their owners; do not revert others' changes to make a merge easy. Run the build and relevant tests on the combined tree. Verify the real journey after replacing boundary fixtures, including invalid input and provider failure where relevant.

Use the actual project commands, normally the module check followed by `./.beryl/scripts/check.sh`. Beryl's project-test configuration must point to real checks; an empty test adapter is not application verification. Review required capabilities against the requirement evidence map before declaring integrated scope complete. Follow [Demo readiness](demo.md) for deployed verification and submission.
