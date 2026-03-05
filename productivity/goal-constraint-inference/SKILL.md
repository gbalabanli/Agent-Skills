---
name: goal-constraint-inference
description: Infer hard constraints, optimization constraints, dependency/conflict relations, and priority weights from high-level goals, then produce alternative solution portfolios and a best balanced recommendation. Use when a user asks to turn a target into feasible constraints, resolve conflicting requirements, compare tradeoffs, define what goal should be optimized, or apply forward and inverse optimization reasoning.
---

# Goal Constraint Inference

## Objective

Convert vague goals into a decision-ready optimization model with explicit constraints, feasibility analysis, alternatives, and a recommended target objective.

## Workflow

### 1) Frame the goal as an objective

1. Rewrite the goal as an objective function statement.
2. Identify objective type: maximize, minimize, hit target band, or multi-objective.
3. Define success metric, threshold, and time horizon.
4. Mark unknowns that block accurate optimization.

### 2) Infer constraints from the goal and context

Infer and classify:
- Hard constraints (must hold; violation invalidates solution)
- Soft constraints (preferences; can be traded off)
- Resource constraints (time, budget, people, compute)
- Policy constraints (legal, compliance, safety, governance)
- Structural constraints (architecture, dependency, capability limits)
- Latent constraints (implied by user intent but unstated)

Each inferred constraint must include:
- Why it exists
- How to test satisfaction
- Confidence level (high, medium, low)

### 3) Model constraint relations

Map explicit relations:
- Depends-on: constraint A requires B
- Blocks: A makes B infeasible
- Amplifies: tightening A increases pressure on B
- Relaxes: relaxing A improves feasibility for B
- Competes: improving A worsens B

Feasibility checks:
1. Detect hard-hard conflicts.
2. Detect chains that make the objective impossible.
3. Flag minimum relaxations required to recover feasibility.

### 4) Run forward and inverse optimization reasoning

Forward optimization:
1. Choose decision variables.
2. Optimize objective under hard constraints.
3. Rank soft constraints by marginal impact.

Inverse optimization:
1. Take desired end-state or preferred plan as input.
2. Infer implied weights/priorities across constraints.
3. Surface hidden priorities or contradictions with stated goals.

Priority model:
- Tier 1: non-negotiable hard constraints
- Tier 2: high-impact optimization constraints
- Tier 3: optional preferences
- Assign relative weights within each tier and explain rationale.

### 5) Build solution portfolios

Produce at least 3 alternatives:
1. Feasibility-first: maximizes constraint satisfaction and delivery certainty.
2. Balanced: best tradeoff across objective value, risk, and cost.
3. Performance-first: prioritizes objective gain and accepts controlled risk.

For each alternative include:
- Objective value (expected)
- Satisfied and violated constraints
- Risk profile and failure mode
- Cost/complexity estimate
- Conditions where it is preferred

### 6) Recommend best target and plan

1. Recommend the best balanced solution.
2. If original goal is infeasible, propose revised goal and explain why.
3. List which constraints are most important and which can be relaxed.
4. Provide stepwise execution order and monitoring checkpoints.

## Output Requirements

Before final answer:
1. Load `references/report-template.md`.
2. Fill every required section.
3. Keep assumptions explicit and traceable to constraints.
4. State uncertainty where confidence is medium or low.

Minimum quality bar:
- At least 8 inferred constraints for non-trivial goals unless scope is tiny.
- At least one dependency/conflict graph summary.
- At least one inverse-optimization insight.
- At least 3 alternatives and one recommended solution.
- Clear statement of which constraints dominate optimization outcome.

## Guardrails

Do not:
- Treat soft preferences as hard constraints without evidence.
- Recommend an option that violates Tier 1 constraints.
- Hide infeasibility; report it and propose a balanced relaxation path.
- Give a single solution without alternatives and rationale.

If required inputs are missing, infer provisional constraints with confidence labels and continue.
