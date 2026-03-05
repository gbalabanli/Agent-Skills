---
name: scrapling-websearch-fetch-data
description: Fetch websites and extract structured data with Scrapling for research and agency workflows. Use when Codex needs to scrape pages, collect data from search result pages, crawl pagination, parse static or dynamic content, or build repeatable web data collection using Scrapling fetchers and sessions.
---

# Scrapling Websearch And Fetch Data

Use this skill to collect web data with Scrapling and return clean, auditable outputs.

## Workflow

1. Define scope and constraints.
- Capture query/topic, target domains, output schema, and freshness requirement.
- Confirm legal and policy constraints for each target site.
- Prefer explicit allowlists for domains and endpoints.

2. Choose fetch strategy.
- Use `Fetcher` for static pages and fast HTTP workflows.
- Use `DynamicFetcher` when content is rendered by JavaScript.
- Use `StealthyFetcher` only when normal fetching fails and a stronger browser profile is required.
- Use sessions for multi-request flows that need shared cookies/state.

3. Build URL discovery plan.
- Start from user-provided URLs when available.
- For websearch collection, fetch query result pages and extract destination links.
- Normalize and deduplicate URLs before deep extraction.

4. Fetch pages with stable settings.
- Use deterministic request parameters and stable headers.
- Add bounded retries and explicit timeout handling.
- Keep request rates conservative and respect robots and site limits.

5. Extract structured data.
- Use CSS/XPath selectors with explicit field mapping.
- Keep extraction schema versioned and consistent.
- Validate required fields and preserve source URL per record.

6. Handle pagination and scale.
- Follow next-page links with loop guards and page limits.
- Move to `Spider` workflow when crawl breadth grows.
- Keep concurrency, throttling, and retry settings explicit.

7. Validate and clean outputs.
- Remove duplicates and empty/invalid records.
- Normalize dates, prices, and text fields.
- Record extraction gaps and partial failures.

8. Deliver results.
- Return data as JSON or JSONL with schema notes.
- Include run summary: pages requested, success rate, and dropped records.
- List follow-up actions for missing fields or blocked targets.

## Output Rules

- Prefer simplest fetcher that works before escalating to stealth/browser modes.
- Keep extraction deterministic and schema-first.
- Include source URL and timestamp for every extracted item.
- Report assumptions and known blind spots explicitly.

## References

- [scrapling-quickstart.md](references/scrapling-quickstart.md)
