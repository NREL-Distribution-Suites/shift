from abc import ABC, abstractmethod
from functools import cached_property

from gdm import Phase

from shift.graph.distribution_graph import DistributionGraph, VALID_NODE_TYPES
from shift.exceptions import InvalidAssetPhase


class BasePhaseMapper(ABC):
    """Abstract class for mapping getting phases for nodes, edges and assets.

    Subclasses must implement following methods.
    * get_node_phase_mapping
    * get_asset_phase_mapping

    Parameters
    ----------

    graph: DistributionGraph
        Instance of `DistributionGraph` for which to implement phase mapping.
    """

    def __init__(self, graph: DistributionGraph):
        self._graph = graph
        self._validate_asset_phases()
        self._validate_node_phases()

    def _validate_node_phases(self):
        "Internal method to validate phase connectivity in graph."
        pass

    def _validate_asset_phases(self):
        """Internal method to validate asset phases with respect to node phases."""
        node_phases = self.get_node_phase_mapping()
        for node, asset_map in self.get_asset_phase_mapping().items():
            phs = set([el for item in asset_map.values() for el in item])
            if not phs.issubset(node_phases[node]):
                msg = f"{phs=} is not subset of {node_phases[node]=}"
                raise InvalidAssetPhase(msg)

    @abstractmethod
    @cached_property
    def get_node_phase_mapping(
        self,
    ) -> dict[str, set[Phase]]:
        """Returns node to phase mapping dictionary.

        Returns
        -------

        dict[str, set[Phase]]
            Dictionary mapping node name to set of phases.
        """

    @abstractmethod
    @cached_property
    def get_asset_phase_mapping(self) -> dict[str, dict[VALID_NODE_TYPES, set[Phase]]]:
        """Returns asset to phase mapping.

        Returns
        -------

        dict[str, dict[VALID_NODE_TYPES, set[Phase]]]
            Dict of dicts mapping nodename to asset type to list of phases.
        """
