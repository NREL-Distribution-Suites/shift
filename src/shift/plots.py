import networkx as nx

from shift.data_model import GeoLocation, ParcelModel
from shift.plot_manager import PlotManager


def add_parcels_to_plots(parcels: list[ParcelModel], plot_manager: PlotManager):
    """Plots given list of parcels.

    Examples
    --------

    >>> plot_parcels(parcels=[ParcelModel(name="parcel-1", geometry=GeoLocation(0, 0))])
    """
    plot_manager.add_plot(
        geometries=[
            el.geometry
            for el in list(filter(lambda x: isinstance(x.geometry, GeoLocation), parcels))
        ],
        name="Point Parcels",
    )
    plot_manager.add_plot(
        geometries=[
            el.geometry for el in list(filter(lambda x: isinstance(x.geometry, list), parcels))
        ],
        name="Polygon Parcels",
        mode="lines",
    )


def add_xy_network_to_plots(graph: nx.Graph, plot_manager: PlotManager):
    """Method to plot network.

    Assumes longitude is availabe as `x` and latitude is
    available as `y`.
    """
    node_data = dict(graph.nodes(data=True))
    geometries = [
        [GeoLocation(node_data[node]["x"], node_data[node]["y"]) for node in edge[:2]]
        for edge in graph.edges
    ]
    plot_manager.add_plot(
        geometries=geometries,
        name="Graph Nodes",
        mode="lines+markers",
    )
