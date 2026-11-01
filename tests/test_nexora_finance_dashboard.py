import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from nexora_finance_dashboard import create_app
from nexora_finance_observer import FinanceStore, Settings


class FinanceDashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "dashboard-test.db"
        self.store = FinanceStore(self.db_path)
        self.store.initialize()
        self.settings = Settings(workers=2, poll_seconds=300)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_status_and_empty_lists(self):
        app = create_app(self.store, self.settings, token="", auto_start=False)
        with TestClient(app) as client:
            status = client.get("/api/status")
            self.assertEqual(status.status_code, 200)
            self.assertEqual(status.json()["observer_state"], "STOPPED")
            self.assertFalse(status.json()["financial_actions_enabled"])
            self.assertEqual(client.get("/api/observations").json()["items"], [])
            self.assertEqual(client.get("/api/revenue-allocations").json()["items"], [])

    def test_dashboard_html_is_available(self):
        app = create_app(self.store, self.settings, token="", auto_start=False)
        with TestClient(app) as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("NEXORA", response.text)
            self.assertIn("تشغيل", response.text)

    def test_api_requires_configured_bearer_token(self):
        app = create_app(self.store, self.settings, token="t" * 32, auto_start=False)
        with TestClient(app) as client:
            self.assertEqual(client.get("/api/status").status_code, 401)
            response = client.get(
                "/api/status",
                headers={"Authorization": "Bearer " + "t" * 32},
            )
            self.assertEqual(response.status_code, 200)

    def test_observation_rows_are_read_from_sqlite(self):
        self.store.save_observation({
            "observed_at": "2026-11-01T05:00:00+00:00",
            "market_cap_change_24h_pct": 1.25,
            "observed_signal": "POSITIVE_MOMENTUM",
            "total_market_cap_usd": 123456.0,
            "total_volume_24h_usd": 7890.0,
            "source": "https://api.coingecko.com/api/v3/global",
        })
        app = create_app(self.store, self.settings, token="", auto_start=False)
        with TestClient(app) as client:
            payload = client.get("/api/observations").json()
            self.assertEqual(len(payload["items"]), 1)
            self.assertEqual(payload["items"][0]["observed_signal"], "POSITIVE_MOMENTUM")

    def test_start_and_stop_control_only_observer_task(self):
        async def idle_run(observer):
            await observer._stop.wait()

        app = create_app(self.store, self.settings, token="", auto_start=False)
        with patch("nexora_finance_dashboard.NexoraFinanceObserver.run", new=idle_run):
            with TestClient(app) as client:
                started = client.post("/api/observer/start")
                self.assertEqual(started.status_code, 200)
                self.assertEqual(started.json()["status"], "STARTING")
                self.assertEqual(client.get("/api/status").json()["observer_state"], "RUNNING")
                stopped = client.post("/api/observer/stop")
                self.assertEqual(stopped.status_code, 200)
                self.assertEqual(stopped.json()["status"], "STOPPED")
                self.assertEqual(client.get("/api/status").json()["observer_state"], "STOPPED")


if __name__ == "__main__":
    unittest.main()
