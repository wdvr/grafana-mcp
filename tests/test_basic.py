"""Basic tests for the grafana_mcp package."""

import unittest

class TestGrafanaMCP(unittest.TestCase):
    """Basic tests for the grafana_mcp package."""
    
    def test_import(self):
        """Test that the package can be imported."""
        try:
            import grafana_mcp
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import grafana_mcp")
            
    def test_version(self):
        """Test that the version is defined."""
        import grafana_mcp
        self.assertIsNotNone(grafana_mcp.__version__)
        
if __name__ == "__main__":
    unittest.main()