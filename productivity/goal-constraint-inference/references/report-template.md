# Goal Constraint Inference Report Template

Use this template for final output.

## 1. Goal Definition
- Original goal:
- Objective function statement:
- Objective type: maximize | minimize | target-band | multi-objective
- Success metric(s):
- Time horizon:
- Key assumptions:

## 2. Inferred Constraints
| ID | Constraint | Type (Hard/Soft) | Category | Test Method | Confidence | Priority Tier | Weight |
|----|------------|------------------|----------|-------------|------------|---------------|--------|
| C1 |            |                  |          |             |            |               |        |

Categories: Resource, Policy, Structural, Risk, Quality, Timeline, Cost.

## 3. Constraint Relations
### 3.1 Dependency and Conflict Summary
- Depends-on:
- Blocks:
- Competes:
- Relaxes:
- Amplifies:

### 3.2 Feasibility Assessment
- Is original goal feasible under inferred hard constraints? yes/no
- If no, minimum required relaxations:
- Critical bottlenecks:

## 4. Optimization Analysis
### 4.1 Forward Optimization View
- Decision variables:
- Objective under full hard constraints:
- Highest-impact soft constraints:
- Sensitivity notes:

### 4.2 Inverse Optimization View
- Desired end-state provided:
- Implied hidden weights/priorities:
- Contradictions between stated goal and implied priorities:

## 5. Alternative Solutions
### Alternative A: Feasibility-First
- Objective score:
- Hard constraints satisfied:
- Soft constraints sacrificed:
- Risk/cost/complexity:
- Best when:

### Alternative B: Balanced
- Objective score:
- Hard constraints satisfied:
- Soft constraints traded off:
- Risk/cost/complexity:
- Best when:

### Alternative C: Performance-First
- Objective score:
- Hard constraints satisfied:
- Soft constraints sacrificed:
- Risk/cost/complexity:
- Best when:

## 6. Recommended Solution
- Recommended alternative:
- Why this is best balanced:
- Dominant constraints (most important):
- Relaxable constraints (lowest cost to relax):
- Revised goal (if original is infeasible):

## 7. Execution and Monitoring Plan
1. Step 1:
2. Step 2:
3. Step 3:

Monitoring checkpoints:
- Leading indicators:
- Constraint breach alerts:
- Rollback triggers:

## 8. Decision Summary
- What should be optimized first:
- What to protect at all costs:
- What tradeoff is acceptable:
- Final decision statement:
