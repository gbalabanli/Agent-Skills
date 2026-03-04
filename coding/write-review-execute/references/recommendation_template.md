# Recommendation Output Template

Use this section order exactly.

## 1. Problem Framing

- Objective
- Constraints
- In-scope and out-of-scope

## 2. Clarifications and Assumptions

- User clarifications received
- Remaining assumptions
- Ambiguity impact on confidence

## 3. Execution Mode

- User choice: `theoretical-only` or `proof-of-concept`
- Why this mode applies
- Fallback usage if the user did not answer

## 4. Three Scaffold Alternatives

For each scaffold include:

- `name`
- `approach_summary`
- `assumptions`
- `key_differences` from other scaffolds
- `review_findings`

## 5. Execution Evidence

For each scaffold include:

- Command or reason not executed
- Output summary
- Pass or fail signal

## 6. Weighted Scoring

- Criteria table with scores and weights
- Weighted total score per scaffold
- Hard-gate pass or fail status
- Sensitivity note (stable or rank-flip)

## 7. Recommendation and Fallback

- Primary recommendation
- Why it wins under current constraints
- Explicit switch condition to runner-up

## 8. Next Validation Step

- One fast validation action
- Success signal
- Failure signal and next move
