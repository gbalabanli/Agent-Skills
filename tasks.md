# Tasks: Design-to-Code Explanation Skill

## Goal
Create a new coding skill that helps an LLM understand UI implementation from annotated screenshots. The workflow should let a user upload one or more screen images, point to exact areas on each image, describe what each area does, connect one screen to another, and export the result as a structured explanation the LLM can use while coding.

## Product Summary
- Input: screenshots of one or more screens
- Interaction: select an area on the image and attach notes
- Behavior mapping: describe what happens when a user clicks or interacts with that area
- Screen flow: link an annotated area to another screenshot
- Output: structured markdown and JSON that explain what the UI should do
- Primary use case: give the exported explanation to an LLM so it can build the UI more accurately

## Task 1: Create the Skill
### Deliverables
- New skill folder under `coding/`
- `SKILL.md` with clear trigger rules and workflow instructions
- `agents/openai.yaml`
- Optional `references/` docs for schema and examples
- Optional `assets/` or `templates/` for exported output examples

### Prompt
```text
Create a new coding skill for this repository.

Skill goal:
Help an LLM understand what to build from annotated UI screenshots.

The skill should be used when the user provides one or more screenshots and wants to explain:
- what a specific button, panel, field, or section does
- what screen transition happens after clicking an area
- what content appears or changes between screens
- what implementation hints matter for development

The skill must guide Codex to:
1. Read exported screenshot annotations
2. Convert them into a build-ready implementation brief
3. Explain screen-to-screen transitions
4. Identify components, states, actions, and developer notes
5. Produce structured output that another LLM can use while coding

Create the skill in the `coding/` category with a practical name and concise instructions.
```

## Task 2: Define the Annotation Format
### Deliverables
- A simple JSON schema for screenshots and annotated regions
- A matching markdown export format for LLM-friendly explanation
- Support for multiple screens and links between screens

### Required Fields
- `screen_id`
- `screen_title`
- `image_path` or image reference
- `annotations`
- `annotation_id`
- `label`
- `x`, `y`, `width`, `height`
- `interaction_type`
- `description`
- `expected_result`
- `target_screen_id`
- `component_hint`
- `development_notes`
- `priority`

### Prompt
```text
Design a compact annotation schema for a screenshot-driven UI explanation workflow.

Requirements:
- Support multiple screenshots
- Support selecting rectangular areas on an image
- Support a note for each selected area
- Support linking one annotated area to another screen
- Support implementation notes for developers
- Support export to both JSON and markdown

The output should be easy for an LLM to read and should clearly explain:
- what the user sees
- what the user can click
- what changes after the interaction
- which screen comes next
- any important implementation hints

Propose the schema and include one realistic example with two linked screens.
```

## Task 3: Build the Screenshot Annotation UI
### Deliverables
- Simple HTML/CSS/JavaScript UI
- Image upload for one or more screenshots
- Canvas or overlay-based area selection
- Annotation form for the selected area
- Ability to edit and delete annotations
- Ability to link an area to another uploaded screenshot
- Export button for JSON and markdown

### Prompt
```text
Build a lightweight browser-based annotation tool using HTML, CSS, and JavaScript.

Core features:
- Upload one or more screenshots
- Display the selected screenshot on screen
- Let the user draw or place a rectangular hotspot on the image
- After selecting an area, open a form with fields for:
  - label
  - description
  - interaction type
  - expected result
  - target screen
  - component hint
  - development notes
  - priority
- Show existing annotations as overlays
- Allow selecting, editing, and deleting overlays
- Allow exporting the full project as JSON and markdown

Keep the implementation simple and dependency-light.
Prefer a single-page app that can run locally in the browser.
```

## Task 4: Generate LLM-Ready Build Explanations
### Deliverables
- Export template for markdown brief
- Section for screen inventory
- Section for interactive elements
- Section for navigation flow
- Section for implementation notes
- Optional section for unanswered questions or assumptions

### Prompt
```text
Create a markdown export template for annotated UI screenshots so an LLM can use it as a build spec.

The exported brief must include:
- overview of the feature or flow
- per-screen summary
- list of annotated elements on each screen
- interaction behavior for each element
- transitions from one screen to another
- implementation hints for developers
- open questions or missing details

Write the template and include a sample export for a two-screen interaction where clicking a button on screen A opens screen B.
```

## Task 5: Add Example Data and Usage Guidance
### Deliverables
- At least one sample annotation project
- Example screenshots or placeholders
- Example exported JSON
- Example exported markdown
- Short usage notes inside the skill or references

### Prompt
```text
Create example data for the screenshot-annotation skill.

Include:
- two example screens
- at least three annotated regions
- one transition from the first screen to the second
- realistic component hints
- realistic development notes

Provide both JSON and markdown exports so future users can understand the expected format immediately.
```

## Task 6: Validate and Refine
### Deliverables
- Validate the skill structure
- Smoke-test the HTML annotation UI
- Confirm export files are readable and complete
- Confirm linked screen navigation is preserved in export

### Prompt
```text
Review the completed screenshot-annotation skill and its HTML annotation UI.

Check for:
- missing fields in the annotation schema
- unclear instructions in the skill
- broken or incomplete export behavior
- weak prompt formatting for downstream LLM use
- missing examples

Then propose targeted fixes that make the workflow more reliable for design-to-code explanation.
```

## Suggested Skill Names
- `design-to-code-annotator`
- `ui-screenshot-explainer`
- `screen-flow-annotator`
- `annotated-design-spec`

