import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from web.agent_api import AgentHandler


class TestAgentApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), AgentHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get(self, path):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=3)
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read()
        headers = dict(response.getheaders())
        connection.close()
        return response.status, headers, json.loads(body)

    def test_health_endpoint(self):
        status, headers, payload = self.get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "ok", "service": "nexora-agent-api"})
        self.assertEqual(headers.get("Cache-Control"), "no-store")
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")

    def test_agents_not_fabricated_when_registry_missing(self):
        status, _, payload = self.get("/api/agents")
        self.assertEqual(status, 503)
        self.assertEqual(payload["error"], "agent_registry_not_configured")
        self.assertNotIn("agents", payload)

    def test_vault_balance_not_fabricated_when_provider_missing(self):
        status, _, payload = self.get("/api/vault/balance")
        self.assertEqual(status, 503)
        self.assertEqual(payload["error"], "vault_provider_not_configured")
        self.assertNotIn("vault_balance", payload)

    def test_unknown_route_returns_404(self):
        status, _, payload = self.get("/unknown")
        self.assertEqual(status, 404)
        self.assertEqual(payload["error"], "not_found")


if __name__ == "__main__":
    unittest.main()
