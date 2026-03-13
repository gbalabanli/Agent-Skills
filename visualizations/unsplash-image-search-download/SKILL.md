---
name: unsplash-image-search-download
description: Search Unsplash for images related to a natural-language user prompt and download a selected result to disk using the official API and tracked download endpoint. Use when Codex needs stock photos from Unsplash for articles, slide decks, social posts, mockups, inspiration boards, or any prompt-to-image download workflow.
---

# Unsplash Image Search Download

Use this skill to turn a user prompt into a downloaded Unsplash image file.

## Workflow

1. Confirm the search intent.
- Use the user prompt as `--query`.
- Keep nouns and style words that affect visuals (for example, "minimal office desk at sunrise").
- Default output directory to `downloads/unsplash` unless the user gives a path.

2. Prepare credentials.
- Set `UNSPLASH_ACCESS_KEY` in the shell or pass `--access-key`.
- Use the official API endpoints from [references/unsplash-api.md](references/unsplash-api.md); do not scrape Unsplash HTML pages.

3. Run the script.
```bash
python visualizations/unsplash-image-search-download/scripts/find_and_download_unsplash.py --query "mountain sunset"
```

4. Tune result selection when needed.
- Use `--index N` to pick a different result from the same search response.
- Use `--orientation landscape|portrait|squarish` for layout-specific images.
- Use `--filename hero-image` to force a stable output name.

5. Return actionable output.
- Report absolute output path, photo ID, and photographer.
- Keep attribution metadata from `--print-json` output for downstream publishing workflows.

## Script Reference

Path:
`visualizations/unsplash-image-search-download/scripts/find_and_download_unsplash.py`

Main arguments:
- `--query` (required): Search phrase from user prompt.
- `--output-dir`: Target folder for downloaded images.
- `--index`: 1-based result index to download.
- `--per-page`: Number of results to request (max 30).
- `--orientation`: Optional Unsplash orientation filter.
- `--content-filter`: Unsplash safety filter (`low` or `high`).
- `--filename`: Optional file name (extension inferred).
- `--print-json`: Print machine-readable metadata.

## Failure Handling

- Missing key: ask user for an Unsplash API access key and retry.
- No matches: tighten or broaden query terms and run again.
- Index out of range: increase `--per-page` or decrease `--index`.
- API error `401`/`403`: verify key validity and app permissions.
