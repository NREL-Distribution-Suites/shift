"""Main MCP server implementation for NREL-shift."""

import sys
import asyncio
from typing import Any, Optional
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent
from loguru import logger

from shift.mcp_server.config import config, load_config
from shift.mcp_server.state import StateManager
from shift.mcp_server import tools


def create_server() -> tuple[Server, StateManager]:  # noqa: C901
    """Create and configure the MCP server.

    Returns
    -------
    tuple[Server, StateManager]
        Configured server and state manager
    """
    # Initialize server
    server = Server(config.server_name)

    # Initialize state manager
    state_manager = StateManager(storage_dir=config.state_storage_dir)

    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        level=config.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    )

    logger.info(f"Initializing {config.server_name} v{config.server_version}")

    # Register tools
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available MCP tools."""
        return [
            Tool(
                name="fetch_parcels",
                description="Fetch building parcels from OpenStreetMap for a given location",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "oneOf": [
                                {
                                    "type": "string",
                                    "description": "Address string (e.g., 'Fort Worth, TX')",
                                },
                                {
                                    "type": "object",
                                    "properties": {
                                        "longitude": {"type": "number"},
                                        "latitude": {"type": "number"},
                                    },
                                    "required": ["longitude", "latitude"],
                                },
                            ],
                            "description": "Location as address string or coordinates",
                        },
                        "distance_meters": {
                            "type": "number",
                            "description": f"Search distance in meters (max: {config.max_search_distance_m})",
                            "default": config.default_search_distance_m,
                        },
                    },
                    "required": ["location"],
                },
            ),
            Tool(
                name="cluster_parcels",
                description="Cluster parcels into groups using K-means for transformer placement",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "parcels": {
                            "type": "array",
                            "description": "Array of parcel objects with geometry",
                            "items": {"type": "object"},
                        },
                        "num_clusters": {
                            "type": "integer",
                            "description": "Number of clusters to create",
                            "default": config.default_cluster_count,
                        },
                    },
                    "required": ["parcels"],
                },
            ),
            Tool(
                name="create_graph",
                description="Create a new empty distribution graph",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Optional name for the graph"}
                    },
                },
            ),
            Tool(
                name="add_node",
                description="Add a node to a distribution graph",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "Graph identifier"},
                        "node_name": {"type": "string", "description": "Name for the node"},
                        "longitude": {"type": "number", "description": "Longitude coordinate"},
                        "latitude": {"type": "number", "description": "Latitude coordinate"},
                        "assets": {
                            "type": "array",
                            "description": "Asset types: DistributionLoad, DistributionSolar, DistributionCapacitor, DistributionVoltageSource",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["graph_id", "node_name", "longitude", "latitude"],
                },
            ),
            Tool(
                name="add_edge",
                description="Add an edge (line or transformer) to a distribution graph",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "Graph identifier"},
                        "from_node": {"type": "string", "description": "Source node name"},
                        "to_node": {"type": "string", "description": "Target node name"},
                        "edge_name": {"type": "string", "description": "Name for the edge"},
                        "edge_type": {
                            "type": "string",
                            "description": "Edge type",
                            "enum": ["DistributionBranchBase", "DistributionTransformer"],
                        },
                        "length_meters": {
                            "type": "number",
                            "description": "Edge length in meters (required for branches)",
                        },
                    },
                    "required": ["graph_id", "from_node", "to_node", "edge_name", "edge_type"],
                },
            ),
            Tool(
                name="query_graph",
                description="Query information about a distribution graph",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "Graph identifier"},
                        "query_type": {
                            "type": "string",
                            "description": "Type of query",
                            "enum": ["summary", "nodes", "edges", "vsource"],
                            "default": "summary",
                        },
                    },
                    "required": ["graph_id"],
                },
            ),
            Tool(
                name="list_resources",
                description="List available graphs and systems",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "resource_type": {
                            "type": "string",
                            "description": "Type of resources to list",
                            "enum": ["all", "graphs", "systems"],
                            "default": "all",
                        }
                    },
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent]:
        """Handle tool calls."""
        try:
            logger.debug(f"Tool call: {name} with arguments: {arguments}")

            # Route to appropriate tool handler
            if name == "fetch_parcels":
                result = tools.fetch_parcels_tool(
                    state_manager, arguments.get("location"), arguments.get("distance_meters")
                )
            elif name == "cluster_parcels":
                result = tools.cluster_parcels_tool(
                    state_manager, arguments.get("parcels"), arguments.get("num_clusters")
                )
            elif name == "create_graph":
                result = tools.create_graph_tool(state_manager, arguments.get("name"))
            elif name == "add_node":
                result = tools.add_node_tool(
                    state_manager,
                    arguments["graph_id"],
                    arguments["node_name"],
                    arguments["longitude"],
                    arguments["latitude"],
                    arguments.get("assets"),
                )
            elif name == "add_edge":
                result = tools.add_edge_tool(
                    state_manager,
                    arguments["graph_id"],
                    arguments["from_node"],
                    arguments["to_node"],
                    arguments["edge_name"],
                    arguments["edge_type"],
                    arguments.get("length_meters"),
                )
            elif name == "query_graph":
                result = tools.query_graph_tool(
                    state_manager, arguments["graph_id"], arguments.get("query_type", "summary")
                )
            elif name == "list_resources":
                result = tools.list_resources_tool(
                    state_manager, arguments.get("resource_type", "all")
                )
            else:
                result = {"success": False, "error": f"Unknown tool: {name}"}

            # Format response
            import json

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.error(f"Error in tool {name}: {e}")
            import json

            return [
                TextContent(
                    type="text", text=json.dumps({"success": False, "error": str(e)}, indent=2)
                )
            ]

    return server, state_manager


async def main(config_path: Optional[Path] = None):
    """Run the MCP server.

    Parameters
    ----------
    config_path : Optional[Path]
        Path to configuration file
    """
    # Load configuration
    if config_path:
        global config
        config = load_config(config_path)

    # Create server
    server, state_manager = create_server()

    logger.info(f"Starting {config.server_name} via stdio")

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def cli_main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="NREL-shift MCP Server for distribution system modeling"
    )
    parser.add_argument("--config", type=Path, help="Path to configuration file")

    args = parser.parse_args()

    asyncio.run(main(args.config))


if __name__ == "__main__":
    cli_main()
