"""MCP tools for NREL-shift operations."""

from typing import Any, Dict, List, Optional
from loguru import logger

from gdm.quantities import Distance
from infrasys import Location

from shift import (
    parcels_from_location,
    get_kmeans_clusters,
    NodeModel,
    EdgeModel,
    GeoLocation,
)
from shift.mcp_server.state import StateManager
from shift.mcp_server.config import config


def fetch_parcels_tool(
    state_manager: StateManager,
    location: str | Dict[str, float],
    distance_meters: Optional[float] = None,
) -> Dict[str, Any]:
    """Fetch building parcels from OpenStreetMap.

    Parameters
    ----------
    state_manager : StateManager
        State manager instance
    location : str | Dict[str, float]
        Address string or dict with 'longitude' and 'latitude' keys
    distance_meters : Optional[float]
        Search distance in meters. Uses default if None.

    Returns
    -------
    Dict[str, Any]
        Result containing parcels list and metadata
    """
    try:
        # Parse location
        if isinstance(location, dict):
            loc = GeoLocation(longitude=location["longitude"], latitude=location["latitude"])
        else:
            loc = location

        # Get distance
        dist = distance_meters or config.default_search_distance_m
        if dist > config.max_search_distance_m:
            return {
                "success": False,
                "error": f"Distance {dist}m exceeds maximum {config.max_search_distance_m}m",
            }

        distance = Distance(dist, "m")

        # Fetch parcels
        logger.info(f"Fetching parcels for location={loc}, distance={dist}m")
        parcels = parcels_from_location(loc, distance)

        # Convert to serializable format
        parcels_data = [
            {
                "name": p.name,
                "geometry": [
                    {"longitude": geo.longitude, "latitude": geo.latitude} for geo in p.geometry
                ]
                if isinstance(p.geometry, list)
                else {"longitude": p.geometry.longitude, "latitude": p.geometry.latitude},
                "building_type": p.building_type,
                "city": p.city,
                "state": p.state,
                "postal_address": p.postal_address,
            }
            for p in parcels
        ]

        return {
            "success": True,
            "parcel_count": len(parcels),
            "parcels": parcels_data,
            "location": str(loc),
            "distance_meters": dist,
        }

    except Exception as e:
        logger.error(f"Error in fetch_parcels: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in fetch_parcels: {e}")
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


def cluster_parcels_tool(
    state_manager: StateManager, parcels: List[Dict[str, Any]], num_clusters: Optional[int] = None
) -> Dict[str, Any]:
    """Cluster parcels into groups for transformer placement.

    Parameters
    ----------
    state_manager : StateManager
        State manager instance
    parcels : List[Dict[str, Any]]
        List of parcel dictionaries with geometry
    num_clusters : Optional[int]
        Number of clusters. Uses default if None.

    Returns
    -------
    Dict[str, Any]
        Result containing cluster information
    """
    try:
        # Extract GeoLocations from parcels
        points = []
        for parcel in parcels:
            geom = parcel.get("geometry")
            if isinstance(geom, dict) and "longitude" in geom:
                points.append(GeoLocation(longitude=geom["longitude"], latitude=geom["latitude"]))
            elif isinstance(geom, list) and len(geom) > 0:
                # Use first point for polygon
                points.append(
                    GeoLocation(longitude=geom[0]["longitude"], latitude=geom[0]["latitude"])
                )

        if not points:
            return {"success": False, "error": "No valid points found in parcels"}

        n_clusters = num_clusters or config.default_cluster_count
        n_clusters = min(n_clusters, len(points))

        logger.info(f"Clustering {len(points)} parcels into {n_clusters} clusters")
        clusters = get_kmeans_clusters(n_clusters, points)

        # Serialize clusters
        clusters_data = [
            {
                "center": {"longitude": c.center.longitude, "latitude": c.center.latitude},
                "point_count": len(c.points),
                "points": [{"longitude": p.longitude, "latitude": p.latitude} for p in c.points],
            }
            for c in clusters
        ]

        return {"success": True, "cluster_count": len(clusters), "clusters": clusters_data}

    except Exception as e:
        logger.error(f"Error in cluster_parcels: {e}")
        return {"success": False, "error": str(e)}


def create_graph_tool(state_manager: StateManager, name: Optional[str] = None) -> Dict[str, Any]:
    """Create a new distribution graph.

    Parameters
    ----------
    state_manager : StateManager
        State manager instance
    name : Optional[str]
        Name for the graph

    Returns
    -------
    Dict[str, Any]
        Result containing graph ID
    """
    try:
        graph_id = state_manager.create_graph(name)
        return {"success": True, "graph_id": graph_id, "message": f"Created graph: {graph_id}"}
    except Exception as e:
        logger.error(f"Error creating graph: {e}")
        return {"success": False, "error": str(e)}


