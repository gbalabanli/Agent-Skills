---
name: docx-create-edit
description: Create new DOCX files from prompts and update existing application-form, formal-request, or similar professional DOCX files with AI-drafted sections while preserving structure, tone, and file safety. Use when Codex must read a `.docx`, draft content such as qualifications, supporting statements, examples, motivation paragraphs, or formal responses, insert or replace targeted sections, or generate a fresh document from scratch.
---

# DOCX Create Edit

Use this skill to create or update professional `.docx` files without treating the document like freeform text.

## Workflow

1. Classify the task before editing.
- `create`: build a new application-form document from scratch.
- `edit`: read an existing `.docx`, draft new content, and insert or replace only the requested portion.
- Capture the document goal, audience, applicant details, required sections, tone, and output filename.

2. Read the document structure before writing.
- For edits, extract the document text and identify the best insertion anchor before generating replacement text.
- Prefer explicit anchors such as `Supporting Information`, `Why I am suitable`, `Personal Statement`, `Qualifications`, `Additional Notes`, or a user-named heading.
- If no anchor is obvious, append a clearly labeled section instead of forcing text into the wrong field.

3. Draft the new content in plain text first.
- Write the added section before touching the `.docx`.
- For qualification statements, prefer this shape:
  - one direct claim
  - two concrete examples or supporting ideas
  - one closing sentence tied to the application goal
- If the user provides rough wording such as `I am computer engineer so that I can do this`, rewrite it into professional prose without inventing facts.

4. Create or update the `.docx`.
- For new files, generate a clean structure with a title, labeled sections, and simple paragraphs or tables only when the form requires them.
- For edits, preserve existing section order, labels, and official wording unless the user asked to rewrite them.
- Keep formatting changes narrow. Match the local style rather than restyling the whole document.
- Save edits to a new file by default, such as `application-form-updated.docx`, unless the user explicitly asks to overwrite the original.

5. Validate the output.
- Confirm the new `.docx` exists and can be reopened or re-extracted.
- Confirm the requested text is present in the output and that adjacent document content still exists.
- For edits, compare the surrounding text before and after the insertion point to verify the change landed in the intended place.

6. Report the result.
- Return the output path and summarize what was created or inserted.
- Call out assumptions, especially when applicant facts, dates, experience, or target role details were inferred.

## Output Rules

- Default to preserving the source file and writing a new output copy.
- Preserve official form language, field labels, and instructions unless the user explicitly asks to change them.
- Do not invent credentials, projects, employers, dates, or certifications.
- If required facts are missing, use placeholders or state the gap instead of fabricating content.
- If the form is rigid or field-based, prefer short targeted insertions over long essay-style rewrites.
- If the best insertion point is ambiguous, state the assumption and use the safest section-level placement.

## References

- [prompt-patterns.md](references/prompt-patterns.md)
- [edit-anchors.md](references/edit-anchors.md)
