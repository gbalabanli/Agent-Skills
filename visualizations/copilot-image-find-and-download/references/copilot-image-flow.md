# Copilot Image Flow Notes

Use this note when result selection or download retries are needed.

## Search Source

- Query endpoint:
  - `https://www.bing.com/images/search?q=<prompt>&form=HDRSC3`
- Extraction strategy:
  - Parse image URLs from `murl` values in page HTML.

## Completion Signal

Treat download as complete when:

1. At least one image URL is extracted.
2. Selected image URL returns binary content.
3. The output file exists in `~/Downloads/temp` (or chosen output dir).

## Failure Recovery

- If no image URLs are found: rewrite prompt with more concrete nouns.
- If the first image is not suitable: rerun with `--index 2` or higher.
- If download fails: rerun once and verify the source URL in output logs.
