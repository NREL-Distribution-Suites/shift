# Building Distribution System

Creating distribution system from distribution graph and mappers.

```python
from shift import DistributionSystemBuilder

builder = DistributionSystemBuilder(
    name="Test system",
    dist_graph=graph,
    phase_mapper=phase_mapper,
    voltage_mapper=voltage_mapper,
    equipment_mapper=eq_mapper,
)
sys = builder.get_system()
sys.to_json(MODELS_FOLFER / "system.json")
```