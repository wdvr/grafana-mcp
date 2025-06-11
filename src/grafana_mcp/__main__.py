#!/usr/bin/env python3
"""
Grafana MCP server entry point
"""

from grafana_mcp.mcp_server import mcp


def main():
    """Main entry point for the application."""
    print("Starting Grafana MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
