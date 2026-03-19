#!/usr/bin/env python3
"""Start a local server and open the annotation tool with demo data preloaded."""

from __future__ import annotations

import argparse
import functools
import pathlib
import socketserver
import webbrowser
from http.server import SimpleHTTPRequestHandler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the repository locally and open the design-to-code annotator demo."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port to bind the local HTTP server (default: 8765).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace_root = pathlib.Path(__file__).resolve().parents[5]
    route = "/designing/design-to-code-annotator/assets/annotation-tool/index.html?demo=1"
    url = f"http://127.0.0.1:{args.port}{route}"

    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(workspace_root))
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as server:
        print(f"Serving {workspace_root}")
        print(f"Opening demo at {url}")
        print("Press Ctrl+C to stop.")
        webbrowser.open(url)
        server.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo server stopped.")
