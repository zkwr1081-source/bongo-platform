from collections import Counter
import time

class Metrics:
    def __init__(self):
        self.counters = Counter()
        self.started = time.time()

    def inc(self, name, value=1):
        self.counters[name] += value

    def snapshot(self):
        return {
            "uptime": round(time.time() - self.started, 3),
            "counters": dict(self.counters)
        }
