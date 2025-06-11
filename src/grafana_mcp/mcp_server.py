"""
Grafana MCP server implementation
"""

from grafana_client.client import TokenAuth
from grafana_client import GrafanaApi
import os
import requests
import json
import uuid
from typing import Dict, Any, Optional

from fastmcp import FastMCP

from importlib import resources

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


def make_dashboard_public(dashboard_uid: str) -> Dict[str, Any]:
    """Makes a dashboard public using the Grafana HTTP API.

    Args:
        dashboard_uid (str): The UID of the dashboard to make public.

    Returns:
        Dict[str, Any]: The API response containing public dashboard details.
    """
    grafana_url = os.getenv("GRAFANA_URL", "http://pytorchci.grafana.net")
    api_key = os.getenv("GRAFANA_API_TOKEN")

    if not api_key:
        raise ValueError("GRAFANA_API_TOKEN environment variable is not set.")

    endpoint = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}/public-dashboards/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Create public dashboard payload
    payload = {
        "isEnabled": True,
        "timeSelectionEnabled": True,
        "share": "public"
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors

    return response.json()


def get_public_dashboard_url(dashboard_uid: str) -> Optional[str]:
    """Get the public URL for a shared dashboard.

    Args:
        dashboard_uid (str): The UID of the dashboard.

    Returns:
        Optional[str]: The public URL for the dashboard, or None if not found or not public.
    """
    grafana_url = os.getenv("GRAFANA_URL", "https://pytorchci.grafana.net")
    api_key = os.getenv("GRAFANA_API_TOKEN")

    if not api_key:
        raise ValueError("GRAFANA_API_TOKEN environment variable is not set.")

    endpoint = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}/public-dashboards/"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 404:
        return None

    response.raise_for_status()

    data = response.json()
    if not data:
        return None

    # Extract public dashboard access URL
    # Format will depend on specific Grafana setup, adjust as needed
    public_dashboard_uid = data.get("uid")
    access_token = data.get("accessToken")

    if public_dashboard_uid and access_token:
        return f"{grafana_url}/public-dashboards/{access_token}"

    return None


@mcp.tool()
def create_time_series_dashboard(
    title: str,
    raw_sql: str,
    description: str = None,
    panel_title: str = None,
    make_public: bool = True
) -> Dict[str, Any]:
    """    Create a Grafana dashboard (ClickHouse data-source) with a single
    **Time-series** panel.

    -------------------- SQL CONTRACT (Grafana ClickHouse v4+) --------------------
    • The query should return at least a time column and one numeric metric column. The time column must be a DateTime (or DateTime64) type so Grafana recognizes it as the timestamp. For instance: `SELECT timestamp AS time, count() AS total ...`.

    • Always include a time filter macro to respect the dashboard’s time range.
        For tables with a single DateTime timestamp column, use `WHERE $__timeFilter(<TimeColumn_OR_Expression>)`. If the table has separate date and datetime columns, use `WHERE $__dateTimeFilter(<DateColumn>, <DateTimeColumn>)` to ensure both partition and time are filtered.


    • Follow with one or more numeric columns.  Each column’s alias becomes the
      series name.  If you need multiple lines from a single numeric column,
      insert a string label between `time` and the metric.

    • Finish with:

          GROUP BY time
          ORDER BY time

      Order results by the time column ascending (oldest first) for proper chronological rendering, unless the data source or Grafana does this automatically.

    • **No trailing semicolon** — Grafana appends fragments internally.

    • Other clickhouse/grafana macros and variables are not supported, **avoid them**.

    Example minimal queries:

        SELECT
          created_at AS time,
          avg(load_1m) AS "Load-1m"
        FROM system.metrics
        WHERE $__timeFilter(created_at)
        GROUP BY time
        ORDER BY time

        SELECT
            toStartOfInterval(event_time, INTERVAL 1 minute) as time,
            count() as value
        FROM events
        WHERE $__timeFilter(event_time)
        GROUP BY time
        ORDER BY time


    Args:
        title (str): Title of the dashboard.
        description (str): Description of the dashboard.
        panel_title (str): Title of the panel.
        raw_sql (str): Raw SQL query to be used in the panel. Make sure the query is adapted to use grafana magic strings for date ranges, as well as has the correct timeseries fields.
        make_public (bool): Whether to make the dashboard public. Defaults to True.

    Returns:
        JSON response from the Grafana API with additional public URL if requested.
    """
    client = get_grafana_client()

    with resources.files("grafana_mcp").joinpath("dashboard.json").open("r") as f:
        dashboard = json.load(f)

    dashboard_uid = str(uuid.uuid4())
    dashboard["dashboard"]["uid"] = dashboard_uid
    dashboard["dashboard"]["title"] = title
    dashboard["dashboard"]["panels"][0]["targets"][0]["rawSql"] = raw_sql

    # datasource
    dashboard["dashboard"]["panels"][0]["targets"][0]["datasource"]["uid"] = os.getenv(
        "GRAFANA_DATASOURCE_UID", "Clickhouse")
    dashboard["dashboard"]["panels"][0]["datasource"]["uid"] = os.getenv(
        "GRAFANA_DATASOURCE_UID", "Clickhouse")

    # set the panel title
    dashboard["dashboard"]["panels"][0]["title"] = title
    # set the panel description
    dashboard["dashboard"]["panels"][0]["description"] = description if description else ""
    # set the dashboard description
    dashboard["dashboard"]["description"] = description if description else ""
    res = client.dashboard.update_dashboard(dashboard)

    # If requested, make the dashboard public
    if make_public:
        try:
            make_dashboard_public(dashboard_uid)
            public_url = get_public_dashboard_url(dashboard_uid)

            # Add public URL to the response
            if public_url:
                res["public_url"] = public_url

        except Exception as e:
            # Log the error but don't fail the entire operation
            print(f"Failed to make dashboard public: {e}")

    return res


# Run the server if executed directly
if __name__ == "__main__":
    mcp.run(transport="sse")
