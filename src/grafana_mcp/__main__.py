#!/usr/bin/env python3
"""Grafana MCP server entry point.

This module runs the ``FastMCP`` server exposing the MCP API at ``/mcp``.
Executing ``python -m grafana_mcp`` starts the built-in HTTP server.
"""

from grafana_mcp.mcp_server import mcp

if __name__ == "__main__":
    """Main entry point for the application."""
    # print("Starting Grafana MCP server...")

    mcp.run(transport="sse", host="0.0.0.0")
