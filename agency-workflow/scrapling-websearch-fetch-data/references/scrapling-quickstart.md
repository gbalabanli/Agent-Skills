# Scrapling Quickstart

## Install

```bash
pip install -U "scrapling[ai]"
```

## Choose The Right Fetcher

- `Fetcher`: static pages, fastest option.
- `DynamicFetcher`: JavaScript-rendered pages (browser automation).
- `StealthyFetcher`: harder anti-bot surfaces and stricter fingerprinting cases.
- `FetcherSession`, `DynamicSession`, `StealthySession`: persistent state across requests.

## Basic Fetch And Extract

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get("https://quotes.toscrape.com/")
quotes = page.css(".quote .text::text").getall()
```

## Session-Based Flow

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate="chrome") as session:
    page = session.get("https://quotes.toscrape.com/", stealthy_headers=True)
    items = page.css(".quote .text::text").getall()
```

## Dynamic Content

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch("https://example.com")
records = page.xpath("//div[@class='card']").getall()
```

## Stealth Mode

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch("https://example.com", headless=True, network_idle=True)
```

## Spider Pattern

```python
from scrapling.spiders import Spider, Response

class DemoSpider(Spider):
    name = "demo"
    start_urls = ["https://quotes.toscrape.com/"]

    async def parse(self, response: Response):
        for quote in response.css(".quote"):
            yield {"text": quote.css(".text::text").get()}
```

## Practical Notes

- Keep selectors specific and schema-aligned.
- Add max-page and max-item guards to prevent runaway crawls.
- Keep per-domain concurrency conservative unless you control the target.
- Always store source URL and fetch timestamp with extracted records.
- Prefer the Scrapling MCP server for one-off fetch and extraction tasks inside Codex; use Python code when the task needs reusable scripts or custom control flow.
