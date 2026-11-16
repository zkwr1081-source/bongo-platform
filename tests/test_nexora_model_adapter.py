import os
import unittest
from unittest.mock import patch

from nexora_model_adapter import ModelConfigurationError, _settings


class ModelAdapterConfigTests(unittest.TestCase):
    def test_local_qwen_does_not_require_api_key(self):
        values = {
            "NEXORA_BASE_URL": "http://127.0.0.1:8090/v1",
            "NEXORA_MODEL": "qwen2.5-3b",
        }
        with patch.dict(os.environ, values, clear=True):
            self.assertEqual(_settings(), ("http://127.0.0.1:8090/v1", "", "qwen2.5-3b"))

    def test_localhost_does_not_require_api_key(self):
        values = {"NEXORA_BASE_URL": "http://localhost:8090/v1", "NEXORA_MODEL": "qwen"}
        with patch.dict(os.environ, values, clear=True):
            self.assertEqual(_settings()[1], "")

    def test_remote_requires_key_and_https(self):
        with patch.dict(os.environ, {"NEXORA_BASE_URL":"https://api.example.com/v1","NEXORA_MODEL":"m"}, clear=True):
            with self.assertRaises(ModelConfigurationError):
                _settings()

    def test_remote_http_is_rejected(self):
        values = {"NEXORA_BASE_URL":"http://api.example.com/v1","NEXORA_API_KEY":"k","NEXORA_MODEL":"m"}
        with patch.dict(os.environ, values, clear=True):
            with self.assertRaises(ModelConfigurationError):
                _settings()

    def test_remote_https_with_key_is_allowed(self):
        values = {"NEXORA_BASE_URL":"https://api.example.com/v1","NEXORA_API_KEY":"k","NEXORA_MODEL":"m"}
        with patch.dict(os.environ, values, clear=True):
            self.assertEqual(_settings(), ("https://api.example.com/v1", "k", "m"))

    def test_rejects_url_credentials(self):
        values = {"NEXORA_BASE_URL":"https://user:pass@api.example.com/v1","NEXORA_API_KEY":"k","NEXORA_MODEL":"m"}
        with patch.dict(os.environ, values, clear=True):
            with self.assertRaises(ModelConfigurationError):
                _settings()

    def test_requires_url_and_model(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ModelConfigurationError):
                _settings()


if __name__ == "__main__":
    unittest.main()
