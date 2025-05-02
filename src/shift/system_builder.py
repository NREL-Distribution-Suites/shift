from functools import reduce
import operator
from uuid import uuid4
import math

from gdm.distribution.equipment import DistributionTransformerEquipment
from gdm.distribution import DistributionSystem
from gdm.distribution.components import (
    DistributionTransformer,
    DistributionBranchBase,
    DistributionBus,
)
from gdm.distribution.enums import (
    VoltageTypes,
    Phase,
)
from gdm.quantities import PositiveVoltage
import numpy as np

from shift.data_model import (
    VALID_NODE_TYPES,
    EdgeModel,
    NodeModel,
)
from shift.graph.distribution_graph import DistributionGraph
from shift.mapper.base_equipment_mapper import BaseEquipmentMapper
from shift.mapper.base_phase_mapper import BasePhaseMapper
from shift.mapper.base_voltage_mapper import BaseVoltageMapper
from shift.constants import EQUIPMENT_TO_CLASS_TYPE


class DistributionSystemBuilder:
    """Class interface for building distribution system.


    Parameters
    ----------
    name: str
        Name of the system.
    dist_graph: DistributionGraph
        Instance of the `DistributionGraph`.
    phase_mapper: BasePhaseMapper
        Instance of class of type `BasePhaseMapper`.
    voltage_mapper: BaseVoltageMapper
        Instance of class of type `BaseVoltageMapper`.
    equipment_mapper: BaseEquipmentMapper
        Instance of class of type `BaseEquipmentMapper`.

    """

    def __init__(
        self,
        name: str,
        dist_graph: DistributionGraph,
        phase_mapper: BasePhaseMapper,
        voltage_mapper: BaseVoltageMapper,
        equipment_mapper: BaseEquipmentMapper,
    ):
        self.dist_graph = dist_graph
        self.phase_mapper = phase_mapper
        self.voltage_mapper = voltage_mapper
        self.equipment_mapper = equipment_mapper

        self._system = DistributionSystem(name=name, auto_add_composed_components=True)
        self._build_system()

    def _build_system(self):
        """Internal method to build distribution system."""
        for node in self.dist_graph.get_nodes():
            self._add_bus(node)
            for asset in node.assets or {}:
                self._add_asset(node.name, asset)

        for from_node, to_node, edge_data in self.dist_graph.get_edges():
            equipment = self.equipment_mapper.edge_equipment_mapping[edge_data.name]

            if type(equipment) is not EQUIPMENT_TO_CLASS_TYPE.get(edge_data.edge_type):
                msg = (
                    f"{equipment=} is not supported for {edge_data=}"
                    f"Supported types are {EQUIPMENT_TO_CLASS_TYPE.keys()}"
                )
                raise NotImplementedError(msg)
            if issubclass(edge_data.edge_type, DistributionBranchBase):
                self._add_branch(from_node, to_node, edge_data)
            elif issubclass(edge_data.edge_type, DistributionTransformer):
                self._add_transformer(from_node, to_node, edge_data)
            else:
                msg = f"{edge_data.edge_type=} not supported. {edge_data=}"
                raise NotImplementedError(msg)

    def _add_asset(self, bus_name: str, asset_type: VALID_NODE_TYPES):
        """Internal method to add asset to a bus."""
        asset_obj = asset_type(
            name=str(uuid4()),
            bus=self._system.get_component(DistributionBus, bus_name),
            phases=self.phase_mapper.asset_phase_mapping[bus_name][asset_type],
            equipment=self.equipment_mapper.node_asset_equipment_mapping[bus_name][asset_type],
        )

        self._system.add_component(asset_obj)

    def _add_bus(self, node_obj: NodeModel):
        """Internal method to add bus in the system."""
        bus = DistributionBus(
            name=node_obj.name,
            phases=self.phase_mapper.node_phase_mapping[node_obj.name],
            coordinate=node_obj.location,
            rated_voltage=self.voltage_mapper.node_voltage_mapping[node_obj.name],
            voltage_type=VoltageTypes.LINE_TO_GROUND,
        )
        self._system.add_component(bus)

    def _add_branch(self, from_node: str, to_node: str, edge_data: EdgeModel):
        """Internal method to add branch."""
        edge = edge_data.edge_type(
            name=edge_data.name,
            buses=[
                self._system.get_component(DistributionBus, from_node),
                self._system.get_component(DistributionBus, to_node),
            ],
            phases=self.phase_mapper.node_phase_mapping[from_node]
            & self.phase_mapper.node_phase_mapping[to_node],
            equipment=self.equipment_mapper.edge_equipment_mapping[edge_data.name],
            length=edge_data.length,
        )
        self._system.add_component(edge)

    @staticmethod
    def _get_wdg_voltages(tr_equipment: DistributionTransformerEquipment) -> PositiveVoltage:
        """Internal method to return winding phase voltages."""
        return PositiveVoltage(
            [
                wdg.rated_voltage.to("kilovolt").magnitude
                / (
                    1 / math.sqrt(3)
                    if wdg.voltage_type == VoltageTypes.LINE_TO_GROUND
                    else 1
                    if not tr_equipment.is_center_tapped
                    else 2
                )
                for wdg in tr_equipment.windings
            ],
            "kilovolt",
        )

    def _get_wdg_buses(
        self, from_node: str, to_node: str, tr_equipment: DistributionTransformerEquipment
    ) -> list[str]:
        """Internal method to get buses for tranformer equipment windings."""
        wdg_voltages = self._get_wdg_voltages(tr_equipment)
        from_bus_voltage = self.voltage_mapper.node_voltage_mapping[from_node]
        to_bus_voltage = self.voltage_mapper.node_voltage_mapping[to_node]
        buses = [from_node, to_node]
        voltages = np.array(
            [from_bus_voltage.to("kilovolt").magnitude, to_bus_voltage.to("kilovolt").magnitude],
        )
        mapped_buses = [
            buses[abs(voltages - el.to("kilovolt").magnitude).argmin()] for el in wdg_voltages
        ]
        if len(set(mapped_buses)) != len(set(wdg_voltages)):
            msg = f"{set(mapped_buses)=} not matching winding voltages {set(wdg_voltages)=}"
            raise ValueError(msg)
        return mapped_buses

    def _get_wdg_phases(self, wdg_buses: list[str]) -> list[set[Phase]]:
        """Internal method to return phases for winding nodes."""
        wdg_phases = [self.phase_mapper.node_phase_mapping[bus] for bus in wdg_buses]
        is_split_phase = bool(set([Phase.S1, Phase.S2]) & reduce(operator.or_, wdg_phases))
        if not is_split_phase:
            return wdg_phases
        if len(wdg_buses) != 3 or len(set(wdg_buses)) != 2:
            msg = f"Invalid split phase winding buses {wdg_buses=}"
            raise ValueError(msg)
        split_phases = [set([Phase.S1, Phase.N]), set([Phase.N, Phase.S2])]
        for idx, wdg_ph in enumerate(wdg_phases):
            if not bool(set([Phase.S1, Phase.S2]) & wdg_ph):
                split_phases.insert(idx, wdg_ph)
        return split_phases

    def _add_transformer(self, from_node: str, to_node: str, edge_data: EdgeModel):
        """Internal method to add transformer."""
        tr_equipment: DistributionTransformerEquipment = (
            self.equipment_mapper.edge_equipment_mapping[edge_data.name]
        )

        wdg_buses = self._get_wdg_buses(from_node, to_node, tr_equipment)
        wdg_phases = self._get_wdg_phases(wdg_buses)

        edge = edge_data.edge_type(
            name=edge_data.name,
            buses=[self._system.get_component(DistributionBus, node) for node in wdg_buses],
            winding_phases=wdg_phases,
            equipment=tr_equipment,
        )
        self._system.add_component(edge)

    def get_system(self) -> DistributionSystem:
        """Method to return distribution system.

        Returns
        -------
        DistributionSystem
        """
        return self._system