## Acceptance Criteria
- A user can upload screenshots in the UI
- A user can select an area on a screenshot
- A user can attach explanation text to that area
- A user can link that area to another screenshot
- The tool exports structured JSON
- The tool exports markdown that an LLM can use directly
- The skill explains how Codex should interpret the exported files while building UI

## Run Status (2026-03-07)

- [x] Task 1: Create the Skill
  - Added `designing/design-to-code-annotator/` with `SKILL.md`, `agents/openai.yaml`, references, templates, and assets.
- [x] Task 2: Define the Annotation Format
  - Added `references/annotation-schema.md` and machine-validatable `references/annotation-schema.json`.
  - Included multi-screen linked example in `references/annotation-export-example.json`.
- [x] Task 3: Build the Screenshot Annotation UI
  - Added dependency-light browser app under `assets/annotation-tool/` (`index.html`, `styles.css`, `app.js`).
  - Supports upload, rectangular annotation, edit/delete, screen linking, JSON/markdown export.
- [x] Task 4: Generate LLM-Ready Build Explanations
  - Added reusable markdown template at `templates/build-brief-template.md`.
  - Added sample markdown export at `references/annotation-export-example.md`.
- [x] Task 5: Add Example Data and Usage Guidance
  - Added two placeholder screen images (`references/examples/screens/*.svg`).
  - Added realistic example annotation project (JSON + markdown) and usage notes.
- [x] Task 6: Validate and Refine
  - Ran JS syntax check on annotation app.
  - Parsed schema and example JSON; verified required annotation fields exist.
  - Refined usage notes and output consistency across files.

## Upcoming Tasks (2026-03-19)

- [x] Task 7: Add Import Workflow
  - Let users import a previously exported JSON project back into the annotation UI.
  - Validate schema and surface readable errors for invalid files.
  - Added import controls (`Import JSON Project`) and file handling in `assets/annotation-tool/index.html` + `app.js`.
  - Added import validation with readable error reporting in `assets/annotation-tool/model.js` (`validateImportProject`).

- [x] Task 8: Add Basic Test Coverage
  - Add lightweight tests for JSON export structure and markdown export generation.
  - Include one test case for linked-screen transitions.
  - Added Node tests at `assets/annotation-tool/tests/model.test.mjs` (validation, export links, markdown flow, path normalization).
  - Verified with: `node --test designing/design-to-code-annotator/assets/annotation-tool/tests/model.test.mjs` (5/5 pass).

- [x] Task 9: Improve Annotation Editing UX
  - Add drag-to-move and resize handles for existing annotation rectangles.
  - Preserve overlay alignment when image display size changes.
  - Added drag-to-move and corner resize handle support in `assets/annotation-tool/app.js` + `styles.css`.
  - Kept normalized coordinates and resize re-render behavior for viewport/image-size alignment.

- [x] Task 10: Add Keyboard Productivity Shortcuts
  - Add shortcuts for creating, saving, deleting, and navigating annotations.
  - Document shortcuts in the tool UI and references.
  - Added keyboard handling in `assets/annotation-tool/app.js`: `Ctrl/Cmd+S`, `Delete/Backspace`, `Esc`, `[`, `]`, `Arrow Up/Down`.
  - Documented shortcuts in tool sidebar (`index.html`) and `references/usage-notes.md`.

- [x] Task 11: Package Demo for Fast Onboarding
  - Add a one-command local demo flow with sample data preloaded.
  - Update usage notes with a 2-minute quickstart path.
  - Added one-command demo runner: `assets/annotation-tool/scripts/start-demo.py`.
  - Added demo preload route (`?demo=1`) that fetches sample project and resolves sample image paths.
  - Updated quickstart docs in `references/usage-notes.md`.

- [x] Task 12: Install and Validate Wiki-Humanizer Skill
  - Find the skill in `skills.sh` that checks wiki rules and humanizes writing.
  - Install that skill in this workspace.
  - Test the produced writing with `https://aidetector.com/`.
  - Installed `blader/humanizer` to `C:\Users\Bora\.codex\skills\humanizer`.
  - Validation (2026-03-19): `aidetector.com` scored an AI-style sample at `92.5% AI detected`, and a humanized rewrite at `15.75% AI detected` (`Likely human`).

- [x] Task 13: Promote Verified Skill to `writing/`
  - Only if Task 12 works well, add the validated skill under `C:\Users\Bora\Desktop\Workspace\agents\agent-skills\writing`.
  - Prepare it for GitHub in the `writing/` directory structure used by this repository.
  - Added to repo path: `C:\Users\Bora\Desktop\Workspace\agents\agent-skills\writing\humanizer`.

- [x] Task 14: Add `frontend-slides` Skill Under `visualizations/`
  - Source repository: `https://github.com/zarazhangrui/frontend-slides`.
  - Add/import the skill into `C:\Users\Bora\Desktop\Workspace\agents\agent-skills\visualizations`.
  - Ensure it is ready for git in this repository.
  - Added to repo path: `C:\Users\Bora\Desktop\Workspace\agents\agent-skills\visualizations\frontend-slides`.

- [x] Task 15: Add `ui-ux-pro-max-skill` Under `designing/`
  - Source repository: `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill`.
  - Add/import the skill into `C:\Users\Bora\Desktop\Workspace\agents\agent-skills\designing`.
  - Ensure it is prepared for git in this repository.
  - Added `ui-ux-pro-max` skill from `.claude/skills/ui-ux-pro-max` to repo path: `C:\Users\Bora\Desktop\Workspace\agents\agent-skills\designing\ui-ux-pro-max`.
