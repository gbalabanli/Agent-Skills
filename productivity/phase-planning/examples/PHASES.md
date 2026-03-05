# Phased Roadmap

## Phase 01: Foundation
Status: Done
Goal: Establish the delivery baseline needed for safe migration.
Duration Target (Optional): 3 weeks

### In Scope
- CI pipeline
- Baseline tests
- Observability baseline

### Out Of Scope
- Business workflow migration

### Dependencies
- None

### Deliverables
- Working CI pipeline
- Smoke test suite
- Shared logging dashboard

### Acceptance Criteria
- Every pull request runs CI and smoke tests.
- Core services emit baseline logs and metrics.

### Progress Snapshot (Optional)
#### Delivered So Far
- CI/CD baseline is deployed.

#### Known Gaps / Deferred Items
- Load testing deferred to Phase 02.

### Risks And Blockers
- None

### Exit Criteria
- Delivery foundation supports safe workflow migration.

### Master Plan Sync Notes
- Keep Phase 01 status as `Done` in the master plan.

## Phase 02: Core Workflows
Status: In progress
Goal: Move core workflows to the new service layer.
Duration Target (Optional): 5 weeks

### In Scope
- Stock adjustments
- Purchase order ingestion
- Inventory reconciliation

### Out Of Scope
- Reporting improvements

### Dependencies
- Phase 01 complete
- Stable legacy schema contracts

### Deliverables
- New workflow service endpoints
- Dual-run validation for critical jobs
- Cutover checklist draft

### Acceptance Criteria
- Core workflows run reliably in staging.
- Validation confirms parity with legacy outcomes.

### Risks And Blockers
- Legacy schema drift may invalidate migration assumptions.

### Exit Criteria
- Core workflows are ready for production cutover planning.

### Master Plan Sync Notes
- Keep Phase 02 marked `In progress`.
- Mirror schema drift risk in the master plan.

## Cross-Phase Validation Checklist (Optional)
- Keep schema changes backward compatible until cutover.
- Preserve current SLO targets during migration.
