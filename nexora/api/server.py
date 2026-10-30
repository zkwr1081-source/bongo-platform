import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from nexora.runtime.app import app


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data, extra_headers=None):
        raw = json.dumps(
            data,
            ensure_ascii=False,
            default=str
        ).encode("utf-8")

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            return self._send(200, app.kernel.status())

        if path == "/health":
            return self._send(
                200,
                {"status": "ok", "health": app.kernel.health.check()}
            )

        if path == "/metrics":
            return self._send(200, app.kernel.metrics.snapshot())

        if path == "/agents":
            return self._send(200, {"agents": app.kernel.agents.list()})

        if path == "/tools":
            return self._send(200, {"tools": app.kernel.tools.list()})

        if path == "/plugins":
            return self._send(
                200,
                {"plugins": app.kernel.plugin_manager.status()}
            )

        if path == "/task":
            return self._send(
                405,
                {"error": "method_not_allowed", "allowed": ["POST"]},
                {"Allow": "POST"}
            )

        return self._send(404, {"error": "not_found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/task":
            return self._send(404, {"error": "not_found"})

        if self.headers.get_content_type() != "application/json":
            return self._send(415, {"error": "application_json_required"})

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self._send(400, {"error": "invalid_content_length"})

        if length <= 0 or length > 16_384:
            return self._send(413, {"error": "invalid_body_size"})

        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self._send(400, {"error": "invalid_json"})

        if not isinstance(payload, dict):
            return self._send(400, {"error": "json_object_required"})

        goal = payload.get("goal")
        if not isinstance(goal, str) or not goal.strip():
            return self._send(400, {"error": "goal_required"})
        if len(goal) > 2_000:
            return self._send(400, {"error": "goal_too_long"})

        task = app.task(goal.strip())
        return self._send(
            200,
            {
                "id": task.id,
                "state": task.state.value,
                "result": task.result,
                "error": task.error
            }
        )

    def log_message(self, *_):
        pass


def run(host="127.0.0.1", port=8082):
    app.start()
    server = ThreadingHTTPServer((host, port), Handler)

    print(f"NEXORA INFRASTRUCTURE → http://{host}:{port}")
    print("Endpoints: /, /health, /metrics, /agents, /tools, /plugins")
    print("Submit tasks with POST /task and JSON body: {\"goal\": \"...\"}")

    server.serve_forever()
