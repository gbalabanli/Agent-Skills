# Phase Template

Use this template for each file in `docs/phases/`.

```md
# Phase <NN>: <Phase Name>

## Phase Metadata
- Status:
- Last Updated:
- Related Master Plan: [../master_plan.md](../master_plan.md)

## Objective
- State the single primary outcome for this phase.

## Entry Criteria
- Describe what must already be true before this phase starts.

## In Scope
- List the work this phase owns.

## Out Of Scope
- List nearby work that belongs to other phases.

## Dependencies
- List upstream phases, external blockers, and required decisions.

## Phase Constraints
- List only the constraints that actively shape this phase.
- Reference master-plan constraint labels when available.
- Note whether each constraint must be respected, validated, reduced, or retired in this phase.

## Phase TODOs
- List the concrete work items required to complete the phase.
- Each TODO must map to a deliverable, dependency, or active phase constraint.
- Call out the related constraint label when the task exists because of a constraint.

## Deliverables
- List the concrete outputs this phase must produce.

## Acceptance Criteria
- Define what must be true to mark the phase complete.
- Show that the required phase constraints were satisfied or validated.

## Risks And Blockers
- Record phase-specific risks, unknowns, and blockers.

## Exit Criteria
- Define what this phase hands to the next phase.
- State which constraints are resolved here and which are intentionally carried into later phases.

## Master Plan Sync Notes
- Note any status, scope, dependency, milestone, risk, or constraint changes that must also be reflected in `docs/master_plan.md`.
```
