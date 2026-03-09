# Scrapling MCP

## Install

```bash
pip install -U "scrapling[ai]"
```

## Codex MCP Config

Add Scrapling as a stdio MCP server in `C:\Users\Bora\.codex\config.toml`:

```toml
[mcp_servers.scrapling]
command = 'C:\Users\Bora\AppData\Local\Programs\Python\Python312\Scripts\scrapling.exe'
args = ["mcp"]
startup_timeout_sec = 20.0
```

Restart Codex after editing the config so the server is loaded on the next session.

## Transports

- `scrapling mcp`: stdio transport for MCP clients.
- `scrapling mcp --http --host 127.0.0.1 --port 8000`: streamable HTTP transport when the client expects a URL.

## MCP Tools

- `get`: fast HTTP fetch for one URL.
- `bulk_get`: fast HTTP fetch for multiple URLs.
- `fetch`: browser-backed fetch for dynamic pages.
- `bulk_fetch`: browser-backed fetch for multiple dynamic pages.
- `stealthy_fetch`: stealth browser fetch for stronger anti-bot targets.
- `bulk_stealthy_fetch`: stealth browser fetch for multiple stronger anti-bot targets.

## Selection Rules

1. Start with `get` for ordinary static pages.
2. Move to `fetch` when the page requires JavaScript or browser execution.
3. Move to `stealthy_fetch` only when lighter approaches fail or the target clearly needs stronger evasion.
4. Use bulk variants only when the task is naturally batched and rate limits remain conservative.

## Response Shape

Each MCP call returns:

- `status`: returned status code.
- `content`: extracted content as Markdown, HTML, or text.
- `url`: final URL associated with the response.

## Usage Guidance For Codex

- Prefer MCP for exploratory or conversational scraping in the current chat.
- Ask for markdown or text output when the goal is summarization or analysis.
- Ask for HTML when selectors or raw structure matter.
- Include CSS selectors only when the task needs a focused extraction instead of whole-page content.
- Fall back to local Python scripts when the workflow needs pagination loops, sessions, custom transforms, or saved artifacts.
