# Optional instructions for a hackathon UI project

> This is a template. Review it, then merge the sections you want into your repository's existing `AGENTS.md`. Do not blindly replace an existing file.

## UI/UX priorities
- Deliver one convincing end-to-end user journey before adding side features.
- Use the Figma design supplied by the user as the UI source of truth. When Figma cannot be accessed, request/inspect screenshots and note what is inferred.
- Preserve the existing stack, routing, API contracts, data model, tests and working functionality.
- Favor original design choices tied to the product and audience; do not add generic gradient/card templates by default.
- Maintain a coherent system of typography, spacing, colours, states and reusable components.
- Respect accessibility, responsive behavior, keyboard controls, and reduced-motion preferences.
- Report visual observations only when a screen was actually rendered. Never claim tests ran without their output.
- Prioritize usability blockers before polish or animations. Do not introduce engagement mechanics unless they clearly benefit users.

## Skills workflow
- New screen or Figma-to-code: `hackathon-frontend-art-direction`.
- Whole-feature UI redesign: `hackathon-ui-pipeline`.
- Styling and hierarchy problems: `hackathon-visual-refactor`.
- Flow, navigation and error handling: `hackathon-ux-heuristics`.
- Retention/return value only when appropriate: `hackathon-ethical-engagement`.
- Before the demo: `hackathon-design-qa`.

## Definition of done for a demo-critical screen
- Primary task works end to end.
- Loading, empty, error and success states exist where relevant.
- No obvious overflow at target mobile/desktop widths.
- Keyboard and focus behavior are usable.
- Tests/build checks run and outcomes reported.
- Visual quality checked against actual render and Figma, when those are available.
