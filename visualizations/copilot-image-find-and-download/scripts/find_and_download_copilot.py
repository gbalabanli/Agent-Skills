#!/usr/bin/env python3
"""Find an image from Copilot/Bing results and download it."""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

SEARCH_URL = "https://www.bing.com/images/search"
DEFAULT_TIMEOUT = 30
IMAGE_URL_PATTERNS = (
    r'murl&quot;:&quot;(https?://[^"&]+)&quot;',
    r'"murl":"(https?://[^"]+)"',
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search Copilot/Bing Images for a prompt and download one result "
            "without requiring login."
        )
    )
    parser.add_argument("--prompt", required=True, help="Prompt or search query.")
    parser.add_argument(
        "--index",
        type=int,
        default=1,
        help="1-based image index to download from results.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path.home() / "Downloads" / "temp"),
        help="Output directory (default: ~/Downloads/temp).",
    )
    parser.add_argument(
        "--filename",
        help="Optional filename. Extension is inferred if missing.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="HTTP timeout seconds (default: 30).",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print metadata as JSON.",
    )
    return parser.parse_args()


def build_request(url: str) -> urllib.request.Request:
    return urllib.request.Request(
        url=url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    )


def fetch_text(url: str, timeout: int) -> str:
    req = build_request(url)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as err:
        body = ""
        try:
            body = err.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise RuntimeError(f"Search request failed ({err.code}): {body[:200]}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"Network error while loading search page: {err.reason}") from err


def extract_image_urls(page_html: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for pattern in IMAGE_URL_PATTERNS:
        for match in re.finditer(pattern, page_html):
            raw = match.group(1).strip()
            decoded = html.unescape(raw)
            cleaned = (
                decoded.replace("\\/", "/")
                .replace("\\u0026", "&")
                .replace("\\u003d", "=")
            )
            if not cleaned.startswith("http"):
                continue
            if cleaned in seen:
                continue
            seen.add(cleaned)
            urls.append(cleaned)
    return urls


def infer_extension(content_type: str | None, image_url: str) -> str:
    if content_type:
        mime = content_type.split(";")[0].strip()
        ext = mimetypes.guess_extension(mime)
        if ext:
            return ".jpg" if ext == ".jpe" else ext
    path = urllib.parse.urlparse(image_url).path
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    return ".jpg"


def slugify(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return clean or "copilot-image"


def resolve_output_path(
    output_dir: Path,
    filename: str | None,
    prompt: str,
    extension: str,
) -> Path:
    if filename:
        base = Path(filename).name
        target = output_dir / base
        if target.suffix:
            return target
        return target.with_suffix(extension)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"copilot-image-{slugify(prompt)}-{stamp}"
    return output_dir / f"{name}{extension}"


def download_binary(url: str, timeout: int) -> tuple[bytes, str | None]:
    req = build_request(url)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read(), response.headers.get("Content-Type")
    except urllib.error.HTTPError as err:
        body = ""
        try:
            body = err.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise RuntimeError(f"Image download failed ({err.code}): {body[:200]}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"Network error while downloading image: {err.reason}") from err


def main() -> int:
    args = parse_args()
    prompt = args.prompt.strip()
    if not prompt:
        print("Prompt cannot be empty.", file=sys.stderr)
        return 2
    if args.index < 1:
        print("--index must be >= 1.", file=sys.stderr)
        return 2

    params = {"q": prompt, "form": "HDRSC3"}
    search_url = f"{SEARCH_URL}?{urllib.parse.urlencode(params)}"
    page_html = fetch_text(search_url, timeout=args.timeout)

    image_urls = extract_image_urls(page_html)
    if not image_urls:
        print("No image URLs found in search results.", file=sys.stderr)
        return 1
    if args.index > len(image_urls):
        print(
            f"--index {args.index} out of range. Found {len(image_urls)} image URL(s).",
            file=sys.stderr,
        )
        return 1

    selected_url = image_urls[args.index - 1]
    data, content_type = download_binary(selected_url, timeout=args.timeout)

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    ext = infer_extension(content_type, selected_url)
    output_path = resolve_output_path(output_dir, args.filename, prompt, ext)
    output_path.write_bytes(data)

    result = {
        "prompt": prompt,
        "source": "copilot-bing-images-search",
        "selected_index": args.index,
        "selected_url": selected_url,
        "output_path": str(output_path),
        "bytes_written": len(data),
    }
    if args.print_json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    else:
        print(f"Downloaded image to {output_path} ({len(data)} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
