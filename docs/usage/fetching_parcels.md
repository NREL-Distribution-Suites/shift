# Getting Parcels

First step in building distribution model is to get parcels.
You can either bring your own parcels or provide location from where
parcels will be downloaded.

Fetching parcels from csv. Only requirement for this csv is it needs to have
`geometry` column. Shift uses geopandas to load geometries from this file.
Currently we only support `Point`, `Polygon` and `MultiPolygon` shapes.

```python
from shift import parcels_from_csv
points = parcels_from_csv("my_parcel.csv")
```

You can also fetch parcels by providing location. You can also provide point or polygon
to fetch parcels.

```python
from shift import parcels_from_location
from infrasys.quantites import Distance
points = parcels_from_location("Fort Worth, TX", Distance(400, "m"))
```

Now if you want to visualize these parcels. You can leverage plot manager.

```python
from shift import PlotManager, add_parcels_to_plots
import osmnx as ox
plot_manager = PlotManager(center=GeoLocation(*reversed(ox.geocode("Fort Worth, TX"))))
add_parcels_to_plots(points, plot_manager)
plot_manager.show()
```