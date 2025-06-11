#!/usr/bin/env python3
"""
Simple script to test Grafana connection using token auth.
Run this script to verify your Grafana credentials are working correctly.
"""
import os
import sys
from dotenv import load_dotenv
from grafana_client import GrafanaApi
from grafana_client.client import TokenAuth


def test_grafana_connection():
    """Test connection to Grafana using credentials from .env file."""
    # Load environment variables
    load_dotenv()
    
    # Get Grafana credentials
    grafana_url = os.getenv("GRAFANA_URL")
    grafana_token = os.getenv("GRAFANA_API_TOKEN")
    
    # Check if credentials are available
    if not grafana_url or not grafana_token:
        print("Error: Grafana credentials not found.")
        print("Make sure you have a .env file with GRAFANA_URL and GRAFANA_API_TOKEN defined.")
        print("You can copy .env.example to .env and edit it with your credentials.")
        sys.exit(1)
    
    try:
        print(f"Connecting to Grafana at {grafana_url}...")
        
        # Initialize Grafana client with token auth
        grafana = GrafanaApi.from_url(
            url=grafana_url,
            credential=TokenAuth(token=grafana_token)
        )
        
        # Check Grafana health
        health = grafana.health.check()
        print(f"✅ Connected successfully to Grafana {health.get('version', 'unknown')}")
        print(f"   Database status: {health.get('database', 'unknown')}")
        
        # Get organization info
        org = grafana.organization.get_current_organization()
        print(f"   Organization: {org.get('name')} (ID: {org.get('id')})")
        
        # List dashboards
        dashboard = grafana.dashboard.get_dashboard("90ffba76-fcf8-4094-8b41-dd7055f7b9d7")
        print(f"   Found {dashboard} dashboard")

        # List datasources
        datasources = grafana.datasource.list_datasources()
        print(f"   Found {len(datasources)} data sources")

        print("\nConnection test successful!")
        return True
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        print("\nPossible issues:")
        print(" - Invalid Grafana URL")
        print(" - Invalid API token")
        print(" - Network connectivity issues")
        print(" - Insufficient permissions for the API token")
        return False


# create a test dashboard
def create_test_dashboard():
    load_dotenv()

    # Get Grafana credentials
    grafana_url = os.getenv("GRAFANA_URL")
    grafana_token = os.getenv("GRAFANA_API_TOKEN")

    # Check if credentials are available
    if not grafana_url or not grafana_token:
        print("Error: Grafana credentials not found.")
        print("Make sure you have a .env file with GRAFANA_URL and GRAFANA_API_TOKEN defined.")
        print("You can copy .env.example to .env and edit it with your credentials.")
        sys.exit(1)

    try:
        print(f"Connecting to Grafana at {grafana_url}...")

        # Initialize Grafana client with token auth
        grafana = GrafanaApi.from_url(
            url=grafana_url,
            credential=TokenAuth(token=grafana_token)
        )

        """Create a test dashboard in Grafana."""
        # load from json file
        import json
        with open("test_dashboard.json", "r") as f:
            dashboard = json.load(f)

        print(grafana.dashboard.update_dashboard(dashboard))
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        print("\nPossible issues:")
        print(" - Invalid Grafana URL")
        print(" - Invalid API token")
        print(" - Network connectivity issues")
        print(" - Insufficient permissions for the API token")


if __name__ == "__main__":
    # create_test_dashboard()
    success = test_grafana_connection()
    #
    # sys.exit(0 if success else 1)