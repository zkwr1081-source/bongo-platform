from pathlib import Path
import subprocess
import sys
import time
import os
import signal
import urllib.request
import socket

ROOT = Path.cwd()
RUNTIME = ROOT / "data" / "runtime"
RUNTIME.mkdir(parents=True, exist_ok=True)

API_PORT = 8082
DASHBOARD_PORT = 8091

API_LOG = RUNTIME / "api.log"
DASH_LOG = RUNTIME / "dashboard.log"
API_PID = RUNTIME / "api.pid"
DASH_PID = RUNTIME / "dashboard.pid"


def port_open(port):
    s = socket.socket()
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except Exception:
        return False
    finally:
        s.close()


def read_pid(path):
    try:
        pid = int(path.read_text().strip())
        return pid
    except Exception:
        return None


def alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def stop_old(path):
    pid = read_pid(path)
    if alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
        except Exception:
            pass


def start_process(command, log_file, pid_file):
    log = open(log_file, "a", encoding="utf-8")

    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=log,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True
    )

    pid_file.write_text(str(process.pid))
    return process


def wait_port(port, timeout=15):
    started = time.time()

    while time.time() - started < timeout:
        if port_open(port):
            return True
        time.sleep(0.25)

    return False


def open_browser(url):
    methods = [
        ["termux-open-url", url],
        ["am", "start", "-a", "android.intent.action.VIEW", "-d", url],
    ]

    for command in methods:
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass

    return False


def detect_dashboard():

    # Known NEXORA dashboard launcher
    candidates = [
        ROOT / "dashboard.py",
        ROOT / "run_dashboard.py",
        ROOT / "app.py",
        ROOT / "server.py",
    ]

    for p in candidates:
        if p.exists():
            text = p.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            # Avoid accidentally launching the API as dashboard
            if "8091" in text:
                return [sys.executable, str(p)]

    # Search common dashboard files
    for p in ROOT.rglob("*.py"):
        if any(x in p.parts for x in [
            ".git",
            "__pycache__",
            "tests"
        ]):
            continue

        try:
            text = p.read_text(
                encoding="utf-8",
                errors="ignore"
            )
        except Exception:
            continue

        if "8091" in text and (
            "HTTPServer" in text
            or "ThreadingHTTPServer" in text
            or "uvicorn" in text
            or "FastAPI" in text
            or "Flask" in text
        ):
            return [sys.executable, str(p)]

    return None


print()
print("=" * 70)
print("              NEXORA ONE-CLICK INFRASTRUCTURE")
print("=" * 70)

# ------------------------------------------------------------
# 1. Validate installation
# ------------------------------------------------------------

print("\n[1/7] Validating NEXORA...")

required = [
    ROOT / "nexora",
    ROOT / "run_nexora.py",
]

missing = [str(x) for x in required if not x.exists()]

if missing:
    print("❌ Missing:")
    for x in missing:
        print("   ", x)
    sys.exit(1)

print("✓ Core installation detected")


# ------------------------------------------------------------
# 2. Tests
# ------------------------------------------------------------

print("\n[2/7] Running tests...")

test = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "nexora/tests"],
    cwd=ROOT
)

if test.returncode != 0:
    print("\n❌ Tests failed.")
    print("NEXORA will NOT be started.")
    sys.exit(test.returncode)

print("✓ All tests passed")


# ------------------------------------------------------------
# 3. Stop old instances
# ------------------------------------------------------------

print("\n[3/7] Cleaning previous runtime...")

stop_old(API_PID)
stop_old(DASH_PID)

print("✓ Previous managed processes stopped")


# ------------------------------------------------------------
# 4. Start API
# ------------------------------------------------------------

print("\n[4/7] Starting NEXORA API...")

if port_open(API_PORT):
    print(f"✓ API already responding on {API_PORT}")
else:
    api = start_process(
        [sys.executable, "run_nexora.py"],
        API_LOG,
        API_PID
    )

    if not wait_port(API_PORT):
        print("❌ API failed to start.")
        print(f"Check: {API_LOG}")
        sys.exit(1)

    print(f"✓ API online → http://127.0.0.1:{API_PORT}")


# ------------------------------------------------------------
# 5. Start dashboard
# ------------------------------------------------------------

print("\n[5/7] Detecting NEXORA dashboard...")

dashboard = detect_dashboard()

if port_open(DASHBOARD_PORT):
    print(
        f"✓ Dashboard already online → "
        f"http://127.0.0.1:{DASHBOARD_PORT}"
    )

elif dashboard:
    print("✓ Dashboard launcher detected:")
    print(" ", " ".join(map(str, dashboard)))

    start_process(
        dashboard,
        DASH_LOG,
        DASH_PID
    )

    if wait_port(DASHBOARD_PORT):
        print(
            f"✓ Dashboard online → "
            f"http://127.0.0.1:{DASHBOARD_PORT}"
        )
    else:
        print(
            "⚠ Dashboard process started, "
            "but port 8091 did not respond yet."
        )
        print(f"Check: {DASH_LOG}")

else:
    print("⚠ No existing dashboard launcher detected.")
    print("API will continue running.")


# ------------------------------------------------------------
# 6. Health verification
# ------------------------------------------------------------

print("\n[6/7] Performing health verification...")

try:
    with urllib.request.urlopen(
        f"http://127.0.0.1:{API_PORT}/health",
        timeout=5
    ) as response:

        body = response.read().decode(
            "utf-8",
            errors="replace"
        )

        print("✓ API health:", body)

except Exception as e:
    print("⚠ Health request failed:", e)


# ------------------------------------------------------------
# 7. Open interface
# ------------------------------------------------------------

print("\n[7/7] Opening NEXORA...")

if port_open(DASHBOARD_PORT):
    url = f"http://127.0.0.1:{DASHBOARD_PORT}"
else:
    url = f"http://127.0.0.1:{API_PORT}"

if open_browser(url):
    print("✓ Browser opened automatically")
else:
    print("⚠ Automatic browser opening unavailable")

print()
print("=" * 70)
print("                 NEXORA IS ONLINE")
print("=" * 70)
print()
print(f"API       : http://127.0.0.1:{API_PORT}")
print(f"DASHBOARD : http://127.0.0.1:{DASHBOARD_PORT}")
print()
print("Runtime files:")
print(f"  API PID : {API_PID}")
print(f"  API LOG : {API_LOG}")
print(f"  DASH PID: {DASH_PID}")
print(f"  DASH LOG: {DASH_LOG}")
print()
print("🚀 ONE COMMAND → TEST → START → HEALTH → OPEN")
print("=" * 70)
