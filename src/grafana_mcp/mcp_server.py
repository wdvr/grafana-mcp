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
def create_time_series_dashboard(
    title: str,
    raw_sql: str,
) -> Dict[str, Any]:
    """Function to create a Grafana dashboard with a single time series panel.
    Clickhouse data source is used.

    Args:
        title (str): Title of the dashboard.
        raw_sql (str): Raw SQL query to be used in the panel.

    Returns:
        JSON response from the Grafana API.
    """
    client = get_grafana_client()

    import json
    with open("dashboard.json", "r") as f:
        dashboard = json.load(f)

    import uuid

    dashboard["dashboard"]["uid"] = str(uuid.uuid4())
    dashboard["dashboard"]["title"] = title
    dashboard["dashboard"]["panels"][0]["targets"][0]["rawSql"] = raw_sql
    # datasource
    dashboard["dashboard"]["panels"][0]["targets"][0]["datasource"]["uid"] = os.getenv("GRAFANA_DATASOURCE_UID", "Clickhouse")
    dashboard["dashboard"]["panels"][0]["datasource"]["uid"] = os.getenv("GRAFANA_DATASOURCE_UID", "Clickhouse")


    res = client.dashboard.update_dashboard(dashboard)

    return res


# Run the server if executed directly
if __name__ == "__main__":
    mcp.run()
