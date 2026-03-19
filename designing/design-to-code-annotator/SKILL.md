---
name: design-to-code-annotator
description: Convert annotated UI screenshots into build-ready implementation briefs with screen flow, interaction behavior, and component/state hints for downstream coding.
---

# Design to Code Annotator

Use this skill when a user provides annotated screenshots (or asks to create annotations) and wants an LLM-ready explanation of what to build.

## Trigger Rules

Use this skill when the user asks to:
- explain a UI from screenshots or image annotations
- map click targets, form fields, panels, or buttons to behavior
- describe screen-to-screen transitions
- generate build specs from design images
- export JSON and markdown specs for another LLM

## Workflow

1. Gather or create annotation inputs.
- Prefer an existing JSON annotation export if provided.
- If only images are provided, create annotations with the local tool at `assets/annotation-tool/index.html`.
- Ensure each screen and annotation has stable IDs.

2. Validate schema completeness.
- Validate JSON against [annotation-schema.md](references/annotation-schema.md).
- Require all fields listed in the schema before generating final output.
- Mark unknown values as `"unknown"` and list them as open questions.

3. Build implementation model.
- Extract per-screen inventory: visible sections, key components, and major states.
- Extract per-annotation behavior: interaction type, expected result, and constraints.
- Resolve links via `target_screen_id` and compile navigation flow.

4. Generate LLM-ready outputs.
- Export normalized JSON using the schema in [annotation-schema.md](references/annotation-schema.md).
- Export markdown using [build-brief-template.md](templates/build-brief-template.md).
- Include assumptions and unanswered questions in the markdown export.

5. Produce coding guidance.
- Identify reusable components and likely state machines.
- Call out API/data dependencies implied by annotations.
- Flag risky ambiguities before implementation starts.

## Output Rules

- Never invent interactions that are not present in annotations or user input.
- Keep annotation IDs and screen IDs stable across JSON and markdown exports.
- Include explicit screen transition lines (from annotation to destination screen).
- Prefer concrete implementation hints over generic UI prose.
- If links are missing, keep `target_screen_id` as `null` and surface an open question.

## References

- [annotation-schema.md](references/annotation-schema.md)
- [annotation-schema.json](references/annotation-schema.json)
- [annotation-export-example.json](references/annotation-export-example.json)
- [annotation-export-example.md](references/annotation-export-example.md)
- [build-brief-template.md](templates/build-brief-template.md)
- Annotation tool: `assets/annotation-tool/index.html`
