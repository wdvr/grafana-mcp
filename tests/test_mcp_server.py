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

    def test_main_uses_same_mcp(self):
        """Ensure the __main__ module references the same MCP instance."""
        from grafana_mcp.__main__ import mcp as main_mcp
        from grafana_mcp.mcp_server import mcp
        self.assertIs(main_mcp, mcp)
            
if __name__ == "__main__":
    unittest.main()