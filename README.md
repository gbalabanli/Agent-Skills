# Agent Skills

Central repository for organizing reusable agent skills by category.

## Overview

This repository is a structured skill pool for agent workflows. Skills are grouped into high-level categories, and each category contains one or more skill directories with the files needed for that skill.

The goal is to keep skill discovery simple, make maintenance predictable, and provide a consistent place to add new capabilities over time.

## Repository Structure

```text
Agent-Skills/
|-- coding/
|   `-- <skill-name>/
|       |-- SKILL.md
|       |-- scripts/
|       |-- templates/
|       `-- assets/
|-- research/
|-- search/
|-- visualizations/
|-- game-dev/
|-- productivity/
`-- README.md
```

## Categories

- `coding`: Skills related to software development, debugging, refactoring, testing, code generation, and architecture work.
- `research`: Skills focused on analysis, investigation, synthesis, and structured information gathering.
- `search`: Skills for fast lookup, retrieval, navigation, and targeted discovery tasks.
- `visualizations`: Skills for charts, diagrams, dashboards, slide assets, and visual content generation.
- `game-dev`: Skills for gameplay systems, engines, assets, tooling, and game production workflows.
- `productivity`: Skills for task management, documentation workflows, planning, and personal or team efficiency.

## Current Skills

- `productivity/phase-planning`: Create `docs/master_plan.md` and linked `docs/phases/phase-XX-<slug>.md` files, then keep the master plan synchronized when phase docs change.
- `coding/code-documentation`: Create, rewrite, and review code documentation for repositories, modules, APIs, inline docs, and engineering workflows using a practical template plus a direct review pass.
- `coding/solution-alternatives`: Generate and optimize competing solution alternatives for hard issues using constraint modeling, dependency analysis, and bounded ambiguity handling.
- `coding/tdd`: Implement features and bug fixes with a strict Test-Driven Development workflow (Red-Green-Refactor) and regression-first bugfixing.
- `coding/write-review-execute`: Compare exactly three implementation scaffolds using a write-review-execute loop with optional proof-of-concept runs and weighted scoring.
- `visualizations/stitch-remotion-walkthrough`: Turn Stitch screens or exported screenshots into modular Remotion walkthrough videos with staged assets, a stable screen manifest, and render validation.
- `productivity/prompt-improvement`: Improve vague prompts through targeted clarifying questions, structured prompt specs, and quality scoring with explicit goal, hard constraints, and optimization constraints.
- `productivity/document-creator`: Generate template-driven formal documents as PDFs, including an official paper template with title page, index page, ordered sections, and Wikipedia-style references.
- `productivity/create-guidance`: Clarify vague or high-level requests, propose options with tradeoffs, and provide direct step-by-step guidance.
- `productivity/goal-constraint-inference`: Infer hard and soft constraints from goals, model dependency/conflict relations, run forward and inverse optimization reasoning, and deliver alternatives plus a best balanced recommendation report.
- `research/notebooklm`: Research assistant workflow for NotebookLM including authentication, notebook management, iterative questioning, and synthesis with source-grounded responses.
- `research/google-ai-mode-skill`: Browser-driven Google AI Mode research workflow with query planning, iterative search passes, extraction, and synthesized markdown reporting.
- `research/web-deepsearch`: Deep web research workflow for complex questions using decomposition, multi-query coverage, evidence synthesis, contradiction handling, and prioritized recommendations with citations.

## External Local Skills

- `web-scraping`: Installed in the local agent environment outside this repository at `%USERPROFILE%\.agents\skills\web-scraping\SKILL.md`. Provenance is locked in `%USERPROFILE%\.agents\.skill-lock.json` to `mindrally/skills` via `https://github.com/mindrally/skills.git`, skill path `web-scraping/SKILL.md`, installed on `2026-03-09`. This is distinct from the `jamditis/claude-skills-journalism` skill published on `skills.sh`.

## Adding a New Skill

1. Choose the most appropriate category at the repository root.
2. Create a new directory using a clear, lowercase skill name such as `api-docs` or `bug-triage`.
3. Add a `SKILL.md` file that explains the skill's purpose, workflow, and usage rules.
4. Add supporting files only when needed, such as scripts, templates, reference docs, or assets.

## Skill Starter Template

A reusable scaffold is available at `templates/skill-template/`.

1. Copy `templates/skill-template/` into the target category and rename the folder to your new skill name.
2. Rename `SKILL.md.template` to `SKILL.md`.
3. Rename `agents/openai.yaml.template` to `agents/openai.yaml`.
4. Replace placeholder values and remove optional folders you do not need.

## Suggested Skill Layout

```text
<skill-name>/
|-- SKILL.md
|-- scripts/
|-- templates/
|-- references/
`-- assets/
```

Use only the folders that are relevant for the skill. Keep each skill self-contained and focused on one job.

## Contributing

Keep naming consistent, prefer concise instructions, and avoid duplicating existing skills. If a new skill overlaps with an existing one, extend the current skill instead of creating a parallel version unless the workflow is genuinely different.

## License

This repository is licensed under the terms in `LICENSE`.
