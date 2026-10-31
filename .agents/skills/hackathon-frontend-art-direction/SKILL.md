---
name: hackathon-frontend-art-direction
description: Design and implement distinctive, high-quality frontend screens that avoid generic AI-generated layouts. Use when creating a new screen, redesigning a landing page or dashboard, implementing Figma visuals, choosing typography/colours/composition, or when a user says a UI looks generic or templated.
---

# Frontend art direction and code

## Intent
Every screen needs a specific audience, product job, and visual rationale. A good result looks designed for this product, not randomly decorated to seem original.

## Design procedure
1. Define the screen's one-sentence job and the action that matters most. Determine whether the screen is task-dense (dashboard/form) or expressive (marketing/onboarding).
2. Identify constraints: target device, framework, codebase, Figma or screenshots, accessibility, existing visual language, brand colour/font.
3. If a Figma design exists, honor its spacing, hierarchy, typography, imagery, content, and component relationships; add missing details conservatively. Originality is subordinate to the user-approved design.
4. Otherwise generate **two distinct, grounded concepts** in a brief sentence each (e.g. editorial, product-tool, playful tactile). Choose one and state why its typography, density, palette and composition fit the task.
5. Define small design tokens: 3 text tiers, 1-2 font families, 4-8 spacing steps, surface/background/text/accent/semantic colours, border radii, and meaningful elevation levels. Reuse existing tokens if possible.
6. Shape hierarchy through layout, contrast and content before decoration: clear entry point, single dominant action per context, aligned edges, deliberate whitespace and grouping.
7. Implement reusable real components with realistic states, not a flat screenshot mock. Preserve current navigation, business logic and API wiring. If functionality is not yet available, label it clearly as a prototype.
8. Review screenshots if rendering tools are available. Adjust based on what the screen *looks like* as well as what the JSX/CSS says.

## Anti-generic checks
Avoid defaulting without reason to: purple-blue gradients, identical white cards for all content, huge centred heroes for every screen, decorative floating icons, random glassmorphism, six equal-weight CTAs, excessive badges, random font pairings or placeholder copy. This is not a blanket ban; explain the product-specific reason if used.

## Responsiveness and craft
- Maintain information priority on smaller screens. Do not merely shrink desktop columns.
- Ensure readable typography, sufficient contrast, semantic landmarks, labeled controls, focus states, and reduced-motion support when relevant.
- Ensure image cropping, long labels, missing data, and error states are designed, not ignored.
- Prefer purposeful animation that explains state or hierarchy over novelty.

## Output
State visual concept; component and token decisions; files changed; screenshots/viewport checks actually performed; known gaps. Include a short note on why this is not a generic template.
