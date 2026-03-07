---
name: code-documentation
description: Create, rewrite, and review code documentation for repositories, modules, APIs, functions, and engineering workflows. Use when Codex must add or improve README sections, architecture notes, inline code docs, onboarding guides, usage docs, or review existing technical documentation for accuracy, gaps, and maintainability.
---

# Code Documentation

Use this skill to produce technical documentation that helps the next engineer understand and change the code safely.

## Workflow

1. Define the documentation target.
- Identify the artifact: repository doc, feature note, module doc, API contract, inline comment set, runbook, or migration note.
- Identify the primary reader: maintainer, teammate, reviewer, operator, or new contributor.
- Prefer the smallest documentation artifact that resolves the user's need.

2. Read the source of truth before writing.
- Inspect code, tests, config, commands, and existing docs before drafting.
- Treat implementation as authoritative over stale prose.
- Mark anything unverified as an assumption or TODO instead of presenting it as fact.

3. Apply the Code Documentation template.
- Start from [code-documentation-template.md](references/code-documentation-template.md).
- Select only the sections that materially help the reader.
- Prefer examples, command snippets, and tables only when they reduce ambiguity.

4. Write in a practical engineering style.
- Lead with purpose, entry points, and usage.
- Explain constraints, side effects, failure modes, and operational caveats.
- Prefer concrete names, file paths, interfaces, and examples over abstract filler.
- Do not restate obvious code line by line.

5. Review with a direct editor pass.
- Run the checklist in [review-style-checklist.md](references/review-style-checklist.md).
- Fix incorrect or weak sections instead of only pointing them out.
- Call out missing verification, risky assumptions, and maintenance traps plainly.

6. Finalize for long-term use.
- Keep headings shallow and scannable.
- Place docs close to the code they describe when possible.
- Link related files, commands, or docs that a maintainer will need next.

## Output Rules

- Never invent behavior that was not verified in code, tests, or user input.
- Prefer documentation that explains why, boundaries, and usage over prose that only paraphrases implementation.
- Keep inline comments and docstrings terse; reserve longer explanations for module, API, or design docs.
- If the request is review-only, return findings first, then propose or apply revisions.
- If existing documentation is mostly correct, tighten and restructure it instead of rewriting for style alone.

## References

- [code-documentation-template.md](references/code-documentation-template.md)
- [review-style-checklist.md](references/review-style-checklist.md)
