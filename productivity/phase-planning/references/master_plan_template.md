# Master Plan Template

Use this template for `docs/master_plan.md`.

```md
# <Project Name> Master Plan

## Planning Metadata
- Last Updated:
- Planning Horizon:
- Overall Status:

## Project Goal
- State the end result in one clear paragraph.

## Success Criteria
- Define measurable outcomes that prove the plan is complete.

## Scope Summary
### In Scope
- List the workstreams this plan covers.

### Out of Scope
- List explicitly excluded work.

## Assumptions And Open Questions
- Prefix uncertain statements with `Assumption:` or `Open question:`.

## Key Constraints
- List the hard limits or obligations that shape the plan.
- Give reusable short labels such as `C1`, `C2`, and `C3` when phases need to reference them.

## Delivery Strategy
- Explain why the project is divided into these phases.
- Note how the key constraints affect sequencing, handoffs, or parallel tracks.

## Phase Index
| Phase | Status | Goal | Depends On | Document |
| --- | --- | --- | --- | --- |
| Phase 01 | Planned | <Short goal> | None | [phase-01-<slug>.md](phases/phase-01-<slug>.md) |

## Constraint Coverage
| Constraint | Affects Phases | Planned Response | Resolved By |
| --- | --- | --- | --- |
| C1 | Phase 01 | <Short mitigation, validation, or guardrail> | Phase 02 |

## Cross-Phase Dependencies
- Track dependencies and carried-forward constraints that affect more than one phase.

## Major Milestones
- List milestone names and what unlocks them.

## Global Risks And Decisions
- Record high-impact risks, decisions, and tradeoffs.

## Change Log
- Summarize material planning changes when phases are added, removed, or re-scoped.
```
