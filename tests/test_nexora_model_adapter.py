import os
import unittest
from unittest.mock import patch

from nexora_model_adapter import ModelConfigurationError, _settings


class ModelAdapterConfigTests(unittest.TestCase):
    def test_requires_all_environment_values(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ModelConfigurationError):
                _settings()

    def test_normalizes_base_url(self):
        values = {
            "NEXORA_BASE_URL": "https://api.example.test/v1/",
            "NEXORA_API_KEY": "test-key",
            "NEXORA_MODEL": "test-model",
        }
        with patch.dict(os.environ, values, clear=True):
            self.assertEqual(
                _settings(),
                ("https://api.example.test/v1", "test-key", "test-model"),
            )

    def test_rejects_invalid_base_url_scheme(self):
        values = {
            "NEXORA_BASE_URL": "file:///tmp",
            "NEXORA_API_KEY": "test-key",
            "NEXORA_MODEL": "test-model",
        }
        with patch.dict(os.environ, values, clear=True):
            with self.assertRaises(ModelConfigurationError):
                _settings()


if __name__ == "__main__":
    unittest.main()
