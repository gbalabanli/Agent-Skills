# Weighted Scoring Rubric

Use normalized scores in the range `[0.0, 1.0]` where higher is better.

## Default Criteria and Weights

`score(a) = sum(weight_i * metric_i(a))`

| criterion | weight | description |
|---|---:|---|
| `correctness` | `0.40` | Behavioral correctness and requirement coverage from review and tests. |
| `execution_evidence` | `0.20` | Validation strength from command outcomes in selected execution mode. |
| `maintainability` | `0.20` | Readability, modularity, and ease of safe change. |
| `complexity` | `0.10` | Implementation simplicity and cognitive load. |
| `performance_risk` | `0.10` | Runtime efficiency posture and operational risk profile. |

## Hard Gates

- Gate 1: `correctness` must be at least `0.60`.
- Gate 2 in `proof-of-concept` mode: scaffold execution must not end in hard failure.
- If all alternatives fail a gate, still rank them by weighted score and call out the risk explicitly.

## Execution Evidence Scoring

- `proof-of-concept` mode:
  - command passes: `1.00`
  - command fails: `0.20`
  - command times out or cannot run: `0.00`
- `theoretical-only` mode:
  - no command run: `0.50` (neutral evidence baseline with reduced confidence)

## Sensitivity Note

Run a quick stability check on the top 2 weighted criteria:

1. Increase one top weight by `+20%` and re-normalize.
2. Decrease one top weight by `-20%` and re-normalize.
3. Report any rank flips. If flips occur, mark recommendation as weight-sensitive.
