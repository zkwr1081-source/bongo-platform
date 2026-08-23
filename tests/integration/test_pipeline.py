from core.engine.engine import NexoraEngine

class Agent:
    def run(self, context):
        return {"task": context.request}

def test_pipeline():
    engine = NexoraEngine()
    engine.register_agent("TEST", Agent())
    result = engine.run("1", "hello")
    assert result.status == "completed"
