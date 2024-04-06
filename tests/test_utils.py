import numpy as np
from infrasys.quantities import Distance
import pytest
from shapely import Polygon
import networkx as nx

from shift import (
    get_nearest_points,
    GeoLocation,
    get_kmeans_clusters,
    GroupModel,
    get_mesh_network,
    get_polygon_from_points,
    split_network_edges,
)


TEST_NEAREST_NODE_INPUTS = [{"input": [[[1, 2], [2, 3]], [[4, 4]]], "output": [[2, 3]]}]


@pytest.mark.parametrize("data", TEST_NEAREST_NODE_INPUTS)
def test_nearest_node(data):
    """Test function to check nearest nodes."""
    nearest_node = get_nearest_points(*data["input"])
    assert np.array_equal(nearest_node, data["output"])


TEST_CLUSTER_POINTS = [
    [
        2,
        [
            GeoLocation(*el)
            for el in [
                (-73.935242, 40.730610),
                (-73.934657, 40.731008),
                (-73.934952, 40.730456),
                (-73.935751, 40.730240),
                (-73.935302, 40.729913),
                (-73.935860, 40.730362),
                (-73.935479, 40.730812),
                (-73.935071, 40.730628),
                (-73.935530, 40.730160),
                (-73.935171, 40.730527),
            ]
        ],
    ]
]


@pytest.mark.parametrize("input", TEST_CLUSTER_POINTS)
def test_point_clustering(input):
    """Test point clustering function."""
    clusters = get_kmeans_clusters(*input)
    assert len(clusters) == input[0]
    assert isinstance(clusters[0], GroupModel)


TEST_POLYGON_POINTS = [[[[-97.32, 43.22], [-98.33, 45.35]], Distance(20, "m")]]


@pytest.mark.parametrize("input", TEST_POLYGON_POINTS)
def test_polygon_from_points(input):
    """Test polygon from points."""
    poly = get_polygon_from_points(*input)
    assert isinstance(poly, Polygon)


TEST_INPUT_RECTANGULAR_MESH = [
    [GeoLocation(-97.33, 45.56), GeoLocation(-97.32, 45.58), Distance(100, "m")]
]


@pytest.mark.parametrize("input", TEST_INPUT_RECTANGULAR_MESH)
def test_rectangular_mesh(input):
    """Test function for checking rectangular mesh network."""

    graph = get_mesh_network(*input)
    assert isinstance(graph, nx.Graph)


def test_split_network_edges():
    """Function to test edge splitting."""

    graph = nx.Graph()
    graph.add_node("node_1", x=-97.33, y=45.56)
    graph.add_node("node_2", x=-97.32, y=45.58)
    graph.add_edge("node_1", "node_2")
    split_network_edges(graph, split_length=Distance(50, "m"))
