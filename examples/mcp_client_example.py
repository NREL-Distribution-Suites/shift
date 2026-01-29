"""Example MCP client for NREL-shift server.

This script demonstrates how to interact with the NREL-shift MCP server
to build a simple distribution system model.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_example():
    """Run example workflow."""

    # Server parameters
    server_params = StdioServerParameters(command="shift-mcp-server", args=[], env=None)

    print("🚀 Starting NREL-shift MCP Server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()

            print("✅ Connected to server\n")

            # List available tools
            tools = await session.list_tools()
            print(f"📋 Available tools: {[t.name for t in tools.tools]}\n")

            # Example 1: Fetch parcels
            print("=" * 60)
            print("Example 1: Fetch Parcels from OpenStreetMap")
            print("=" * 60)

            result = await session.call_tool(
                "fetch_parcels", arguments={"location": "Fort Worth, TX", "distance_meters": 500}
            )

            response = json.loads(result.content[0].text)
            print(f"✅ Fetched {response.get('parcel_count', 0)} parcels")

            if response.get("success") and response.get("parcels"):
                print(f"   Location: {response.get('location')}")
                print(f"   First parcel: {response['parcels'][0]['name']}")
            print()

            # Example 2: Cluster parcels
            if response.get("success") and response.get("parcels"):
                print("=" * 60)
                print("Example 2: Cluster Parcels")
                print("=" * 60)

                cluster_result = await session.call_tool(
                    "cluster_parcels",
                    arguments={
                        "parcels": response["parcels"][:10],  # Use first 10
                        "num_clusters": 3,
                    },
                )

                cluster_response = json.loads(cluster_result.content[0].text)
                print(f"✅ Created {cluster_response.get('cluster_count', 0)} clusters")

                if cluster_response.get("clusters"):
                    for i, cluster in enumerate(cluster_response["clusters"]):
                        center = cluster["center"]
                        print(
                            f"   Cluster {i + 1}: {cluster['point_count']} points at "
                            f"({center['longitude']:.4f}, {center['latitude']:.4f})"
                        )
                print()

            # Example 3: Create a graph
            print("=" * 60)
            print("Example 3: Create Distribution Graph")
            print("=" * 60)

            graph_result = await session.call_tool(
                "create_graph", arguments={"name": "example_graph"}
            )

            graph_response = json.loads(graph_result.content[0].text)
            graph_id = graph_response.get("graph_id")
            print(f"✅ Created graph: {graph_id}\n")

            # Example 4: Add nodes
            print("=" * 60)
            print("Example 4: Add Nodes to Graph")
            print("=" * 60)

            # Add voltage source node
            await session.call_tool(
                "add_node",
                arguments={
                    "graph_id": graph_id,
                    "node_name": "substation",
                    "longitude": -97.33,
                    "latitude": 32.75,
                    "assets": ["DistributionVoltageSource"],
                },
            )
            print("✅ Added voltage source node: substation")

            # Add load nodes
            for i in range(3):
                await session.call_tool(
                    "add_node",
                    arguments={
                        "graph_id": graph_id,
                        "node_name": f"load_{i}",
                        "longitude": -97.33 + i * 0.001,
                        "latitude": 32.75 + i * 0.001,
                        "assets": ["DistributionLoad"],
                    },
                )
                print(f"✅ Added load node: load_{i}")
            print()

            # Example 5: Add edges
            print("=" * 60)
            print("Example 5: Connect Nodes with Edges")
            print("=" * 60)

            for i in range(3):
                await session.call_tool(
                    "add_edge",
                    arguments={
                        "graph_id": graph_id,
                        "from_node": "substation",
                        "to_node": f"load_{i}",
                        "edge_name": f"line_{i}",
                        "edge_type": "DistributionBranchBase",
                        "length_meters": 100.0 * (i + 1),
                    },
                )
                print(f"✅ Added edge: line_{i} (substation -> load_{i})")
            print()

            # Example 6: Query graph
            print("=" * 60)
            print("Example 6: Query Graph Summary")
            print("=" * 60)

            query_result = await session.call_tool(
                "query_graph", arguments={"graph_id": graph_id, "query_type": "summary"}
            )

            query_response = json.loads(query_result.content[0].text)
            print("✅ Graph Summary:")
            print(f"   Nodes: {query_response.get('node_count')}")
            print(f"   Edges: {query_response.get('edge_count')}")
            print(f"   Voltage Source: {query_response.get('vsource_node')}")
            print()

            # Example 7: List all resources
            print("=" * 60)
            print("Example 7: List All Resources")
            print("=" * 60)

            resources_result = await session.call_tool(
                "list_resources", arguments={"resource_type": "all"}
            )

            resources_response = json.loads(resources_result.content[0].text)
            print("✅ Available Resources:")
            print(f"   Graphs: {len(resources_response.get('graphs', []))}")
            for graph in resources_response.get("graphs", []):
                print(
                    f"      - {graph['name']}: {graph['node_count']} nodes, "
                    f"{graph['edge_count']} edges"
                )
            print()

            print("=" * 60)
            print("✅ Example completed successfully!")
            print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("NREL-shift MCP Server - Example Client")
    print("=" * 60 + "\n")

    asyncio.run(run_example())
