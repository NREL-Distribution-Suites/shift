# Mapping Equipment

You will need to extend exsiting equipment mapper class to map equipment
to nodes and edges depending on your need.

Here is an example where `EdgeEquipmentMapper` is extended to map equipment to nodes and assets.
`EdgeEquipmentMapper` takes care of mapping equipment to edges (both transformer and branch) from 
a given catalog. You can use any valid `DistributionSystem` as catalog. Here we are using `p4u.json`
file (which was created using ditto reader by passing P4U SMARTDS models.) as catalog file. 
We are mapping load kW based on parcels area in this example. Assuming `points` are already available.


```python
from shift import (
    EdgeEquipmentMapper, 
    BaseVoltageMapper,
    BasePhaseMapper,
    ParcelModel,
    GeoLocation
)

from gdm import (
    DistributionGraph,
    LoadEquipment,
    PhaseLoadEquipment,
    PhaseVoltageSourceEquipment,
    VoltageSourceEquipment
)
from gdm.quantities import (
    ReactivePower,
    Reactance
)

from infrasys import System
from infrasys.quantities import ActivePower, Resistance, Voltage, Angle

catalog_sys = DistributionSystem.from_json("p4u.json")

class AreaBasedLoadMapper(EdgeEquipmentMapper):

    def __init__(
        self,
        graph: DistributionGraph,
        catalog_sys: System,
        voltage_mapper: BaseVoltageMapper,
        phase_mapper: BasePhaseMapper,
        points: list[ParcelModel],
    ):

        self.points = points
        super().__init__(graph, catalog_sys, voltage_mapper, phase_mapper)

    def _get_area_for_node(self, node: NodeModel) -> float:
        """Internal function to return point"""
        tree = KDTree(_get_parcel_points(self.points))
        _, idx = tree.query([GeoLocation(node.location.x, node.location.y)], k=1)
        first_indexes = [el[0] for el in idx]
        nearest_point: ParcelModel = self.points[first_indexes[0]]
        return (
            Polygon(nearest_point.geometry).area if isinstance(nearest_point.geometry, list) else 0
        )

    @cached_property
    def node_asset_equipment_mapping(self):
        node_equipment_dict = {}

        for node in self.graph.get_nodes():
            node_equipment_dict[node.name] = {}
            area = self._get_area_for_node(node)
            if area > 10 and area < 30:
                kw = 1.2
            elif area <= 10:
                kw = 0.8
            else:
                kw = 1.3

            num_phase = len(self.phase_mapper.node_phase_mapping[node.name] - set(Phase.N))
            node_equipment_dict[node.name][DistributionLoad] = LoadEquipment(
                name=f"load_{node.name}",
                phase_loads=[
                    PhaseLoadEquipment(
                        name=f"load_{node.name}_{idx}",
                        z_real=ActivePower(0, "kilowatt"),
                        i_real=ActivePower(0, "kilowatt"),
                        p_real=ActivePower(kw / num_phase, "kilowatt"),
                        z_imag=ReactivePower(0, "kilovar"),
                        i_imag=ReactivePower(0, "kilovar"),
                        p_imag=ReactivePower(0, "kilovar"),
                    )
                    for idx in range(num_phase)
                ],
            )

            if DistributionVoltageSource in node.assets:
                node_equipment_dict[node.name][DistributionVoltageSource] = VoltageSourceEquipment(
                    name="vsource_test",
                    sources=[
                        PhaseVoltageSourceEquipment(
                            name=f"vsource_{idx}",
                            r0=Resistance(1e-5, "ohm"),
                            r1=Resistance(1e-5, "ohm"),
                            x0=Reactance(1e-5, "ohm"),
                            x1=Reactance(1e-5, "ohm"),
                            voltage=Voltage(27, "kilovolt"),
                            angle=Angle(0, "degree"),
                        )
                        for idx in range(3)
                    ],
                )

        return node_equipment_dict


eq_mapper = AreaBasedLoadMapper(
    new_graph,
    catalog_sys=catalog_sys,
    voltage_mapper=voltage_mapper,
    phase_mapper=phase_mapper,
    points=points,
)
```