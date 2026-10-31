# Demo readiness

Define the demo outline during scope selection and refine it as the product becomes real. Keep the exact user → action → visible result sequence in `.beryl/agent/hackathon/demo.md`.

## Verify the product

- Run actual build, contract, critical-logic, and integration checks. Exercise persistence if required and likely invalid-input/provider-failure paths.
- Have a teammate validate setup from a fresh checkout using the documented environment. Check the deployed URL in a clean browser and on the actual demo device.
- Make the main action obvious; provide useful loading, empty, success, and error states, readable layout, labels, keyboard access, and appropriate mobile behavior. Follow the [UI/UX owner's chosen workflow](ui-ux.md) for design and frontend work while verifying these outcomes.
- Provide repeatable representative demo data and a seed/reset procedure limited to the demo environment. Label synthetic inputs and recorded results. Fixtures cannot prove required live integrations.
- Record a known-working commit and deployment before the freeze. Recheck requirements against concrete evidence, not only a polished scripted path.

## Explain and submit

Use the event's actual presentation format and time limit. Prepare a short explanation and, when useful, a longer technical walkthrough. Cover the user's problem, working action and result, differentiator, technical contribution, evidence, limitations, and sensible next steps. Practice transitions and questions about architecture, sponsor usage, team contributions, and tradeoffs.

Use only observed or sourced metrics with provenance. A test result in one demo does not establish user adoption, broad accuracy, or market impact. Hypothetical outcomes and extensions stay labeled. Do not copy invented pilots, testimonials, or statistics from example pitches.

Prepare the required submission fields and files, accessible URL, repo README with setup and architecture, sponsor evidence, team attribution, screenshots, and a working recorded backup. Check the actual submission deadline and leave upload buffer. A second hosting provider, custom domain, fundraising plan, and networking campaign are optional, not default deliverables. Sending messages or submitting externally needs the user's authorization for that action.

If live behavior fails, state the failure and show the accurately labeled recording or fixture fallback. Report remaining gaps honestly. Completion means the required real journey is verified and submission materials are ready, not that winning is guaranteed.
