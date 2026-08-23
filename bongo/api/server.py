import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from bongo import create_runtime

runtime = create_runtime(1000)
sessions = {}

def json_bytes(data):
    return json.dumps(data, ensure_ascii=False).encode("utf-8")

class BongoHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json_bytes(data)

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json({"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.send_json({
                "name": "بونجو",
                "title": "بونجو — ممر الحلول المتكامل",
                "status": "online",
                "services": runtime.registry.count(),
                "capabilities": sum(
                    len(runtime.integration.capabilities.get(s.name))
                    for s in runtime.registry.list()
                )
            })
            return

        if parsed.path == "/health":
            self.send_json(runtime.status())
            return

        if parsed.path == "/discover":
            query = parse_qs(parsed.query).get("q", [""])[0]

            self.send_json({
                "query": query,
                "results": (
                    runtime.integration.find(query)
                    if query else []
                )
            })
            return

        if parsed.path.startswith("/service/"):
            name = parsed.path[len("/service/"):]
            service = runtime.registry.get(name)

            if not service:
                self.send_json(
                    {
                        "ok": False,
                        "error": "service_not_found"
                    },
                    404
                )
                return

            self.send_json(
                runtime.integration.execute(name)
            )
            return

        self.send_json(
            {
                "ok": False,
                "error": "not_found"
            },
            404
        )

    def do_POST(self):
        parsed = urlparse(self.path)

        length = int(
            self.headers.get("Content-Length", "0")
        )

        raw = self.rfile.read(length)

        try:
            data = json.loads(raw or b"{}")
        except Exception:
            self.send_json(
                {
                    "ok": False,
                    "error": "invalid_json"
                },
                400
            )
            return

        if parsed.path == "/auth/login":
            name = str(data.get("name", "")).strip()

            if not name:
                self.send_json(
                    {
                        "ok": False,
                        "error": "name_required"
                    },
                    400
                )
                return

            token = secrets.token_urlsafe(32)

            sessions[token] = {
                "name": name
            }

            self.send_json({
                "ok": True,
                "token": token,
                "user": {
                    "name": name
                }
            })
            return

        if parsed.path == "/auth/logout":
            token = str(data.get("token", ""))

            sessions.pop(token, None)

            self.send_json({
                "ok": True
            })
            return

        if parsed.path == "/auth/me":
            token = str(data.get("token", ""))
            user = sessions.get(token)

            if not user:
                self.send_json(
                    {
                        "ok": False,
                        "authenticated": False
                    },
                    401
                )
                return

            self.send_json({
                "ok": True,
                "authenticated": True,
                "user": user
            })
            return

        self.send_json(
            {
                "ok": False,
                "error": "not_found"
            },
            404
        )

    def log_message(self, format, *args):
        return

def run(host="127.0.0.1", port=8092):
    server = ThreadingHTTPServer(
        (host, port),
        BongoHandler
    )

    print(
        f"بونجو API: http://{host}:{port}",
        flush=True
    )

    server.serve_forever()

if __name__ == "__main__":
    run()
