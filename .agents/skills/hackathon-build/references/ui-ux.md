# UI/UX ownership and integration

The accountable UI/UX owner chooses the skills, tools, and workflow for UX exploration, visual design, prototyping, and frontend implementation. Use their preferred installed skills and existing project conventions. If no preference is known, inspect the repo and available design capabilities, then ask the owner only when the choice materially affects the work. Do not force Superpowers/ECC, a universal aesthetic, a component library, or a design methodology onto this work. The owner's workflow is the primary UI route, not a fallback or user override, even when Superpowers/ECC is installed. Record the chosen workflow and any skills actually used in the ticket/handoff; a personal procedure does not require an external skill name.

## Agree the product structure

Before marking broad UI implementation ready, establish a compact shared brief in the existing product/folder context and link it from tickets:

- Target user, core journey, and required demo outcome.
- Required screens/views, their purposes, navigation, main actions, and essential content or sections. This is a functional outline; layout, visual hierarchy, components, typography, and motion belong to the UI/UX owner unless the team has explicit requirements.
- Data needed by each action/view, its agreed backend or shared-code interface, validation, and relevant loading, empty, success, and error behavior.
- Actual device/accessibility constraints and observable acceptance checks.

Read settled requirements first. Ask focused questions about material gaps in the journey, navigation, screen responsibilities, required data, or interaction behavior, and resolve those before implementing dependent behavior. Propose concrete options when useful; record the decision rather than leaving it only in chat. Do not restart discovery for settled scope, demand pixel-level decisions, or block independent design work on an unrelated open question. Changes to shared scope or interfaces go through their owners; local visual decisions do not require repeated coordinator approval.

## Build against agreed contracts

Link the actual request/response schemas, shared types or server-action signatures, validation rules, errors, and representative fixtures the UI consumes. A separate HTTP backend is not required. Do not invent endpoints, fields, capabilities, or success results to make a screen work. If a contract is missing, coordinate it with the interface owner before wiring dependent behavior. A backend implementation need not be finished: agreed contract-shaped fixtures allow parallel UI work and remain visibly identified in the handoff until replaced.

Mixed tickets keep the owner's workflow for UI work. Backend behavior, API/schema changes, and shared integration logic follow [engineering routing](capabilities.md) and contract ownership separately; do not use that routing to take over the UI design process or turn a visual-only task into a backend task.

## Verify the result

Require working navigation and actions, correct contract consumption and error handling, relevant UI states, and applicable keyboard/device checks. Use the owner's workflow and actual repo checks to obtain evidence; do not prescribe TDD for visual exploration or styling. Shared logic still follows its selected engineering/testing workflow. Replace fixtures and verify the real UI-to-backend journey before declaring integration complete. Record browser observations, checks run, contract revision, remaining fixtures, and gaps in the handoff. Visual polish alone does not prove the required product behavior works.
