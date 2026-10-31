---
name: hackathon-design-qa
description: Perform a final shipping-quality review of UI screenshots, responsiveness, accessibility, transitions, forms, error states and design consistency. Use for final polish, pre-demo review, animation feedback, or checking whether a frontend is truly ready to show judges.
---

# UI design QA / polish

## Sources of truth
Respect approved Figma frames or brand guidance. Inspect the running UI and the code where possible. If you lack browser/visual access, clearly separate code-based checks from unverified visual concerns.

## Test matrix
- **Task flow:** can a first-time user finish the main action and observe a genuine result?
- **Viewports:** one compact mobile width, one tablet-ish width if relevant, and one desktop width; capture horizontal overflow, stacking, order, sticky bars, and forms.
- **States:** initial, hover, focus, keyboard, pressed, pending/loading, empty, invalid, success, failure, long-text, disabled.
- **Accessibility:** keyboard reachability, meaningful labels, visible focus, suitable contrast, reduced-motion handling, readable zoom and semantic structure.
- **Visual polish:** hierarchy, whitespace, type rhythm, alignment, consistent buttons and icon treatment, appropriate elevation and image cropping.
- **Motion:** animate to communicate change and continuity. Favor short, interruptible, restrained transitions; avoid large layout jumps and excessive loading delays; don't move UI when reduced motion is requested.
- **Reliability:** console errors, failing requests, broken navigation, dead buttons, typecheck/build/lint/test failures.
- **Demo mode:** startup state, availability of safe demo data, loading time, offline/unstable-network failure handling if relevant.

## Reporting
Score *readiness* by blocking evidence rather than arbitrary aesthetics:
- **P0** broken primary flow or data loss.
- **P1** unusable on a target viewport, inaccessible core control, or high-impact confusion.
- **P2** recurring inconsistency, mild usability friction, or poor fallback state.
- **P3** purely cosmetic issue.

Produce an evidence-first findings table, 3 recommended changes ordered by impact/time, checks actually run (with exact commands), and items not verified.
If asked to fix, address P0/P1 first, then meaningful P2/P3 polish. Do not rewrite or restyle unrelated code in the name of quality.

## Tooling notes
Where Impeccable is separately installed, it may add automatic design checks, `critique`, `audit`, and `polish`. Treat its results as signals, not proof. Review its project hook before enabling; do not install or execute third-party packages without user consent where required.
