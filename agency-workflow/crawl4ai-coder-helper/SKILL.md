---
name: crawl4ai-coder-helper
description: Build, extend, and debug Crawl4AI-based scrapers, crawlers, and small services. Use when Codex needs to choose how to use Crawl4AI for a target website, inspect the site, pick an extraction strategy, and write the actual project files such as scraper modules, service endpoints, configs, schemas, dependency files, and sample outputs instead of only giving guidance.
---

# Crawl4AI Coder Helper

## Overview

Use this skill to produce working Crawl4AI code and supporting files for a scraping goal. Prefer concrete implementation over conceptual explanation.

## Workflow

1. Inspect the existing workspace before designing anything.
2. Inspect the target website enough to determine whether the work needs:
   - static HTML extraction
   - browser rendering
   - JavaScript actions such as click, scroll, wait, login, or pagination
   - structured repeated-item extraction
3. Retrieve current Crawl4AI documentation before using non-trivial APIs. Prefer Context7 or official Crawl4AI docs.
4. Choose the smallest architecture that satisfies the goal.
5. Write the required files, not just snippets in chat.
6. Run a narrow validation pass against a real page or fixture and report limits clearly.

## Architecture Choice

Choose one of these shapes unless the repo already dictates another pattern:

- Single-file scraper for one-off extraction or prototyping.
- Small package with `main.py`, `scraper.py`, and schema/config files for repeatable jobs.
- Service shape for API-driven use cases, usually with a scraper module plus HTTP entrypoint.

Prefer simpler extraction first:

- Use CSS/XPath or Crawl4AI extraction strategies before LLM-based extraction.
- Use browser actions only when direct fetch/parse is insufficient.
- Scope the crawl narrowly around the requested region, category, or filters.

## Required Outputs

When the user asks to "build" or "set up" a Crawl4AI solution, create the files needed to run it end to end. Typical outputs include:

- Dependency file such as `requirements.txt` or `pyproject.toml`
- Scraper module
- Entrypoint such as CLI script, worker, or service endpoint
- Config or selector/schema file when extraction rules should be isolated
- `.env.example` when secrets, cookies, or credentials are involved
- Sample output file or fixture when useful for validation
- Minimal test or smoke-check when the project already uses tests

Do not create extra documentation files unless they materially help execution.

## Implementation Rules

- Preserve the repo's existing structure and conventions if a project already exists.
- Keep selectors/config separate when the target site is likely to change.
- Normalize extracted fields into stable names such as `title`, `price`, `location`, `url`, `published_at`, and domain-specific attributes.
- Build pagination and deduplication deliberately; do not assume the first page is enough unless the user asked for a prototype.
- Add polite rate limiting and conservative crawl scope.
- Respect target-site terms, robots, and legal constraints when relevant.

## Validation

Validate the implementation with the lightest test that proves the chosen approach:

- run the scraper against one real target page or one result page
- verify selectors and extracted fields
- verify output serialization
- confirm service startup or CLI execution if those files were created

If blocked by anti-bot measures, login, or legal restrictions, state that clearly and downgrade the implementation to the safest workable shape.

## References

Read [implementation-patterns.md](./references/implementation-patterns.md) when choosing file layout, extraction strategy, and validation shape.
