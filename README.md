# Grafana MCP

This project provides [MCP](https://modelcontextprotocol.io/) server for Grafana, including MCP tools to interact with Grafana dashboards, data sources, alerts, and more.

The package includes a dashboard template resource that is properly bundled with the package for use when installed.

## Usage

### Installation

1. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate
```

2. Install this package directly from GitHub using pip:

```bash
pip install -e git+https://github.com/your-username/grafana-mcp.git#egg=grafana_mcp
```

(Alternatively, you can install it locally with `pip install -e .`)

3. Configure Grafana authentication

Create a `.env` file with your Grafana URL and API token:

```bash
cp .env.example .env
```

Then edit the `.env` file to add your actual Grafana URL and API token:

```
GRAFANA_URL=http://your-grafana-server:3000
GRAFANA_API_TOKEN=your-api-token-here
```

You can generate an API token in Grafana by navigating to: Configuration → API Keys → New API key.

4. After installation, the MCP server can be run as:

```bash
python -m grafana_mcp
```

5. Add this MCP server to Claude Code:

```bash
claude mcp add-json grafana '{ "type": "stdio", "command": "python", "args": [ "-m", "grafana_mcp" ], "env": {} }'
```

Note: By default, MCP config applies only to the current directory. If you want to use it globally, add `--scope user` to the command above:

```bash
claude mcp add-json --scope user grafana '{ "type": "stdio", "command": "python", "args": [ "-m", "grafana_mcp" ], "env": {} }'
```

6. Run Claude Code as usual:

```bash
claude
```

## Development

### Development Installation

1. Clone the repository
2. Install in development mode:
   ```bash
   pip install -e .
   ```

The package uses Python's package resource management system to include the dashboard template. The dashboard.json file is stored in the src/grafana_mcp/ directory and is accessed using importlib.resources when the package is installed.

### Testing

Run unit tests:

```bash
python -m unittest discover tests
```

For testing with token authentication, ensure you have created a `.env` file with your Grafana credentials as described above. The test suite includes mocked tests that don't require an actual Grafana instance.

## Tools

The Grafana MCP provides the following tools:

### Available Tools

#### Dashboard Management
- `get_grafana_info()`: Get information about the connected Grafana instance including version and connection status
- `list_dashboards()`: List all dashboards from the connected Grafana instance
- `get_dashboard(uid)`: Get details about a specific dashboard by UID

#### Organization Management
- `get_organization()`: Get information about the current organization 

#### Data Source Management
- `list_datasources()`: List all available data sources

### Requirements

- `grafana-client`: Python client for Grafana API
- `python-dotenv`: For loading environment variables from `.env` file
- `mcp`: Model Context Protocol server implementation

## Authentication

This package uses token authentication with the Grafana API. To configure authentication:

1. In your Grafana instance, create an API key with appropriate permissions
2. Create a `.env` file with the following variables:
   ```
   GRAFANA_URL=http://your-grafana-url:3000
   GRAFANA_API_TOKEN=your-api-token-here
   ```
3. The MCP server will automatically load these credentials when started

More tools and features will be added in future versions.
