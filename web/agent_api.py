#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8082
class AgentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        res = {
            "status": "ok",
            "agents": ["Astra", "Cipher"],
            "vault_balance": 105000.0,
            "passer_token": "PASS-NEX-9982-X"
        }
        self.wfile.write(json.dumps(res).encode('utf-8'))
    def log_message(self, *_): pass

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', PORT), AgentHandler)
    server.serve_forever()
