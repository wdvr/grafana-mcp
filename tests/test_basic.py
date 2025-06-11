"""Basic tests for the grafana_mcp package."""

import importlib
import unittest


class TestGrafanaMCP(unittest.TestCase):
    """Basic tests for the grafana_mcp package."""

    def test_import(self):
        """Test that the package can be imported."""
        try:
            importlib.import_module("grafana_mcp")
        except ImportError as exc:
            self.fail(f"Failed to import grafana_mcp: {exc}")

    def test_version(self):
        """Test that the version is defined."""
        mod = importlib.import_module("grafana_mcp")
        self.assertIsNotNone(mod.__version__)


if __name__ == "__main__":
    unittest.main()
