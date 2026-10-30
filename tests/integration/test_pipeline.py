import http.client
import json
import threading
from http.server import ThreadingHTTPServer

from core.engine.engine import NexoraEngine
from nexora.api.server import Handler


class Agent:
    def run(self, context):
        return {"task": context.request}


def test_pipeline():
    engine = NexoraEngine()
    engine.register_agent("TEST", Agent())
    result = engine.run("1", "hello")
    assert result.status == "completed"


def _request_api(method, path, body=None, headers=None):
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    try:
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        payload = json.loads(response.read())
        return response.status, response.getheader("Allow"), payload
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_task_endpoint_rejects_get():
    status, allowed, payload = _request_api("GET", "/task?goal=hello")
    assert status == 405
    assert allowed == "POST"
    assert payload["error"] == "method_not_allowed"


def test_task_endpoint_requires_json():
    status, _, payload = _request_api(
        "POST",
        "/task",
        body="goal=hello",
        headers={"Content-Type": "text/plain"},
    )
    assert status == 415
    assert payload["error"] == "application_json_required"


def test_task_endpoint_rejects_missing_goal():
    status, _, payload = _request_api(
        "POST",
        "/task",
        body=json.dumps({}),
        headers={"Content-Type": "application/json"},
    )
    assert status == 400
    assert payload["error"] == "goal_required"
