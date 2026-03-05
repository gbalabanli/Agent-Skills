# Master Plan Template

Use this template for `docs/master_plan.md` (or an existing equivalent path/casing such as `docs/MASTER_PLAN.md`).

```md
# <Project Name> Master Plan

## Planning Metadata
- Last Updated:
- Planning Horizon:
- Overall Status:

## Project Goal
- State the end result in one clear paragraph.

## Current Status Snapshot (Optional)
- Summarize what is already complete and what is currently active.

## Success Criteria
- Define measurable outcomes that prove the plan is complete.

## Scope Summary
### In Scope
- List the workstreams this plan covers.

### Out of Scope
- List explicitly excluded work.

## Assumptions And Open Questions
- Prefix uncertain statements with `Assumption:` or `Open question:`.

## Delivery Strategy
- Explain why the project is divided into these phases.
- Note any sequencing constraints or parallel tracks.

## Phase Index
Use file links for split layouts, or section-anchor links for consolidated roadmaps.

| Phase | Status | Goal | Depends On | Document |
| --- | --- | --- | --- | --- |
| Phase 01 | Planned | <Short goal> | None | [phase-01-<slug>.md](phases/phase-01-<slug>.md) |

## Phase Gates (Optional)
- Define named gates and the criteria to pass each gate.

## Quality Targets (Optional)
- Define non-functional targets that phases must preserve (for example performance, reliability, usability).

## Cross-Phase Dependencies
- Track dependencies that affect more than one phase.

## Major Milestones
- List milestone names and what unlocks them.

## End-State Deliverables (Optional)
- List the concrete artifacts or outcomes expected at project completion.

## Global Risks And Decisions
- Record high-impact risks, decisions, and tradeoffs.

## Change Log
- Summarize material planning changes when phases are added, removed, or re-scoped.
```
