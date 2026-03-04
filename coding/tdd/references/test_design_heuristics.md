# Test Design Heuristics

## Prioritize by Risk

- Start with behavior that is user-visible or business-critical.
- Cover failure modes that can corrupt data, break contracts, or cause outages.

## Keep Tests Stable

- Assert observable behavior, not internal implementation.
- Control time, randomness, and external I/O with fakes or deterministic fixtures.

## Cover Key Dimensions

- Happy path
- Boundary values
- Invalid inputs
- Error propagation
- Idempotency or retry behavior when relevant

## Scope Selection

- Prefer unit tests for fast feedback.
- Add integration tests only where boundaries or contracts matter.
- Use end-to-end tests for critical user journeys, not every branch.

## Readability Rules

- Use test names in behavior format: `should_<behavior>_when_<condition>`.
- Keep arrange-act-assert structure clear.
- One primary reason to fail per test when possible.
