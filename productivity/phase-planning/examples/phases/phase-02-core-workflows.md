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

## Phase Constraints
- C1: Warehouse operations cannot be interrupted, so migration work must be validated before any production cutover.
- C2: Legacy schema contracts must stay backward compatible until the final cutover phase.
- C3: Reporting improvements remain deferred to protect delivery capacity for migration work.

## Phase TODOs
- Implement new service endpoints behind compatibility-safe contracts. (C2)
- Run dual-run validation for the highest-risk jobs before staging cutover. (C1)
- Draft the cutover checklist around rollback, parity checks, and compatibility verification. (C1, C2)
- Keep reporting changes out of active work so migration capacity stays focused on core workflows. (C3)

## Deliverables
- New service endpoints for core workflows
- Dual-run validation for critical jobs
- Cutover checklist draft

## Acceptance Criteria
- Core workflows run reliably on the new service layer in staging.
- Validation confirms parity with legacy outcomes.
- Backward compatibility is preserved for the legacy schema contracts.

## Risks And Blockers
- Legacy schema drift may invalidate migration assumptions.

## Exit Criteria
- C1 and C2 remain active and are handed forward with validation evidence and a cutover checklist draft.
- C3 remains satisfied by keeping reporting improvements outside this phase.

## Master Plan Sync Notes
- Keep Phase 02 marked `In progress`.
- Reflect the schema drift risk and the carried-forward C1/C2 constraints in `docs/master_plan.md`.
