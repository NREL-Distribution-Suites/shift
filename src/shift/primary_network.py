from abc import ABC, abstractmethod
from shift.data_model import GeoLocation

import networkx as nx


class PrimaryNetworkBuilder(ABC):
    """Abstract class interface for building primary network."""

    @abstractmethod
    def get_graph(self) -> nx.Graph:
        """Returns network representation of the graph."""

    @abstractmethod
    def get_transformer_nodes(self) -> list[str]:
        """Returns a list of transformer nodes."""

    @abstractmethod
    def get_source_node(self) -> str:
        """Returns source node name."""

    @abstractmethod
    def get_transformer_node(self, point: GeoLocation) -> str:
        """Returns a transformer node for a given given location."""
