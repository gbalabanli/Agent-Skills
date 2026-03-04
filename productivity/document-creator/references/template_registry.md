# Template Registry

This skill accepts free-text template names, then maps to official template IDs.

## Selection Rule

1. Ask for template if not provided.
2. Normalize user input (lowercase, trim punctuation, collapse spaces).
3. Map to an official template.
4. If no confident mapping, ask one clarification question.

## Official Templates

### `official-paper`

- Public display name: `official paper`
- Purpose: formal paper-like document with academic layout conventions.
- Required structure:
  - Page 1: title page
  - Page 2: index of main sections with page numbers
  - Section order:
    1. Introduction
    2. Findings
    3. Pros and Cons
    4. Conclusion
  - References section at end

## Free-Text Mapping Hints

Map input to `official-paper` when user mentions phrases like:

- `official paper`
- `official`
- `paper format`
- `wikipedia official paper style`
- `academic paper style`

If input mentions multiple template intents, ask for one final choice.
