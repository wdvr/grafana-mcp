#!/usr/bin/env python3
"""Grafana MCP server entry point.

This module exposes a Starlette ``app`` that mounts the MCP server at the
``/mcp`` route. Executing ``python -m grafana_mcp`` runs the app using
``uvicorn``.
"""

from starlette.applications import Starlette
import uvicorn
import os

from grafana_mcp.mcp_server import mcp

# Starlette application with the MCP server mounted at /mcp
app = Starlette()
app.mount("/mcp", mcp.streamable_http_app())


def main() -> None:
    """Run the Starlette application using ``uvicorn``."""
    print("Starting Grafana MCP server on http://0.0.0.0:8000/mcp ...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))


if __name__ == "__main__":
    main()
