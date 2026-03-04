# Input Contract

Use structured JSON as the canonical input for `scripts/render_document.py`.

## Minimal Valid Input

```json
{
  "template": "official paper",
  "title": "Document Title",
  "sections": {
    "introduction": [
      { "type": "paragraph", "text": "..." }
    ],
    "findings": [
      { "type": "paragraph", "text": "..." }
    ],
    "pros_and_cons": [
      { "type": "paragraph", "text": "..." }
    ],
    "conclusion": [
      { "type": "paragraph", "text": "..." }
    ]
  },
  "index_descriptions": {
    "introduction": "Scope and assumptions",
    "findings": "Evidence and observations",
    "pros_and_cons": "Tradeoff discussion",
    "conclusion": "Final synthesis"
  },
  "references": [
    {
      "title": "Source title",
      "url": "https://example.org/page",
      "note": "Why this source is relevant for the paper."
    }
  ]
}
```

## Top-Level Fields

- `template` (string, required): free-text name mapped to official template ID.
- `title` (string, required): document title used on page 1.
- `subtitle` (string, optional): title page subtitle.
- `authors` (array of strings, optional): rendered on title page.
- `date` (string, optional): rendered on title page.
- `sections` (object, required): keyed by required main section IDs.
- `index_descriptions` (object, optional): explanatory summary text per main section for page-2 index.
- `references` (array, optional): rendered at end in Wikipedia style.

## Required Section Keys

- `introduction`
- `findings`
- `pros_and_cons`
- `conclusion`

Each section value is a list of typed blocks.

## Block Types

### Paragraph Block

```json
{ "type": "paragraph", "text": "Paragraph text." }
```

### Table Block

```json
{
  "type": "table",
  "caption": "Comparative metrics",
  "columns": ["Metric", "Option A", "Option B"],
  "rows": [
    ["Accuracy", "0.91", "0.89"],
    ["Latency", "120ms", "90ms"]
  ]
}
```

### Math/Schema Block (Structured, Human-Readable)

```json
{
  "type": "math",
  "caption": "Coordinate transform schema",
  "schema": {
    "equation": "x' = ax + b",
    "variables": { "a": "scale", "b": "offset" }
  }
}
```

Use math/schema blocks only when the user explicitly asks for formulas, coordinate schemas, or quantitative models.

### Code Schema Block

```json
{
  "type": "code",
  "caption": "Validation logic schema",
  "schema": {
    "language": "python",
    "purpose": "Validate expected section order.",
    "code": "def is_valid(order):\n    return order == ['introduction','findings','pros_and_cons','conclusion']",
    "inputs": { "order": "List[str]" },
    "output": "bool"
  }
}
```

Use code schema blocks when implementation snippets are needed in the document.

## Content Quality Target

- For broad analysis prompts (like labor-market or technology impact papers), target at least `250-300` body words across the four main sections.
- The renderer warns when body word count falls below template minimum.

## Fallback Behavior

- Missing required section: add placeholder paragraph.
- Empty references: create `References` heading with `No references provided.`.
- Unknown block type: render JSON dump as a schema block and keep generation moving.
