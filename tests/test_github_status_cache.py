import threading
import urllib.error
from types import SimpleNamespace

import server


def reset_cache(monkeypatch):
    monkeypatch.setattr(server, "_github_status_cache", None)
    monkeypatch.setattr(server, "_github_status_cache_at", 0.0)
    monkeypatch.setattr(server, "_github_status_refreshing", False)
    monkeypatch.setattr(server, "_github_status_refresh_error", None)
    monkeypatch.setattr(server, "_github_status_retry_after", 0.0)
    monkeypatch.setattr(server, "_github_status_refresh_event", threading.Event())
    server._github_status_refresh_event.set()


def fake_github_api(path):
    if path.endswith("/actions/runs?per_page=1"):
        return {
            "workflow_runs": [
                {
                    "name": "Python CI",
                    "status": "completed",
                    "conclusion": "success",
                    "html_url": "https://github.com/example/repo/actions",
                }
            ]
        }
    if "/commits/" in path:
        return {
            "sha": "a" * 40,
            "commit": {"message": "test commit\nbody"},
            "html_url": "https://github.com/example/repo/commit/" + "a" * 40,
        }
    return {
        "full_name": "example/repo",
        "html_url": "https://github.com/example/repo",
        "visibility": "public",
        "default_branch": "main",
    }


def test_github_status_cache_uses_ttl_and_background_refresh(monkeypatch):
    reset_cache(monkeypatch)
    clock = [100.0]
    monkeypatch.setattr(server, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    calls = []
    monkeypatch.setattr(
        server,
        "github_api_json",
        lambda path: (calls.append(path), fake_github_api(path))[1],
    )

    first = server.github_status()
    assert first["connected"] is True
    assert first["cached"] is False
    assert first["stale"] is False
    assert len(calls) == 3

    second = server.github_status()
    assert second["cached"] is True
    assert second["stale"] is False
    assert len(calls) == 3

    clock[0] += server.GITHUB_STATUS_CACHE_TTL_SECONDS + 1
    stale = server.github_status()
    assert stale["connected"] is True
    assert stale["cached"] is True
    assert stale["stale"] is True

    assert server._github_status_refresh_event.wait(timeout=2)
    refreshed = server.github_status()
    assert refreshed["connected"] is True
    assert refreshed["stale"] is False
    assert len(calls) == 6


def test_github_status_serves_stale_cache_and_backoffs_after_upstream_fails(monkeypatch):
    reset_cache(monkeypatch)
    clock = [100.0]
    monkeypatch.setattr(server, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    monkeypatch.setattr(server, "github_api_json", fake_github_api)

    first = server.github_status()
    assert first["connected"] is True

    clock[0] += server.GITHUB_STATUS_CACHE_TTL_SECONDS + 1
    attempts = []

    def unavailable(path):
        attempts.append(path)
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(server, "github_api_json", unavailable)
    stale = server.github_status()
    assert stale["connected"] is True
    assert stale["stale"] is True
    assert stale["repository"] == "example/repo"

    assert server._github_status_refresh_event.wait(timeout=2)
    assert server._github_status_refresh_error == "URLError"
    assert len(attempts) == 1

    clock[0] += 60
    still_stale = server.github_status()
    assert still_stale["connected"] is True
    assert still_stale["stale"] is True
    assert len(attempts) == 1

    clock[0] += server.GITHUB_STATUS_REFRESH_ERROR_BACKOFF_SECONDS
    retry = server.github_status()
    assert retry["stale"] is True
    assert server._github_status_refresh_event.wait(timeout=2)
    assert len(attempts) == 2

def test_github_status_marks_cache_expired_after_max_stale(monkeypatch):
    reset_cache(monkeypatch)
    clock = [100.0]
    monkeypatch.setattr(server, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    monkeypatch.setattr(server, "github_api_json", fake_github_api)

    server.github_status()
    assert server._github_status_refresh_event.wait(timeout=2)

    clock[0] += server.GITHUB_STATUS_MAX_STALE_SECONDS + 1
    expired = server.github_status()
    assert expired["connected"] is False
    assert expired["stale"] is True
    assert expired["error"] == "cache_expired"

    assert server._github_status_refresh_event.wait(timeout=2)
    refreshed = server.github_status()
    assert refreshed["connected"] is True
    assert refreshed["stale"] is False
