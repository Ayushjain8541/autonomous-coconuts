# Source lenses for each custom subagent

These are original role prompts informed by the linked design frameworks, **not copies of the upstream SKILL.md files**. The external repos are optional. Custom role TOMLs work with the bundled original `hackathon-*` skills alone. To use upstream commands and hooks, install those packages separately after reviewing their licenses and scripts.

| Upstream repository | Relevant subagents | Main purpose |
|---|---|---|
| [Lovro Refactoring UI](https://github.com/LovroPodobnik/refactoring-ui-skill) | `ui_refactoring_specialist`, `design_system_architect` | Hierarchy, scales, depth and styling |
| [Wondel UX heuristics](https://github.com/wondelai/skills/tree/main/ux-heuristics) | `ux_heuristics_auditor`, `product_flow_strategist`, `independent_design_challenger` | Nielsen/Krug audits and recovery |
| [Wondel Hooked UX](https://github.com/wondelai/skills/tree/main/hooked-ux) | `ethical_engagement_analyst` | Ethical return-value loops |
| [Anthropic frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | `visual_art_director`, `frontend_implementer` | Distinctive art direction |
| [Impeccable](https://github.com/pbakaus/impeccable) | `design_director`, `visual_critique_reviewer`, `accessibility_auditor`, `responsive_layout_auditor`, `functional_ui_tester` | Critique, technical audit and polish |
| [Emil Kowalski](https://github.com/emilkowalski/skills) | `motion_interaction_engineer`, `ux_microcopy_editor` | Motion craft and interaction details |
| [Taste Skill v2](https://github.com/leonxlnx/taste-skill) | `visual_art_director`, `visual_critique_reviewer` | Original art direction and anti-slop |
| [Wondel Refactoring UI](https://github.com/wondelai/skills/tree/main/refactoring-ui) | `ui_refactoring_specialist`, `design_system_architect` | Visual refactoring and constrained systems |

**Source precedence:** the user owns their design. Upstream advice is a lens to check decisions, not permission to override a user-approved interface.
