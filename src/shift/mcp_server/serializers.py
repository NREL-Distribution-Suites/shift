"""Serialization helpers — convert shift objects to JSON-safe dicts."""

from __future__ import annotations

from typing import Any

from shift.data_model import GeoLocation, ParcelModel, GroupModel, NodeModel, EdgeModel


def serialize_geo_location(loc: GeoLocation) -> dict[str, float]:
    return {"longitude": loc.longitude, "latitude": loc.latitude}


def serialize_parcel(parcel: ParcelModel) -> dict[str, Any]:
    if isinstance(parcel.geometry, list):
        geom = [serialize_geo_location(g) for g in parcel.geometry]
    else:
        geom = serialize_geo_location(parcel.geometry)
    return {
        "name": parcel.name,
        "building_type": parcel.building_type,
        "city": parcel.city,
        "state": parcel.state,
        "postal_address": parcel.postal_address,
        "geometry": geom,
    }


def serialize_group(group: GroupModel) -> dict[str, Any]:
    return {
        "center": serialize_geo_location(group.center),
        "points": [serialize_geo_location(p) for p in group.points],
        "num_points": len(group.points),
    }


def serialize_node(node: NodeModel) -> dict[str, Any]:
    assets = []
    if node.assets:
        assets = [t.__name__ for t in node.assets]
    return {
        "name": node.name,
        "longitude": node.location.x,
        "latitude": node.location.y,
        "assets": assets,
    }


def serialize_edge(edge: EdgeModel) -> dict[str, Any]:
    result: dict[str, Any] = {
        "name": edge.name,
        "edge_type": edge.edge_type.__name__,
    }
    if edge.length is not None:
        result["length_meters"] = float(edge.length.to("m").magnitude)
    return result


def serialize_edge_tuple(from_node: str, to_node: str, edge: EdgeModel) -> dict[str, Any]:
    result = serialize_edge(edge)
    result["from_node"] = from_node
    result["to_node"] = to_node
    return result


def serialize_graph_summary(graph, graph_id: str, meta=None) -> dict[str, Any]:
    """Produce a compact summary dict for a DistributionGraph."""

    nodes = list(graph.get_nodes())
    edges = list(graph.get_edges())
    summary: dict[str, Any] = {
        "graph_id": graph_id,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "vsource_node": graph.vsource_node,
    }
    if meta:
        summary["name"] = meta.name
        summary["created_at"] = meta.created_at
    return summary


def serialize_nx_graph_summary(graph) -> dict[str, Any]:
    """Summarize a raw networkx graph (from road network etc.)."""
    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
    }
