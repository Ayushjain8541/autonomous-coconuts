---
name: hackathon-subagent-director
description: Coordinate a multi-agent design team in Codex using project-scoped .codex/agents roles. Use when the user requests a full UI/UX design, Figma-to-code implementation, broad visual audit, or multi-agent self and independent review. Select only agents needed; the parent Codex thread coordinates, integrates and verifies their work.
---

# Hackathon multi-agent UI design director

## Read first
- Read `codex-ui-ux-docs/README.md`, `codex-ui-ux-docs/DESIGN_REVIEW_PROTOCOL.md`, project `AGENTS.md`, `UI_DESIGN_BRIEF.md`, `DESIGN.md`, and provided Figma frames or screenshots.
- Read or apply the relevant sibling skills as available: `hackathon-ui-pipeline`, `hackathon-frontend-art-direction`, `hackathon-visual-refactor`, `hackathon-ux-heuristics`, `hackathon-ethical-engagement`, `hackathon-design-qa`.
- The user's directions and approved reference are the target, not generic design trends. Do not silently alter backend behavior.

## Delegation modes — spawn only needed roles
- **Quick visual cleanup (2-3 roles):** `ui_refactoring_specialist` + `visual_critique_reviewer`; `frontend_implementer` if editing.
- **New feature or Figma build (5-7 roles across stages):** `product_flow_strategist`, `visual_art_director` (if direction isn't approved), `figma_handoff_specialist` (if Figma), `design_system_architect` (only for shared tokens), `frontend_implementer`, then `ux_heuristics_auditor` + `visual_critique_reviewer`.
- **Full hackathon demo (select ~8-11 roles total, NOT simultaneously):** strategy/art direction; Figma + systems when needed; one implementer; parallel independent visual, UX, accessibility, responsive and functional audit; optional motion/microcopy; independent challenger at final gate.
- **Read-only audit:** visual critique, usability, accessibility, responsive and functional reviewers; do not spawn implementer or edit files.
- **Engagement:** `ethical_engagement_analyst` ONLY for products where recurring use provides legitimate user value.

## Parent orchestration sequence
1. Identify approved references, design constraints, stack, demo-critical path and the file-change ownership boundary. State a short work plan. Do not ask the user to repeat facts already given.
2. Delegate independent exploratory/review tasks in parallel where useful. Wait for necessary results before deciding what to implement.
3. The parent chooses a coherent contract from results, documenting rejected proposals and conflicts. If a Figma frame is approved, do not reinvent it.
4. Assign ONE frontend code integrator for overlapping files. The other specialists advise or add disjoint tests only if authorized; avoid parallel write conflicts.
5. Implement -> implementer's self-review -> independent reviewers -> targeted fixes -> reverify the corrected UI. Do not accept a reviewer's opinion as a tested fact unless there is evidence.
6. If tools permit, inspect actual rendered UI at relevant viewports; run real build/lint/typecheck/tests. Report what was not verified.
7. Finish with accepted design choices, changed files, P0-P3 findings, tests/results, outstanding trade-offs, and any areas where user feedback is needed.

## Severity and stop rules
- P0 = task impossible, safety/privacy regression or data loss; P1 = core-flow failure or major accessibility blocker; P2 = major confusion/responsiveness/visual mismatch; P3 = cosmetic polish. Specialist heuristic 0-4 scores must not be conflated with P0-P3.
- Do not endlessly ask reviewers to improve a beautiful enough feature. Stop after core flow works, meaningful accessibility/responsiveness blockers are fixed, and remaining polish issues are clearly documented.
- Do not claim a multi-agent run happened merely because role files exist. Actual subagent spawning requires a Codex session with this capability and a delegation instruction.

## Default output contract for each subagent
`Intent & scope | Evidence (OBSERVED/CODE-INFERRED/UNVERIFIED) | Findings P0-P3 | Specific proposed changes | Self-critique | Validation performed | Unknowns`.
