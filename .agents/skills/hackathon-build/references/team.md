# Team tickets

Use lightweight Kanban plus small stories and technical tasks. Apply INVEST where practical: especially clear value, small size, and testability; unavoidable dependencies are explicit. Use Given/When/Then for observable behavior. Estimate short time ranges and uncertainty, not fictitious sprint velocity.

These ticket conventions supplement the selected workflow. Creating or materially changing the shared implementation plan requires [engineering routing](capabilities.md), including an explicit fallback record when no usable installed planning workflow exists. UI-specific plans and implementation follow the [UI/UX owner's workflow](ui-ux.md), with agreed product structure, interfaces, and acceptance checks.

## Assign

Map the dependency graph before dividing work. Assign ready tasks based on capacity and complexity; N people does not imply N artificial modules or equal feature counts. One person owns integration and can also build. Name owners for shared contracts, dependency locks, data migrations, and deployment. Coordinate changes to those files with their owners.

Use [the ticket template](../templates/ticket.md). A story may span several module tickets. Each ticket has one accountable human, an isolated branch, requirement links, relevant agent capabilities, owned files, ordered reading, exact interfaces, dependencies, acceptance criteria, verification commands, timebox, demo contribution, and handoff. Do not invent file paths or commands: discover and verify them. Replace template markers before marking a ticket ready.

Reading order: root entry instructions → brief and linked requirements → ticket → relevant folder context → consumed/produced contracts → current source and tests. Expand context when a boundary change requires it. Folder instructions guide discovery; they do not guarantee context isolation or enforce a security boundary.

## Join independently

Read the current plan and ticket from the checked-out revision, then inspect fetched issue/PR state if available. Confirm prerequisites are integrated and the branch is based on the correct baseline. If required work is absent, mark the blocker with an owner; do not fabricate an implementation of an unowned shared contract. Use agreed fixtures to progress independently when permitted.

The human's agent may use Codex, Claude Code, or Cursor. For UI work, read [UI/UX ownership](ui-ux.md) first and use the owner's chosen workflow. For other engineering work, apply [Required engineering workflow routing](capabilities.md) in this agent's own environment, even if the coordinator already recorded a provider. Use a relevant usable installed Superpowers or ECC workflow and its applicable testing/verification instructions. Record the local selection and evidence in this ticket's handoff; it may differ from the coordinator's provider without reopening approved scope. If none is usable, announce and record the fallback before proceeding with an otherwise executable ticket. Scope approval must be backed by the build plan or direct user authorization; never change its flag to approve your own work.

## Handoff

Use [the handoff template](../templates/handoff.md), including the actual commit or PR and evidence. Status moves ready → in progress → review → integrated → verified. Blocked records the reason and next action. Code submitted for review is not integrated. Local tests passing is not deployed verification. Update local context when a lasting decision changes; keep temporary debugging in the ticket handoff rather than expanding global docs.
