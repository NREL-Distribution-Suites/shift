import pytest
from gdm.distribution.components import (
    DistributionVoltageSource,
    DistributionTransformer,
    DistributionBranchBase,
    DistributionLoad,
)
from infrasys import Location
from gdm.quantities import PositiveDistance

from shift import DistributionGraph, NodeModel, EdgeModel
from shift.exceptions import (
    EdgeAlreadyExists,
    EdgeDoesNotExist,
    NodeAlreadyExists,
    NodeDoesNotExist,
    VsourceNodeAlreadyExists,
)


@pytest.fixture
def distribution_graph():
    graph = DistributionGraph()
    node_1 = NodeModel(name="node_1", location=Location(x=-93.33, y=45.56))
    node_2 = NodeModel(
        name="node_2",
        location=Location(x=-93.33, y=45.56),
        assets={DistributionVoltageSource},
    )
    node_3 = NodeModel(
        name="node_3",
        location=Location(x=-93.35, y=45.58),
        assets={DistributionLoad},
    )
    graph.add_edge(
        node_1,
        node_2,
        edge_data=EdgeModel(name="line-1", edge_type=DistributionTransformer, length=None),
    )
    graph.add_edge(
        node_1,
        node_3,
        edge_data=EdgeModel(
            name="line-2", edge_type=DistributionBranchBase, length=PositiveDistance(1, "m")
        ),
    )

    yield graph


def test_node_addition(distribution_graph):
    node = NodeModel(
        name="node_5", location=Location(x=-93.33, y=45.56), assets={DistributionLoad}
    )
    distribution_graph.add_node(node)
    assert distribution_graph.get_node("node_5") == node


def test_nodes_addition(distribution_graph):
    distribution_graph.add_nodes(
        [
            NodeModel(name="node_4", location=Location(x=-93.33, y=45.56)),
            NodeModel(name="node_5", location=Location(x=-93.33, y=45.56)),
        ]
    )


def test_edge_addition():
    graph = DistributionGraph()
    node_1 = NodeModel(name="node_1", location=Location(x=1, y=1))
    node_2 = NodeModel(name="node_2", location=Location(x=1, y=2))
    graph.add_nodes([node_1, node_2])
    edge_data = EdgeModel(
        name="line-1", edge_type=DistributionBranchBase, length=PositiveDistance(1, "m")
    )
    graph.add_edge(
        node_1.name,
        node_2.name,
        edge_data=edge_data,
    )
    assert graph.get_edge("node_1", "node_2") == edge_data


def test_removing_edge(distribution_graph):
    distribution_graph.remove_edge("node_1", "node_2")


def test_remove_node(distribution_graph):
    node_name = "node_1"
    assert distribution_graph.get_node(node_name)
    distribution_graph.remove_node(node_name)
    with pytest.raises(NodeDoesNotExist) as _:
        distribution_graph.get_node(node_name)


def test_adding_node_that_already_exists(distribution_graph):
    node_1 = NodeModel(name="node_1", location=Location(x=-93.33, y=45.56))
    with pytest.raises(NodeAlreadyExists) as _:
        distribution_graph.add_node(node_1)


def test_adding_multiple_vsource(distribution_graph):
    node_4 = NodeModel(
        name="node_4",
        location=Location(x=0, y=0),
        assets={DistributionVoltageSource},
    )
    with pytest.raises(VsourceNodeAlreadyExists) as _:
        distribution_graph.add_node(node_4)


def test_adding_edge_that_already_exists(distribution_graph):
    with pytest.raises(EdgeAlreadyExists) as _:
        distribution_graph.add_edge(
            "node_1",
            "node_3",
            edge_data=EdgeModel(
                name="line-1", edge_type=DistributionBranchBase, length=PositiveDistance(1, "m")
            ),
        )


def test_quering_node_that_does_not_exist():
    graph = DistributionGraph()
    with pytest.raises(NodeDoesNotExist) as _:
        graph.get_node("node_1")


def test_querying_edge_that_does_not_exist():
    graph = DistributionGraph()
    with pytest.raises(EdgeDoesNotExist) as _:
        graph.get_edge("node_1", "node_2")
