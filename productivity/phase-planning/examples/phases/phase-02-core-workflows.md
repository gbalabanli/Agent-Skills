# Phase 02: Core Workflows

## Phase Metadata
- Status: In progress
- Last Updated: 2026-03-02
- Related Master Plan: [../master_plan.md](../master_plan.md)

## Objective
- Move the highest-value inventory workflows to the new service layer.

## Entry Criteria
- Phase 01 is complete.

## In Scope
- Stock adjustments
- Purchase order ingestion
- Inventory reconciliation

## Out Of Scope
- Reporting improvements

## Dependencies
- Phase 01 complete
- Stable legacy schema contracts

## Deliverables
- New service endpoints for core workflows
- Dual-run validation for critical jobs
- Cutover checklist draft

## Acceptance Criteria
- Core workflows run reliably on the new service layer in staging.
- Validation confirms parity with legacy outcomes.

## Risks And Blockers
- Legacy schema drift may invalidate migration assumptions.

## Exit Criteria
- Core workflows are ready for production cutover planning.

## Master Plan Sync Notes
- Keep Phase 02 marked `In progress`.
- Reflect the schema drift risk in `docs/master_plan.md`.
