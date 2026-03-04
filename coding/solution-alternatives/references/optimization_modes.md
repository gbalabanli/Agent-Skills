# Optimization Modes

## Mode Selection

- `weighted`: default when user does not choose.
- `lexicographic`: use when top constraints are strict priority tiers.
- `pareto`: use when preserving non-dominated options is more important than one scalar score.

## Weighted Mode

Use normalized weighted scoring:

`score(a) = sum(w_i * n_i(a))`

- `w_i`: weight for constraint `i`
- `n_i(a)`: normalized performance of alternative `a` on constraint `i`

### Sensitivity Protocol

- Identify top weighted constraints.
- Vary each top weight by `+20%` and `-20%` while re-normalizing.
- Recompute ranking and report any rank flips.
- If top rank flips frequently, mark recommendation as unstable.

## Lexicographic Mode

- Group constraints into priority tiers.
- Evaluate highest tier first.
- Eliminate alternatives failing any hard requirement in active tier.
- Break ties using the next tier.
- Continue until a winner or final tie state.

Use when user says priorities are non-compensatory.

## Pareto Mode

- Treat constraint outcomes as a vector.
- Identify non-dominated alternatives.
- Do not collapse to one score before frontier analysis.
- If multiple non-dominated options remain, apply explicit tie-break preference:
  - lower implementation risk first
  - then lower complexity
  - then higher expected benefit

## Output Requirements by Mode

- Always state selected mode and why.
- Always show ranking logic or frontier logic clearly.
- Always include a fallback-switch condition.
