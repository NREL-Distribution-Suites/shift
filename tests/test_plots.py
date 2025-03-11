import pytest
import networkx as nx

from shift import PlotManager
from shift.data_model import GeoLocation, ParcelModel
from shift import add_parcels_to_plot, add_xy_network_to_plot


@pytest.fixture
def get_plot_manager():
    plt_manager = PlotManager(center=GeoLocation(10, 10))
    yield plt_manager


def test_plot_manager(get_plot_manager):
    """Function to test plot manager."""
    get_plot_manager.add_plot(
        [GeoLocation(10.1, 10.2), GeoLocation(10.15, 10.25)], name="test-plot"
    )


def test_add_parcel_to_plot(get_plot_manager):
    """Function to test adding parcels to plot manager."""
    add_parcels_to_plot(
        parcels=[
            ParcelModel(
                name="parcel-1",
                geometry=GeoLocation(0, 0),
                city="",
                state="",
                postal_address="",
                building_type="",
            )
        ],
        plot_manager=get_plot_manager,
    )


def test_adding_network_to_plot(get_plot_manager):
    """Function to test adding network to plot manager."""
    graph = nx.Graph()
    graph.add_node("node_1", x=-97.33, y=43.55)
    graph.add_node("node_2", x=-97.34, y=45.56)
    graph.add_edge("node_1", "node_2")
    add_xy_network_to_plot(graph, get_plot_manager)
