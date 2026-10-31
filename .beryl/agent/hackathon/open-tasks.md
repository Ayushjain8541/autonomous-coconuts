# P4 open-task queue

Owner: P4. This is a lightweight local queue until the team chooses GitHub issues. Do not create a second competing status ledger. Role briefs are specifications, not evidence that implementation has begun.

| ID | Task / owned scope | Prerequisite | State |
| --- | --- | --- | --- |
| F-01 | Locate/verify training-data source and document the schema/checksum/access handoff in evidence.md; do not change training code | Source links in evidence.md; coordinate local transfer with P3 | Ready for P4 to claim |
| F-02 | Check JSON fixture consistency and propose contract edge cases; own test helper under tests/contracts/ if needed | Current contracts/examples; no schema mutation without P2 | Ready for P4 to claim |
| F-03 | Prepare concise demo/evidence checklist and submission requirements in demo.md | Product brief; portal details may need human input | Ready for P4 to claim |
| F-04 | Verify UI/API/model real round trip and invalid-input/provider-failure behavior; own tests/e2e/ | Actual app baselines and model adapter integrated | Bootstrap round trip checked; full-product path blocked on P1/P2/P3 |
| F-05 | Consolidate root setup, optional CI and deployment instructions | Owners' verified setup commands; authorized deployment target/access | Local setup/CI now present; deployment remains blocked on target/access |

Claim record: task ID, P4, branch, exact file scope, start/status, dependency evidence. Complete with commit/PR and check results in handoffs/P4.md. Take one task at a time. Do not claim blocked work by fabricating its dependency. For help in another person's files, agree scope with that owner first. Creating accounts, obtaining credentials, changing shared interfaces or messaging people are not implicit queue permissions.
