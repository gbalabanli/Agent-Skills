---
name: solution-alternatives
description: Generate and compare multiple solution alternatives for hard issues using explicit constraint modeling, dependency and conflict analysis, and optimization-function reasoning. Use when Codex must evaluate tradeoffs, handle ambiguity with clarifying questions, refine problematic constraints, and recommend a primary option with fallback conditions.
---

# Solution Alternatives

Use this skill to produce decision-quality alternatives for hard issues with conflicting constraints.

## Workflow

1. Run intake.
- Capture objective, context, hard constraints, soft constraints, preferred risk level, and timeline.
- Ask which optimization mode to use: `weighted`, `lexicographic`, or `pareto`.
- Default to `weighted` if no mode is selected.

2. Resolve ambiguity with a bounded protocol.
- Ask clarifying questions only when ambiguity can change feasibility or ranking.
- Run up to 2 rounds of clarification.
- In round 1, ask direct questions to fill missing high-impact inputs.
- In round 2, use a different questioning approach from [ambiguity_questioning_patterns.md](references/ambiguity_questioning_patterns.md).
- After round 2, stop asking and proceed with explicit assumptions.
- Mark unresolved ambiguity and confidence impact in output.

3. Build and refine the constraint model.
- Classify constraints as `hard`, `soft`, `derived`, or `optimization`.
- Detect problematic constraints: vague, not measurable, contradictory, or disconnected from the objective.
- Rewrite problematic constraints into measurable forms.
- Add derived constraints when dependency analysis reveals hidden limits.
- Add optimization constraints when objective or utility tradeoff is under-specified.
- Follow [constraint_modeling_guide.md](references/constraint_modeling_guide.md).

4. Analyze constraint dependencies and crush risks.
- Identify pairwise dependency status: `supports`, `conflicts`, or `independent`.
- Detect crush risk where optimizing one constraint materially harms another.
- Rate conflict severity and include mitigation notes.

5. Generate alternatives.
- Produce exactly 3 materially different alternatives by default.
- Ensure alternatives are distinct in approach, not minor variants.
- For each alternative, map impacts to the full constraint set.

6. Apply optimization function.
- Use the selected optimization mode rules in [optimization_modes.md](references/optimization_modes.md).
- Always include the optimization function logic in the output.
- In `weighted` mode, include sensitivity checks and report rank flips.

7. Recommend and define fallback.
- Select one primary recommendation.
- Define explicit switch conditions where runner-up becomes preferred.
- Include next validation step that can confirm or falsify the recommendation quickly.

## Output Rules

- Always use the section order in [decision_brief_template.md](references/decision_brief_template.md).
- Keep assumptions explicit and scoped to unresolved ambiguity.
- Do not claim certainty when key assumptions remain unvalidated.
- Keep reasoning concise, concrete, and tied to constraint evidence.

## Defaults

- Alternatives count: `3`
- Ambiguity rounds: `2`
- Default optimization mode: `weighted`

## References

- [decision_brief_template.md](references/decision_brief_template.md)
- [constraint_modeling_guide.md](references/constraint_modeling_guide.md)
- [optimization_modes.md](references/optimization_modes.md)
- [ambiguity_questioning_patterns.md](references/ambiguity_questioning_patterns.md)
