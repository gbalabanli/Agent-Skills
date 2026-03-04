# Constraint Modeling Guide

## Constraint Types

- `hard`: must be satisfied; violation makes option infeasible.
- `soft`: should be optimized; tradeoff is allowed.
- `derived`: introduced from dependency analysis to prevent hidden failures.
- `optimization`: added to formalize objective tradeoff when utility is unclear.

## Rules for Good Constraints

- Make every constraint measurable.
- Use one metric per constraint where possible.
- Define explicit target or bound.
- Link each constraint to decision impact.

## Rewrite Rules for Problematic Constraints

If a constraint is vague, rewrite it:

- Vague: "fast system"
- Measurable rewrite: "p95 latency <= 200 ms under 2k rps"

If a constraint is contradictory, split and prioritize:

- Conflict: "zero downtime" and "single maintenance window restart"
- Rewrite: mark uptime as `hard`; mark restart window as `soft` with fallback plan

If a constraint is disconnected from objective, either:

- connect it with a measurable impact, or
- drop it from scoring and mark it informational.

## Derived Constraint Rules

Add derived constraints when a dependency implies hidden limits.

Examples:

- If "cost cap" and "throughput target" both exist, derive "max cost per request."
- If "tight deadline" and "new stack adoption" both exist, derive "migration surface area limit."

## Dependency and Conflict Analysis

For each pair of constraints, classify as:

- `supports`
- `conflicts`
- `independent`

Flag crush risk when improving one constraint materially degrades another.

## Conflict Severity Rubric

- `low`: tradeoff exists but bounded and reversible.
- `medium`: tradeoff affects one core objective and needs mitigation.
- `high`: tradeoff can invalidate feasibility or primary objective.

For every `high` conflict, provide:

- mitigation option
- monitoring signal
- fallback decision trigger
