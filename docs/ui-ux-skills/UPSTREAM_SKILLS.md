# Optional third-party skills you referenced

This pack contains **original Codex-native skills**, not copies of the upstream copyrighted files. You can install these third-party packages independently. Review each repository's license, dependencies, scripts and hooks before installing. Do not install multiple identically named skills without checking for conflicts.

## Suggested upstream choices (most useful first)

1. **Anthropic frontend-design** — distinctive frontend decisions. <https://github.com/anthropics/skills/tree/main/skills/frontend-design>
2. **Wondel UX heuristics** — structured usability review. <https://github.com/wondelai/skills/tree/main/ux-heuristics>
3. **Wondel Refactoring UI** — Codex-ready alternative to the Claude-specific Lovro skill, with similar visual system objectives. <https://github.com/wondelai/skills/tree/main/refactoring-ui>
4. **Impeccable** — all-round polish, critique, audit, layout and design detector. <https://github.com/pbakaus/impeccable>
5. **Emil Kowalski** — motion/design engineering; choose `review-animations` or `emil-design-eng`, not all skills automatically. <https://github.com/emilkowalski/skills>
6. **Hooked UX** — optional engagement and retention analysis only when it fits the product. <https://github.com/wondelai/skills/tree/main/hooked-ux>
7. **Taste Skill v2** — art direction especially for public-facing web pages, with support for app screens. <https://github.com/Leonxlnx/taste-skill/tree/main/skills/taste-skill>
8. **Lovro's Refactoring UI skill** — originally packaged under `.claude/skills/ui-refactor`; manual relocation is needed for a Codex-native `.agents/skills` project setup. It includes reference files that must travel with its SKILL.md. <https://github.com/LovroPodobnik/refactoring-ui-skill>

## Installation examples to paste into Codex

The built-in `$skill-installer` can install a GitHub directory URL. Ask Codex to install one at a time, so you can confirm its instructions and dependencies.

```
$skill-installer install https://github.com/anthropics/skills/tree/main/skills/frontend-design
$skill-installer install https://github.com/wondelai/skills/tree/main/ux-heuristics
$skill-installer install https://github.com/wondelai/skills/tree/main/refactoring-ui
$skill-installer install https://github.com/wondelai/skills/tree/main/hooked-ux
$skill-installer install https://github.com/emilkowalski/skills/tree/main/skills/review-animations
$skill-installer install https://github.com/Leonxlnx/taste-skill/tree/main/skills/taste-skill
```

Upstream Impeccable documents an independent installation command. Run from your project root if you trust its installer:

```bash
npx impeccable install
```

It may offer to add an automatic hook; review and approve the hook in Codex if you want it. It also documents `$impeccable init` as the first-run project setup. No third-party installation is required to use **this** pack.

## Avoid accidental overlap
- Use **one** primary art-direction skill, not frontend-design + Taste + this pack simultaneously in every task.
- Use one broad UX audit and one targeted visual audit. Distinguish visual quality from task success.
- Impeccable's detector may flag intentional style choices; Figma and user direction take precedence.
- Hook Model applies only to products where meaningful repeat use is appropriate.
- Treat third-party skills as code/instructions from outside the project and audit any execution steps before running them.
