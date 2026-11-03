"""Unit tests for the NEXORA connector registry."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from nexora_connector_registry import CONNECTORS, list_connectors


class ConnectorRegistryTests(unittest.TestCase):
    def test_registry_has_unique_ids(self) -> None:
        ids = [connector.connector_id for connector in CONNECTORS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_model_provider_reports_missing_configuration(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = list_connectors()
        model = next(item for item in result["connectors"] if item["id"] == "model-provider")
        self.assertFalse(model["configured"])
        self.assertEqual(model["status"], "needs_configuration")
        self.assertEqual(
            model["missing_environment"],
            ["NEXORA_BASE_URL", "NEXORA_API_KEY", "NEXORA_MODEL"],
        )

    def test_model_provider_reports_configured_without_leaking_key(self) -> None:
        env = {
            "NEXORA_BASE_URL": "https://example.invalid/v1",
            "NEXORA_API_KEY": "test-secret-value",
            "NEXORA_MODEL": "test-model",
        }
        with patch.dict(os.environ, env, clear=True):
            result = list_connectors()
        model = next(item for item in result["connectors"] if item["id"] == "model-provider")
        self.assertTrue(model["configured"])
        self.assertNotIn("test-secret-value", repr(result))
        self.assertEqual(model["missing_environment"], [])

    def test_github_connector_is_read_only(self) -> None:
        result = list_connectors()
        github = next(item for item in result["connectors"] if item["id"] == "github-rest")
        self.assertEqual(github["access_mode"], "public-read-only")
        self.assertTrue(github["configured"])


if __name__ == "__main__":
    unittest.main()
