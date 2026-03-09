from __future__ import annotations

import json
import socket
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from detect_ai_score import analyze_text
from humanize_retry import humanize_with_retry


ROOT = Path(__file__).resolve().parent.parent
UI_ROOT = ROOT / "ui"
HOST = "127.0.0.1"
PORT = 8765


def _port_is_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


class HumanizeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_ROOT), **kwargs)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/analyze", "/api/humanize-retry"}:
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        text = payload.get("text", "")
        if parsed.path == "/api/analyze":
            response = analyze_text(text)
        else:
            max_attempts = int(payload.get("max_attempts", 3))
            response = humanize_with_retry(text, max_attempts=max(1, min(max_attempts, 5)))
        encoded = json.dumps(response).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> None:
    if _port_is_in_use(HOST, PORT):
        print(f"Port {PORT} is already in use on {HOST}.")
        print("Stop the existing Humanize Text server instance, then start again.")
        sys.exit(1)

    with ThreadingHTTPServer((HOST, PORT), HumanizeHandler) as server:
        print(f"Humanize Text UI running at http://{HOST}:{PORT}")
        print("Press Ctrl+C to stop.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
