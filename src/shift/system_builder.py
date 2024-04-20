from uuid import uuid4

from gdm import (
    DistributionSystem,
    DistributionBus,
    VoltageTypes,
    DistributionBranch,
    DistributionTransformer,
    MatrixImpedanceBranchEquipment,
    MatrixImpedanceBranch,
    SequenceImpedanceBranchEquipment,
    SequenceImpedanceBranch,
    GeometryBranchEquipment,
    GeometryBranch,
    MatrixImpedanceFuseEquipment,
    MatrixImpedanceFuse,
    MatrixImpedanceSwitch,
    MatrixImpedanceRecloser,
    MatrixImpedanceRecloserEquipment,
    MatrixImpedanceSwitchEquipment,
    DistributionTransformerEquipment,
    Phase,
)

from shift.graph.distribution_graph import (
    VALID_NODE_TYPES,
    DistributionGraph,
    EdgeModel,
    NodeModel,
)
from shift.mapper.base_equipment_mapper import BaseEquipmentMapper
from shift.mapper.base_phase_mapper import BasePhaseMapper
from shift.mapper.base_voltage_mapper import BaseVoltageMapper


EQUIPMENT_TO_CLASS_TYPE = {
    MatrixImpedanceBranch: MatrixImpedanceBranchEquipment,
    MatrixImpedanceFuse: MatrixImpedanceFuseEquipment,
    MatrixImpedanceRecloser: MatrixImpedanceRecloserEquipment,
    MatrixImpedanceSwitch: MatrixImpedanceSwitchEquipment,
    SequenceImpedanceBranch: SequenceImpedanceBranchEquipment,
    GeometryBranch: GeometryBranchEquipment,
    DistributionTransformer: DistributionTransformerEquipment,
}


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
            for asset in node.assets:
                self._add_asset(node.name, asset)

        for from_node, to_node, edge_data in self.dist_graph.get_edges():
            equipment = self.equipment_mapper.edge_equipment_mapping[edge_data.name]
            if type(equipment) != EQUIPMENT_TO_CLASS_TYPE.get(edge_data.edge_type):
                msg = (
                    f"{equipment=} is not supported for {edge_data=}"
                    f"Supported types are {EQUIPMENT_TO_CLASS_TYPE.keys()}"
                )
                raise NotImplementedError(msg)
            if edge_data.edge_type == DistributionBranch:
                self._add_branch(from_node, to_node, edge_data.edge_type, edge_data.name)
            elif edge_data.edge_type == DistributionTransformer:
                self._add_transformer(from_node, to_node, edge_data.edge_type, edge_data.name)
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
            nominal_voltage=self.voltage_mapper.node_voltage_mapping[node_obj.name],
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

    def _add_transformer(self, from_node: str, to_node: str, edge_data: EdgeModel):
        """Internal method to add transformer."""
        from_bus_phase = self.phase_mapper.node_phase_mapping[from_node]
        to_bus_phase = self.phase_mapper.node_phase_mapping[to_node]
        tr_phase = self.phase_mapper.transformer_phase_mapping[edge_data.name]

        from_wdg_phase = from_bus_phase if set([Phase.S1, Phase.S2]) & from_bus_phase else tr_phase
        to_wdg_phase = to_bus_phase if set([Phase.S1, Phase.S2]) & to_bus_phase else tr_phase

        edge = edge_data.edge_type(
            name=edge_data.name,
            buses=[
                self._system.get_component(DistributionBus, from_node),
                self._system.get_component(DistributionBus, to_node),
            ],
            winding_phases=[from_wdg_phase, to_wdg_phase],
            equipment=self.equipment_mapper.edge_equipment_mapping[edge_data.name],
        )
        self._system.add_component(edge)

    def get_system(self) -> DistributionSystem:
        """Method to return distribution system.

        Returns
        -------
        DistributionSystem
        """
        return self._system
