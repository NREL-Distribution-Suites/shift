from uuid import uuid4

import networkx as nx
import numpy as np
from infrasys.quantities import Distance

from shift.data_model import GeoLocation
from shift.exceptions import EmptyGraphError

DEGREE_TO_METER = 111139


def get_mesh_network(
    lower_left: GeoLocation,
    upper_right: GeoLocation,
    spacing: Distance,
) -> nx.Graph:
    """Creates a rectangular mesh network from a given set of points.

    Parameters
    ----------
        lower_left: tuple
            gelocation representing lower left point
        upper_right: tuple
            geolocation representing upper right point
        spacing: Distance
            spacing between nodes.

    Returns
    -------
        nx.Graph

    Examples
    --------

    >>> from shift import get_mesh_network
    >>> from infrasys.quantities import Distance
    >>> lower_left = GeoLocation(-97.33, 45.56)
    >>> upper_right = GeoLocation(-97.31, 45.64)
    >>> graph = get_mesh_network(lower_left, upper_right, Distance(10, "m"))
    >>> len(graph.nodes)
    199584
    """

    spacing_degrees = spacing.to("m").magnitude / DEGREE_TO_METER

    graph = nx.grid_2d_graph(
        np.arange(lower_left.longitude, upper_right.longitude + spacing_degrees, spacing_degrees),
        np.arange(lower_left.latitude, upper_right.latitude + spacing_degrees, spacing_degrees),
    )
    if not graph.nodes:
        point_distance = (
            np.sqrt(np.sum((np.array(upper_right) - np.array(lower_left)) ** 2)) * DEGREE_TO_METER
        )
        msg = (
            f"Empty graph for {lower_left=}, {upper_right=}, {spacing=}. "
            f"Diagonal distance is {point_distance=} meter."
        )
        raise EmptyGraphError(msg)

    for node in graph.nodes:
        graph.nodes[node]["x"] = node[0]
        graph.nodes[node]["y"] = node[1]
    return nx.relabel_nodes(graph, {node: str(uuid4()) for node in graph.nodes})
