#!/usr/bin/env python3
"""Local NEXORA agent API health and capability status endpoints.

No agent registry or vault provider is configured by this module. The API
reports those capabilities as unavailable instead of inventing data.
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

HOST = "127.0.0.1"
PORT = 8082


class AgentHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/health":
            self._send_json(200, {"status": "ok", "service": "nexora-agent-api"})
            return
        if path == "/api/agents":
            self._send_json(503, {
                "error": "agent_registry_not_configured",
                "message": "No verified agent registry is connected.",
            })
            return
        if path == "/api/vault/balance":
            self._send_json(503, {
                "error": "vault_provider_not_configured",
                "message": "No verified vault provider is connected; balance is unavailable.",
            })
            return
        self._send_json(404, {"error": "not_found"})

    def log_message(self, _format: str, *args) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), AgentHandler)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
