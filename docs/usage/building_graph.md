# Building Distribution Graph

Assuming you have list of parcels (of type `ParcelModel` from shift). Here is a script to
generate distribution graph.


```python
from shift import ParcelModel, get_kmeans_clusters, PRSG

def _get_parcel_points(parcels: list[ParcelModel]) -> list[GeoLocation]:
    return [el.geometry[0] if isinstance(el.geometry, list) else el.geometry for el in parcels]


num_clusters = int(len(points) / 2)
clusters = get_kmeans_clusters(max([num_clusters, 1]), _get_parcel_points(points))

builder = PRSG(
    groups=clusters,
    source_location=GeoLocation(-87.7044461105055, 41.049957636092465),
)
graph = builder.get_distribution_graph()
```
Here we are first creating clusters of approximately 10 customers each and using cluster center
as distribution transformer location to build distribution graph. A distribution graph is simply a
connectivity model between nodes and edges. `PRSG` class builds primary distribution network
by reducing road network available in the area abd builds secondary network using 2d grid approach.
The node closest to `source_location` will be treated as substation.


If you want to visualize this graph, you can again use `PlotManager`.

```python
from shift import add_distribution_graph_to_plot, PlotManager
add_distribution_graph_to_plot(graph, plot_manager)
plot_manager.show()
```