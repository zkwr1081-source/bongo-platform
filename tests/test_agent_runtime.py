import tempfile
import unittest
from pathlib import Path

from bongo_agents.runtime import Agent, AgentRuntime, MockProvider


class AgentRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runtime = AgentRuntime(Path(self.tmp.name) / "tasks.sqlite3",
                                    provider=MockProvider(), max_workers=2)

    def tearDown(self):
        self.tmp.cleanup()

    def test_registry_has_unique_agents(self):
        self.assertGreaterEqual(len(self.runtime.agents), 5)
        self.assertEqual(len(self.runtime.agents), len(set(self.runtime.agents)))

    def test_registry_accepts_generator(self):
        agents = (agent for agent in (
            Agent("one", "One", "test", "prompt"),
            Agent("two", "Two", "test", "prompt"),
        ))
        runtime = AgentRuntime(Path(self.tmp.name) / "generator.sqlite3", agents=agents)
        self.assertEqual(set(runtime.agents), {"one", "two"})

    def test_registry_rejects_duplicate_ids_from_generator(self):
        duplicate_agents = (
            agent for agent in (
                Agent("same", "First", "test", "prompt"),
                Agent("same", "Second", "test", "prompt"),
            )
        )
        with self.assertRaises(ValueError):
            AgentRuntime(Path(self.tmp.name) / "duplicate.sqlite3", agents=duplicate_agents)

    def test_submit_and_execute(self):
        task = self.runtime.submit("scout-01", "Find unmet needs in water access")
        result = self.runtime.run_batch()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, "completed")
        stored = self.runtime.get_task(task.task_id)
        self.assertEqual(stored["status"], "completed")
        self.assertIn("MOCK RESULT", stored["output"])

    def test_unknown_agent_rejected(self):
        with self.assertRaises(KeyError):
            self.runtime.submit("missing-agent", "Do work")

    def test_empty_instruction_rejected(self):
        with self.assertRaises(ValueError):
            self.runtime.submit("scout-01", "  ")

    def test_batch_limit_is_bounded(self):
        runtime = AgentRuntime(Path(self.tmp.name) / "limited.sqlite3",
                               provider=MockProvider(), max_tasks_per_batch=2)
        for _ in range(3):
            runtime.submit("scout-01", "task")
        self.assertEqual(len(runtime.run_batch()), 2)
        self.assertEqual(len(runtime.run_batch()), 1)


if __name__ == "__main__":
    unittest.main()
