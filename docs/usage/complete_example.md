# Complete Example: Building a Distribution System

This example demonstrates the complete workflow of building a distribution system model using NREL-shift.

## Overview

We'll go through the following steps:
1. Fetch parcels from OpenStreetMap
2. Get road network
3. Build a distribution graph
4. Map equipment, phases, and voltages
5. Build the final distribution system

## Step-by-Step Guide

### Step 1: Import Required Modules

```python
from shift import (
    parcels_from_location,
    get_road_network,
    DistributionGraph,
    DistributionSystemBuilder,
    BaseGraphBuilder,
    OpenStreetGraphBuilder,
    BalancedPhaseMapper,
    TransformerVoltageMapper,
    EdgeEquipmentMapper,
    GeoLocation,
    NodeModel,
    EdgeModel,
    PlotManager,
    add_parcels_to_plot,
    add_xy_network_to_plot,
)

from gdm.quantities import Distance, Voltage, ApparentPower
from gdm.distribution.components import (
    DistributionLoad,
    DistributionVoltageSource,
    DistributionBranchBase,
    DistributionTransformer,
)
from infrasys import Location
```

### Step 2: Fetch Parcels and Road Network

```python
# Define location
location = "Fort Worth, TX"
search_distance = Distance(500, "m")

# Fetch parcels (buildings) from OpenStreetMap
parcels = parcels_from_location(location, search_distance)
print(f"Found {len(parcels)} parcels")

# Get road network
road_network = get_road_network(location, search_distance)
print(f"Road network has {road_network.number_of_nodes()} nodes and {road_network.number_of_edges()} edges")
```

### Step 3: Build Distribution Graph

There are two main approaches to building a distribution graph:

#### Approach A: Manual Graph Construction

```python
# Create empty graph
dist_graph = DistributionGraph()

# Add source node
source_node = NodeModel(
    name="source",
    location=Location(x=-97.33, y=32.75),
    assets={DistributionVoltageSource}
)
dist_graph.add_node(source_node)

# Add transformer nodes
for i, parcel in enumerate(parcels[:10]):  # First 10 parcels
    # Extract location from parcel
    if isinstance(parcel.geometry, list):
        # For polygon, use centroid
        lons = [loc.longitude for loc in parcel.geometry]
        lats = [loc.latitude for loc in parcel.geometry]
        location = Location(x=sum(lons)/len(lons), y=sum(lats)/len(lats))
    else:
        location = Location(x=parcel.geometry.longitude, y=parcel.geometry.latitude)
    
    # Create transformer node
    tx_node = NodeModel(
        name=f"tx_{i}",
        location=location,
        assets={DistributionLoad}
    )
    dist_graph.add_node(tx_node)
    
    # Connect source to transformer
    dist_graph.add_edge(
        "source",
        tx_node.name,
        edge_data=EdgeModel(
            name=f"line_{i}",
            edge_type=DistributionBranchBase,
            length=Distance(100, "m")
        )
    )
```

#### Approach B: Using OpenStreet Graph Builder

```python
from shift import OpenStreetGraphBuilder

# Build graph from OpenStreetMap data
graph_builder = OpenStreetGraphBuilder(
    location=location,
    search_distance=search_distance
)

# Get the distribution graph
dist_graph = graph_builder.build()
```

### Step 4: Map Equipment, Phases, and Voltages

```python
# Define equipment mapping
# This maps which equipment is used at each node/edge

# Example: Create simple equipment mapper
equipment_mapper = EdgeEquipmentMapper(dist_graph)

# Map phases (balance loads across phases)
phase_mapper = BalancedPhaseMapper(
    dist_graph=dist_graph,
    transformers=[
        {
            "name": f"tx_{i}",
            "capacity": ApparentPower(50, "kVA"),
            "type": "THREE_PHASE"
        }
        for i in range(10)
    ]
)

# Map voltages
voltage_mapper = TransformerVoltageMapper(
    dist_graph=dist_graph,
    primary_voltage=Voltage(12.47, "kV"),
    secondary_voltage=Voltage(0.24, "kV")
)
```

### Step 5: Build the Distribution System

```python
# Create the distribution system
system = DistributionSystemBuilder(
    name="fort_worth_feeder",
    dist_graph=dist_graph,
    phase_mapper=phase_mapper,
    voltage_mapper=voltage_mapper,
    equipment_mapper=equipment_mapper
)

print(f"Built system: {system._system.name}")
print(f"Total buses: {len(list(system._system.buses))}")
print(f"Total branches: {len(list(system._system.branches))}")
```

### Step 6: Visualize the Network (Optional)

```python
# Create plot manager
center_location = GeoLocation(-97.33, 32.75)
plot_manager = PlotManager(center=center_location)

# Add parcels to plot
add_parcels_to_plot(parcels, plot_manager)

# Add network to plot
add_xy_network_to_plot(road_network, plot_manager)

# Show the plot
plot_manager.show()
```

## Advanced Usage

### Custom Equipment Mapping

```python
from shift import BaseEquipmentMapper

class CustomEquipmentMapper(BaseEquipmentMapper):
    """Custom equipment mapper with specific equipment assignments."""
    
    def __init__(self, dist_graph):
        super().__init__(dist_graph)
        self._map_equipment()
    
    def _map_equipment(self):
        """Map equipment to nodes and edges."""
        # Your custom equipment mapping logic
        for node in self.dist_graph.get_nodes():
            # Assign equipment based on node properties
            pass
```

### Custom Phase Mapping

```python
from shift import BasePhaseMapper

class CustomPhaseMapper(BasePhaseMapper):
    """Custom phase mapper with specific phase assignments."""
    
    def __init__(self, dist_graph):
        super().__init__(dist_graph)
        self._assign_phases()
    
    def _assign_phases(self):
        """Assign phases to components."""
        # Your custom phase assignment logic
        pass
```

## Export to Simulator

Once you have built the system, you can export it to various power system simulators:

```python
# The system uses Grid Data Models, which can be exported to:
# - OpenDSS
# - CYME
# - Synergi
# - And other simulators via Ditto

# Export example (requires Ditto package)
# from ditto.writers.opendss import OpenDSSWriter
# writer = OpenDSSWriter()
# writer.write(system._system, output_path="./opendss_model")
```

## Tips and Best Practices

1. **Start Small**: Begin with a small search distance and few parcels when testing
2. **Validate Data**: Check the quality of OpenStreetMap data for your location
3. **Equipment Sizing**: Ensure transformer capacities match load requirements
4. **Phase Balance**: Use BalancedPhaseMapper for residential feeders
5. **Voltage Levels**: Verify voltage levels are appropriate for your region
6. **Error Handling**: Wrap API calls in try-except blocks for robustness

## Common Issues and Solutions

### Issue: No Parcels Found
**Solution**: Try increasing the search distance or choose a different location with better OpenStreetMap coverage.

### Issue: Graph is Disconnected
**Solution**: Use a road network builder or manually connect isolated components.

### Issue: Equipment Mapping Errors
**Solution**: Ensure all nodes and edges have appropriate equipment assignments before building the system.

## Next Steps

- Explore [Building a Graph](./building_graph.md) for detailed graph construction
- Learn about [Phase Mapping](./mapping_phases.md) for different strategies
- Check [Voltage Mapping](./mapping_voltages.md) for voltage assignment options
- See [Equipment Mapping](./mapping_equipment.md) for equipment configuration
