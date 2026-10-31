# Copy-paste prompts for Codex

## 1 — Entire UI workflow
Use `$hackathon-ui-pipeline` for this repository. Inspect the existing frontend and available Figma/screenshots first. Preserve the working backend and API contracts. Identify the user and the single demo-critical flow, propose an intentional visual direction, implement the screen, then review hierarchy, heuristic UX, mobile behavior, and states. Run relevant checks and show exactly what changed and what remains unverified. Do not add unnecessary dependencies or features.

## 2 — From my Figma frame
Use `$hackathon-frontend-art-direction` to implement the UI from this Figma frame: [PASTE FRAME LINK]. The chosen Figma composition is the source of truth. Reuse my application's existing framework/components and preserve state, routing, API calls, and business logic. Use existing design tokens when consistent; identify gaps and implement responsive, accessible states. Inspect the rendered result against Figma when available and report mismatches.

## 3 — My UI looks off
Use `$hackathon-visual-refactor`. Audit the visible interface for hierarchy, rhythm, type, alignment, colours, shadows, and component consistency. List up to 7 evidence-based issues, prioritize 3, then make focused changes without modifying unrelated logic. Compare before and after if render tools are available.

## 4 — UX judge perspective
Use `$hackathon-ux-heuristics`. Act as a first-time hackathon judge. Try the main user flow, evaluate all ten Nielsen heuristics and clarity/scanability, and produce a severity 0–4 table with exact screen locations, why users are affected, evidence versus hypotheses, and recommended fixes. Do not change the code yet.

## 5 — Does this app bring users back?
Use `$hackathon-ethical-engagement`. First determine whether repeat use genuinely helps users. If so, map trigger, action, reward, and voluntary investment; identify where the experience breaks and how to fix it without dark patterns, artificial urgency, or compulsive engagement. State what is hypothetical.

## 6 — Final polish before presentation
Use `$hackathon-design-qa`. Review the core flow on mobile and desktop, actual loading/success/error/empty states, button affordance, focus, contrast, motion, overflow, and console/build/test failures. Return P0–P3 findings and fix the highest-impact issues only. Never claim to have seen screens or run tests that you could not access.
