# Airbus #2 — UI-led idea cards

These are candidates for discussion, not approved scope. All three must satisfy A2-01 through A2-10 in [requirements](airbus-2-requirements.md). Recommendation: **Recovery Desk**, because one disrupted arrival gives the three agents a clear shared decision and makes both disagreement and agreement visible in a short demo.

## 1. Recovery Desk — recommended

- **Problem/current workaround:** a disruption forces ATC, cockpit and ground teams to reconcile arrival timing and gate readiness through separate updates; this manual coordination problem is described in the brief.
- **Specific user:** an airport duty manager reviewing one disrupted arrival and its resource conflicts.
- **One-sentence solution:** three independent agents negotiate one validated recovery plan while the duty manager sees what changed and why.
- **Smallest input → action → result:** select one qualifying historical delay row plus visibly labeled operational scenario inputs → run bounded negotiation → review revised arrival/gate plan, constraint outcomes and the complete agreement record.
- **Requirements:** all A2 requirements; foreground A2-05/06/09 through a live negotiation trace. Model all role responsibilities, with hard checks only where inputs/rules are supported; label any omitted factors explicitly.
- **Differentiator/source pattern:** a proposal comparison table and shared resource timeline make trade-offs inspectable. Original candidate derived from the supplied challenge; no external idea catalog used.
- **Tentative capabilities:** independent role contexts/invocations; bounded coordinator; deterministic feasibility checker/candidate search; trace stream. Runtime/provider not selected.
- **Demo/evidence:** show an initial timing/gate conflict; reject an invalid candidate with a rule and values; converge on the same plan revision; show the fallback/infeasible case. Compare with a first-feasible deterministic baseline under identical simulator constraints.
- **Feasibility/uncertainty:** lowest scope of these candidates; actual estimate awaits deadline/team. Dataset lacks verified schema/access; detailed operational inputs are unverified. First investigation: representative row and minimum resource model, not model training.
- **Optional extension:** a what-if replay can expose sensitivity; requires a stable simulator and displaces visual polish or extra scenarios. Defer until the core journey works.
- **Facts vs hypotheses:** independent roles, dataset predicate and turn bound are source facts. Adoption, improved decisions and saved delay are hypotheses; no savings claimed.

### UI to react to

One primary workspace, with a compact case selector and history drawer rather than multiple dashboards:

```text
Recovery Desk   |   historical replay + simulated operations
Case / disruption / source row   |   Run negotiation   |   Round 1 of 2

Affected flights + inputs | Arrival and gate timeline | ATC / Pilot / Ground
                         | Current vs proposed plan  | Proposal / counteroffer
                         | Resource conflicts        | Accept / reject + reason

Plan comparison: arrival / gate / holding / constraint results / assumptions
Consensus: plan revision + 3 acceptances   |   Review plan / inspect evidence
```

Select an event → inspect input provenance → run negotiation → inspect disagreement → review the validated plan. Clicking a rejected gate/timeline slot opens the applied rule, source/assumption, observed value and limit. Keep the numeric timeline and proposed changes more prominent than agent prose. No decorative globe or 3D airport is needed for this decision.

Essential states: no data; invalid row; ready; running by round; proposal rejected; consensus; timeout/fallback; infeasible/escalate; missing evidence. Consensus is not execution. A later execution action, if included, belongs only to the simulator and must be labeled accordingly.

## 2. Runway Recovery Board

