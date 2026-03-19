# Build Brief: {{project_title}}

## 1. Overview
- **Feature**: {{feature_name_or_scope}}
- **Goal**: {{primary_user_goal}}
- **Summary**: {{feature_summary}}

## 2. Screen Inventory
{{#each screens}}
### {{screen_id}} - {{screen_title}}
- **Image**: `{{image_path}}`
- **Summary**: {{screen_summary}}
- **Notes**: {{screen_notes}}
{{/each}}

## 3. Interactive Elements
{{#each screens}}
### {{screen_id}}
{{#each annotations}}
1. **{{annotation_id}}** (`{{interaction_type}}`)
- Label: {{label}}
- Region: x={{x}}, y={{y}}, w={{width}}, h={{height}}
- Description: {{description}}
- Expected Result: {{expected_result}}
- Target Screen: {{target_screen_id_or_none}}
- Component Hint: `{{component_hint}}`
- Development Notes: {{development_notes}}
- Priority: {{priority}}
{{/each}}
{{/each}}

## 4. Navigation Flow
{{#if links_present}}
{{#each links}}
1. `{{from_screen_id}}.{{from_annotation_id}}` -> `{{to_screen_id}}`
- Transition note: {{transition_note}}
{{/each}}
{{else}}
- No explicit screen transitions are defined.
{{/if}}

## 5. Implementation Notes
- Reusable components:
- State model:
- API and data dependencies:
- Error and loading behavior:

## 6. Open Questions and Assumptions
- Missing detail 1:
- Missing detail 2:
