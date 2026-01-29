# NREL-shift MCP Server

Model Context Protocol (MCP) server for NREL-shift distribution system modeling.

## Overview

This MCP server exposes NREL-shift's distribution system modeling capabilities as structured tools that can be used by AI assistants, IDEs, and other MCP clients. The server enables:

- Fetching building parcels from OpenStreetMap
- Clustering parcels for transformer placement
- Building and manipulating distribution graphs
- Managing graph state across sessions
- Querying graph structure and properties

## Installation

```bash
# Install with MCP support
pip install -e ".[mcp]"

# Or install MCP dependencies separately
pip install mcp pyyaml loguru
```

**Note:** There is currently a pydantic version dependency conflict between the MCP library (requires pydantic 2.12.x) and grid-data-models (requires pydantic 2.10.x). The MCP server code is ready but may require resolving this dependency conflict before full operation. You can:
1. Use a separate virtual environment for the MCP server
2. Wait for grid-data-models to update its pydantic dependency
3. Use the core NREL-shift library without MCP features

## Quick Start

### Running the Server

```bash
# Run with default configuration
shift-mcp-server

# Run with custom configuration
shift-mcp-server --config config.yaml
```

### Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "nrel-shift": {
      "command": "shift-mcp-server",
      "args": []
    }
  }
}
```

Or if using a virtual environment:

```json
{
  "mcpServers": {
    "nrel-shift": {
      "command": "/path/to/venv/bin/shift-mcp-server",
      "args": []
    }
  }
}
```

## Available Tools

### Data Acquisition

#### `fetch_parcels`
Fetch building parcels from OpenStreetMap.

**Parameters:**
- `location` (string | object): Address string or {longitude, latitude} coordinates
- `distance_meters` (number, optional): Search distance in meters (default: 500, max: 5000)

**Example:**
```json
{
  "location": "Fort Worth, TX",
  "distance_meters": 1000
}
```

#### `cluster_parcels`
Cluster parcels into groups using K-means for transformer placement.

**Parameters:**
- `parcels` (array): Array of parcel objects with geometry
- `num_clusters` (integer, optional): Number of clusters (default: 5)

**Example:**
```json
{
  "parcels": [...],
  "num_clusters": 10
}
```

### Graph Management

#### `create_graph`
Create a new empty distribution graph.

**Parameters:**
- `name` (string, optional): Optional name for the graph

**Returns:** Graph ID for use in subsequent operations

#### `add_node`
Add a node to a distribution graph.

**Parameters:**
- `graph_id` (string): Graph identifier
- `node_name` (string): Name for the node
- `longitude` (number): Longitude coordinate
- `latitude` (number): Latitude coordinate
- `assets` (array, optional): Asset types (e.g., ["DistributionLoad", "DistributionVoltageSource"])

**Asset Types:**
- `DistributionLoad`: Load/customer connection
- `DistributionSolar`: Solar generation
- `DistributionCapacitor`: Capacitor bank
- `DistributionVoltageSource`: Voltage source (substation)

#### `add_edge`
Add an edge (line or transformer) to a distribution graph.

**Parameters:**
- `graph_id` (string): Graph identifier
- `from_node` (string): Source node name
- `to_node` (string): Target node name
- `edge_name` (string): Name for the edge
- `edge_type` (string): "DistributionBranchBase" (line) or "DistributionTransformer"
- `length_meters` (number, optional): Edge length in meters (required for branches)

#### `query_graph`
Query information about a distribution graph.

**Parameters:**
- `graph_id` (string): Graph identifier
- `query_type` (string): Type of query
  - `summary`: Node/edge counts and vsource
  - `nodes`: List all nodes with locations
  - `edges`: List all edges with connections
  - `vsource`: Get voltage source node

#### `list_resources`
List available graphs and systems.

**Parameters:**
- `resource_type` (string): "all", "graphs", or "systems"

## Example Workflows

### Workflow 1: Fetch and Cluster Parcels

```
1. Use fetch_parcels with location="Denver, CO" and distance_meters=1000
2. Use cluster_parcels with the returned parcels and num_clusters=5
3. Review cluster centers for transformer placement
```

### Workflow 2: Build a Simple Graph

```
1. Use create_graph to create a new graph (returns graph_id)
2. Use add_node to add a voltage source node with assets=["DistributionVoltageSource"]
3. Use add_node to add load nodes at parcel locations with assets=["DistributionLoad"]
4. Use add_edge to connect source to loads with edge_type="DistributionBranchBase"
5. Use query_graph with query_type="summary" to verify the graph
```

### Workflow 3: Query Existing Graphs

```
1. Use list_resources with resource_type="graphs" to see available graphs
2. Use query_graph with specific graph_id and query_type="nodes" to see details
3. Use query_graph with query_type="edges" to see connections
```

## Configuration

Create a `config.yaml` file:

```yaml
server_name: "nrel-shift-mcp-server"
server_version: "0.1.0"
default_search_distance_m: 500.0
max_search_distance_m: 5000.0
default_cluster_count: 5
state_storage_dir: null  # or path like "./mcp_state"
enable_visualization: true
log_level: "INFO"
max_concurrent_fetches: 3
```

## State Management

The server maintains in-memory state for graphs created during a session. Graphs are identified by unique IDs and can be queried and modified across multiple tool calls.

To enable persistent storage:
```yaml
state_storage_dir: "/path/to/storage/directory"
```

This will save graphs to JSON files that persist across server restarts.

## Error Handling

All tools return a consistent response format:

**Success:**
```json
{
  "success": true,
  "...": "... tool-specific data ..."
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

## Logging

The server uses `loguru` for logging. Logs are output to stderr with timestamps and level indicators.

Configure log level in config.yaml:
- `DEBUG`: Detailed debugging information
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

## Limitations

Current version limitations:

1. **Read-only Operations**: The server currently supports graph construction and querying but not full system building with phase/voltage/equipment mapping (coming in next version)

2. **In-memory State**: Default state is in-memory only and cleared on server restart (enable `state_storage_dir` for persistence)

3. **No Authentication**: Server runs locally without authentication (suitable for single-user desktop use)

4. **Limited Visualization**: Visualization tools not yet implemented

5. **No Async Operations**: Long-running operations (like large OpenStreetMap fetches) may cause timeouts

## Future Enhancements

Planned features for upcoming versions:

- [ ] Phase mapping tools (balanced, custom allocation)
- [ ] Voltage mapping tools
- [ ] Equipment mapping tools
- [ ] Complete system builder tool
- [ ] Visualization tools (interactive plots, diagrams)
- [ ] Export tools (OpenDSS, CYME, etc.)
- [ ] Async operations with progress reporting
- [ ] Resource streaming for large graphs
- [ ] Graph validation and health checks
- [ ] Network analysis tools (connectivity, power flow)

## Troubleshooting

### Server won't start
- Ensure MCP dependencies are installed: `pip install mcp pyyaml loguru`
- Check Python version >= 3.10
- Verify shift package is installed: `pip install -e ".[mcp]"`

### Tool calls timeout
- Reduce search distance for `fetch_parcels`
- Check internet connection for OpenStreetMap access
- Increase timeout in client configuration

### Graph not found errors
- Use `list_resources` to verify graph ID
- Remember graphs are per-session unless `state_storage_dir` is configured
- Graph IDs are case-sensitive

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/NREL-Distribution-Suites/shift/issues
- Documentation: https://github.com/NREL-Distribution-Suites/shift

## License

BSD-3-Clause License - see LICENSE.txt for details
