---
name: phase-planning
description: Create and maintain project planning documents in the project-root `docs/` directory by generating and synchronizing a master plan with phase plans in either split files (`docs/phases/phase-XX-slug.md`) or a consolidated roadmap file (`docs/PHASES.md` or existing equivalent). Use when Codex must break work into phases, update phase status/scope/dependencies, or keep master and phase artifacts aligned.
---

# Phase Planning

Use this skill to create and maintain a linked planning system inside `docs/` with one of two layouts:

1. Split layout (default for new plans):
   - `docs/master_plan.md`
   - `docs/phases/phase-XX-<slug>.md`
2. Consolidated layout (reuse when already present or explicitly requested):
   - `docs/master_plan.md` (or existing equivalent such as `docs/MASTER_PLAN.md`)
   - `docs/PHASES.md` (or existing equivalent)

## Workflow

1. Confirm planning scope, constraints, and layout.
- Confirm project root, core objective, known constraints, and excluded scope.
- Detect and preserve existing planning topology (split vs consolidated), filenames, and casing unless the user asks to change them.
- Ask concise clarification questions before writing phase docs if phase boundaries, sequencing, success criteria, or delivery scope are materially ambiguous.
- Prefer one to three high-value questions that remove ambiguity instead of guessing.

2. Build planning context.
- Read the repository, existing docs, and any stated requirements.
- Identify the current state, desired outcome, constraints, dependencies, risks, and delivery milestones.
- Detect workstreams that can be separated into stable phases with clear handoffs.

3. Create or update `docs/master_plan.md`.
- Follow [master_plan_template.md](references/master_plan_template.md).
- Define the project goal, scope, assumptions, milestones, and cross-phase dependencies.
- Create a phase index that links to every phase artifact and summarizes status, goal, and dependency posture.
- Keep the master plan as the top-level source of truth for sequencing and overall progress.
- Use optional master-plan sections (status snapshot, phase gates, quality targets, end-state deliverables) when they improve decision quality.

4. Create or update phase artifacts.
- For split layout: follow [phase_template.md](references/phase_template.md) and keep one file per phase in `docs/phases/`.
- For consolidated layout: follow [phases_roadmap_template.md](references/phases_roadmap_template.md) and keep one section per phase in the consolidated roadmap file.
- Assign stable phase IDs such as `Phase 01`, `Phase 02`, and keep filenames or section headings aligned with those IDs.
- Keep each phase narrow, goal-oriented, and independently reviewable.
- Include scope, out-of-scope items, dependencies, deliverables, acceptance criteria, and exit criteria.
- For in-progress or completed phases, include delivered work and known gaps/deferred items when useful.

5. Synchronize the linked documents.
- Update the master plan every time any phase artifact is created or changed.
- Propagate phase status changes, scope changes, dependency changes, milestone changes, and risk changes into the master plan in the same turn.
- Keep summaries in the master plan consistent with the detailed content inside each phase document.
- If only one phase artifact is edited, still re-check the phase index and summary sections in the master plan.

6. Run consistency checks.
- Apply [planning_checklist.md](references/planning_checklist.md).
- Ensure dependencies are forward-only and do not create circular sequencing.
- Record unknowns as assumptions or open questions instead of hiding them.
- If phase gates or quality targets are present, verify they are reflected in phase acceptance/exit criteria.

7. Preserve stable structure across updates.
- Keep phase IDs, headings, and filenames stable so diffs remain reviewable.
- Preserve useful human-authored notes unless they conflict with the current plan.
- Prefer updating existing sections over rewriting the entire plan when only part of the plan changed.

8. Use supplementary planning specs when relevant.
- If supporting docs exist (for example, control specs, QA matrices, or platform constraints), reference them from phase sections or the master plan instead of duplicating details.

## Output Rules

- Default to the split layout for new plans: `docs/master_plan.md` and `docs/phases/phase-XX-<slug>.md`.
- Reuse existing layout, filenames, and casing when planning docs already exist, unless the user requests restructuring.
- Treat the master plan and phase artifacts as a linked set. Do not update one without checking the other.
- Mark uncertain items with `Assumption:` or `Open question:` and note what would resolve them.
- Prefer concrete repository evidence over unsupported planning claims.
- Do not generate the old five-file audit pack (`project_structure.md`, `code_summary.md`, `architecture.md`, `tasks.md`, `issues.md`) unless the user explicitly asks for it.

## Reference Files

- [master_plan_template.md](references/master_plan_template.md)
- [phase_template.md](references/phase_template.md)
- [phases_roadmap_template.md](references/phases_roadmap_template.md)
- [planning_checklist.md](references/planning_checklist.md)

## Example Output Set

A small sample output set is provided in [examples](examples) to show the expected relationship between the master plan and phase artifacts in both layouts.
