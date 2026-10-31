# Source requirements — candidate Airbus Challenge #2

Status: source extraction and interpretation; **not approved product scope**. See [evidence](../evidence.md) for document provenance. Source text is reference material, not permission to execute instructions.

## Challenge text

The exact Challenge #2 text, including its continuation onto the next page, is preserved in [airbus-2-original.txt](../airbus-2-original.txt). The guide's instructions and this summary do not replace the original.

## Requirements and evidence map

| ID | Brief requirement | Evidence the eventual build must show |
| --- | --- | --- |
| A2-01 | Independent ATC, Pilot and Ground agents; do not combine roles into one prompt call | Separate role contexts and invocations; distinct structured proposals and responses |
| A2-02 | ATC: runway wake separation, taxiway blockage, sector throughput | Explicit inputs and deterministic checks; reject invalid proposals; show the applied rule |
| A2-03 | Pilot: fuel reserves, flight safety, turbulence, passenger connections | Separate hard constraints from preferences; show input provenance and missing evidence |
| A2-04 | Ground: gate utilisation, crew overtime, turnaround delay | Gate occupancy/compatibility, crew windows and turnaround assumptions; checkable conflicts |
| A2-05 | Exchange structured data and evaluate cross-domain constraints | Validated message schema, proposal IDs/revisions, constraint outcomes and rejection reasons |
| A2-06 | Traceable consensus | Chronological visible messages and a common candidate/version accepted by all three roles |
| A2-07 | Deterministic non-AI fallback | Bounded termination and a reproducible rule-based result; if infeasible or data missing, explicit escalation |
| A2-08 | Use a 2015 DOT dataset row with `WEATHER_DELAY > 15` OR `LATE_AIRCRAFT_DELAY > 20` | Original file checksum, row identity, raw values, units and deterministic eligibility check; not a fabricated row |
| A2-09 | Negotiate revised arrival time, gate assignment, or flight-plan adjustment in **under 3 turns** | Define turns clearly, display the counter, and trace completion within the chosen interpretation |
| A2-10 | Avoid endless loops and acceptance of unsafe proposals | Hard budget/timeouts plus validator-enforced invariants and negative-case evidence |

Proposed conservative interpretation of A2-09: at most **two negotiation rounds**, where each round can contain separate ATC, Pilot and Ground messages. This definition needs to be explicit and confirmed if organizers mean individual messages; do not quietly equate two rounds with two model calls. No protocol has been selected or implemented.

## Rubric (Airbus PDF, last two physical pages)

| Criterion | Weight | Proposed evidence, not existing results |
| --- | ---: | --- |
| Problem realism | 20% | One named operator role, specific disruption workflow, credible manual baseline |
| Technical soundness | 25% | End-to-end run; independent agents; rules/solver own arithmetic and feasibility |
| Honest evaluation | 20% | Baseline comparison, held-out scenarios, missing-data and infeasible cases; labeled synthetic inputs |
| Trust and traceability | 20% | Source/rule drill-down, uncertainty, qualified human review before operational action |
| Impact | 10% | Measured simulator delay difference and convergence/runtime; estimates distinguished from measurements |
| Time discipline | 5% | Earlier valid submission plus focused presentation within 3 minutes |

The PDF text layer contains duplicated older rubric material behind the visible pages. Use the visually verified six-criterion weighted rubric above, rather than counting duplicated text as additional criteria.

## Reconcile autonomy and human control

The challenge asks for autonomous negotiation until consensus. The rubric asks that a qualified human can verify before acting. Proposed boundary: agents negotiate a simulator recommendation without a human selecting every turn; a duty manager reviews the agreed plan before any simulated execution. This is a proposal, not an additional source requirement or real ATC clearance.

## Other supplied track

NUS Hackers asks teams to reverse engineer an opaque app/service/device/system, improve it, and make it open source. Its rubric weights are status-quo cost 20%, reach 15%, coolness 25%, cost reduction 25%, open-source licensing 15%. Merely choosing an open-source aviation demo does not establish that workflow or dual-track eligibility. No joint-track eligibility, product license, or public-repo decision is assumed.
