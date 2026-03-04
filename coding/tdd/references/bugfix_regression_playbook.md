# Bugfix Regression Playbook

## 1. Reproduce

- Capture exact failure signal: stack trace, wrong output, or broken behavior.
- Isolate minimal input or scenario that reproduces the bug.

## 2. Lock with Regression Test

- Add a failing test that reproduces the bug.
- Name test to describe broken behavior, not implementation detail.
- Verify failure on current code before fixing.

## 3. Fix Minimally

- Change only code required to make regression test pass.
- Preserve surrounding behavior unless explicitly requested.

## 4. Guard Against Relapse

- Add at least one nearby edge case test.
- If root cause is category-wide, add parameterized or table-driven coverage.

## 5. Verify

- Run focused tests around the bug path.
- Run broader suite appropriate for impact radius.

## 6. Report

- Root cause summary.
- Regression test added.
- Fix summary.
- Residual risk and follow-up suggestions.
