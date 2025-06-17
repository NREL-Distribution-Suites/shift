from abc import ABC, abstractmethod
from functools import cached_property

from gdm.quantities import Voltage

from shift.graph.distribution_graph import DistributionGraph


class BaseVoltageMapper(ABC):
    """Abstract class for mapping voltage to transformers

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
    def node_voltage_mapping(self) -> dict[str, Voltage]:
        """Returns dictionary mapping node name to line to ground voltage.

        Returns
        -------
        dict[str, tuple[Voltage, Voltage]]
        """
