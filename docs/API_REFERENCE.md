# API Quick Reference

Quick reference guide for NREL-shift's main classes and functions.

## Data Models

### GeoLocation
```python
from shift import GeoLocation

# Create a geographic location
location = GeoLocation(longitude=-97.33, latitude=32.75)
```

### ParcelModel
```python
from shift import ParcelModel, GeoLocation

# Create a parcel with point geometry
parcel = ParcelModel(
    name="parcel-1",
    geometry=GeoLocation(-97.33, 32.75),
    building_type="residential",
    city="Fort Worth",
    state="TX",
    postal_address="76102"
)
```

### NodeModel
```python
from shift import NodeModel
from infrasys import Location
from gdm.distribution.components import DistributionLoad

# Create a node for the distribution graph
node = NodeModel(
    name="node-1",
    location=Location(x=-97.33, y=32.75),
    assets={DistributionLoad}
)
```

### EdgeModel
```python
from shift import EdgeModel
from gdm.distribution.components import DistributionBranchBase
from gdm.quantities import Distance

# Create an edge for the distribution graph
edge = EdgeModel(
    name="line-1",
    edge_type=DistributionBranchBase,
    length=Distance(100, "m")
)
```

## Data Fetching

### Fetch Parcels
```python
from shift import parcels_from_location, GeoLocation
from gdm.quantities import Distance

# By address
parcels = parcels_from_location("Fort Worth, TX", Distance(500, "m"))

# By coordinates
location = GeoLocation(longitude=-97.33, latitude=32.75)
parcels = parcels_from_location(location, Distance(500, "m"))

# By polygon
polygon = [
    GeoLocation(-97.33, 32.75),
    GeoLocation(-97.32, 32.76),
    GeoLocation(-97.31, 32.75)
]
parcels = parcels_from_location(polygon)
```

### Get Road Network
```python
from shift import get_road_network
from gdm.quantities import Distance

# Get road network by address
network = get_road_network("Fort Worth, TX", Distance(500, "m"))

# Returns: networkx.Graph
```

## Graph Construction

### DistributionGraph
```python
from shift import DistributionGraph, NodeModel, EdgeModel
from gdm.distribution.components import DistributionBranchBase
from infrasys import Location

# Create graph
graph = DistributionGraph()

# Add nodes
node1 = NodeModel(name="node-1", location=Location(x=-97.33, y=32.75))
node2 = NodeModel(name="node-2", location=Location(x=-97.32, y=32.76))
graph.add_node(node1)
graph.add_node(node2)

# Add edge
edge = EdgeModel(name="line-1", edge_type=DistributionBranchBase)
graph.add_edge("node-1", "node-2", edge_data=edge)

# Query nodes
all_nodes = graph.get_nodes()
single_node = graph.get_node("node-1")
filtered_nodes = graph.get_nodes(filter_func=lambda n: n.assets is not None)

# Query edges
all_edges = graph.get_edges()
single_edge = graph.get_edge("node-1", "node-2")

# Remove elements
graph.remove_node("node-1")
graph.remove_edge("node-1", "node-2")

# Copy graph
graph_copy = graph.copy()
```

### OpenStreetGraphBuilder
```python
from shift import OpenStreetGraphBuilder
from gdm.quantities import Distance

# Build graph from OpenStreetMap
builder = OpenStreetGraphBuilder(
    location="Fort Worth, TX",
    search_distance=Distance(500, "m")
)
graph = builder.build()
```

## Mappers

### BalancedPhaseMapper
```python
from shift import BalancedPhaseMapper
from gdm.quantities import ApparentPower

# Create phase mapper
phase_mapper = BalancedPhaseMapper(
    dist_graph=graph,
    transformers=[
        {
            "name": "tx-1",
            "capacity": ApparentPower(50, "kVA"),
            "type": "THREE_PHASE"
        }
    ]
)

# Access phase mappings
asset_phases = phase_mapper.asset_phase_mapping
branch_phases = phase_mapper.branch_phase_mapping
```

### TransformerVoltageMapper
```python
from shift import TransformerVoltageMapper
from gdm.quantities import Voltage

# Create voltage mapper
voltage_mapper = TransformerVoltageMapper(
    dist_graph=graph,
    primary_voltage=Voltage(12.47, "kV"),
    secondary_voltage=Voltage(0.24, "kV")
)

# Access voltage mappings
bus_voltages = voltage_mapper.bus_voltage_mapping
```

