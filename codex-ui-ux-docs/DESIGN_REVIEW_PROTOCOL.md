# UI design quality gates and independent review protocol

## Source of truth / decision order
1. Latest explicit user instructions and restrictions; preserve existing code functionality.
2. User-approved Figma frames / reference screenshots (when available), including specifically requested visual departures.
3. Existing repo `AGENTS.md`, design brief, brand system, technical constraints and core user job.
4. Accessibility, understandable control states, error handling and functional correctness. If a supplied design conflicts, explicitly flag and propose a faithful, safe correction instead of silently overriding it.
5. Well-supported design principles from Refactoring UI, Nielsen/Krug, Impeccable, Emil's motion approach and Taste.

Do not 'fix' a user's intentional aesthetic choice merely because a skill dislikes it. Distinguish must-fix defects from preferences.

## Three checkpoints

### A. Design review (before code)
- Parent consolidates flow, art direction and design-system advice into one brief.
- Check fidelity with user instruction and any Figma frames.
- Concrete outputs: one primary CTA per screen; main success path; token choices; prohibited elements; target widths; nonfunctional constraints.

### B. Implementation review (writer checks own work)
- `frontend_implementer` checks its diff and actual browser render if available.
- Self-review prompts: What user instruction might I have missed? Did I change unrelated logic? Which UI elements aren't functional? Which states are missing? Did I invent copy or data? Can keyboard and mobile users complete the action?
- Correct obvious failures before passing to independent reviewers.

### C. Independent challenge / audit
- `visual_critique_reviewer`: hierarchy, aesthetic, fidelity, anti-slop.
- `ux_heuristics_auditor`: Nielsen/Krug task usability, navigation, status and recovery.
- `accessibility_auditor`: labels, focus, contrast, reduced motion and interaction.
- `responsive_layout_auditor`: target viewport usability and overflow.
- `functional_ui_tester`: actual end-to-end behavior and regressions.
- `independent_design_challenger`: user brief compliance and unsupported claims.

Use only roles justified by task size; at most a few simultaneously. Independent reviewers remain read-only. Parent reconciles and instructs ONE implementer to apply approved fixes.

## Severity
| Priority | Meaning | Stop-the-ship? |
|---|---|---|
| P0 | Core operation impossible, severe data loss/privacy/security issue | Yes |
| P1 | Core user path broken, serious accessibility barrier | Yes |
| P2 | Significant confusion, responsive breakage or major reference mismatch | Usually fix in a hackathon demo |
| P3 | Cosmetic/optional polish | Document if time is tight |

A 0-4 Nielsen severity rating is a *different scale* from P0-P3 prioritization.

## Evidence labels
- `OBSERVED`: actual visual screenshot, run, automated/manual test. Include path, screenshot/viewport, command result or reproduction.
- `CODE-INFERRED`: observation from source only. State why it might break, mark as untested.
- `UNVERIFIED`: resource or environment unavailable; do not claim pass or pixel-perfect reproduction.

## Issue report format
| ID | Priority | Evidence level | Screen/file | Expected | Actual/Concern | Smallest fix | Verification |
|---|---|---|---|---|---|---|---|

**Completion criteria:** demo-critical flow works; user-approved design is substantially honored; major usability, accessibility and viewport issues addressed; build/tests reported truthfully. The parent outputs remaining uncertainties and accepts that a prototype may have documented P3 issues.
