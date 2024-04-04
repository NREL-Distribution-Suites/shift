from sklearn.neighbors import KDTree
import numpy as np


def get_nearest_nodes(graph_nodes: list[list[float]], points: list[list[float]]):
    """Function to find nearest point in graph nodes for all points."""

    tree = KDTree(graph_nodes)
    _, idx = tree.query(points, k=1)
    first_indexes = [el[0] for el in idx]
    return np.array(graph_nodes)[first_indexes]
