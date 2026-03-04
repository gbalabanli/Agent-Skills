# Decision Brief Template

Use this section order exactly.

## 1. Problem Framing
- Objective
- Context
- In-scope and out-of-scope

## 2. Clarifications and Assumptions
- Clarifications received
- Remaining assumptions
- Confidence impact from unresolved ambiguity

## 3. Constraint Register
- Include a table with:
  - `id`
  - `type` (`hard|soft|derived|optimization`)
  - `statement`
  - `metric`
  - `target_or_limit`
  - `priority_or_weight`
  - `dependencies`
  - `risk_if_violated`

## 4. Constraint Dependency and Conflict Analysis
- Dependency map summary (`supports|conflicts|independent`)
- Conflict severity (`low|medium|high`)
- Crush-risk findings and mitigation notes

## 5. Optimization Function
- Mode selected (`weighted|lexicographic|pareto`)
- Function or ranking rule
- Inputs used
- Sensitivity or tie-break treatment

## 6. Alternative Solutions
- Provide exactly 3 alternatives unless user asks for a different count.
- For each alternative include:
  - `name`
  - `approach_summary`
  - `assumptions`
  - `constraint_impacts`
  - `risks`
  - `implementation_complexity`
  - `expected_benefit`

## 7. Comparative Scoring
- Show comparative table aligned to selected optimization mode.
- Highlight dominant strengths and critical weaknesses.
- Report ranking stability if sensitivity checks were run.

## 8. Recommendation and Fallback Trigger
- Primary recommendation
- Why it wins under current constraints
- Explicit condition that triggers switch to runner-up

## 9. Next Validation Step
- One fast validation action
- Success signal
- Failure signal and what to do next
