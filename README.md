# Grafana MCP

This project provides [MCP](https://modelcontextprotocol.io/) server for Grafana, including MCP tools to interact with Grafana dashboards, data sources, alerts, and more.

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

3. After installation, the MCP server can be run as:

```bash
python -m grafana_mcp
```

4. Add this MCP server to Claude Code:

```bash
claude mcp add-json grafana '{ "type": "stdio", "command": "python", "args": [ "-m", "grafana_mcp" ], "env": {} }'
```

Note: By default, MCP config applies only to the current directory. If you want to use it globally, add `--scope user` to the command above:

```bash
claude mcp add-json --scope user grafana '{ "type": "stdio", "command": "python", "args": [ "-m", "grafana_mcp" ], "env": {} }'
```

5. Run Claude Code as usual:

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

### Testing

Run unit tests:

```bash
python -m unittest discover tests
```

## Tools

The Grafana MCP provides the following tools (placeholders):

More tools will be added in future versions.
