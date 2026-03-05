---
name: playwright
description: Build, debug, and maintain Playwright end-to-end browser tests for web workflows. Use when Codex needs to create or update Playwright tests, fix flaky E2E behavior, configure Playwright projects, improve selectors and fixtures, or verify critical user journeys across browsers.
---

# Playwright

Use this skill to implement reliable Playwright test automation for product and agency workflows.

## Workflow

1. Clarify test objective.
- Capture user journey, expected behavior, and pass/fail criteria.
- Define scope: new test, flaky test fix, config update, or debug task.
- Confirm browser/device coverage needed for the task.

2. Inspect existing setup.
- Locate `playwright.config.*`, test folder layout, and shared fixtures.
- Reuse existing helpers, page objects, and conventions before adding new structure.
- Align naming, tagging, and project configuration with current repo standards.

3. Implement deterministic tests.
- Prefer resilient locators (`getByRole`, `getByLabel`, `getByTestId`) over brittle CSS/XPath.
- Use web-first assertions instead of fixed sleeps.
- Keep tests isolated with explicit setup and cleanup expectations.

4. Handle auth and state safely.
- Use setup projects or storage state for authenticated flows.
- Keep test data deterministic and minimize cross-test coupling.
- Avoid hidden dependencies on shared accounts or mutable global state.

5. Debug and stabilize failures.
- Run targeted tests first, then broader suites.
- Use trace viewer, screenshots, and videos to identify root causes.
- Fix timing, selector, and environment issues directly instead of retry inflation.

6. Prepare for CI reliability.
- Tune timeouts, retries, and workers for stable CI behavior.
- Separate smoke coverage from full regression by tags or projects.
- Keep cross-browser coverage focused on high-risk journeys.

7. Report outcomes.
- Summarize tests added or updated and why.
- Include commands run and observed results.
- Note residual risks and next validation steps.

## Output Rules

- Keep changes minimal and focused on requested behavior.
- Do not use arbitrary `waitForTimeout` unless there is no observable state to await.
- Prefer explicit assertions over implicit assumptions.
- Document unresolved flakiness with reproducible signals and likely causes.
