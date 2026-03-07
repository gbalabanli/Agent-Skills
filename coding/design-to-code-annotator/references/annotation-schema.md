# Annotation Schema

This schema defines a compact multi-screen annotation model for converting UI screenshots into build-ready implementation guidance.

## Root Object

- `project_id` (string): Stable ID for the annotation project.
- `project_title` (string): Human-readable title.
- `feature_summary` (string): What this flow implements.
- `screens` (array): List of annotated screens.
- `links` (array, optional): Explicit cross-screen links derived from annotations.

## Screen Object

- `screen_id` (string): Unique ID.
- `screen_title` (string): Human-readable title.
- `image_path` (string): Local or remote image reference.
- `screen_notes` (string, optional): Notes about layout/state.
- `annotations` (array): List of region annotations.

## Annotation Object

Required fields:

- `annotation_id` (string)
- `label` (string)
- `x` (number, 0 to 1 normalized)
- `y` (number, 0 to 1 normalized)
- `width` (number, 0 to 1 normalized)
- `height` (number, 0 to 1 normalized)
- `interaction_type` (string enum): `click`, `tap`, `input`, `hover`, `scroll`, `view`, `submit`, `navigate`, `custom`
- `description` (string): What the user sees or does.
- `expected_result` (string): UI/state change after interaction.
- `target_screen_id` (string or null): Destination screen for navigation.
- `component_hint` (string): Implementation hint (component/widget name).
- `development_notes` (string): Engineering details, dependencies, edge cases.
- `priority` (string enum): `high`, `medium`, `low`

Optional fields:

- `state_before` (string)
- `state_after` (string)
- `data_dependencies` (array of strings)

## Link Object (Optional)

- `link_id` (string)
- `from_screen_id` (string)
- `from_annotation_id` (string)
- `to_screen_id` (string)
- `transition_note` (string)

Use the machine-validatable JSON Schema in `annotation-schema.json`.
