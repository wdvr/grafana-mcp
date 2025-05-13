"""
Grafana MCP server implementation
"""

from grafana_client.client import TokenAuth
from grafana_client import GrafanaApi
import os
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

import grafana_client
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Create an MCP server
mcp = FastMCP("Grafana MCP")


def get_grafana_client():
    """Creates a Grafana client instance.

    Returns:
        A Grafana client instance.
    """
    grafana_url = os.getenv("GRAFANA_URL", "http://pytorchci.grafana.net")
    api_key = os.getenv("GRAFANA_API_TOKEN")
    if not api_key:
        raise ValueError("GRAFANA_API_TOKEN environment variable is not set.")

    return GrafanaApi.from_url(
        url=grafana_url,
        credential=TokenAuth(token=api_key)
    )


@mcp.tool()
def get_grafana_info() -> str:
    """Returns basic information about using Grafana MCP tools.
    """
    return (
        """
        Grafana MCP provides tools for interacting with Grafana instances.
        
        This is a placeholder implementation. Actual tools will be implemented in future versions.
        
        Planned tools:
        - Dashboards management
        - Data sources management
        - Alerting management
        - User/Organization management
        - Documentation search
        """
    )


@mcp.tool()
def list_dashboards() -> Dict[str, Any]:
    """Placeholder function to list Grafana dashboards.

    Returns:
        A placeholder response indicating this is not yet implemented.
    """
    return {
        "status": "not_implemented",
        "message": "This feature is not yet implemented."
    }


@mcp.tool()
def get_dashboard(uid: str) -> Dict[str, Any]:
    """Placeholder function to get a specific Grafana dashboard.

    Args:
        uid: The UID of the dashboard to retrieve.

    Returns:
        A placeholder response indicating this is not yet implemented.
    """
    return {
        "status": "not_implemented",
        "message": "This feature is not yet implemented.",
        "requested_uid": uid
    }


@mcp.tool()
def create_dashboard(dashboard: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder function to create a new Grafana dashboard.

    Args:
        dashboard: The dashboard configuration to create.

    Returns:
        The HTTP status and a message indicating the result.
    """
    client = get_grafana_client()

    res = client.dashboard.update_dashboard(
        dashboard=dashboard, overwrite=True)

    return {
        "status": res.status_code,
        "message": res.text
    }


@mcp.tool()
def create_dummy_dashboard(uuid_suffix: str) -> Dict[str, Any]:
    """Placeholder function to create a new Grafana dashboard.

    Args:
        dashboard: The dashboard configuration to create.

    Returns:
        The HTTP status and a message indicating the result.
    """
    client = get_grafana_client()

    import json
    with open("tools/test_dashboard.json", "r") as f:
        dashboard = json.load(f)

    dashboard["meta"]["slug"] += uuid_suffix
    dashboard["meta"]["url"] += uuid_suffix

    dashboard["dashboard"]["uid"] += uuid_suffix
    dashboard["dashboard"]["title"] += uuid_suffix

    res = client.dashboard.update_dashboard(dashboard)

    return res


# Run the server if executed directly
if __name__ == "__main__":
    mcp.run()
