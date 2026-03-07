# Crawl4AI Implementation Patterns

## Use This Reference For

- deciding what files to create
- choosing between direct extraction and browser actions
- shaping a prototype versus a reusable service

## File Sets

### Prototype

Create only:

- `requirements.txt` or `pyproject.toml`
- one scraper entrypoint such as `main.py`
- optional `output/sample.json`

Use for one URL pattern, quick validation, or proving selectors.

### Reusable Scraper Package

Create:

- `requirements.txt` or `pyproject.toml`
- `src/<package>/scraper.py`
- `src/<package>/models.py` or `schema.py` if fields need structure
- `src/<package>/config.py` or `selectors.json` when selectors may change
- `main.py` or `cli.py`

Use for repeated crawling jobs, pagination, filtering, and export.

### Small Service

Create:

- dependency file
- scraper module
- service entrypoint such as `app.py`
- request/response schema file when the API accepts filters
- `.env.example` if secrets or cookies are needed

Use when another system will call the scraper as a service.

## Extraction Strategy

Prefer this order:

1. Plain repeated-item extraction from stable HTML
2. Browser rendering without user actions
3. Browser rendering with actions such as scroll, click, or wait
4. LLM-assisted filtering only when rule-based extraction is too brittle

For listing sites, usually:

- extract summary rows first
- collect detail URLs only if summary rows do not contain enough data
- keep the page object small and avoid over-crawling

## Selector Strategy

- Target stable containers first, then child fields.
- Keep selectors close to the actual listing structure.
- Store fragile selectors in config if the site will likely change.
- Normalize empty/missing values consistently.

## Validation Strategy

For a prototype:

- run one page
- print or save 3 to 10 extracted records

For a reusable scraper:

- run one page
- verify field names and types
- check duplicate handling and pagination stop logic

For a service:

- start the service
- send one request
- verify the response schema and an example payload
