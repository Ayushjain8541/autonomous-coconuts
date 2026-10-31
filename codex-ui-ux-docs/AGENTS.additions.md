# OPTIONAL snippet to merge into your repository's AGENTS.md

> This file is not loaded as `AGENTS.md` automatically. Paste/merge relevant sections into an existing root `AGENTS.md` *without overwriting its other instructions*. Codex can discover `.codex/agents/*.toml` by itself, but this makes its selection and review behavior explicit.

## User-led UI/UX design
- Follow user instructions, chosen Figma frames, screenshots, existing brand and product constraints; they take precedence over agent tastes. Escalate material usability or accessibility conflicts.
- For any substantial UI request, consider invoking `$hackathon-subagent-director` and delegating relevant custom subagent roles. Use a small appropriate subset, not every agent.
- Before implementation, ask `product_flow_strategist` / `visual_art_director` for independent input when the feature is new or ambiguous, and `figma_handoff_specialist` if a Figma design is provided.
- Assign overlapping frontend code edits only to `frontend_implementer`. Keep reviewers read-only. Other roles may change disjoint files only with explicit assignment.
- Require implementer self-check plus at least one independent reviewer (`visual_critique_reviewer` or `ux_heuristics_auditor`) for significant design edits. Also use `functional_ui_tester` for any interaction changes.
- For full-screen changes, check accessibility and responsive layouts. Use `motion_interaction_engineer` and `ethical_engagement_analyst` only when relevant.
- Record actual build/test/browser observations and distinguish source-inferred or unverified findings; never pretend agents, Figma or browsers were used when they were not.
- Fix P0/P1 and demo-blocking P2 issues before cosmetic polish. Preserve backend logic, user data and routing, and avoid broad rewrites not explicitly requested.
- End with a concise summary: implemented, tested, reviewed, unresolved issues and reason.
