#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8091
class DashHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = "<html><body style='background:#000;color:#00f3ff;font-family:sans-serif;'><h2>NEXORA DASHBOARD ACTIVE</h2></body></html>"
        self.wfile.write(html.encode('utf-8'))
    def log_message(self, *_): pass

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', PORT), DashHandler)
    server.serve_forever()
