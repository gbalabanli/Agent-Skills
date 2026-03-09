---
name: goal-constraint-inference
description: Infer hard constraints, negative constraints, optimization constraints, dependency/conflict relations, and priority weights from high-level goals, then produce alternative solution portfolios and a best balanced recommendation. Use when a user asks to turn a target into feasible constraints, clarify what must not happen, resolve conflicting requirements, compare tradeoffs, define what goal should be optimized, or apply forward and inverse optimization reasoning.
---

# Goal Constraint Inference

## Objective

Convert vague goals into a decision-ready optimization model with explicit constraints, feasibility analysis, alternatives, and a recommended target objective.

## Workflow

### 1) Frame the goal as an objective

1. Rewrite the goal as an objective function statement.
2. Identify objective type: maximize, minimize, hit target band, or multi-objective.
3. Define success metric, threshold, and time horizon.
4. Capture anti-goals or negative-space signals: what the user does not want, what outcomes are unacceptable, and what the solution must not become.
5. Mark unknowns that block accurate optimization.

### 2) Infer constraints from the goal and context

Infer and classify:
- Hard constraints (must hold; violation invalidates solution)
- Soft constraints (preferences; can be traded off)
- Negative constraints (explicit don'ts, anti-goals, exclusions, forbidden states)
- Resource constraints (time, budget, people, compute)
- Policy constraints (legal, compliance, safety, governance)
- Structural constraints (architecture, dependency, capability limits)
- Latent constraints (implied by user intent but unstated)

Each inferred constraint must include:
- Why it exists
- How to test satisfaction
- Confidence level (high, medium, low)

Negative constraint handling:
- Treat statements like "don't", "avoid", "must not", "not X", and "anything except Y" as candidate constraints, not side comments.
- Preserve the original negative wording and also translate it into a testable boundary condition.
- If a negative constraint implicitly defines the feasible set, surface that explicitly.
- Classify each negative constraint as hard or soft based on user wording and consequence severity.

Ambiguity protocol for negative constraints:
1. When the feasible set is under-specified, ask up to 3 targeted anti-goal questions before assuming preferences.
2. Prefer prompts such as:
   - What would make this solution unacceptable even if it achieves the goal?
   - What approaches, outputs, or side effects must be avoided?
   - What should this not turn into?
3. If the user does not answer, infer provisional negative constraints with confidence labels and continue.

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
3. Detect negative constraints that collapse the feasible space to an empty or near-empty set.
4. Flag minimum relaxations required to recover feasibility.

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
- Negative constraints may appear in any tier; do not downgrade them solely because they are expressed as exclusions.
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
4. Call out which negative constraints define the boundary of the solution set.
5. Provide stepwise execution order and monitoring checkpoints.

## Example Pattern

### Example: Negative Constraint Defines the Set

User goal:
- Build a note system for research ideas, but do not turn it into a task manager.

Interpretation:
- Positive objective: maximize idea capture and retrieval quality.
- Negative constraint: the system must not introduce task-tracking structures as a primary interaction model.
- Boundary insight: by excluding "task manager" behavior, the user is already defining the allowed solution set.

Targeted ambiguity questions:
- What specific task-manager behaviors should be excluded: due dates, priorities, assignees, status columns, reminders?
- Is lightweight tagging or inbox triage acceptable if it does not become a workflow board?
- What would make the result feel too much like task management?

Example inferred constraints:
- C1 Hard/Negative: no required fields for due date, owner, or status progression.
- C2 Hard/Structural: primary object must be a note or idea entry, not a task card.
- C3 Soft/Negative: avoid UI metaphors associated with kanban or sprint planning.

Resulting modeling rule:
- When a user defines the space through exclusions, preserve the exclusion as a first-class constraint and optimize only within the remaining feasible set.

### Example: Define the Set Through Non-Membership

User goal:
- Design a collaboration workflow, but not something that behaves like a ticket queue.

Interpretation:
- Positive objective: improve coordination speed and clarity.
- Negative constraint: exclude queue-like behaviors from the solution class.
- Set insight: saying "not a ticket queue" already defines the boundary of the acceptable set by ruling out one family of structures.

Targeted ambiguity questions:
- Which queue signals are unacceptable: numbered intake, FIFO ordering, mandatory assignment, status transitions, SLA tracking?
- Can requests still be logged if they are treated as conversations instead of queue items?
- What is the closest acceptable behavior without crossing into ticket-queue semantics?

Example inferred constraints:
- C4 Hard/Negative: no canonical workflow where work enters a single ordered backlog and advances through fixed queue states.
- C5 Hard/Structural: collaboration must center on shared context and live negotiation, not serialized intake-processing.
- C6 Soft/Negative: avoid terminology such as ticket, triage, backlog, or resolve if those terms would push user behavior toward queue management.

Resulting modeling rule:
- If the user defines a concept by excluding neighboring concepts, model those excluded neighbors as negative constraints that carve the feasible set.

## Output Requirements

Before final answer:
1. Load `references/report-template.md`.
2. Fill every required section.
3. Keep assumptions explicit and traceable to constraints.
4. State uncertainty where confidence is medium or low.

Minimum quality bar:
- At least 8 inferred constraints for non-trivial goals unless scope is tiny.
- At least one explicit negative constraint or a statement that no meaningful negative constraints were identified.
- At least one dependency/conflict graph summary.
- At least one inverse-optimization insight.
- At least 3 alternatives and one recommended solution.
- Clear statement of which constraints dominate optimization outcome.

## Guardrails

Do not:
- Treat soft preferences as hard constraints without evidence.
- Drop or paraphrase away a user-stated negative constraint if it changes feasibility or ranking.
- Recommend an option that violates Tier 1 constraints.
- Hide infeasibility; report it and propose a balanced relaxation path.
- Give a single solution without alternatives and rationale.

If required inputs are missing, infer provisional constraints with confidence labels and continue.
