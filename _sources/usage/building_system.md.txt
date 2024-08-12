# Building Distribution System

Creating distribution system from distribution graph and mappers.

```python
builder = DistributionSystemBuilder(
    name="Test system",
    dist_graph=new_graph,
    phase_mapper=phase_mapper,
    voltage_mapper=voltage_mapper,
    equipment_mapper=eq_mapper,
)
sys = builder.get_system()
sys.to_json(base_path / "system.json")
```