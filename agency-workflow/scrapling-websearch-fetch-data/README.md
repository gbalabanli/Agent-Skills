# Scrapling Websearch And Fetch Data

Use [SKILL.md](SKILL.md) for the full workflow. This note exists to make one lesson explicit:

## Protected Site Lesson

- Start with Scrapling MCP for normal pages and lightweight extraction.
- If the target falls into Cloudflare, `checkLoading`, forced login redirects, or repeated `403` responses, switch to Playwright real-browser automation early.
- Keep the scrape inside the same working Playwright tab and browser context. Do not assume a separate Python script or a different browser instance will inherit the cleared session.
- Once the page is open cleanly, paginate and extract in-browser with Playwright tools such as `browser_snapshot`, `browser_evaluate`, and `browser_run_code`.

## Sahibinden Example

- The working `Altintepe` result path resolves under `Kucukyali` on Sahibinden.
- A valid filtered example is:
  - `https://www.sahibinden.com/satilik-daire/istanbul-maltepe-kucukyali-altintepe-mh.?sorting=price_asc&a20=38470`
- In this case, Playwright real-browser extraction is more reliable than retrying isolated Scrapling fetchers after anti-bot checks appear.

## Files

- [SKILL.md](SKILL.md): full decision workflow
- [references/scrapling-quickstart.md](references/scrapling-quickstart.md): Scrapling usage notes
- [references/scrapling-mcp.md](references/scrapling-mcp.md): MCP setup and tool notes
