from typing import Annotated, Callable, Iterable, Type

import networkx as nx
from pydantic import BaseModel, Field
from shift.exceptions import EdgeAlreadyExists, NodeAlreadyExists, VsourceNodeAlreadyExists
from gdm import (
    DistributionLoad,
    DistributionSolar,
    DistributionCapacitor,
    DistributionVoltageSource,
    DistributionBranch,
    DistributionTransformer,
)

VALID_NODE_TYPES = Annotated[
    Type[DistributionLoad]
    | Type[DistributionSolar]
    | Type[DistributionCapacitor]
    | Type[DistributionVoltageSource],
    Field(..., description="Possible node types."),
]


VALID_EDGE_TYPES = Annotated[
    Type[DistributionBranch] | Type[DistributionTransformer],
    Field(..., description="Possible edge types."),
]


class NodeModel(BaseModel):
    """Interface for node model."""

    name: Annotated[str, Field(..., description="Name of the node.")]
    assets: Annotated[
        set[VALID_NODE_TYPES], Field([], description="Set of asset types attached to node.")
    ]


class EdgeModel(BaseModel):
    """Interface for edge model."""

    name: Annotated[str, Field(..., description="Name of the node.")]
    edge_type: Annotated[VALID_EDGE_TYPES, Field(..., description="Edge type.")]


class DistributionGraph:
    """A class representing distribution system as a graph.

    Internally, graph data is stored using networkx Graph instance.

    Examples
    --------
    >>> dgraph = DistributionGraph()

    Adding a node the system.

    >>> from shift import NodeModel
    >>> dgraph.add_node(NodeModel(name="node_1", assets=[]))

    Adding multiple nodes to the system.

    >>> from gdm import DistributionLoad
    >>> dgraph.add_nodes([NodeModel(name="node_2", assets={DistributionLoad}),
        NodeModel(name="node_3")])

    Adding an edge to the system.

    >>> from shift import EdgeModel
    >>> dgraph.add_edge("node_1", "node_2", edge_data=EdgeModel(name="node1_node2",
        edge_type=DistributionBranch))

    Getting node data.

    >>> dgraph.get_node("node_1")

    Getting all nodes.

    >>> dgraph.get_nodes()

    Getting filtered nodes.

    >>> dgraph.get_nodes(filter_func=lambda x: len(x.assets) == 0)

    Remove a node.

    >>> dgraph.remove_node("node_2")
    """

    def __init__(self):
        self._graph = nx.Graph()
        self.vsource_node = None

    def add_node(self, node: NodeModel):
        """Adds node to the graph.

        Parameters
        ----------
        node : NodeModel
            Instance of `NodeModel` to add to the graph.

        Raises
        ------
        NodeAlreadyExists
            Raises this exception if node already exists.
        VsourceNodeAlreadyExists:
            Raises this exception if an attempt is made to add
            node with substation in assets more than once.

        Examples
        --------

        >>> import shift as sf
        >>> dg = sf.DistributionGraph()
        >>> dg.add_node(sf.NodeModel(name="node_1"))
        """

        if self._graph.has_node(node.name):
            msg = f"{node=} already exists in the graph."
            raise NodeAlreadyExists(msg)
        if self.vsource_node is not None:
            msg = f"{self.vsource_node=} already exists. Cannot add {node=}"
            raise VsourceNodeAlreadyExists(msg)
        self._graph.add_node(node.name, node_data=node)
        if DistributionVoltageSource in node.assets:
            self.substation_node = node.name

    def add_nodes(self, nodes: list[NodeModel]):
        """Adds multiple nodes to the graph.

        Parameters
        ----------
        nodes : NodeModel
            Instance of `NodeModel` to add to the graph.

        Examples
        --------

        >>> import shift as sf
        >>> dg = sf.DistributionGraph()
        >>> dg.add_nodes([sf.NodeModel(name="node_1"),
            sf.NodeModel(name="node_2")])
        """
        for node in nodes:
            self.add_node(node)

    def add_edge(self, from_node: str, to_node: str, edge_data: EdgeModel):
        """Adds edge to the graph.

        Parameters
        ----------
        from_node : str
            Name of the from node.
        to_node : str
            Name of the to node.
        edge_data : EdgeModel
            Instance of the `EdgeModel`.

        Raises
        ------
            EdgeAlreadyExists
                Raises an exception if edge already exists.

        Examples
        --------

        >>> import shift as sf
        >>> dg = sf.DistributionGraph()
        >>> dg.add_nodes([sf.NodeModel(name="node_1"),
            sf.NodeModel(name="node_2")])
        >>> df.add_edge("node_1", "node_2")
        """
        if self._graph.has_edge(from_node, to_node):
            msg = f"Edge already exists between {from_node=} and {to_node=}"
            raise EdgeAlreadyExists(msg)
        self._graph.add_edge(from_node, to_node, edge_data=edge_data)

    def get_node(self, node_name: str) -> NodeModel:
        """Get node data by node name.

        Parameters
        ----------
        node_name : str
            Name of the node.

        Returns
        -------
        NodeModel

        Examples
        --------

        >>> import shift as sf
        >>> from gdm import DistributionLoad
        >>> dg = sg.DistributionGraph()
        >>> dg.add_node(sf.NodeModel(name="node_1", assets={DistributionLoad}))
        >>> dg.get_node("node_1")
        """
        return self._graph.nodes[node_name]["node_data"]

    def get_nodes(
        self, filter_func: Callable[[NodeModel], bool] | None = None
    ) -> Iterable[NodeModel]:
        """Returns list of nodes.

        Parameters
        ----------
        filter_func : Callable[[NodeModel], bool] | None, optional
            Filter function for getting nodes., by default None

        Returns
        -------
        Iterable[NodeModel]
            Iterable for getting node.

        Examples
        --------

        >>> import shift as sf
        >>> from gdm import DistributionLoad
        >>> dg = sf.DistributionGraph()
        >>> dg.add_node(sf.NodeModel(name="node_1", assets={DistributionLoad}))
            dg.get_node("node_1")
        >>> dg.get_nodes()
        """
        for node in self._graph.nodes:
            node_obj = self._graph.nodes[node]["node_data"]
            if (filter_func and filter_func(node_obj)) or filter_func is None:
                yield node_obj

    def remove_node(self, node_name: str):
        """Removes a node from the system.

        Parameters
        ----------
        node_name: str
            Name of the node to remove.

        Examples
        --------

        >>> import shift as sf
        >>> dg = sf.DistributionGraph()
        >>> dg.add_node(sf.NodeModel(name="node_1"))
        >>> dg.remove_node("node_1")
        """
        self._graph.remove_node(node_name)
