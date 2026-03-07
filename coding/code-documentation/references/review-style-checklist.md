# Review Style Checklist

Use this pass after drafting or revising documentation.

## Correctness

- Confirm names, paths, flags, APIs, and commands match the current codebase.
- Remove statements that cannot be verified.
- Replace vague claims like "easy" or "simple" with specifics or delete them.

## Completeness

- Check for missing prerequisites, configuration, edge cases, and failure behavior.
- Confirm the doc answers what it does, how to use it, and what can break.
- Add follow-up TODOs only when the gap cannot be resolved from available context.

## Clarity

- Put the most useful information first.
- Replace broad paragraphs with compact sections, tables, or examples when that improves scanning.
- Cut repetition and obvious commentary.

## Maintenance

- Prefer durable explanations over line-by-line narration of current implementation.
- Keep docs near the code they describe when possible.
- Note invariants and contracts that future changes must preserve.

## Tone

- Be direct, technical, and specific.
- State tradeoffs plainly.
- Optimize for the engineer who needs to modify the code next week.
