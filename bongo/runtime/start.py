import sys
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def running(port):
    try:
        import socket

        with socket.create_connection(
            ("127.0.0.1", port),
            timeout=0.5
        ):
            return True

    except Exception:
        return False

def start_process(module, port, logfile):

    if running(port):
        return None

    log = open(
        logfile,
        "a",
        encoding="utf-8"
    )

    return subprocess.Popen(
        [sys.executable, "-m", module],
        cwd=ROOT,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True
    )

api = start_process(
    "bongo.api.server",
    8092,
    ROOT / "bongo_api.log"
)

client = start_process(
    "bongo.runtime.serve_client",
    8093,
    ROOT / "bongo_client.log"
)

time.sleep(1)

print("==========================================")
print(" بونجو — ممر الحلول المتكامل")
print("==========================================")
print("API    : http://127.0.0.1:8092")
print("CLIENT : http://127.0.0.1:8093")
print("==========================================")
