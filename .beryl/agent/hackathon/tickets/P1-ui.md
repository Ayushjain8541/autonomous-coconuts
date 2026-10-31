# P1 — Operator UI

**Owner:** P1. **Suggested branch:** `p1/ui`. **Scope:** `web/` and its UI-specific setup/dependencies/checks; `.beryl/agent/hackathon/handoffs/P1.md`. **Requirements:** A1-03/04, U-01/02; support evidence for A1-01/02/U-03. Role specification only; no implementation is claimed.

## Read

Root AGENTS.md → [product brief](../product-brief.md) → this file → [contracts](../contracts.md) and the two JSON fixtures → current source/PRs relevant to your work. You do not need P3's training internals. Choose your own design tools, framework, components and implementation workflow. No exact layout, aesthetic, chart library or 3D engine is prescribed.

## Outcome you own

A coherent operator dashboard with Load Demo/upload, source-mode label, global critical banner, encounter list, relative timeline, globe/schematic selection aid, selected detail panel and Encounter geometry. Numeric analysis loads independently of LLM insights. Maintain one selection by event ID across views; filtering changes membership, not classification or global alerts.

The provided demo has a critical event in 36h and no critical event within 24h. The list's empty state, global banner persistence and outside-filter selected-detail state are all intentional. Details show predicted vs reported Pc, distance units, time basis, rule reasons and source/model metadata. Relative geometry is data-backed; schematic globe placement must be identified as schematic. The organizer asks for trajectories: coordinate a local relative-motion illustration with P3 where supportable, label assumptions, and record any unmet trajectory scope. Static geometry or a decorative globe alone is not complete trajectory coverage.

## Interfaces and dependencies

Consume the v1 analysis/insight responses and proposed HTTP routes in contracts.md. P2 owns the shared contract and API; P3 owns geometry/rule meaning. Start with labeled synthetic fixtures if the backend is absent; report that mode in your handoff. Coordinate type/shape amendments instead of adding incompatible UI-only success fields. Do not implement your own ML/risk tier engine in the frontend.

## Acceptance outcomes

- Load Demo shows the specified linked interaction, including a persistent 36h banner outside the 24h list.
- Upload errors are actionable; stale LLM responses do not replace the current selection/analysis. Pending, unavailable and fixture insight states are distinct.
- Missing geometry/probability is visible. Essential actions work with keyboard, and risk is not color-only. Narrow layouts remain usable.
- Once P2/P3 are integrated, the real upload-to-results journey works; remaining fixtures are named explicitly.

Record actual setup/check commands, browser observations, responsive/keyboard coverage and remaining dependencies in your handoff. Visual checks and targeted behavior checks are your choice; no mandatory test-writing procedure is imposed. Coordinate root/deployment changes with P4 and leave model/backend internals to their owners.