- **Problem/current workaround:** a runway closure causes re-sequencing that ripples into gate occupancy and airborne holding.
- **Specific user:** an ATC supervisor coordinating a small arrival queue with cockpit and ground constraints.
- **Solution/journey:** select a qualifying row and a labeled runway-closure scenario → agents negotiate arrival slots → show a feasible revised queue or escalation.
- **Requirements:** all A2 IDs; puts A2-02/03 and A2-10 at the center. Each role must still have independent evidence and responses.
- **UI/differentiator:** runway lanes and time blocks, paired with gate lanes and a visible fuel-limit marker; click a move to explain the ripple. Prefer agent-generated candidate moves; avoid manual drag-and-drop in the MVP.
- **Tentative capabilities:** adds multi-flight sequencing, resource intervals and deterministic search to the same independent-agent framework.
- **Demo/evidence:** closure → rejected landing sequence → feasible re-sequence; compare feasibility and total simulator delay with first-come-first-served under identical rules.
- **Feasibility/uncertainty:** larger deterministic modeling burden. Need validated wake/separation inputs, closure bounds, multiple flights and fuel assumptions, none verified in the organizer data. Timebox the resource-model investigation before committing.
- **Optional extension:** animated airport schematic may help spatial blockage explanation but displaces solver coverage and adds UI work. Only add if spatial topology actually changes the decision.
- **Facts vs hypotheses:** source requires wake separation and taxiway handling; queue size, closure length, airport layout and benefit numbers are proposed simulation inputs.

## 3. Connection Rescue

- **Problem/current workaround:** a late arrival threatens passenger transfers, while arrival priority, gate assignment and crew windows compete.
- **Specific user:** an airline operations duty manager coordinating a connection-sensitive arrival.
- **Solution/journey:** qualifying delay row plus labeled connection/gate assumptions → three agents negotiate a recovery option → explain who benefits, who waits and which hard constraints remain satisfied.
- **Requirements:** all A2 IDs; foreground Pilot passenger preferences and Ground gate/turnaround trade-offs without hiding ATC checks.
- **UI/differentiator:** flight and connection timeline, gate alternatives and a comparison of estimated connection exposure. Show source badges beside assumed passenger counts/walking times; no unsupported passenger-saving claim.
- **Tentative capabilities:** same core framework plus a connection model and an explicit, non-safety preference objective.
- **Demo/evidence:** reject an attractive gate that is incompatible or occupied; choose a feasible alternative; compare only simulator connection outcomes against the same deterministic baseline.
- **Feasibility/uncertainty:** stronger human story but largest evidence gap: itineraries, passenger counts and terminal walking times have not been obtained. Drop this candidate if such assumptions would dominate the demo.
- **Optional extension:** terminal walking visualization needs credible topology and transfer times; it displaces core negotiation coverage. Do not implement before data/benefit can be checked.
- **Facts vs hypotheses:** protecting connections is in the brief; detailed passenger transfer data and improvement are not verified.

## Comparison (coordinator judgment, not judging predictions)

| Candidate | Main visible decision | Build burden | Main uncertainty |
| --- | --- | --- | --- |
| Recovery Desk | Which arrival/gate plan can all three accept? | Smallest | Minimum operational scenario data |
| Runway Recovery Board | Which arrival order works after closure? | Larger | Separation and multi-flight resource model |
| Connection Rescue | Which plan best protects connections within constraints? | Larger | Passenger/terminal data and assumed benefits |

## Proposed common guardrails and evaluation

For any selected candidate, independent agents exchange structured proposal/response records. The deterministic engine checks hard constraints before acceptance. All roles must accept the same immutable proposal revision; prior acceptances do not survive a modification. Bound rounds and wall-clock time. Invalid/malformed messages consume the budget rather than opening unlimited retries. Fallback is deterministic and validates its output; missing critical inputs or no feasible candidate yields escalation, not a fabricated clearance.

Evaluate against the same scenario set and rules: eligibility correctness; zero accepted hard-constraint violations; exact plan-version agreement; convergence within the defined budget; runtime/model-call count; fallback coverage; simulator objective versus first-feasible baseline. Include at least one infeasible case, one missing-input case and one invalid-agent-output case. These are proposed checks, not implemented tests or existing results.

Historical delay records seed replay scenarios. Keep observed source columns separate from simulated fuel, wake categories, gates, crews and passenger data. The challenge does not imply the provided CSV contains every operational input. Label assumptions on screen and export them with the trace. Avoid claiming causal real-world savings from retrospective data or a simulator comparison.
