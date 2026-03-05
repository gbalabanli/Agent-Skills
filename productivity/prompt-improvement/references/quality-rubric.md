# Prompt Quality Rubric

Use this pass/fail-oriented scoring before returning an improved prompt.

## Scoring

- `0`: missing or weak
- `1`: present but incomplete
- `2`: clear, explicit, and testable

## Categories

1. Intent Fidelity (max 2)
- Is original user intent preserved without scope drift?

2. Objective and Format Specificity (max 2)
- Are objective and output format explicit?

3. Constraint Clarity (max 2)
- Are hard constraints and optimization constraints explicit and testable?

4. Verification Strength (max 2)
- Are validation expectations defined where relevant (tests/lint/citations/sanity checks)?

5. Conciseness and Token Efficiency (max 2)
- Is wording compact and free from redundant instructions?

## Thresholds

- `8-10`: ready for execution
- `6-7`: usable but should be tightened
- `<6`: must refine before returning

## Required Pass Conditions

- Explicit objective
- At least one hard constraint
- Ranked optimization constraints
- Explicit output format/schema
- Verification expectation when task requires validation
