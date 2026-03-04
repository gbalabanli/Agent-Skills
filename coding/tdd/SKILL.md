---
name: tdd
description: Build features and fix bugs using a strict Test-Driven Development workflow (Red-Green-Refactor), with regression-first bugfixing and explicit clarification when expected behavior is ambiguous. Use when Codex must implement or repair behavior with high confidence, test evidence, and minimal-risk changes.
---

# TDD

Use this skill to implement features and fix bugs with a test-first workflow.

## Workflow

1. Classify task and goal.
- Determine whether the request is `feature`, `bugfix`, or mixed.
- Capture expected behavior, acceptance criteria, and non-functional constraints.
- If behavior is ambiguous, ask concise clarifying questions before writing tests.

2. Resolve ambiguity before test design.
- Ask only high-impact questions that change expected behavior or test assertions.
- Ask up to 2 rounds of clarifying questions.
- If still unresolved, proceed with explicit assumptions and mark risk.

3. Write failing test first (`Red`).
- Add or update tests that express expected behavior before production changes.
- For bugfixes, reproduce the bug with a regression test that fails on current code.
- Prefer the smallest test scope that proves behavior.

4. Implement minimal change (`Green`).
- Modify production code only after the failing test exists.
- Make the minimal change needed for tests to pass.
- Avoid broad refactors during this step.

5. Refactor safely (`Refactor`).
- Improve design only with tests passing.
- Keep behavior unchanged while reducing complexity and duplication.

6. Strengthen test coverage.
- Add edge, negative, and boundary cases relevant to risk.
- Validate that original failing scenario is permanently covered.

7. Run verification.
- Run focused tests first, then broader suite as appropriate.
- If tests fail, return to `Red` and iterate.

8. Report outcome.
- Summarize failing test introduced, code change, and proof of pass state.
- List assumptions, residual risks, and follow-up tests if needed.

## Mode Rules

- Never implement behavior without first expressing it in a failing test.
- For bugfixes, require a regression test that fails before the fix.
- Keep each cycle small and reversible.
- Prefer deterministic tests over brittle integration-only checks.

## Output Rules

- Use [tdd_output_template.md](references/tdd_output_template.md) for final responses.
- Include the exact tests added/updated and what they verify.
- Explicitly separate facts from assumptions.
- If blocked by ambiguity, show the missing detail and why it affects test validity.

## References

- [tdd_cycle_checklist.md](references/tdd_cycle_checklist.md)
- [bugfix_regression_playbook.md](references/bugfix_regression_playbook.md)
- [test_design_heuristics.md](references/test_design_heuristics.md)
- [tdd_output_template.md](references/tdd_output_template.md)
