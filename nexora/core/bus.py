from collections import defaultdict
from threading import RLock

class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)
        self._lock = RLock()

    def subscribe(self, event, handler):
        with self._lock:
            self._handlers[event].append(handler)

    def publish(self, event, payload=None):
        payload = payload or {}
        with self._lock:
            handlers = list(self._handlers.get(event, []))

        results = []
        for handler in handlers:
            results.append(handler(payload))
        return results
