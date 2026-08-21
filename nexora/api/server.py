import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from nexora.runtime.app import app

class Handler(BaseHTTPRequestHandler):

    def _send(self, code, data):
        raw = json.dumps(
            data,
            ensure_ascii=False,
            default=str
        ).encode()

        self.send_response(code)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(raw))
        )
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            return self._send(
                200,
                app.kernel.status()
            )

        if parsed.path == "/health":
            return self._send(
                200,
                {
                    "status": "ok",
                    "health": app.kernel.health.check()
                }
            )

        if parsed.path == "/metrics":
            return self._send(
                200,
                app.kernel.metrics.snapshot()
            )

        if parsed.path == "/agents":
            return self._send(
                200,
                {"agents": app.kernel.agents.list()}
            )

        if parsed.path == "/tools":
            return self._send(
                200,
                {"tools": app.kernel.tools.list()}
            )

        if parsed.path == "/plugins":
            return self._send(
                200,
                {
                    "plugins": app.kernel.plugin_manager.status()
                }
            )

        if parsed.path == "/task":
            query = parse_qs(parsed.query)
            goal = query.get("goal", [""])[0]

            if not goal:
                return self._send(
                    400,
                    {"error": "goal_required"}
                )

            task = app.task(goal)

            return self._send(
                200,
                {
                    "id": task.id,
                    "state": task.state.value,
                    "result": task.result,
                    "error": task.error
                }
            )

        self._send(404, {"error": "not_found"})

    def log_message(self, *_):
        pass

def run(host="127.0.0.1", port=8082):
    app.start()

    server = ThreadingHTTPServer(
        (host, port),
        Handler
    )

    print(f"NEXORA INFRASTRUCTURE → http://{host}:{port}")
    print("Endpoints:")
    print("  /")
    print("  /health")
    print("  /metrics")
    print("  /agents")
    print("  /tools")
    print("  /plugins")
    print("  /task?goal=hello")

    server.serve_forever()
