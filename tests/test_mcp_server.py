"""Tests for the grafana_mcp.mcp_server module."""

import unittest

class TestMCPServer(unittest.TestCase):
    """Tests for the grafana_mcp.mcp_server module."""
    
    def test_import(self):
        """Test that the mcp_server module can be imported."""
        try:
            from grafana_mcp import mcp_server
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import grafana_mcp.mcp_server")
    
    def test_mcp_instance(self):
        """Test that the mcp instance is defined."""
        from grafana_mcp.mcp_server import mcp
        self.assertIsNotNone(mcp)

    def test_app_mount(self):
        """Ensure the Starlette app mounts the MCP server at /mcp."""
        from grafana_mcp.__main__ import app
        paths = [getattr(r, "path", None) for r in app.routes]
        self.assertIn("/mcp", paths)
            
if __name__ == "__main__":
    unittest.main()