from functools import cached_property
import math

from infrasys.component import Component
from gdm.dataset.dataset_system import DatasetSystem
from gdm.quantities import PositiveApparentPower, PositiveCurrent
from gdm import (
    DistributionTransformer,
    DistributionBranch,
    Phase,
    DistributionTransformerEquipment,
)

from shift.exceptions import EquipmentNotFoundError
from shift.graph.distribution_graph import DistributionGraph
from shift.mapper.base_equipment_mapper import BaseEquipmentMapper
from shift.mapper.base_phase_mapper import BasePhaseMapper
from shift.mapper.base_voltage_mapper import BaseVoltageMapper


class EdgeEquipmentMapper(BaseEquipmentMapper):
    """Class interface for selecting edge equipment
    based on load equipment.

    Parameters
    ----------
    graph: DistributionGraph
        Instance of the distribution graph.
    catalog_sys: DatasetSystem
        Instance of Dataset system containing catalogs.
    voltage_mapper: BaseVoltageMapper
        Instance of the voltage mapper.
    phase_mapper: BasePhaseMapper
        Instance of the base phase mapper.

    """

    def __init__(
        self,
        graph: DistributionGraph,
        catalog_sys: DatasetSystem,
        voltage_mapper: BaseVoltageMapper,
        phase_mapper: BasePhaseMapper,
    ):
        self.catalog_sys = catalog_sys
        self.voltage_mapper = voltage_mapper
        self.phase_mapper = phase_mapper
        super().__init__(graph)

    def _get_served_load(self, edge_name: str) -> PositiveApparentPower:
        """Internal method to get load served downward from this edge."""
        pass

    def _get_closest_higher_capacity_transformer(
        self, capacity: PositiveApparentPower
    ) -> Component:
        """Internal method to return transformer equipment by capacity."""
        trs: list[DistributionTransformerEquipment] = list(
            self.catalog_sys.get_components(
                DistributionTransformerEquipment,
                filter_func=lambda x: x.windings[0].rated_power > capacity,
            )
        )
        if not trs:
            msg = f"Equipment of type {DistributionTransformerEquipment} not found in catalog system."
            raise EquipmentNotFoundError(msg)

        return sorted(trs, key=lambda x: x.windings[0].rated_power)[0]

    def __get_closest_highest_capacity_branch(self, current: PositiveCurrent) -> Component:
        """Internal method to return closest conductor equipment."""

    @cached_property
    def edge_equipment_mapping(self) -> dict[str, Component]:
        edge_equipment_mapper = {}
        for from_node, _, edge in self.graph.get_edges():
            served_load = self._get_served_load(edge.name)
            if issubclass(edge.edge_type, DistributionTransformer):
                edge_equipment_mapper[edge.name] = self._get_closest_higher_capacity_transformer(
                    served_load
                )
            elif issubclass(edge.edge_type, DistributionBranch):
                kv = self.voltage_mapper.node_voltage_mapping[from_node].to("kilovolt").magnitude
                kva = served_load.to("kilova").magnitude
                phases = self.phase_mapper.node_phase_mapping[from_node] - set(Phase.N)
                num_phase = len(phases)
                is_split_phase = Phase.S1 in phases or Phase.S2 in phases
                current = (
                    kva / kv
                    if num_phase == 1
                    else kva / (2 * kv)
                    if is_split_phase
                    else kva / (math.sqrt(3) * kv)
                )

                edge_equipment_mapper[edge.name] = self._get_closest_highest_capacity_branch(
                    PositiveCurrent(current, "ampere")
                )
        return edge_equipment_mapper
