# Getting Parcels

First step in building distribution model is to get parcels.
You can either bring your own parcels or provide location from where
parcels will be downloaded.

There are three helper functions provided in SHIFT that enables users to fetch parcels


* `parcels_from_csv`: Fetching parcels from csv. Only requirement for this csv is it needs to have
`geometry` column. Shift uses geopandas to load geometries from this file.
Currently we only support `Point`, `Polygon` and `MultiPolygon` shapes.

```python
from shift import parcels_from_csv
points = parcels_from_csv("my_parcel.csv")
```

* `parcels_from_location`: You can also fetch parcels by providing location. You can also provide point or polygon
to fetch parcels.

```python
from shift import parcels_from_location
from infrasys.quantites import Distance
points = parcels_from_location("Fort Worth, TX", Distance(400, "m"))
```

* `parcels_from_geodataframe`: Finally, you can also fetch parcels directly from a geodataframe. 


Now if you want to visualize these parcels. You can leverage plot manager.

```python
from shift import PlotManager, GeoLocation, add_parcels_to_plot
import osmnx as ox
coordinate_center = GeoLocation(*reversed(ox.geocode("Fort Worth, TX")))
plot_manager = PlotManager(center=coordinate_center)
add_parcels_to_plot(points, plot_manager)
plot_manager.show()
```