### EdgeEquipmentMapper
```python
from shift import EdgeEquipmentMapper

# Create equipment mapper
equipment_mapper = EdgeEquipmentMapper(dist_graph=graph)

# Access equipment mappings
node_equipment = equipment_mapper.node_asset_equipment_mapping
edge_equipment = equipment_mapper.edge_equipment_mapping
```

## System Builder

### DistributionSystemBuilder
```python
from shift import DistributionSystemBuilder

# Build the complete system
system = DistributionSystemBuilder(
    name="my_feeder",
    dist_graph=graph,
    phase_mapper=phase_mapper,
    voltage_mapper=voltage_mapper,
    equipment_mapper=equipment_mapper
)

# Access the built system
gdm_system = system._system
```

## Utility Functions

### Clustering
```python
from shift import get_kmeans_clusters, GeoLocation

# Cluster points
points = [
    GeoLocation(-97.33, 32.75),
    GeoLocation(-97.32, 32.76),
    GeoLocation(-97.31, 32.77)
]
clusters = get_kmeans_clusters(num_cluster=2, points=points)

# Each cluster has center and points
for cluster in clusters:
    print(f"Center: {cluster.center}")
    print(f"Points: {len(cluster.points)}")
```

### Nearest Points
```python
from shift import get_nearest_points

# Find nearest points
source = [[1, 2], [2, 3], [3, 4]]
target = [[4, 5], [0.5, 1.5]]
nearest = get_nearest_points(source, target)
# Returns: numpy array of nearest points
```

### Mesh Network
```python
from shift import get_mesh_network, GeoLocation
from gdm.quantities import Distance

# Create mesh network
corner1 = GeoLocation(-97.33, 32.75)
corner2 = GeoLocation(-97.32, 32.76)
mesh = get_mesh_network(corner1, corner2, Distance(100, "m"))
# Returns: networkx.Graph
```

### Split Network Edges
```python
from shift import split_network_edges
from gdm.quantities import Distance
import networkx as nx

# Create graph
graph = nx.Graph()
graph.add_node("node_1", x=-97.33, y=32.75)
graph.add_node("node_2", x=-97.32, y=32.76)
graph.add_edge("node_1", "node_2")

# Split long edges
split_network_edges(graph, split_length=Distance(50, "m"))
```

### Polygon from Points
```python
from shift import get_polygon_from_points
from gdm.quantities import Distance

# Create polygon buffer around points
points = [[-97.33, 32.75], [-97.32, 32.76]]
polygon = get_polygon_from_points(points, Distance(20, "m"))
# Returns: shapely.Polygon
```

## Visualization

### PlotManager
```python
from shift import PlotManager, GeoLocation
from shift import add_parcels_to_plot, add_xy_network_to_plot

# Create plot manager
plot_manager = PlotManager(center=GeoLocation(-97.33, 32.75))

# Add elements to plot
plot_manager.add_plot(
    [GeoLocation(-97.33, 32.75), GeoLocation(-97.32, 32.76)],
    name="my-line"
)

# Add parcels
add_parcels_to_plot(parcels, plot_manager)

# Add network
add_xy_network_to_plot(network, plot_manager)

# Show plot
plot_manager.show()
```

## Constants

### Transformer Types
```python
from shift import TransformerTypes

TransformerTypes.THREE_PHASE
TransformerTypes.SINGLE_PHASE
TransformerTypes.SPLIT_PHASE
TransformerTypes.SINGLE_PHASE_PRIMARY_DELTA
TransformerTypes.SPLIT_PHASE_PRIMARY_DELTA
```

### Valid Types
```python
from shift import VALID_NODE_TYPES, VALID_EDGE_TYPES

# Node types: DistributionLoad, DistributionSolar, 
#             DistributionCapacitor, DistributionVoltageSource

# Edge types: DistributionBranchBase, DistributionTransformer
```

## Exceptions

```python
from shift.exceptions import (
    ShiftBaseException,
    EdgeAlreadyExists,
    EdgeDoesNotExist,
    NodeAlreadyExists,
    NodeDoesNotExist,
    VsourceNodeAlreadyExists,
    VsourceNodeDoesNotExists,
    InvalidInputError
)

# All exceptions inherit from ShiftBaseException
try:
    graph.add_node(existing_node)
except NodeAlreadyExists as e:
    print(f"Node already exists: {e}")
```

## See Also

- [Complete Example](complete_example.md)
- [Building Graphs](building_graph.md)
- [Mapping Phases](mapping_phases.md)
- [Mapping Voltages](mapping_voltages.md)
- [Mapping Equipment](mapping_equipment.md)
