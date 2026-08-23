from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent / "client"
os.chdir(ROOT)

server = ThreadingHTTPServer(
    ("127.0.0.1", 8093),
    SimpleHTTPRequestHandler
)

print("بونجو Client: http://127.0.0.1:8093")
server.serve_forever()
