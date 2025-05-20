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
from mcp.server.fastmcp import FastMCP
import requests
import json

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
    grafana_url = os.getenv("GRAFANA_URL", "http://pytorchci.grafana.net")
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
    make_public: bool = True
) -> Dict[str, Any]:
    """Function to create a Grafana dashboard with a single time series panel.
    Clickhouse data source is used.


    Args:
        title (str): Title of the dashboard.
        raw_sql (str): Raw SQL query to be used in the panel. Make sure the query is adapted to use grafana magic strings for date ranges, as well as has the correct timeseries fields.
                        For example: SELECT toUnixTimestamp(toStartOfInterval(event_time, INTERVAL 1 minute)) as time_sec, count() as value FROM events WHERE event_time >= $__timeFrom() AND event_time <= $__timeTo() GROUP BY time_sec ORDER BY time_sec
        make_public (bool): Whether to make the dashboard public. Defaults to True.

    Returns:
        JSON response from the Grafana API with additional public URL if requested.
    """
    client = get_grafana_client()

    with open("dashboard.json", "r") as f:
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

    res = client.dashboard.update_dashboard(dashboard)

    # If requested, make the dashboard public
    if make_public:
        try:
            public_dashboard = make_dashboard_public(dashboard_uid)
            public_url = get_public_dashboard_url(dashboard_uid)

            # Add public URL to the response
            if public_url:
                res["public_url"] = public_url

        except Exception as e:
            # Log the error but don't fail the entire operation
            print(f"Failed to make dashboard public: {e}")

    return res


def make_dashboard_public(grafana_url: str, api_key: str, dashboard_uid: str) -> str:
    """Makes a dashboard public using the public dashboards API and returns the public URL.

    Args:
        grafana_url (str): The Grafana URL.
        api_key (str): The Grafana API key.
        dashboard_uid (str): The dashboard UID.

    Returns:
        str: The public URL for the dashboard, or None if the operation failed.
    """
    # Set up headers for API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        # Create a public dashboard using the public dashboards API
        public_dashboard_url = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}/public-dashboards/"

        # Simple empty POST request to create a public dashboard
        response = requests.post(public_dashboard_url,
                                 headers=headers, json={})

        print(f"Public dashboard API response status: {response.status_code}")
        print(f"Public dashboard API response: {response.text}")

        if response.status_code >= 200 and response.status_code < 300:
            result = response.json()
            # The response should contain the accessToken for the public URL
            access_token = result.get("accessToken")
            if access_token:
                public_url = f"{grafana_url}/public-dashboards/{access_token}"
                print(f"Created public dashboard at {public_url}")
                return public_url

        # Fallback to direct dashboard URL
        return f"{grafana_url}/d/{dashboard_uid}"
    except Exception as e:
        print(f"Error making dashboard public: {e}")
        return f"{grafana_url}/d/{dashboard_uid}"


# Run the server if executed directly
if __name__ == "__main__":
    mcp.run()
