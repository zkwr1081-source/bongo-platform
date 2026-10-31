"""NEXORA web entry point.

Serves the maintained responsive dashboard from web/index.html.
Run with: python server.py
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 8080
ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "web" / "index.html"


class NexoraHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if path not in ("/", "/index.html"):
            self.send_error(404, "Not found")
            return

        try:
            html = INDEX.read_bytes()
        except OSError:
            self.send_error(500, "Dashboard file is unavailable")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(html)

    def log_message(self, format_string, *args):
        # Keep the local console concise; never log request headers or secrets.
        print("%s - %s" % (self.address_string(), format_string % args))


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), NexoraHandler)
    print(f"NEXORA dashboard available at http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping NEXORA dashboard...")
    finally:
        server.server_close()
