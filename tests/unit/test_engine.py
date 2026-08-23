from core.engine.engine import NexoraEngine

def test_engine_context():
    engine = NexoraEngine()
    context = engine.create_context("1", "hello")
    assert context.task_id == "1"
    assert context.request == "hello"
