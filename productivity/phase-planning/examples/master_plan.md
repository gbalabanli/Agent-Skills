# Inventory Platform Master Plan

## Planning Metadata
- Last Updated: 2026-03-02
- Planning Horizon: 12 weeks
- Overall Status: In progress

## Project Goal
- Modernize the inventory platform without interrupting warehouse operations.

## Success Criteria
- New deployment pipeline is live.
- Core inventory workflows run on the new service layer.
- Legacy batch jobs are retired.

## Scope Summary
### In Scope
- Platform foundation
- Service extraction
- Cutover and stabilization

### Out of Scope
- New warehouse hardware integrations

## Assumptions And Open Questions
- Assumption: Existing warehouse devices keep using the current protocol.

## Delivery Strategy
- Establish safe foundations first, then move business workflows, then cut over traffic and remove the legacy path.

## Phase Index
| Phase | Status | Goal | Depends On | Document |
| --- | --- | --- | --- | --- |
| Phase 01 | Done | Establish delivery foundation | None | [phase-01-foundation.md](phases/phase-01-foundation.md) |
| Phase 02 | In progress | Migrate core inventory workflows | Phase 01 | [phase-02-core-workflows.md](phases/phase-02-core-workflows.md) |

## Cross-Phase Dependencies
- Data contract changes from Phase 02 must stay backward compatible until final cutover.

## Major Milestones
- CI and observability baseline complete.
- Core workflows run through the new service layer.
- Production cutover complete.

## Global Risks And Decisions
- Risk: Legacy schema drift could delay the cutover plan.
- Decision: Delay reporting improvements until after production cutover.

## Change Log
- 2026-03-02: Marked Phase 01 complete and started Phase 02.
