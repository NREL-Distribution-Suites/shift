import copy
import uuid

import networkx as nx
from geopy.distance import geodesic
import numpy as np
from infrasys.quantities import Distance
from gdm.quantities import PositiveDistance

from shift.data_model import GeoLocation


def get_distance_between_points(
    from_point: GeoLocation, to_point: GeoLocation
) -> PositiveDistance:
    """Returns distance betwee two geo points.

    Parameters
    ----------

    from_point: GeoLocation
        From point
    to_point: GeoLocation
        To point.

    Returns
    -------
    PositiveDistance
    """

    return PositiveDistance(
        geodesic(*[reversed(point) for point in [from_point, to_point]]).m, "m"
    )


def split_network_edges(graph: nx.Graph, split_length: Distance) -> nx.Graph:
    """Creates a new graph with edges sliced by given distance in meter.

    Parameters
    ----------

    graph: nx.Graph
        Networkx graph instance
    split_length: Distance
        Maximum length of edge used for splitting.

    Returns
    -------
        nx.Graph
            Splitted graph.

    Examples
    --------

    >>> import networkx as nx
    >>> graph = nx.Graph()
    >>> graph.add_node("node_1", x=-97.33, y=45.56)
    >>> graph.add_node("node_2", x=-97.32, y=45.58)
    >>> graph.add_edge("node_1", "node_2")
    >>> split_network_edges(graph, split_length=Distance(50, "m"))
    """
    sliced_graph = copy.deepcopy(graph)
    graph_nodes = dict(graph.nodes(data=True))
    split_length_m = split_length.to("m").magnitude
    for edge in graph.edges():
        from_point = GeoLocation(graph_nodes[edge[0]]["x"], graph_nodes[edge[0]]["y"])
        to_point = GeoLocation(graph_nodes[edge[1]]["x"], graph_nodes[edge[1]]["y"])
        edge_length_m = get_distance_between_points(from_point, to_point).to("m").magnitude
        if edge_length_m <= split_length_m:
            continue

        sliced_graph.remove_edge(*edge)
        edge_slices = [x / edge_length_m for x in np.arange(1, edge_length_m, split_length_m)]

        x1, y1 = (from_point.longitude, from_point.latitude)
        x2, y2 = (to_point.longitude, to_point.latitude)

        sliced_nodes = []
        for slice_ in edge_slices:
            node_name = str(uuid.uuid4())
            new_x, new_y = x1 + (x2 - x1) * slice_, y1 + (y2 - y1) * slice_
            sliced_graph.add_node(node_name, x=new_x, y=new_y)
            sliced_nodes.append(node_name)

        sliced_nodes = [edge[0]] + sliced_nodes + [edge[1]]
        for i in range(len(sliced_nodes) - 1):
            sliced_graph.add_edge(sliced_nodes[i], sliced_nodes[i + 1])

    return sliced_graph
