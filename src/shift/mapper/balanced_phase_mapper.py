from enum import Enum
from functools import cached_property, reduce
from itertools import combinations, groupby
import operator

from gdm import DistributionTransformer, Phase
from pydantic import BaseModel, ConfigDict
from gdm.quantities import PositiveApparentPower
import numpy as np
import networkx as nx

from shift.graph.distribution_graph import DistributionGraph, VALID_NODE_TYPES
from shift.mapper.base_phase_mapper import BasePhaseMapper


class TransformerTypes(str, Enum):
    """Enumerator for transformer types for phase allocation."""

    THREE_PHASE = "THREE_PHASE"
    SINGLE_PHASE_PRIMARY_DELTA = "SINGLE_PHASE_PRIMARY_DELTA"
    SINGLE_PHASE = "SINGLE_PHASE"
    SPLIT_PHASE = "SPLIT_PHASE"
    SPLIT_PHASE_PRIMARY_DELTA = "SPLIT_PHASE_PRIMARY_DELTA"


class TransformerPhaseMapperModel(BaseModel):
    """Class interface for phase mapper model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    tr_name: str
    tr_type: TransformerTypes
    tr_capacity: PositiveApparentPower


def greedy_allocations(weights: list[tuple[str, float]], num_categories: int) -> list[list[str]]:
    """Greedy allocation algorithm to assign weights to categories
    in balanced way as much as possible."""

    sorted_weights = sorted(weights, key=lambda x: x[1], reverse=True)
    allocations = [[] for _ in range(num_categories)]
    sums = [0 for _ in range(num_categories)]
    for weight in sorted_weights:
        min_sum_index = np.argmin(sums)
        sums[min_sum_index] += weight[1]
        allocations[min_sum_index].append(weight[0])
    return allocations


class BalancedPhaseMapper(BasePhaseMapper):
    """Class interface for balanced phase mapper.

    Parameters
    ----------

    graph: DistributionGraph
        Instance of the distribution graph.
    mapper: list[TransformerPhaseMapperModel]
        List of phase mapper models.
    """

    def __init__(self, graph: DistributionGraph, mapper: list[TransformerPhaseMapperModel]):
        self.mapper = mapper

        missing_transformers = set([item.tr_name for item in self.mapper]) - set(
            edge.name
            for _, _, edge in graph.get_edges()
            if edge.edge_type == DistributionTransformer
        )
        if missing_transformers:
            msg = f"Missing transformers from mapping {missing_transformers=}"
            raise ValueError(msg)
        self._transformer_phase_mapping: dict[str, set[Phase]] = {}
        super().__init__(graph)

    def _get_nodes_by_edge_names(self, edge_names: list[str]) -> set[str]:
        """Internal method to get three phase nodes."""
        nodes = set()
        for from_node, to_node, _ in self.graph.get_edges(
            filter_func=lambda x: x.name in edge_names
        ):
            edge_node_set = set([from_node, to_node])
            nodes = reduce(operator.or_, [nodes, edge_node_set])
        return nodes

    def _update_three_phase_nodes(
        self, trs: list[TransformerPhaseMapperModel], container: dict, transformer_mapper: dict
    ):
        """Internal method to update three phase nodes."""
        tr_names = [item.tr_name for item in trs]
        three_phase = set([Phase.A, Phase.B, Phase.C])
        for tr in tr_names:
            transformer_mapper[tr] = three_phase
        for node in self._get_nodes_by_edge_names(tr_names):
            container[node] = three_phase

    def _get_head_node(self, edge_name: str) -> str:
        """Internal method to return head node."""
        nodes = list(self._get_nodes_by_edge_names([edge_name]))
        return (
            nodes[0]
            if nodes[1]
            in nx.dfs_successors(self.graph.get_dfs_tree(), source=nodes[0], depth_limit=1)[
                nodes[0]
            ]
            else nodes[1]
        )

    def _update_single_phase_tr_nodes(
        self,
        trs: list[TransformerPhaseMapperModel],
        ht_phases: list[list[Phase]],
        is_split_phase: bool,
        container: dict,
        transformer_mapper: dict,
    ):
        """Internal method to update three phase nodes."""
        allocations = greedy_allocations(
            [(tr.tr_name, tr.tr_capacity.to("va").magnitude) for tr in trs], len(ht_phases)
        )
        for allocation, phases in zip(allocations, ht_phases):
            for tr in allocation:
                nodes = self._get_nodes_by_edge_names([tr])
                head_node = self._get_head_node(tr)
                tail_node = list(set(nodes) - set([head_node]))[0]
                container[head_node] = set(phases)
                container[tail_node] = (
                    set([Phase.S1, Phase.N, Phase.S2]) if is_split_phase else set(phases)
                )
                transformer_mapper[tr] = set(phases)

    def _update_transformer_node_phases(
        self, mapper: list[TransformerPhaseMapperModel], container: dict, transformer_mapper: dict
    ):
        """Internal method to update transformer nodes phases."""
        delta_phase_combinations = [[Phase.A, Phase.B], [Phase.B, Phase.C], [Phase.C, Phase.A]]
        single_phase_combinations = [[Phase.A], [Phase.B], [Phase.C]]

        type_to_input_mapper = {
            TransformerTypes.SPLIT_PHASE: [single_phase_combinations, True],
            TransformerTypes.SINGLE_PHASE: [single_phase_combinations, False],
            TransformerTypes.SPLIT_PHASE_PRIMARY_DELTA: [delta_phase_combinations, True],
            TransformerTypes.SINGLE_PHASE_PRIMARY_DELTA: [delta_phase_combinations, False],
        }
        for tr_type, group in groupby(mapper, lambda x: x.tr_type):
            if tr_type == TransformerTypes.THREE_PHASE:
                self._update_three_phase_nodes(group, container, transformer_mapper)
            elif tr_type in type_to_input_mapper:
                self._update_single_phase_tr_nodes(
                    group, *type_to_input_mapper[tr_type], container, transformer_mapper
                )
            else:
                msg = f"{tr_type=} not supported yet."
                raise ValueError(msg)

    def _update_node_phases_upward_from_transformer(
        self,
        mapper: list[TransformerPhaseMapperModel],
        container: dict,
    ):
        """Internal method to update transformer nodes phases."""

        for tr in mapper:
            head_node = self._get_head_node(tr.tr_name)
            tr_head_node_phase = container[head_node]
            for node in nx.shortest_path(
                self.graph.get_undirected_graph(),
                source=head_node,
                target=self.graph.vsource_node,
            ):
                container[node] = reduce(
                    operator.or_,
                    [
                        set() if container.get(node) is None else container.get(node),
                        tr_head_node_phase,
                    ],
                )
                three_phase = {Phase.A, Phase.B, Phase.C}
                two_phase_sets = list(combinations(three_phase, 2))
                if container[node] in two_phase_sets:
                    container[node] = three_phase

    def _update_node_phases_downward_from_transformer(
        self,
        mapper: list[TransformerPhaseMapperModel],
        container: dict,
    ):
        """Internal method to update nodes downward of the transformer."""
        for tr in mapper:
            tr_nodes = list(self._get_nodes_by_edge_names([tr.tr_name]))
            head_node = self._get_head_node(tr.tr_name)
            lt_node = list(set(tr_nodes) - set([head_node]))[0]
            lt_phase = container[lt_node]
            is_split_phase = set([Phase.S1, Phase.N, Phase.S2]) == lt_phase
            for descendant in nx.descendants(self.graph.get_dfs_tree(), source=head_node):
                if descendant not in container:
                    container[descendant] = (
                        set([Phase.S1, Phase.S2]) if is_split_phase else lt_phase
                    )

    @cached_property
    def node_phase_mapping(self) -> dict[str, set[Phase]]:
        node_phase_mapping: dict[str, set[Phase]] = {}
        self._update_transformer_node_phases(
            self.mapper, node_phase_mapping, self._transformer_phase_mapping
        )
        self._update_node_phases_upward_from_transformer(self.mapper, node_phase_mapping)
        self._update_node_phases_downward_from_transformer(self.mapper, node_phase_mapping)
        return node_phase_mapping

    @cached_property
    def asset_phase_mapping(self) -> dict[str, dict[VALID_NODE_TYPES, set[Phase]]]:
        asset_mapping: dict[str, dict[VALID_NODE_TYPES, set[Phase]]] = {}
        for node in self.graph.get_nodes():
            asset_mapping[node.name] = {
                asset: self.node_phase_mapping[node.name] for asset in node.assets
            }
        return asset_mapping

    @cached_property
    def transformer_phase_mapping(self) -> dict[str, set[Phase]]:
        _ = self.node_phase_mapping
        return self._transformer_phase_mapping
