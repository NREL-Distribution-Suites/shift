from infrasys.quantities import Distance
from shapely import Polygon, MultiPoint, Point
import networkx as nx
from networkx.algorithms import approximation as ax

from shift.base_graph_builder import BaseGraphBuilder
from shift.distribution_graph import DistributionGraph
from shift.data_model import GeoLocation
from shift.cluster import get_kmeans_clusters
from shift.exceptions import InvalidInputError
from shift.openstreet_roads import get_road_network
from shift.nearest_nodes import get_nearest_nodes
from shift.split_network_edges import split_network_edges


class OpenStreetGraphBuilder(BaseGraphBuilder):
    """Class interface for building distribution graph using openstreet data.

    It searches for available openstreet road network within an area defined by
    `points` + `buffer`. Uses k-means algorithm to figure out transformer location
    and builds a minimum spanning tree connecting transformer locations. Secondary
    network is build by querying road network within the area served by an indentified
    distribution transformer.

    Parameters
    ----------

    points: list[GeoLocation]
        List of geolocations for building distribution graph.
    source_location: GeoLocation
        Power source location.
    num_customers_per_xfmr: int
        Typical number of customers served by a single distribution
        transformer.
    buffer: Distance
        Buffer to be applied in a bounding polygin formed
        by `points` for searching road network.

    Examples
    --------

    >>> from shift.parcel.openstreet import get_parcels
    >>> points = get_parcels("Fort Worth, Texas", Distance(100, "m"))
    >>> builder = OpenStreetGraphBuilder(points, GeoLocation(0, 0), 4)
    >>> graph = builder.get_graph()
    """

    def __init__(
        self,
        points: list[GeoLocation],
        source_location: GeoLocation,
        num_customers_per_xfmr: int,
        buffer: Distance = Distance(20, "m"),
    ):
        """Constructor for the class."""
        self.points = points
        self.source_location = source_location
        self.buffer = buffer
        self.num_customers_per_xfmr = num_customers_per_xfmr
        self.dist_graph = DistributionGraph()

        if len(points) < 2:
            msg = f"Number of points must be at least 2. {points=}"
            raise InvalidInputError(msg)

        if num_customers_per_xfmr < 1:
            msg = "Number of customers per transformer can not be less than 1."
            raise InvalidInputError(msg)

    @staticmethod
    def get_polygon(points: list[GeoLocation], buffer: Distance) -> Polygon:
        """Method to return bounding box polygon for a given set of points.

        Parameters
        ----------

        points: list[GeoLocation]
            List of geo location points
        buffer: Distance
            Buffer distance to include for getting road network.

        Returns
        -------

        Polygon
            Bounding box polygon
        """

        multipoints = MultiPoint([Point(*point) for point in points])
        minx, miny, maxx, maxy = multipoints.buffer((buffer.to("m") / 111139).magnitude).bounds
        return Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)])

    def get_distribution_graph(self) -> DistributionGraph:
        """Method to return distribution graph."""

        road_network_ = get_road_network(self.get_polygon(self.points, self.buffer))
        road_network = split_network_edges(road_network_, split_length=Distance(150, "m"))
        num_clusters = int(len(self.points) / self.num_customers_per_xfmr)
        clusters = get_kmeans_clusters(num_clusters if num_clusters > 1 else 1, self.points)
        road_nodes_mapper = {
            (data["x"], data["y"]): node
            for node, data in dict(road_network.nodes(data=True)).items()
        }
        nearest_nodes = get_nearest_nodes(
            list(road_nodes_mapper.keys()), [c.center for c in clusters] + [self.source_location]
        )
        nx.set_edge_attributes(road_network, 1, "weight")
        reduced_tree = ax.steiner_tree(
            road_network,
            [road_nodes_mapper[tuple(node)] for node in nearest_nodes],
            method="mehlhorn",
        )
        return reduced_tree
