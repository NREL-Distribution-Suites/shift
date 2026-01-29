# NREL-shift 

Python package for developing power distribution models using open-source data. This package uses [Grid Data Models](https://github.nrel.gov/CADET/grid-data-models) to represent power distribution components and [Ditto](https://github.nrel.gov/CADET/ditto) for writing case files specific to simulators such as OpenDSS, Cyme, Synergi and others.

Primarily this package leverages OpenStreetMap parcels and road networks to build synthetic distribution feeder models.

## Features

- **Automated Feeder Generation**: Build distribution feeder models from OpenStreetMap data
- **Graph-Based Network Modeling**: Use NetworkX graphs for flexible network representation
- **Equipment Mapping**: Map transformers, loads, and other equipment to network nodes and edges
- **Phase Balancing**: Automatically balance phases across distribution transformers
- **Voltage Mapping**: Assign appropriate voltage levels throughout the distribution network
- **Visualization Tools**: Built-in plotting capabilities using Plotly
- **Simulator Export**: Export models to various power system simulators via Grid Data Models
- **MCP Server**: Model Context Protocol server for AI assistant integration

## Installation

### From PyPI (when available)
```bash
pip install nrel-shift
```

### From Source
```bash
git clone https://github.com/NREL-Distribution-Suites/shift.git
cd shift
pip install -e .
```

### Development Installation
For development with testing and documentation tools:
```bash
pip install -e ".[dev,doc]"
```

### MCP Server Installation
For MCP (Model Context Protocol) server support:
```bash
pip install -e ".[mcp]"
```

See [MCP Server Documentation](./docs/MCP_SERVER.md) for details on using NREL-shift with AI assistants like Claude.

## Quick Start

### Fetch Parcels from OpenStreetMap
```python
from shift import parcels_from_location, GeoLocation
from gdm.quantities import Distance

# Fetch parcels by address
parcels = parcels_from_location("Fort Worth, TX", Distance(500, "m"))

# Or by coordinates
location = GeoLocation(longitude=-97.3, latitude=32.75)
parcels = parcels_from_location(location, Distance(500, "m"))
```

### Build a Road Network Graph
```python
from shift import get_road_network

# Get road network from address
graph = get_road_network("Fort Worth, TX", Distance(500, "m"))
```

### Create a Distribution System
```python
from shift import (
    DistributionSystemBuilder,
    DistributionGraph,
    BalancedPhaseMapper,
    TransformerVoltageMapper,
    EdgeEquipmentMapper
)

# Initialize components
dist_graph = DistributionGraph()
# ... add nodes and edges to graph

phase_mapper = BalancedPhaseMapper(dist_graph)
voltage_mapper = TransformerVoltageMapper(dist_graph)
equipment_mapper = EdgeEquipmentMapper(dist_graph)

# Build the system
system = DistributionSystemBuilder(
    name="my_feeder",
    dist_graph=dist_graph,
    phase_mapper=phase_mapper,
    voltage_mapper=voltage_mapper,
    equipment_mapper=equipment_mapper
)
```

## Documentation

For detailed usage and API documentation, see the [docs](./docs) directory:

### User Guides
- [Complete Example](./docs/usage/complete_example.md) - End-to-end workflow
- [Building a Graph](./docs/usage/building_graph.md)
- [Building a Distribution System](./docs/usage/building_system.md)
- [Fetching Parcels](./docs/usage/fetching_parcels.md)
- [Mapping Equipment](./docs/usage/mapping_equipment.md)
- [Mapping Phases](./docs/usage/mapping_phases.md)
- [Mapping Voltages](./docs/usage/mapping_voltages.md)

### Developer Resources
- [API Quick Reference](./docs/API_REFERENCE.md) - Quick lookup for all APIs
- [MCP Server Guide](./docs/MCP_SERVER.md) - AI assistant integration
- [Contributing Guidelines](./CONTRIBUTING.md) - How to contribute
- [Quick Start for Developers](./QUICKSTART.md) - Fast-track setup

## Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=shift --cov-report=html

# Run specific test file
pytest tests/test_graph.py
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/shift.git`
3. Install development dependencies: `pip install -e ".[dev,doc]"`
4. Create a feature branch: `git checkout -b feature-name`
5. Make your changes and add tests
6. Run tests: `pytest`
7. Run linter: `ruff check .`
8. Commit and push your changes
9. Create a pull request

## Requirements

- Python >= 3.10
- OSMnx (for OpenStreetMap data)
- NetworkX (for graph operations)
- Grid Data Models (for power system components)
- See [pyproject.toml](./pyproject.toml) for complete dependencies

## License

This project is licensed under the BSD-3-Clause License - see the [LICENSE.txt](./LICENSE.txt) file for details.

## Authors

- Kapil Duwadi (Kapil.Duwadi@nrel.gov)
- Aadil Latif (Aadil.Latif@nrel.gov)
- Erik Pohl (Erik.Pohl@nrel.gov)

## Citation

If you use this package in your research, please cite:

```bibtex
@software{nrel_shift,
  title = {NREL-shift: Framework for Developing Synthetic Distribution Feeder Models},
  author = {Duwadi, Kapil and Latif, Aadil and Pohl, Erik},
  year = {2026},
  url = {https://github.com/NREL-Distribution-Suites/shift}
}
```

## Support

For questions and support:
- Open an [issue](https://github.com/NREL-Distribution-Suites/shift/issues)
- Check the [documentation](https://github.com/NREL-Distribution-Suites/shift#readme) 