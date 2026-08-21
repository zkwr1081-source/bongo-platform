import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from nexora.runtime.app import app

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/":
            return self._send(200, {
                "name": "NEXORA",
                "message": "Infrastructure online",
                "status": app.kernel.status()
            })

        if self.path == "/health":
            return self._send(200, {
                "status": "ok",
                "health": app.kernel.health.check()
            })

        if self.path == "/metrics":
            return self._send(200, app.kernel.metrics.snapshot())

        if self.path == "/agents":
            return self._send(200, {
                "agents": list(app.kernel.agents.agents)
            })

        if self.path == "/plugins":
            return self._send(200, {
                "plugins": app.kernel.plugins.list()
            })

        if self.path == "/memory":
            return self._send(200, {
                "memory": app.kernel.memory.search("")
            })

        self._send(404, {"error": "not_found"})

    def log_message(self, *_):
        pass

def run(host="127.0.0.1", port=8082):
    app.start()
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"NEXORA API → http://{host}:{port}")
    server.serve_forever()
