# Mapping phases

You can either extend `BasePhaseMapper` class or use existing 
phase mapper classes to map phases to nodes and assets.

Let's use balanced phase mapper class to map phases to nodes and assets.
Here we are assuming all transformers are of split phase type and 25 kVA
for the purpose of mapping phases. Actual transformer size can vary depending 
upon which equipment is used by equipment mapper.


```python
from shift import TransformerPhaseMapperModel, TransformerTypes, BalancedPhaseMapper, add_phase_mapper_to_plot
from gdm import DistributionTransformer
from gdm.quantities import PositiveApparentPower

mapper = [
    TransformerPhaseMapperModel(
        tr_name=el.name,
        tr_type=TransformerTypes.SPLIT_PHASE,
        tr_capacity=PositiveApparentPower(
            25,
            "kilova",
        ),
        location=new_graph.get_node(from_node).location,
    )
    for from_node, _, el in new_graph.get_edges()
    if el.edge_type is DistributionTransformer
]

phase_mapper = BalancedPhaseMapper(new_graph, method="greedy", mapper=mapper)
plot_manager = PlotManager(center=coordinate_center)
add_phase_mapper_to_plot(phase_mapper, plot_manager)
plot_manager.show()
```