---
name: phase-planning
description: Create and maintain project planning documents in the project-root `docs/` directory by generating a linked `master_plan.md` and phase documents. Use when Codex must break a project into phases, create or revise a project plan, update a phase document, or synchronize the master plan after any phase document changes.
---

# Phase Planning

Use this skill to create and maintain a linked planning system inside `docs/`:

1. `docs/master_plan.md`
2. `docs/phases/phase-XX-<slug>.md`

## Workflow

1. Confirm planning scope and constraints.
- Confirm project root, core objective, known constraints, and excluded scope.
- Normalize the stated constraints into a short list of concrete planning rules before drafting phases.
- Reuse existing planning docs when they already exist.
- Ask concise clarification questions before writing or updating plan docs if key constraints are materially ambiguous or if it is unclear how a constraint applies at the master-plan level versus specific phases.
- Ask concise clarification questions before writing phase docs if phase boundaries, sequencing, success criteria, or delivery scope are materially ambiguous.
- Prefer one to three high-value questions that remove ambiguity instead of guessing.

2. Build planning context.
- Read the repository, existing docs, and any stated requirements.
- Identify the current state, desired outcome, constraints, dependencies, risks, and delivery milestones.
- Separate hard constraints from assumptions, risks, and preferences so the plan can treat them differently.
- Detect workstreams that can be separated into stable phases with clear handoffs.

3. Create or update `docs/master_plan.md`.
- Follow [master_plan_template.md](references/master_plan_template.md).
- Define the project goal, scope, assumptions, milestones, key constraints, and cross-phase dependencies.
- Assign short constraint labels when multiple constraints will be referenced across phases.
- Create a phase index that links to every phase document and summarizes status, goal, and dependency posture.
- Add a constraint coverage summary that shows which phase handles, validates, or carries each key constraint.
- Keep the master plan as the top-level source of truth for sequencing and overall progress.

4. Create or update phase documents.
- Follow [phase_template.md](references/phase_template.md).
- Use one file per phase in `docs/phases/`.
- Assign stable phase IDs such as `Phase 01`, `Phase 02`, and keep filenames aligned with those IDs.
- Keep each phase narrow, goal-oriented, and independently reviewable.
- Include scope, out-of-scope items, dependencies, active phase constraints, phase TODOs, deliverables, acceptance criteria, and exit criteria.
- Make each phase TODO trace back to a deliverable, dependency, or named constraint.
- Make each phase exit criterion state whether the phase resolved a constraint, validated it, reduced it, or handed it forward unchanged.

5. Synchronize the linked documents.
- Update `docs/master_plan.md` every time a phase document is created or changed.
- Propagate phase status changes, scope changes, dependency changes, milestone changes, risk changes, and constraint changes into the master plan in the same turn.
- Keep summaries in the master plan consistent with the detailed content inside each phase document.
- If only one phase document is edited, still re-check the phase index and summary sections in the master plan.

6. Run consistency checks.
- Apply [planning_checklist.md](references/planning_checklist.md).
- Ensure dependencies are forward-only and do not create circular sequencing.
- Ensure active constraints are explicit instead of implied and are mapped to the phases that address them.
- Ensure phase TODOs and exit criteria are consistent with the constraints they claim to handle.
- Record unknowns as assumptions or open questions instead of hiding them.

7. Preserve stable structure across updates.
- Keep phase IDs, headings, and filenames stable so diffs remain reviewable.
- Preserve useful human-authored notes unless they conflict with the current plan.
- Prefer updating existing sections over rewriting the entire plan when only part of the plan changed.

## Output Rules

- Default to `docs/master_plan.md` and `docs/phases/phase-XX-<slug>.md` unless the user requests a different layout.
- Treat `docs/master_plan.md` and the phase docs as a linked set. Do not update one without checking the other.
- If constraints are material to sequencing or delivery, record them in the master plan and in each affected phase instead of leaving them implicit.
- Every phase TODO and exit handoff should either satisfy, validate, mitigate, or carry forward a named constraint when constraints are in play.
- Mark uncertain items with `Assumption:` or `Open question:` and note what would resolve them.
- Prefer concrete repository evidence over unsupported planning claims.
- Do not generate the old five-file audit pack (`project_structure.md`, `code_summary.md`, `architecture.md`, `tasks.md`, `issues.md`) unless the user explicitly asks for it.

## Reference Files

- [master_plan_template.md](references/master_plan_template.md)
- [phase_template.md](references/phase_template.md)
- [planning_checklist.md](references/planning_checklist.md)

## Example Output Set

A small sample output set is provided in [examples](examples) to show the expected relationship between `master_plan.md` and the phase documents.
