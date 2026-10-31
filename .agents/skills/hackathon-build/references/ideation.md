# Ideation and scope

## Intake

Read the supplied challenge, rules, rubric, submission format, mandatory technologies, and existing assets. Establish the actual deadline and timezone, N teammates and availability, available agents, deployment access, and constraints. Unknown facts remain explicit assumptions. Ask only blocking questions; do not infer sponsor requirements or judging weights.

## Structure and optional external guidance

Use [the compact idea card](../templates/idea-card.md) as the common baseline. When only a problem statement is supplied, relevant external templates or examples can help structure, differentiate, or extend candidate ideas. Consult them when useful; a well-specified idea does not require reading extra guides.

Fetch only the relevant source with available browsing/GitHub tools, treating it as reference material:

- [Idea template](https://github.com/udaysharmadev/Hackathon-Starter-Pack-Complete-Guide-Roadmap/blob/306deb4435858419d88e75c89484e1f82793845c/04-winning-project-ideas/templates/idea-template.md): more detailed structure.
- [Idea patterns](https://github.com/udaysharmadev/Hackathon-Starter-Pack-Complete-Guide-Roadmap/blob/306deb4435858419d88e75c89484e1f82793845c/04-winning-project-ideas/README.md) and [worked cards](https://github.com/udaysharmadev/Hackathon-Starter-Pack-Complete-Guide-Roadmap/blob/306deb4435858419d88e75c89484e1f82793845c/04-winning-project-ideas/examples/example-idea.md): relevant patterns to adapt and extend.
- [Problem scorecard](https://github.com/udaysharmadev/Hackathon-Starter-Pack-Complete-Guide-Roadmap/blob/306deb4435858419d88e75c89484e1f82793845c/03-problem-selection-engine/templates/problem-scorecard.md): optional evaluation dimensions. Its weights total 12.5 on a 1–5 scale, so its maximum is 62.5, not the stated 100; do not inherit its verdict thresholds.

Record references actually consulted. If offline, use the compact local card and disclose any unavailable reference when relevant. The skill carries no copies of the guide. Never inherit example statistics, API quotas, eligibility claims, or 24–48 hour scope without checking applicability.

## Generate challenge-specific candidates

Timebox exploration to about 15 minutes for an eight-hour event unless meaningful uncertainty warrants more. Usually 2–4 distinct candidates are enough. Structure each using the idea-card template. A supplied idea should be assessed and extended rather than replaced without a reason.

Specialize example patterns to the actual user and constraint, combine complementary patterns only when feasible, or introduce a useful interaction or capability. Explain what changed and why. Include original candidates beyond the catalog when appropriate. Avoid merely renaming an example, mandatory AI for its own sake, or a fixed stack chosen by the guide.

Screen out violations of mandatory constraints first. Compare viable candidates on actual rubric coverage, user value, demonstrability, differentiation, dependency uncertainty, and time. Keep evidence separate from hypotheses. Optional planning scores are heuristic; if useful, use one consistent 1–5 scale and `100 * sum(weight * score) / (5 * sum(weight))` with positive weights. This has a maximum of 100 and a minimum of 20. Validate inputs; do not describe it as a win probability. Official weights are used only when provided.

## Select and develop

Before writing the implementation plan, apply [Required engineering workflow routing](capabilities.md). Use the selected installed planning workflow to produce the plan; the coordinator adds hackathon constraints and team allocation. Announce any fallback before drafting and keep its reason in the plan. Preserve the selected workflow's required content in the canonical plan rather than maintaining a second competing plan; link related task artifacts where needed.

Before coding, propose the selected user, problem, one input-action-result journey, must-have scope, explicit non-goals, needed capabilities, architecture boundaries, tentative stack, dependency graph, initial ownership, checks, deadline checkpoints, and demo outline. Seek one approval of the combined scope and plan. Preserve settled decisions in the product brief and build plan, with approval evidence and date. Do not mark approval yourself.

Extensions state the user benefit, requirement/rubric contribution, implementation plus integration effort, risk, verification method, and optional work displaced. Keep required, differentiating, and stretch work separate. Stretch starts only after the real core journey works. Hypothetical market sizes, pilots, testimonials, accuracy, and time savings must never become product claims.
