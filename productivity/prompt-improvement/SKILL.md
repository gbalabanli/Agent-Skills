---
name: prompt-improvement
description: Transform weak prompts into high-performance prompts for OpenAI and Codex workflows by asking targeted clarifying questions, preserving intent, and producing explicit structured prompts with testable constraints, verification expectations, and reliable output schemas.
---

# Prompt Improvement

Use this skill to convert rough requests into intentional prompts that reduce ambiguity, preserve user intent, and improve output reliability.

## Workflow

1. Run intake and classify prompt type.
- Capture the user's raw request, expected deliverable, domain, and context.
- Classify prompt type: `coding`, `reasoning`, `extraction`, `research`, or `general`.
- Restate intent in one sentence before refinement.

2. Run understanding self-check.
- Score understanding `0-5`.
- If score `<= 3`, ask clarifying questions before building the final prompt.
- If score `>= 4`, proceed with explicit assumptions.

3. Ask targeted clarification questions.
- Ask only high-impact questions that change implementation direction or output quality.
- Ask `1-3` questions per round, for up to `2` rounds.
- Prioritize unresolved fields in this order:
  - `model family` (`gpt`, `reasoning`, `codex`) when known
  - `goal`
  - `scope` (`in-scope` and `out-of-scope`)
  - `hard constraints` (must-have limits)
  - `optimization constraints` (what to optimize for)
  - `inputs/context` (files, APIs, examples)
  - `verification expectations` (tests, lint, citations, sanity checks)
  - `output contract` (format and required sections)
  - `success criteria` (what "done" means)
- Use [clarifying-question-bank.md](references/clarifying-question-bank.md).

4. Build a prompt spec.
- Normalize user answers into structured fields:
  - `prompt type`
  - `model family`
  - `role`
  - `goal`
  - `context`
  - `inputs`
  - `scope`
  - `hard constraints`
  - `optimization constraints`
  - `verification`
  - `output contract`
  - `success criteria`
  - `non-goals`
- Detect contradictions and resolve them explicitly.
- If unresolved ambiguity remains after 2 rounds, proceed with bounded assumptions.
- Use [prompt-spec-template.md](references/prompt-spec-template.md).

5. Generate the improved prompt using structured delimiters.
- Produce one final prompt with explicit sections and XML delimiters.
- Keep instruction order stable: role -> objective -> context -> inputs -> constraints -> execution rules -> output format -> verification.
- Default to canonical XML structure from [codex-openai-prompt-improvement-spec.md](references/codex-openai-prompt-improvement-spec.md).
- For `coding`, include minimal-diff and validation requirements.
- For `extraction`, enforce strict schema and "no guessing" behavior.
- Do not add unrelated implementation details not requested by the user.

6. Apply model-specific steering.
- For `gpt`: be explicit on structure and verbosity constraints.
- For `reasoning`: keep prompts direct and do not require chain-of-thought exposition.
- For `codex`: require reproducible validation steps and explicit quality bar (tests/lint/type checks where relevant).

7. Validate quality before finalizing.
- Score the prompt using [quality-rubric.md](references/quality-rubric.md).
- Required pass conditions:
  - intent preserved with no scope drift
  - explicit objective and output format
  - constraints are testable, not vague
  - verification expectations are included when relevant
  - wording is concise and token-efficient
- If score is below `8/10`, revise once with targeted fixes.

8. Deliver refinement output.
- Return:
  - clarifying questions asked (if any)
  - compact prompt spec
  - final improved prompt
  - quality check score
  - assumptions and remaining risks

## Output Rules

- Always distinguish `hard constraints` from `optimization constraints`.
- If key details are missing, ask questions first instead of guessing.
- Keep questions concise and actionable.
- Keep the final prompt deterministic, intentional, and parseable.
- Prefer XML-tagged sections unless user requests another schema.
- Preserve user intent; do not widen task scope without explicit user approval.
- Do not claim certainty when unresolved assumptions remain.

## Defaults

- Clarification rounds: `2`
- Questions per round: `1-3`
- Quality threshold: `>= 8/10`
- Target comprehension confidence: `>= 99%` when required fields are complete
- Output style: `xml-structured`
- Prompt variants: `final` only (optional `compact` variant when requested)

## References

- [clarifying-question-bank.md](references/clarifying-question-bank.md)
- [prompt-spec-template.md](references/prompt-spec-template.md)
- [quality-rubric.md](references/quality-rubric.md)
- [codex-openai-prompt-improvement-spec.md](references/codex-openai-prompt-improvement-spec.md)
