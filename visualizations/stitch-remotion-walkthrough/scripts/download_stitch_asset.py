#!/usr/bin/env python3
"""Download a Stitch-hosted asset to a local path with redirect handling."""

from __future__ import annotations

import argparse
import pathlib
import sys
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a Stitch or Google Storage asset to a local file."
    )
    parser.add_argument("url", help="Asset URL to download")
    parser.add_argument("output", help="Local output path")
    return parser.parse_args()


def download(url: str, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "codex-stitch-remotion-walkthrough/1.0",
        },
    )
    with urllib.request.urlopen(request) as response, output.open("wb") as file_handle:
        file_handle.write(response.read())


def main() -> int:
    args = parse_args()
    output = pathlib.Path(args.output)
    try:
        download(args.url, output)
    except Exception as exc:  # pragma: no cover - surface exact failure for shell use
        print(f"Download failed: {exc}", file=sys.stderr)
        return 1

    print(f"Downloaded {args.url} -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
