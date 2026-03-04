---
name: write-review-execute
description: Generate and compare exactly three code scaffolds through a write-review-execute loop, then recommend the best solution using weighted multi-criteria scoring. Use when Codex must try alternative implementations, review likely failure points, optionally run proof-of-concept execution, and propose a defended best approach.
---

# Write Review Execute

Use this skill to produce decision-quality coding recommendations by trialing alternatives before proposing one.

## Workflow

1. Run intake.
- Capture objective, target files or modules, language or toolchain, hard constraints, soft constraints, and success signals.
- Ask only high-impact clarification questions when ambiguity can change feasibility or ranking.
- Resolve unanswered ambiguity with explicit assumptions.

2. Choose execution mode before recommendation.
- Ask the user to choose one mode:
  - `theoretical-only`: no command execution, recommendation based on static reasoning.
  - `proof-of-concept`: run minimal executable checks for each scaffold.
- If the user does not respond, default to `proof-of-concept` when a runnable command exists. Otherwise default to `theoretical-only`.
- Record the selected mode and confidence impact in the output.
- Follow [execution_modes.md](references/execution_modes.md).

3. Generate exactly three materially different scaffolds.
- Produce exactly 3 alternatives with distinct architecture or implementation strategies.
- Keep each scaffold targeted. Do not over-build production features unless explicitly requested.
- For each scaffold, state assumptions and expected strengths and weaknesses.

4. Review each scaffold before execution.
- Run a focused review per scaffold for correctness, edge cases, error handling, maintainability, and operational risk.
- Identify ambiguity-sensitive parts that are likely to fail at runtime.
- Patch obvious defects before scoring.

5. Execute according to the selected mode.
- In `proof-of-concept` mode, run the smallest command set that can validate expected behavior for each scaffold.
- Capture command, output summary, and pass or fail signal for each scaffold.
- Use `scripts/evaluate_scaffolds.py` for repeatable scoring and evidence capture when applicable.
- In `theoretical-only` mode, skip commands and record explicit non-executed risk notes.

6. Score with weighted multi-criteria.
- Apply [scoring_rubric.md](references/scoring_rubric.md).
- Use normalized weighted scoring and include at least one sensitivity note.
- Enforce hard-gate failures for alternatives that violate critical correctness constraints.

7. Recommend and define fallback.
- Select one primary recommendation.
- Define explicit switch conditions where a runner-up becomes preferred.
- Include one fast follow-up validation step that can confirm or falsify the recommendation.

## Output Rules

- Follow the section order in [recommendation_template.md](references/recommendation_template.md).
- Always include all three alternatives, even when one is weak.
- Keep assumptions explicit and scoped to unresolved ambiguity.
- Do not present unexecuted claims as verified behavior.
- If execution is skipped or partial, reduce confidence and explain why.

## Defaults

- Alternatives count: `3`
- Scoring mode: `weighted`
- Execution decision: ask user (`theoretical-only` or `proof-of-concept`)
- No-mode-response fallback: `proof-of-concept` when runnable, else `theoretical-only`

## References

- [execution_modes.md](references/execution_modes.md)
- [scoring_rubric.md](references/scoring_rubric.md)
- [recommendation_template.md](references/recommendation_template.md)
