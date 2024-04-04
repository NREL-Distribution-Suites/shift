import copy
import networkx as nx
from geopy.distance import geodesic
import numpy as np
from infrasys.quantities import Distance


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
    """
    start_node_num = 100000
    sliced_graph = copy.deepcopy(graph)
    graph_nodes = dict(graph.nodes(data=True))
    split_length_m = split_length.to("m").magnitude
    for edge in graph.edges():
        edge_length_m = geodesic(
            *[(graph_nodes[node]["y"], graph_nodes[node]["x"]) for node in edge]
        ).m
        if edge_length_m <= split_length_m:
            continue

        sliced_graph.remove_edge(*edge)
        edge_slices = [x / edge_length_m for x in np.arange(1, edge_length_m, split_length_m)]

        x1, y1 = (graph_nodes[edge[0]]["x"], graph_nodes[edge[0]]["y"])
        x2, y2 = (graph_nodes[edge[1]]["x"], graph_nodes[edge[1]]["y"])

        sliced_nodes = []
        for slice_ in edge_slices:
            new_x, new_y = x1 + (x2 - x1) * slice_, y1 + (y2 - y1) * slice_
            sliced_graph.add_node(start_node_num, x=new_x, y=new_y)
            sliced_nodes.append(start_node_num)
            start_node_num += 1

        sliced_nodes = [edge[0]] + sliced_nodes + [edge[1]]
        for i in range(len(sliced_nodes) - 1):
            sliced_graph.add_edge(sliced_nodes[i], sliced_nodes[i + 1])

    return sliced_graph
