from functools import cached_property
from typing import Callable

from gdm.quantities import PositiveVoltage
from gdm.distribution.components import DistributionTransformer

import networkx as nx
from shift.graph.distribution_graph import DistributionGraph
from shift.mapper.base_voltage_mapper import BaseVoltageMapper
from shift.data_model import TransformerVoltageModel


class TransformerVoltageMapper(BaseVoltageMapper):
    """Class for mapping voltage to buses based on transformer voltage.


    Parameters
    ----------
    graph: DistributionGraph
        Instance of the DistributionGraph
    xfmr_voltage: list[TransformerVoltageModel]
        List of transformers voltage (assumed all line to ground voltages) models
    """

    def __init__(
        self,
        graph: DistributionGraph,
        xfmr_voltage: list[TransformerVoltageModel],
    ):
        xfmr_names_in_map = set([xfmr.name for xfmr in xfmr_voltage])
        xfmr_names_in_graph = set(
            [
                edge.name
                for _, _, edge in graph.get_edges(
                    filter_func=lambda x: x.edge_type is DistributionTransformer
                )
            ]
        )
        missing_xfmrs = xfmr_names_in_graph - xfmr_names_in_map

        if missing_xfmrs:
            msg = f"Voltages not available for {missing_xfmrs=}"
            raise ValueError(msg)

        self.xfmr_voltage = xfmr_voltage
        super().__init__(graph)

    def _update_mapper_by_func(
        self,
        nodes: list[str],
        xfmr: TransformerVoltageModel,
        mapper: dict[str, PositiveVoltage],
        compare_func: Callable,
    ):
        """Internal function to update voltage mapper."""
        for node in nodes:
            if node in mapper:
                mapper[node] = compare_func(mapper[node], compare_func(xfmr.voltages))
            else:
                mapper[node] = compare_func(xfmr.voltages)

    @cached_property
    def node_voltage_mapping(self) -> dict[str, PositiveVoltage]:
        node_voltages: dict[str, PositiveVoltage] = {}
        dfs_tree = self.graph.get_dfs_tree()
        xfmrs_in_mapper = [xfmr.name for xfmr in self.xfmr_voltage]
        edges = self.graph.get_edges(filter_func=lambda x: x.name in xfmrs_in_mapper)

        for xfmr, edge in zip(self.xfmr_voltage, edges):
            from_node, to_node, _ = edge

            ht_node, lt_node = (
                (from_node, to_node)
                if dfs_tree.has_edge(from_node, to_node)
                else (to_node, from_node)
            )

            self._update_mapper_by_func(
                dfs_tree.subgraph(nx.ancestors(dfs_tree, source=lt_node)), xfmr, node_voltages, max
            )
            self._update_mapper_by_func(
                dfs_tree.subgraph(nx.descendants(dfs_tree, source=ht_node)),
                xfmr,
                node_voltages,
                min,
            )
        return node_voltages
