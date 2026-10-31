---
name: hackathon-visual-refactor
description: Diagnose and improve visual hierarchy, spacing, typography, colours, alignment, shadows, density, and component consistency in an existing interface. Use when a UI looks off, messy, amateur, uneven, flat, cramped, or visually inconsistent. Preserve features and product identity while making targeted changes.
---

# Visual refactor

## Audit before edits
Use a screenshot or rendered page where possible; also inspect CSS/design tokens and relevant components. Do not mistake a code-style review for proof of visual quality. If only source code is available, mark appearance findings provisional.

Review in this order:
1. **Hierarchy:** What do eyes see first? Does the main task dominate? Is metadata appropriately quiet? Can importance survive grayscale?
2. **Grouping and rhythm:** Do related items sit together? Is inter-group space larger than intra-group space? Are margins aligned to a shared grid?
3. **Typography:** Is font usage intentional? Is the type scale constrained? Are line lengths, weights, contrast and line heights appropriate?
4. **Colour:** Does the palette communicate brand and semantics? Is colour overused as a hierarchy shortcut? Confirm actual contrast instead of guessing from hex values.
5. **Depth and affordance:** Do borders/shadows show real elevation and clickability rather than decorate every card?
6. **Density and responsive behavior:** Can forms and data layouts be scanned at target widths? Do long strings, empty states, and touch targets work?
7. **Consistency:** Are similar components styled and behaving similarly? Are token values reused rather than one-off overrides?

## Workflow
- Identify at most 7 meaningful findings, each tied to a screen, element, and evidence.
- Prioritize the top 3 by effect on task clarity, frequency, and implementation cost.
- Propose a small token/component-level correction rather than endless per-element CSS tweaks.
- Implement only if asked; isolate changes from business logic. Prefer existing design tokens and component APIs.
- Compare before/after at the same viewport if screenshots are available. Re-run relevant checks; do not claim visual verification without seeing a render.

## Sample design scale, not a hard rule
Spacing steps could be 4, 8, 12, 16, 24, 32, 48 and 64 px. Type tiers could be 12, 14, 16, 20, 24 and 32 px. Choose scales consistent with the project's design system rather than forcing these exact values.

## Findings format
| Priority | Location | Symptom / evidence | Root cause | Targeted fix |
|---|---|---|---|---|
| P1 | ... | ... | ... | ... |

Separate visual preference from a real usability/accessibility defect. Do not make unnecessary dramatic restyling changes when the user wants a faithful Figma implementation.
