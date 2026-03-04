# TDD Cycle Checklist

## Red

- State expected behavior in one sentence.
- Write a test that fails for the right reason.
- Confirm failure output matches expected gap.

## Green

- Implement the smallest change to pass the failing test.
- Avoid unrelated cleanup in this step.
- Confirm new test passes.

## Refactor

- Improve readability and structure without behavior change.
- Keep all tests green during refactor.
- Re-run affected suite after each meaningful refactor step.

## Loop Rules

- Keep each loop small.
- Start next loop only after current loop is green.
- If behavior changes, go back to Red with a new failing test.
