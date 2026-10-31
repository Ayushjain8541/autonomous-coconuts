# Codex UI/UX Design Team — 16 custom subagents + 7 skills

A ready-to-extract, **project-local** bundle of Codex subagent definitions and reusable UI/UX skills. It preserves the previous 6 hackathon skills and adds `hackathon-subagent-director`, with 16 specialized `.codex/agents/*.toml` roles. Each is an original prompt informed by your chosen upstream GitHub sources.

## Install safely into a project

1. Unzip the release into the **root of your local Codex project** (the folder containing your app), preserving hidden folders. It creates `.codex/agents/`, `.agents/skills/`, and `codex-ui-ux-docs/`.
2. **Do not replace your existing `AGENTS.md` or `.codex/config.toml`.** This ZIP deliberately excludes both. If you'd like automatic design delegation, merge the snippet from `codex-ui-ux-docs/AGENTS.additions.md` into your existing `AGENTS.md` (or create one after review).
3. Optional: merge `codex-ui-ux-docs/CODEX_CONFIG_EXAMPLE.toml` into your `.codex/config.toml` if you want an explicit concurrency cap. Current Codex uses subagents by default; the optional cap is four concurrent subagents.
4. Restart or reopen Codex in the project, request the selected roles by name in natural language (examples in `codex-ui-ux-docs/PROMPTS_FOR_CODEX.md`), and check `/skills` for `$hackathon-subagent-director` and the 6 other skills. In CLI use `/subagents` to inspect threads when available.

Terminal from your existing repo root:

```bash
cd /path/to/your/hackathon-project
unzip -n ~/Downloads/codex-ui-ux-agents-and-skills.zip
```

`-n` means don't overwrite paths that already exist; review collisions if updating a prior version. Files are instructions only: the ZIP does not automatically execute scripts, install dependencies, or connect Figma. As with any custom agent, review instructions before use.

## Agent roster (16)

| Design phase | Custom roles |
|---|---|
| Creative authority and strategy | `design_director`, `product_flow_strategist`, `visual_art_director` |
| Design-to-code handoff | `figma_handoff_specialist`, `design_system_architect`, `frontend_implementer` |
| Specialist critiques | `ui_refactoring_specialist`, `ux_heuristics_auditor`, `accessibility_auditor`, `responsive_layout_auditor` |
| Interaction, copy, return value | `motion_interaction_engineer`, `ux_microcopy_editor`, `ethical_engagement_analyst` |
| Independent quality gates | `visual_critique_reviewer`, `functional_ui_tester`, `independent_design_challenger` |

## How to use this team efficiently

**Do not spawn all 16 agents for every request.** Roles are selectable; each has a specific mandate. For a full hackathon sprint, call 2-3 parallel strategy agents, one `frontend_implementer` for the actual code, and 3-5 independent auditors after implementation. For a small CSS fix, use just one refactor specialist and a reviewer. Codex subagents consume extra tokens.

1. User directions and approved Figma screens define the experience; the team does not dictate its own taste over yours.
2. Design director consolidates recommendations into one consistent contract. Parent Codex thread, not a subagent, integrates and spawns roles.
3. Only one frontend implementation agent edits overlapping UI files; reviewers are read-only by instructions, not separate permission sandboxes.
4. Implementer self-audits, THEN independent reviewers critique its work. Parent applies the smallest important fixes and rechecks them.
5. Observed vs code-inferred vs unverified evidence is always distinguished; no invented screenshots or test passes.

## Skills included

- `$hackathon-subagent-director`: pick agents and run multi-phase reviews.
- `$hackathon-ui-pipeline`: integrated build/audit process.
- `$hackathon-frontend-art-direction`: original design direction.
- `$hackathon-visual-refactor`: hierarchy, spacing, colour and depth.
- `$hackathon-ux-heuristics`: Nielsen/Krug usability audit.
- `$hackathon-ethical-engagement`: safe repeat-use assessment.
- `$hackathon-design-qa`: final design and functional checks.

## Useful docs
- `DESIGN_REVIEW_PROTOCOL.md`: authority, self-review, independent QA and defect priority.
- `AGENTS.additions.md`: optional project instructions for automatic delegation.
- `PROMPTS_FOR_CODEX.md`: paste-ready prompts for full project, Figma fidelity, critique-only, animation and more.
- `UPSTREAM_ROLE_MAPPING.md`: which of your seven GitHub sources informs which role.
- `UPSTREAM_SKILLS.md`: links and optional native upstream installs.
- `REPORT_TEMPLATE.md`: honest evidence-led audit report.
- `UI_DESIGN_BRIEF_TEMPLATE.md`: fill in your visual constraints before implementation.
- `CODEX_CONFIG_EXAMPLE.toml`: optional concurrency config.

## Compatibility and limitations

Codex documentation describes `.codex/agents/<name>.toml` custom roles with mandatory `name`, `description`, and `developer_instructions` and `.agents/skills/<name>/SKILL.md` project skills. Custom roles inherit parent permissions and tool access. The TOML has no hardcoded model choice, so it uses the model available to your Codex session. User-installed Figma/MCP tooling must separately be available in that Codex session to read design files.

This package is **configuration and instructions, not running agents**. Opening your project and explicitly asking Codex to delegate activates the workflow. A subagent's 'read-only' rule is behavioral; it is not an OS-level sandbox. Tests and visual review require an actual project and browser/tooling.

Official docs: https://learn.chatgpt.com/docs/agent-configuration/subagents
