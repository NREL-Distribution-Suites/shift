# Updating Branch Type

In order to use right equipment, you need to update the branch types in the `DistributionGraph`.

Let's say, you want to use `MatrixImpedanceBranch` you can update branches in `graph` with following snippet.

```python
from shift import DistributionGraph
new_graph = DistributionGraph()
for node in graph.get_nodes():
    new_graph.add_node(node)
for from_node, to_node, edge in graph.get_edges():
    if edge.edge_type == DistributionBranch:
        edge.edge_type = MatrixImpedanceBranch
    new_graph.add_edge(from_node, to_node, edge_data=edge)

```