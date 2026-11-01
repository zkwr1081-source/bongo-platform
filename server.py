"""NEXORA dashboard and read-only status API.

Run: python server.py
Dashboard: http://127.0.0.1:8080
Health:    http://127.0.0.1:8080/health
Status:    http://127.0.0.1:8080/api/status
"""
from __future__ import annotations

import asyncio
import hmac
import ipaddress
import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from nexora_agents import REGISTRY, registry_summary, run_batch
from nexora_model_adapter import ModelConfigurationError, model_handler

HOST = os.getenv("NEXORA_HOST", "127.0.0.1")
PORT = int(os.getenv("NEXORA_PORT", "8080"))
ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "web" / "index.html"
GITHUB_REPO = os.getenv("NEXORA_GITHUB_REPO", "zkwr1081-source/bongo-platform")
GITHUB_API = "https://api.github.com"


def is_loopback_bind(host: str) -> bool:
    """Return True only for localhost or a literal loopback IP address."""
    candidate = host.strip().lower()
    if candidate == "localhost":
        return True
    try:
        address = ipaddress.ip_address(candidate.split("%", 1)[0])
    except ValueError:
        return False
    return address.is_loopback


def execution_request_authorized(
    authorization: str | None, token: str, host: str
) -> bool:
    """Allow unauthenticated execution only on a loopback-only bind."""
    if not token:
        return is_loopback_bind(host)
    scheme, separator, supplied = (authorization or "").partition(" ")
    return bool(
        separator
        and scheme.lower() == "bearer"
        and hmac.compare_digest(supplied.strip(), token)
    )


def validate_server_security(host: str, token: str) -> None:
    """Fail closed when execution would be exposed without authentication."""
    if not is_loopback_bind(host) and not token:
        raise RuntimeError(
            "Refusing non-loopback NEXORA_HOST without NEXORA_EXECUTION_TOKEN. "
            "Bind to 127.0.0.1/::1 or configure a strong execution token."
        )


def github_api_json(path: str) -> dict:
    request = urllib.request.Request(
        f"{GITHUB_API}{path}",
        headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "NEXORA-GitHub-Status"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def github_status() -> dict:
    owner, name = GITHUB_REPO.split("/", 1)
    prefix = f"/repos/{owner}/{name}"
    repository = github_api_json(prefix)
    commit = github_api_json(f"{prefix}/commits/{repository['default_branch']}")
    try:
        runs = github_api_json(f"{prefix}/actions/runs?per_page=1")
        latest_run = (runs.get("workflow_runs") or [None])[0]
    except urllib.error.HTTPError as exc:
        if exc.code not in (403, 404):
            raise
        latest_run = None
    return {
        "connected": True,
        "repository": repository["full_name"],
        "html_url": repository["html_url"],
        "visibility": repository["visibility"],
        "default_branch": repository["default_branch"],
        "latest_commit": {"sha": commit["sha"], "short_sha": commit["sha"][:7], "message": commit["commit"]["message"].splitlines()[0], "html_url": commit["html_url"]},
        "latest_workflow": ({"name": latest_run.get("name"), "status": latest_run.get("status"), "conclusion": latest_run.get("conclusion"), "html_url": latest_run.get("html_url")} if latest_run else None),
        "source": "GitHub REST API",
    }


class NexoraHandler(BaseHTTPRequestHandler):
    server_version = "NEXORA/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")


    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/agents/run":
            self._json(404, {"error": "not_found"})
            return
        execution_token = os.getenv("NEXORA_EXECUTION_TOKEN", "").strip()
        if not execution_request_authorized(
            self.headers.get("Authorization"), execution_token, HOST
        ):
            self._json(401, {"error": "unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 16384:
                self._json(413, {"error": "request_body_must_be_between_1_and_16384_bytes"})
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                self._json(400, {"error": "request_body_must_be_a_json_object"})
                return
            goal = payload.get("goal")
            if not isinstance(goal, str) or not goal.strip() or len(goal) > 4000:
                self._json(400, {"error": "goal_must_be_a_non_empty_string_up_to_4000_characters"})
                return
            raw_ids = payload.get("agent_ids")
            if raw_ids is None:
                raw_ids = ["NX-ORCHESTRATION-001", "NX-QUALITY-001"]
            if not isinstance(raw_ids, list) or not 1 <= len(raw_ids) <= 10 or not all(isinstance(x, str) for x in raw_ids):
                self._json(400, {"error": "agent_ids_must_contain_1_to_10_agent_ids"})
                return
            concurrency = payload.get("concurrency", min(len(raw_ids), 5))
            if not isinstance(concurrency, int) or isinstance(concurrency, bool) or not 1 <= concurrency <= 10:
                self._json(400, {"error": "concurrency_must_be_between_1_and_10"})
                return
            results = asyncio.run(run_batch(
                goal=goal.strip(), handler=model_handler, agent_ids=raw_ids,
                concurrency=concurrency, timeout_seconds=75,
            ))
            self._json(200, {"ok": all(r["status"] == "ok" for r in results), "results": results})
        except ModelConfigurationError as exc:
            self._json(503, {"error": "model_not_configured", "detail": str(exc)})
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._json(400, {"error": "invalid_request", "detail": str(exc)[:200]})
        except Exception as exc:
            self._json(500, {"error": "execution_failed", "detail": type(exc).__name__})

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if path == "/health":
            self._json(200, {"ok": True, "service": "nexora-web"})
            return


        if path == "/api/github":
            try:
                self._json(200, github_status())
            except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
                self._json(502, {"connected": False, "error": str(exc)[:240]})
            return

        if path == "/github-status.js":
            script = ROOT / "web" / "github-status.js"
            try:
                self._send(200, script.read_bytes(), "application/javascript; charset=utf-8")
            except OSError:
                self._json(404, {"error": "github_dashboard_script_unavailable"})
            return


        if path == "/api/agents":
            self._json(200, {"agents": [
                {"agent_id": a.agent_id, "department": a.department, "specialty": a.specialty}
                for a in REGISTRY
            ], "count": len(REGISTRY)})
            return

        if path == "/api/status":
            summary = registry_summary()
            configured = all(
                os.getenv(key, "").strip()
                for key in ("NEXORA_BASE_URL", "NEXORA_API_KEY", "NEXORA_MODEL")
            )
            summary["model_configured"] = configured
            summary["model_connected"] = False
            summary["note"] = (
                "Credentials are configured; connectivity has not been tested."
                if configured else
                "Set NEXORA_BASE_URL, NEXORA_API_KEY and NEXORA_MODEL to configure a provider."
            )
            self._json(200, summary)
            return

        if path not in ("/", "/index.html"):
            self._json(404, {"error": "not_found"})
            return

        try:
            html = INDEX.read_bytes()
        except OSError:
            self._json(500, {"error": "dashboard_unavailable"})
            return

        self._send(200, html, "text/html; charset=utf-8")

    def log_message(self, format_string: str, *args) -> None:
        # Request paths only; never log headers, query values, or credentials.
        print("%s - %s" % (self.address_string(), format_string % args))


def main() -> None:
    if not 1 <= PORT <= 65535:
        raise ValueError("NEXORA_PORT must be between 1 and 65535")
    execution_token = os.getenv("NEXORA_EXECUTION_TOKEN", "").strip()
    validate_server_security(HOST, execution_token)
    server = ThreadingHTTPServer((HOST, PORT), NexoraHandler)
    print(f"NEXORA dashboard: http://127.0.0.1:{PORT}")
    print(f"NEXORA status:    http://127.0.0.1:{PORT}/api/status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping NEXORA dashboard...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
