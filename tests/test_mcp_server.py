"""Tests for the grafana_mcp.mcp_server module."""

import importlib
import unittest


class TestMCPServer(unittest.TestCase):
    """Tests for the grafana_mcp.mcp_server module."""

    def test_import(self):
        """Test that the mcp_server module can be imported."""
        try:
            importlib.import_module("grafana_mcp.mcp_server")
        except ImportError as exc:
            self.fail(f"Failed to import grafana_mcp.mcp_server: {exc}")

    def test_mcp_instance(self):
        """Test that the mcp instance is defined."""
        module = importlib.import_module("grafana_mcp.mcp_server")
        self.assertIsNotNone(module.mcp)


if __name__ == "__main__":
    unittest.main()
