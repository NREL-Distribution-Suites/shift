from abc import ABC, abstractmethod
from functools import cached_property

from infrasys.component import Component

from shift.graph.distribution_graph import DistributionGraph
from shift.data_model import VALID_NODE_TYPES


class BaseEquipmentMapper(ABC):
    """Abstract class for mapping equipment to nodes and assets.

    Subclasses must implement following method.
    * transformer_voltage_mapping

    Parameters
    ----------

    graph: DistributionGraph
        Instance of `DistributionGraph` for which to implement voltage mapping.
    """

    def __init__(self, graph: DistributionGraph):
        self.graph = graph

    @abstractmethod
    @cached_property
    def node_asset_equipment_mapping(self) -> dict[str, dict[VALID_NODE_TYPES, Component]]:
        """Returns dictionary mapping node name to asset type
        to equipment component.

        Returns
        -------
        dict[str, dict[VALID_NODE_TYPES, Component]]
        """

    @abstractmethod
    @cached_property
    def edge_equipment_mapping(self) -> dict[str, Component]:
        """Returns dictionary mapping edge name to component.

        Returns
        -------
        dict[str,  Component]
        """
