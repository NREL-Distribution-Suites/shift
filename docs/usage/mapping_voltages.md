# Mapping voltages


You can either extend `BaseVoltageMapper` class or use existing 
phase mapper classes to map voltage to nodes.

Let's use transformer voltage mapper class to map voltages to nodes
using transformer voltages.

```python
from shift import TransformerVoltageMapper, TransformerVoltageModel
from gdm.quantities importPositiveVoltage
from gdm import DistributionTransformer

voltage_mapper = TransformerVoltageMapper(
    new_graph,
    xfmr_voltage=[
        TransformerVoltageModel(
            name=el.name,
            voltages=[PositiveVoltage(2.3, "kilovolt"), PositiveVoltage(120, "volt")],
        )
        for _, _, el in new_graph.get_edges()
        if el.edge_type is DistributionTransformer
    ],
)
```

