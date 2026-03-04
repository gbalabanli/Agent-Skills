---
name: document-creator
description: Create structured documents from selected templates and render PDF outputs with deterministic layout rules, section ordering, and reference formatting. Use when Codex must generate formal papers or reports from user content, ask for template selection first, enforce a chosen template, and produce a final document file.
---

# Document Creator

Use this skill to produce template-driven papers where structure and document quality are first-class requirements.

## Workflow

1. Ask for template first.
- Always ask for template selection before generation when not already stated.
- Accept free-text template names and map them to official templates using [template_registry.md](references/template_registry.md).
- If free-text is ambiguous, ask one concise clarification.

2. Confirm paper context and core inputs.
- Capture document objective, audience, and constraints.
- Require document title and main section content.
- For broad analytical topics, target `250-300` body words unless user requests a shorter format.
- Require or infer:
  - `Introduction`
  - `Findings`
  - `Pros and Cons`
  - `Conclusion`
  - `References`

3. Normalize into structured JSON blocks.
- Build the document payload using [input_contract.md](references/input_contract.md).
- Keep rich content in typed blocks:
  - paragraph blocks
  - table blocks
  - math/schema blocks (structured JSON)
  - code schema blocks (structured JSON with language, purpose, and code)
- Include math/schema blocks only when the user asks for formulas or quantitative schemas.
- Use code schema blocks when user asks to include coding logic or implementation snippets.
- If a required section is missing, add a placeholder paragraph noting missing content.

4. Render by selected template.
- Use `scripts/render_document.py` to generate the output PDF.
- For template `official paper`, enforce [spec.json](templates/official-paper/spec.json):
  - page 1: title page
  - page 2: index page with main-section page numbers and section-purpose descriptions
  - body order: introduction, findings, pros and cons, conclusion
  - references at the end with Wikipedia-style links plus relevance notes

5. Validate output structure.
- Confirm the output file exists.
- Confirm section order and index page contents.
- Confirm table numbering, math schema rendering, and end-positioned references.
- Confirm table numbering, human-readable schema rendering, code schema rendering, and end-positioned references.

6. Report result and assumptions.
- Return the output file path.
- Summarize template applied and any assumptions.
- Flag any missing input that was filled using placeholders.

## Output Rules

- Never skip template selection.
- Do not reorder required main sections.
- Keep index entries to main sections only.
- Format references in Wikipedia style (title + URL) and add short relevance explanations.
- Treat unverified facts as assumptions, not confirmed findings.

## Supported Templates

- `official paper` (free-text mapped to canonical `official-paper`)

## References

- [template_registry.md](references/template_registry.md)
- [input_contract.md](references/input_contract.md)
- [reference_style.md](references/reference_style.md)
