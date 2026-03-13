#!/usr/bin/env python3
"""Search Unsplash by prompt and download one related image."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


SEARCH_ENDPOINT = "https://api.unsplash.com/search/photos"
DEFAULT_TIMEOUT = 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search Unsplash with a text prompt and download a related image. "
            "Requires UNSPLASH_ACCESS_KEY or --access-key."
        )
    )
    parser.add_argument("--query", required=True, help="Search phrase, for example: 'mountain sunset'.")
    parser.add_argument("--output-dir", default="downloads/unsplash", help="Directory where the image is saved.")
    parser.add_argument(
        "--index",
        type=int,
        default=1,
        help="1-based result index to download from the search response.",
    )
    parser.add_argument(
        "--per-page",
        type=int,
        default=10,
        help="How many search results to request (max 30).",
    )
    parser.add_argument(
        "--orientation",
        choices=["landscape", "portrait", "squarish"],
        help="Optional orientation filter.",
    )
    parser.add_argument(
        "--content-filter",
        choices=["low", "high"],
        default="low",
        help="Unsplash content safety filter.",
    )
    parser.add_argument("--filename", help="Optional output filename. Extension is inferred if missing.")
    parser.add_argument("--access-key", help="Unsplash access key. Overrides UNSPLASH_ACCESS_KEY.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print metadata JSON instead of a human-readable summary line.",
    )
    return parser.parse_args()


def build_headers(access_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Client-ID {access_key}",
        "Accept-Version": "v1",
        "User-Agent": "codex-unsplash-image-search-download/1.0",
    }


def fetch_json(url: str, headers: dict[str, str], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(url=url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        body = ""
        try:
            body = err.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        raise RuntimeError(f"Unsplash API request failed ({err.code}): {body or err.reason}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"Network error while calling Unsplash API: {err.reason}") from err
    try:
        return json.loads(payload)
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Could not parse Unsplash JSON response: {err}") from err


def select_photo(data: dict[str, Any], index: int) -> dict[str, Any]:
    results = data.get("results")
    if not isinstance(results, list) or not results:
        raise RuntimeError("No images found for that query.")
    if index < 1 or index > len(results):
        raise RuntimeError(
            f"Requested --index {index} but only {len(results)} result(s) were returned. "
            "Increase --per-page or lower --index."
        )
    selected = results[index - 1]
    if not isinstance(selected, dict):
        raise RuntimeError("Unexpected Unsplash response shape.")
    return selected


def fetch_download_url(photo: dict[str, Any], headers: dict[str, str], timeout: int) -> str:
    links = photo.get("links") or {}
    download_location = links.get("download_location")
    if not download_location:
        download_url = links.get("download")
        if download_url:
            return str(download_url)
        raise RuntimeError("Unsplash response did not include a download URL.")

    payload = fetch_json(str(download_location), headers=headers, timeout=timeout)
    url = payload.get("url")
    if not isinstance(url, str) or not url:
        raise RuntimeError("Unsplash download endpoint did not return a usable URL.")
    return url


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return cleaned or "unsplash-image"


def infer_extension(content_type: str | None, url: str) -> str:
    if content_type:
        mime = content_type.split(";")[0].strip()
        guessed = mimetypes.guess_extension(mime)
        if guessed:
            return guessed
    parsed = urllib.parse.urlparse(url)
    path_suffix = Path(parsed.path).suffix
    if path_suffix:
        return path_suffix
    return ".jpg"


def resolve_output_path(output_dir: Path, filename: str | None, query: str, photo_id: str, extension: str) -> Path:
    if filename:
        target = Path(filename)
        if target.suffix:
            return output_dir / target.name
        return output_dir / f"{target.name}{extension}"
    base = f"{slugify(query)}-{photo_id}"
    return output_dir / f"{base}{extension}"


def download_file(url: str, destination: Path, headers: dict[str, str], timeout: int) -> tuple[int, str | None]:
    request = urllib.request.Request(url=url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type")
            data = response.read()
    except urllib.error.HTTPError as err:
        body = ""
        try:
            body = err.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        raise RuntimeError(f"Image download failed ({err.code}): {body or err.reason}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"Network error while downloading image: {err.reason}") from err

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return len(data), content_type


def main() -> int:
    args = parse_args()

    access_key = args.access_key or os.environ.get("UNSPLASH_ACCESS_KEY")
    if not access_key:
        print(
            "Missing Unsplash access key. Set UNSPLASH_ACCESS_KEY or pass --access-key.",
            file=sys.stderr,
        )
        return 2

    if args.per_page < 1 or args.per_page > 30:
        print("--per-page must be between 1 and 30.", file=sys.stderr)
        return 2
    if args.index < 1:
        print("--index must be >= 1.", file=sys.stderr)
        return 2

    per_page = max(args.per_page, args.index)
    params = {
        "query": args.query,
        "page": 1,
        "per_page": per_page,
        "content_filter": args.content_filter,
    }
    if args.orientation:
        params["orientation"] = args.orientation
    search_url = f"{SEARCH_ENDPOINT}?{urllib.parse.urlencode(params)}"
    headers = build_headers(access_key=access_key)

    search_data = fetch_json(search_url, headers=headers, timeout=args.timeout)
    photo = select_photo(search_data, index=args.index)
    photo_id = str(photo.get("id") or "unknown")
    photo_url = fetch_download_url(photo, headers=headers, timeout=args.timeout)

    temp_name = resolve_output_path(
        output_dir=Path(args.output_dir),
        filename=args.filename,
        query=args.query,
        photo_id=photo_id,
        extension=".jpg",
    )
    byte_count, content_type = download_file(photo_url, temp_name, headers=headers, timeout=args.timeout)

    final_extension = infer_extension(content_type=content_type, url=photo_url)
    final_path = temp_name
    if temp_name.suffix.lower() != final_extension.lower():
        final_path = temp_name.with_suffix(final_extension)
        temp_name.rename(final_path)

    user = photo.get("user") or {}
    username = user.get("username") or "unknown"
    credit_name = user.get("name") or username
    result = {
        "query": args.query,
        "photo_id": photo_id,
        "photographer": credit_name,
        "username": username,
        "output_path": str(final_path.resolve()),
        "bytes_written": byte_count,
        "unsplash_page": photo.get("links", {}).get("html"),
    }

    if args.print_json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(
            f"Downloaded photo {photo_id} by {credit_name} "
            f"to {final_path.resolve()} ({byte_count} bytes)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
