"""NEXORA dashboard and read-only status API.

Run: python server.py
Dashboard: http://127.0.0.1:8080
Health:    http://127.0.0.1:8080/health
Status:    http://127.0.0.1:8080/api/status
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from nexora_agents import registry_summary

HOST = os.getenv("NEXORA_HOST", "127.0.0.1")
PORT = int(os.getenv("NEXORA_PORT", "8080"))
ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "web" / "index.html"


class NexoraHandler(BaseHTTPRequestHandler):
    server_version = "NEXORA/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if path == "/health":
            self._json(200, {"ok": True, "service": "nexora-web"})
            return

        if path == "/api/status":
            summary = registry_summary()
            configured = all(
                os.getenv(key, "").strip()
                for key in ("NEXORA_BASE_URL", "NEXORA_API_KEY", "NEXORA_MODEL")
            )
            summary["model_configured"] = configured
            summary["model_connected"] = False
            summary["note"] = (
                "Credentials are configured; connectivity has not been tested."
                if configured else
                "Set NEXORA_BASE_URL, NEXORA_API_KEY and NEXORA_MODEL to configure a provider."
            )
            self._json(200, summary)
            return

        if path not in ("/", "/index.html"):
            self._json(404, {"error": "not_found"})
            return

        try:
            html = INDEX.read_bytes()
        except OSError:
            self._json(500, {"error": "dashboard_unavailable"})
            return

        self._send(200, html, "text/html; charset=utf-8")

    def log_message(self, format_string: str, *args) -> None:
        # Request paths only; never log headers, query values, or credentials.
        print("%s - %s" % (self.address_string(), format_string % args))


def main() -> None:
    if not 1 <= PORT <= 65535:
        raise ValueError("NEXORA_PORT must be between 1 and 65535")
    server = ThreadingHTTPServer((HOST, PORT), NexoraHandler)
    print(f"NEXORA dashboard: http://127.0.0.1:{PORT}")
    print(f"NEXORA status:    http://127.0.0.1:{PORT}/api/status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping NEXORA dashboard...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