def add_node_tool(
    state_manager: StateManager,
    graph_id: str,
    node_name: str,
    longitude: float,
    latitude: float,
    assets: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add a node to a distribution graph.

    Parameters
    ----------
    state_manager : StateManager
        State manager instance
    graph_id : str
        Graph identifier
    node_name : str
        Name for the node
    longitude : float
        Longitude coordinate
    latitude : float
        Latitude coordinate
    assets : Optional[List[str]]
        List of asset type names (e.g., ["DistributionLoad"])

    Returns
    -------
    Dict[str, Any]
        Result of operation
    """
    try:
        graph = state_manager.get_graph(graph_id)
        if not graph:
            return {"success": False, "error": f"Graph {graph_id} not found"}

        # Parse assets
        asset_types = set()
        if assets:
            from gdm.distribution.components import (
                DistributionLoad,
                DistributionSolar,
                DistributionCapacitor,
                DistributionVoltageSource,
            )

            asset_map = {
                "DistributionLoad": DistributionLoad,
                "DistributionSolar": DistributionSolar,
                "DistributionCapacitor": DistributionCapacitor,
                "DistributionVoltageSource": DistributionVoltageSource,
            }
            for asset_name in assets:
                if asset_name in asset_map:
                    asset_types.add(asset_map[asset_name])

        node = NodeModel(
            name=node_name,
            location=Location(x=longitude, y=latitude),
            assets=asset_types if asset_types else None,
        )

        graph.add_node(node)
        state_manager.save_graph(graph_id, graph)

        return {"success": True, "message": f"Added node {node_name} to graph {graph_id}"}

    except Exception as e:
        logger.error(f"Error adding node: {e}")
        return {"success": False, "error": str(e)}


def add_edge_tool(
    state_manager: StateManager,
    graph_id: str,
    from_node: str,
    to_node: str,
    edge_name: str,
    edge_type: str,
    length_meters: Optional[float] = None,
) -> Dict[str, Any]:
    """Add an edge to a distribution graph.

    Parameters
    ----------
    state_manager : StateManager
        State manager instance
    graph_id : str
        Graph identifier
    from_node : str
        Source node name
    to_node : str
        Target node name
    edge_name : str
        Name for the edge
    edge_type : str
        Edge type: "DistributionBranchBase" or "DistributionTransformer"
    length_meters : Optional[float]
        Edge length in meters (required for branches)

    Returns
    -------
    Dict[str, Any]
        Result of operation
    """
    try:
        graph = state_manager.get_graph(graph_id)
        if not graph:
            return {"success": False, "error": f"Graph {graph_id} not found"}

        # Parse edge type
        from gdm.distribution.components import DistributionBranchBase, DistributionTransformer

        edge_type_map = {
            "DistributionBranchBase": DistributionBranchBase,
            "DistributionTransformer": DistributionTransformer,
        }

        if edge_type not in edge_type_map:
            return {
                "success": False,
                "error": f"Invalid edge_type. Must be one of: {list(edge_type_map.keys())}",
            }

        length = Distance(length_meters, "m") if length_meters else None

        edge = EdgeModel(name=edge_name, edge_type=edge_type_map[edge_type], length=length)

        graph.add_edge(from_node, to_node, edge_data=edge)
        state_manager.save_graph(graph_id, graph)

        return {
            "success": True,
            "message": f"Added edge {edge_name} from {from_node} to {to_node}",
        }

    except Exception as e:
        logger.error(f"Error adding edge: {e}")
        return {"success": False, "error": str(e)}


def query_graph_tool(
    state_manager: StateManager, graph_id: str, query_type: str = "summary"
) -> Dict[str, Any]:
    """Query information about a distribution graph.

    Parameters
    ----------
    state_manager : StateManager
        State manager instance
    graph_id : str
        Graph identifier
    query_type : str
        Type of query: "summary", "nodes", "edges", "vsource"

    Returns
    -------
    Dict[str, Any]
        Query results
    """
    try:
        graph = state_manager.get_graph(graph_id)
        if not graph:
            return {"success": False, "error": f"Graph {graph_id} not found"}

        if query_type == "summary":
            nodes = list(graph.get_nodes())
            edges = list(graph.get_edges())
            return {
                "success": True,
                "graph_id": graph_id,
                "node_count": len(nodes),
                "edge_count": len(edges),
                "vsource_node": graph.vsource_node,
            }

        elif query_type == "nodes":
            nodes = []
            for node in graph.get_nodes():
                nodes.append(
                    {
                        "name": node.name,
                        "location": {"x": node.location.x, "y": node.location.y},
                        "has_assets": node.assets is not None,
                    }
                )
            return {"success": True, "nodes": nodes}

        elif query_type == "edges":
            edges = []
            for from_node, to_node, edge_data in graph.get_edges():
                edges.append(
                    {
                        "from": from_node,
                        "to": to_node,
                        "name": edge_data.name,
                        "type": edge_data.edge_type.__name__,
                    }
                )
            return {"success": True, "edges": edges}

        elif query_type == "vsource":
            return {"success": True, "vsource_node": graph.vsource_node}

        else:
            return {
                "success": False,
                "error": "Invalid query_type. Must be: summary, nodes, edges, or vsource",
            }

    except Exception as e:
        logger.error(f"Error querying graph: {e}")
        return {"success": False, "error": str(e)}


def list_resources_tool(state_manager: StateManager, resource_type: str = "all") -> Dict[str, Any]:
    """List available resources (graphs, systems).

    Parameters
    ----------
    state_manager : StateManager
        State manager instance
    resource_type : str
        Type of resources to list: "all", "graphs", "systems"

    Returns
    -------
    Dict[str, Any]
        List of resources
    """
    try:
        result = {"success": True}

        if resource_type in ["all", "graphs"]:
            result["graphs"] = state_manager.list_graphs()

        if resource_type in ["all", "systems"]:
            result["systems"] = state_manager.list_systems()

        return result

    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        return {"success": False, "error": str(e)}
