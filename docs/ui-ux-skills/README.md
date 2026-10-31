# Codex Hackathon UI / UX Skill Pack

A set of **six original, Codex-native Agent Skills** that coordinate frontend art direction, targeted visual refactoring, usability audits, ethical retention analysis and final UI quality checks. They are designed to work alongside Figma-to-code flows and an existing repository, without silently rewriting backend logic.

## Quick install: one project

1. Extract this ZIP into the root of your project, keeping the `.agents` folder. It will create `.agents/skills/<skill-name>/SKILL.md`.
2. Open (or restart) Codex from that project directory. If the skills do not show immediately, restart Codex.
3. Open `/skills` in Codex to check that the six `hackathon-*` skills appear.
4. Copy one prompt from `PROMPTS_FOR_CODEX.md` into Codex, or invoke a skill directly by name, e.g. `$hackathon-ui-pipeline`.
5. Optionally fill out `UI_DESIGN_BRIEF_TEMPLATE.md` as `UI_DESIGN_BRIEF.md`. If your repo has an `AGENTS.md`, carefully merge in the relevant sections from `AGENTS.ui-example.md`—do not overwrite it.

### Mac terminal example

```bash
cd /path/to/your/hackathon-repo
unzip /path/to/codex-ui-ux-skills.zip -d .
```

**The ZIP doesn't automatically install or execute external code.** It adds Markdown instructions only. The extra root-level Markdown files are guidance; they do not override any existing `AGENTS.md`.

## Skills and invocation

| Skill | Trigger | Typical request |
|---|---|---|
| `hackathon-ui-pipeline` | Full design-to-code work | "Build this Figma flow and audit it before demo" |
| `hackathon-frontend-art-direction` | New screen or distinctive visual identity | "Make a compelling dashboard" |
| `hackathon-visual-refactor` | Looks off, messy or inconsistent | "Fix spacing, typography and hierarchy" |
| `hackathon-ux-heuristics` | Confusing interactions | "Find usability blockers with severity" |
| `hackathon-ethical-engagement` | Legitimate repeat-use design | "Where does the habit/return-value loop fail?" |
| `hackathon-design-qa` | Final responsive/motion/accessibility polish | "Check if demo-ready" |

## Important defaults
- The user's Figma frames, if available, take priority over stylistic guesses.
- Skill audit scores are not user research; findings should cite an observed UI or be labelled hypotheses.
- The main user journey and functionality matter more than visual tricks.
- The engagement skill is optional and should never push unethical or artificial retention mechanics.
- Run real builds/tests and examine rendered screens when tools permit; do not invent evidence.

For the original repositories and optional third-party installation commands, see `UPSTREAM_SKILLS.md`.

## Folder structure

```
.agents/skills/
  hackathon-ui-pipeline/SKILL.md
  hackathon-frontend-art-direction/SKILL.md
  hackathon-visual-refactor/SKILL.md
  hackathon-ux-heuristics/SKILL.md
  hackathon-ethical-engagement/SKILL.md
  hackathon-design-qa/SKILL.md
README.md
PROMPTS_FOR_CODEX.md
UPSTREAM_SKILLS.md
UI_DESIGN_BRIEF_TEMPLATE.md
AGENTS.ui-example.md
```

This is an independent skill pack informed by broad design/UX practices. Original external skill sources are acknowledged in `UPSTREAM_SKILLS.md`; their files are not redistributed.
