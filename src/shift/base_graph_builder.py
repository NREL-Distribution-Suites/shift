from abc import ABC, abstractmethod

from shift.distribution_graph import DistributionGraph


class BaseGraphBuilder(ABC):
    """Abstract class interface for building distribution graph."""

    @abstractmethod
    def get_distribution_graph() -> DistributionGraph:
        """Method to return distribution graph."""
