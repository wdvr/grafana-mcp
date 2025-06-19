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


def get_grafana_folders(parent_uid: str = None) -> Dict[str, Any]:
    """Get all folders from Grafana.

    Returns:
        Dict[str, Any]: Dictionary containing folder information with folder names as keys and folder data as values.
    """
    client = get_grafana_client()
    folders = client.folder.get_all_folders(parent_uid=parent_uid)

    return {folder['title']: folder for folder in folders}


@mcp.tool()
def get_or_create_folder(folder_name: str, parent_uid: str = None) -> int:
    """Get folder ID by name, or create the folder if it doesn't exist.

    Args:
        folder_name (str): Name of the folder to get or create.

    Returns:
        int: The folder ID. Returns None for root folder (empty folder_name).
    """
    return get_or_create_folder_internal(folder_name, parent_uid)


def get_or_create_folder_internal(folder_name: str, parent_uid: Optional[str] = None) -> Optional[int]:
    client = get_grafana_client()
    folders = get_grafana_folders(parent_uid=parent_uid)

    folder_segments = [seg.strip() for seg in folder_name.split("/") if seg.strip()]
    folder_id = None

    for segment in folder_segments:
        folders = get_grafana_folders(parent_uid=parent_uid)
        if segment in folders:
            parent_uid = folders[segment]['uid']
            folder_id = folders[segment]['id']
        else:
            result = client.folder.create_folder(title=segment, parent_uid=parent_uid)
            parent_uid = result['uid']
            folder_id = result['id']

    return folder_id


def validate_grafana_query(raw_sql: str, time_from: str = "now-30d", time_to: str = "now", datasource_uid: str = None) -> Dict[str, Any]:
    """Validate a Grafana query by executing it against the datasource.

    Args:
        raw_sql (str): The SQL query to validate.
        time_from (str): Start time for the query range. Defaults to "now-30d".
        time_to (str): End time for the query range. Defaults to "now".
        datasource_uid (str): The datasource UID. Uses environment default if None.

    Returns:
        Dict[str, Any]: Dictionary with 'is_valid', 'error', and optional 'result' keys.
    """
    grafana_url = os.getenv("GRAFANA_URL", "http://pytorchci.grafana.net")
    api_key = os.getenv("GRAFANA_API_TOKEN")

    if not api_key:
        return {"is_valid": False, "error": "GRAFANA_API_TOKEN environment variable is not set."}

    if not datasource_uid:
        datasource_uid = os.getenv("GRAFANA_DATASOURCE_UID", "Clickhouse")

    try:
        query_endpoint = f"{grafana_url}/api/ds/query"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Prepare query payload
        query_payload = {
            "queries": [{
                "refId": "A",
                "datasource": {
                    "type": "grafana-clickhouse-datasource",
                    "uid": datasource_uid
                },
                "rawSql": raw_sql,
                "format": 0
            }],
            "range": {
                "from": time_from,
                "to": time_to
            },
            "from": time_from,
            "to": time_to
        }

        response = requests.post(query_endpoint, headers=headers, json=query_payload)

        if response.status_code != 200:
            return {
                "is_valid": False,
                "error": f"Query failed with status {response.status_code}: {response.text}"
            }

        query_result = response.json()
        return {"is_valid": True, "result": query_result}

    except Exception as e:
        return {"is_valid": False, "error": str(e)}


def check_dashboard_has_data(dashboard_uid: str) -> Dict[str, Any]:
    """Check if a dashboard has any data for the default time range.

    Args:
        dashboard_uid (str): The UID of the dashboard to check.

    Returns:
        Dict[str, Any]: Dictionary containing check results with 'has_data', 'error', and 'details' keys.
    """
    grafana_url = os.getenv("GRAFANA_URL", "http://pytorchci.grafana.net")
    api_key = os.getenv("GRAFANA_API_TOKEN")

    if not api_key:
        return {"has_data": False, "error": "GRAFANA_API_TOKEN environment variable is not set."}

    try:
        # Get dashboard data
        client = get_grafana_client()
        dashboard_response = client.dashboard.get_dashboard(dashboard_uid)
        dashboard = dashboard_response['dashboard']

        # Extract time range (default from dashboard.json is "now-30d" to "now")
        time_from = dashboard.get('time', {}).get('from', 'now-30d')
        time_to = dashboard.get('time', {}).get('to', 'now')

        # Get the first panel's query
        if not dashboard.get('panels') or len(dashboard['panels']) == 0:
            return {"has_data": False, "error": "No panels found in dashboard"}

        panel = dashboard['panels'][0]
        if not panel.get('targets') or len(panel['targets']) == 0:
            return {"has_data": False, "error": "No queries found in panel"}

        target = panel['targets'][0]
        raw_sql = target.get('rawSql', '')

        if not raw_sql:
            return {"has_data": False, "error": "No SQL query found"}

        datasource_uid = target.get('datasource', {}).get('uid', os.getenv("GRAFANA_DATASOURCE_UID", "Clickhouse"))

        # Use extracted validation method
        validation_result = validate_grafana_query(raw_sql, time_from, time_to, datasource_uid)
        if not validation_result["is_valid"]:
            return {
                "has_data": False,
                "error": validation_result["error"]
            }

        query_result = validation_result["result"]

        # Check if there's any data in the results
        has_data = False
        total_datapoints = 0

        if 'results' in query_result:
            for result_data in query_result['results'].values():
                if 'frames' in result_data:
                    for frame in result_data['frames']:
                        if 'data' in frame and 'values' in frame['data']:
                            for values in frame['data']['values']:
                                if values and len(values) > 0:
                                    has_data = True
                                    total_datapoints += len(values)

        return {
            "has_data": has_data,
            "total_datapoints": total_datapoints,
            "time_range": {"from": time_from, "to": time_to},
            "query": raw_sql
        }

    except Exception as e:
        return {"has_data": False, "error": str(e)}


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
    make_public: bool = True,
    folder: str = ""
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
        folder (str): Name of the folder to create the dashboard in. If empty, uses mcp-generated folder. Defaults to empty string.

    Returns:
        JSON response from the Grafana API with additional public URL if requested.
    """
    # Validate the query before creating the dashboard
    datasource_uid = os.getenv("GRAFANA_DATASOURCE_UID", "Clickhouse")
    validation_result = validate_grafana_query(raw_sql, datasource_uid=datasource_uid)

    if not validation_result["is_valid"]:
        return {
            "error": f"Query validation failed: {validation_result['error']}",
            "dashboard": None
        }

    client = get_grafana_client()

    with resources.files("grafana_mcp").joinpath("dashboard.json").open("r") as f:
        dashboard = json.load(f)

    # Get or create folder and set folderId
    folder_id = get_or_create_folder_internal(folder)
    dashboard["folderId"] = folder_id

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
    dashboard["dashboard"]["panels"][0]["title"] = panel_title if panel_title else title
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


@mcp.tool()
def check_dashboard_data(dashboard_uid: str) -> Dict[str, Any]:
    """Check if a dashboard has any data for its default time range.

    Args:
        dashboard_uid (str): The UID of the dashboard to check.

    Returns:
        Dict[str, Any]: Dictionary containing check results with 'has_data', 'error', and 'details' keys.
    """
    return check_dashboard_has_data(dashboard_uid)


# Run the server if executed directly
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0")
