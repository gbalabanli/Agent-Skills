---
name: scrapling-websearch-fetch-data
description: Fetch websites and extract structured data with Scrapling for research and agency workflows. Use when Codex needs to scrape pages, collect data from search result pages, crawl pagination, parse static or dynamic content, or build repeatable web data collection using Scrapling MCP tools, fetchers, and sessions.
---

# Scrapling Websearch And Fetch Data

Use this skill to collect web data with Scrapling and return clean, auditable outputs.

## Tool Choice

1. Prefer Scrapling MCP for ad hoc acquisition on normal pages.
- Use MCP when the task is to fetch a page, extract content, inspect selectors, compare a small set of URLs, or gather research inputs directly inside the chat session.
- Prefer `get` or `bulk_get` for fast HTTP retrieval on static pages.
- Prefer `fetch` or `bulk_fetch` when the page needs a browser because content is rendered dynamically.
- Escalate to `stealthy_fetch` or `bulk_stealthy_fetch` only after lighter approaches fail or the target clearly has stronger anti-bot protection.

2. Switch to Playwright real browser mode for protected sites.
- If the target shows Cloudflare, `checkLoading`, forced login redirects, anti-bot interstitials, or repeated 403s, stop retrying Scrapling fetch paths and move to Playwright.
- Treat Playwright as a real browser session, not just a rendering helper: open the live page, keep the same tab/context, and do the extraction inside that working browser state.
- On sites like Sahibinden, do not assume a separate local script or a different browser instance will inherit the same cookies, challenge state, or cleared session.
- Once the page is open cleanly, prefer in-browser extraction with `browser_snapshot`, `browser_evaluate`, and `browser_run_code`.

3. Prefer Scrapling Python code for durable workflows.
- Switch to local scripts when the task needs repeatable pipelines, custom pagination loops, schema transforms, file outputs, testable extraction code, or session/state management across many requests.
- Use `Fetcher`, `DynamicFetcher`, `StealthyFetcher`, and the session classes when MCP is too narrow for the workflow.
- If access only works in the live Playwright browser, keep the scrape in Playwright until the data is collected, then export or transform afterward.

4. Keep escalation explicit.
- Start with the least invasive fetch path that can work.
- State when you move from HTTP to browser fetch, when you switch from Scrapling browser fetch to Playwright real-browser automation, and when you escalate to stealth mode.
- Preserve the source URL, fetch timestamp, and extraction assumptions in the final output.

## Workflow

1. Define scope and constraints.
- Capture query/topic, target domains, output schema, and freshness requirement.
- Confirm legal and policy constraints for each target site.
- Prefer explicit allowlists for domains and endpoints.

2. Choose fetch strategy.
- If Scrapling MCP is available, start with MCP tools for short interactive tasks before writing code.
- Use `get`/`bulk_get` or `Fetcher` for static pages and fast HTTP workflows.
- Use `fetch`/`bulk_fetch` or `DynamicFetcher` when content is rendered by JavaScript.
- If a protected site still blocks access after Scrapling browser fetches, switch to Playwright and continue in the same real browser session that successfully loads the page.
- Use `stealthy_fetch`/`bulk_stealthy_fetch` or `StealthyFetcher` only when normal fetching fails and a stronger browser profile is required.
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
- When the working state lives in Playwright, paginate and extract in that same browser context instead of moving the job into a fresh local script mid-run.
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
- For protected sites, prefer the first real browser path that actually clears the challenge over repeated retries in isolated fetchers.
- Keep extraction deterministic and schema-first.
- Include source URL and timestamp for every extracted item.
- Report assumptions and known blind spots explicitly.

## References

- [scrapling-quickstart.md](references/scrapling-quickstart.md)
- [scrapling-mcp.md](references/scrapling-mcp.md)
