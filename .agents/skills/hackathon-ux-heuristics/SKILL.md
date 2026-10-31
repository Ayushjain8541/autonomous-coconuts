---
name: hackathon-ux-heuristics
description: Audit a web or mobile interface using Nielsen's ten usability heuristics and Steve Krug-style low-friction clarity. Use for task flow problems, confusing navigation, unclear labels, onboarding friction, error handling, usability audits, or requests for severity-ranked UX findings.
---

# UX heuristic review

## Evaluate real user tasks
1. Name the likely user, primary task, and expected success result. Where possible actually exercise the interface. Inspect desktop/mobile and UI states; screenshots alone may be insufficient to verify interactions.
2. Walk the task step by step, recording what the user must notice, understand, decide, enter, and recover from.
3. Check all ten heuristic categories explicitly:
   1. System status is visible (loading, saving, completion).
   2. Language and mental model match the user's world.
   3. User can back out, cancel, undo, or regain control.
   4. Controls and behavior follow conventions consistently.
   5. Prevent errors before they happen.
   6. Prefer recognition over memorization.
   7. Serve both novices and experienced users efficiently.
   8. Minimize irrelevant content and visual noise.
   9. Errors are understandable and recoverable.
   10. Help is available at the moment of need.
4. Apply 'don't make me think' principles: scannable hierarchy, self-evident controls, clear navigation, strong information scent, short content, and no surprise outcomes.
5. Include keyboard accessibility, touch target size, focus visibility, contrast, form labels, and mobile interaction concerns. Identify dark patterns or misleading choices.

## Severity scale
- 0 = no issue / observation only.
- 1 = cosmetic annoyance.
- 2 = minor friction, detour or hesitation.
- 3 = major interruption, repeat failure, or frequent confusion.
- 4 = blocks task completion, serious harm, or dangerous misrepresentation.
Severity considers frequency, impact and persistence. Do not make severity 4 synonymous with 'looks bad'.

## Reporting rules
Create a prioritized table: `ID | Screen/step | User-visible problem | Heuristic | Severity 0-4 | Evidence | Fix | Confidence`.
- Distinguish **observed** from **hypothesized** problems. If the app could not be run, say so.
- Summarize the 3 fixes most likely to improve the hackathon demo, including approximate implementation complexity (S/M/L).
- Explain the *user consequence*, not just design rules. Avoid vague 'make this intuitive' advice.
- On request, implement P1/P2 findings and verify the affected flow afterward.
- Do not penalize an interface for missing features that the product explicitly excludes.

## Hackathon lens
A demo-ready UI should let a first-time judge understand the purpose, finish the primary task, see useful feedback, recover from an error, and understand the next step without a live explanation.
