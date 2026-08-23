from core.agents.analyst import AnalystAgent

class Context:
    task_id = "test"
    request = "حلل المشروع وابحث عن الملفات"

def test_analyst():
    result = AnalystAgent().run(Context())
    assert result["agent"] == "ANALYST"
    assert result["requires_tools"] is True
