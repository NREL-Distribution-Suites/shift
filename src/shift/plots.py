import networkx as nx


from shift.data_model import GeoLocation, ParcelModel
from shift.graph.distribution_graph import DistributionGraph
from shift.mapper.base_phase_mapper import BasePhaseMapper
from shift.mapper.base_voltage_mapper import BaseVoltageMapper
from shift.plot_manager import PlotManager


def add_parcels_to_plot(
    parcels: list[ParcelModel], plot_manager: PlotManager, name: str = "Polygon Parcels"
):
    """Plots given list of parcels.

    Parameters
    ----------

    parcels: list[ParcelModel]
        List of parcels to plot
    plot_manager: PlotManager
        Plot manager instance
    name: str
        Name of the plot.

    Examples
    --------

    >>> from shift import PlotManager
    >>> plt_instance = PlotManager(GeoLocation(0, 0))
    >>> add_parcels_to_plots(
        parcels=[ParcelModel(name="parcel-1", geometry=GeoLocation(0, 0))],
        plot_manager=plt_instance
        )
    """

    point_geometries = [
        el.geometry for el in list(filter(lambda x: isinstance(x.geometry, GeoLocation), parcels))
    ]
    if point_geometries:
        plot_manager.add_plot(
            geometries=point_geometries,
            name=name,
        )
    multipoint_geoms = (
        [el.geometry for el in list(filter(lambda x: isinstance(x.geometry, list), parcels))],
    )[0]

    if multipoint_geoms:
        plot_manager.add_plot(
            geometries=multipoint_geoms,
            name=name,
            mode="lines",
        )


def add_xy_network_to_plot(graph: nx.Graph, plot_manager: PlotManager, name: str = "Graph nodes"):
    """Function to plot xy network.

    Assumes longitude is availabe as `x` and latitude is
    available as `y`.

    Parameters
    ----------

    graph: nx.Graph
        Instance of the graph.
    plot_manager: PlotManager
        PlotManager Instance.
    name: str
        Name of the plot.

    Examples
    --------

    >>> import networkx as nx
    >>> from shift import PlotManager, GeoLocation
    >>> graph = nx.Graph()
    >>> graph.add_node("node1", x=-97.332, y=43.223)
    >>> graph.add_node("node2", x=-97.334, y=43.334)
    >>> graph.add_edge("node1", "node2")
    >>> plt_instance = PlotManager(GeoLocation(-97.332, 43.223))
    >>> add_xy_network_to_plots(graph, plt_instance)
    >>> plt_instance.show()
    """
    node_data = dict(graph.nodes(data=True))
    geometries = [
        [GeoLocation(node_data[node]["x"], node_data[node]["y"]) for node in edge[:2]]
        for edge in graph.edges
    ]
    plot_manager.add_plot(
        geometries=geometries,
        name=name,
        mode="lines+markers",
    )


def add_distribution_graph_to_plot(
    graph: DistributionGraph, plot_manager: PlotManager, name: str = "Graph nodes"
):
    """Function to plot distribution graph.

    Parameters
    ----------

    graph: DistributionGraph
        Instance of the `DistributionGraph`.
    plot_manager: PlotManager
        PlotManager Instance.
    name: str
        Name of the plot.
    """
    geometries = [
        [
            GeoLocation(node.location.x, node.location.y)
            for node in [graph.get_node(from_node), graph.get_node(to_node)]
        ]
        for from_node, to_node, _ in graph.get_edges()
    ]
    plot_manager.add_plot(
        geometries=geometries,
        name=name,
        mode="lines+markers",
    )


def add_phase_mapper_to_plot(phase_mapper: BasePhaseMapper, plot_manager: PlotManager):
    """Function to add plots for different combinations of phases."""

    combinations = set(map(frozenset, phase_mapper.node_phase_mapping.values()))

    for combination in combinations:
        geometries = []
        for from_node, to_node, edge in phase_mapper.graph.get_edges():
            if (
                phase_mapper.node_phase_mapping[from_node] == combination
                or phase_mapper.node_phase_mapping[to_node] == combination
            ):
                geometries.append(
                    [
                        GeoLocation(node.location.x, node.location.y)
                        for node in [
                            phase_mapper.graph.get_node(from_node),
                            phase_mapper.graph.get_node(to_node),
                        ]
                    ]
                )
        if geometries:
            plot_manager.add_plot(
                geometries=geometries,
                name=f"{','.join([el.value for el in combination])}",
                mode="lines",
            )


def add_voltage_mapper_to_plot(voltage_mapper: BaseVoltageMapper, plot_manager: PlotManager):
    """Function to add plots for different combinations of phases."""

    voltage_levels = set(voltage_mapper.node_voltage_mapping.values())

    for combination in voltage_levels:
        geometries = []
        for node in voltage_mapper.graph.get_nodes():
            if voltage_mapper.node_voltage_mapping[node.name] == combination:
                geometries.append([GeoLocation(node.location.x, node.location.y)])
        if geometries:
            plot_manager.add_plot(
                geometries=geometries,
                name=f"{combination.magnitude} {combination.units}",
                mode="markers",
            )
