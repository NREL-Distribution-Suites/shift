import uuid

import networkx as nx
from shapely import MultiPoint, Point
from infrasys.quantities import Distance

from shift.data_model import GroupModel, GeoLocation
from shift.graph.openstreet_graph_builder import OpenStreetGraphBuilder
from shift.openstreet_roads import get_road_network
from shift.utils.mesh_network import get_mesh_network
from shift.utils.polygon_from_points import get_polygon_from_points
from shift.utils.split_network_edges import split_network_edges


class PRSG(OpenStreetGraphBuilder):
    """Class interface for Primary Road and Secondary Grid distribution graph builder.

    It searches for available openstreet road network within an area defined by
    `points` + `buffer`. Primary network is build by applying steiner tree algorithm from road
    network and connecting all nodes closest to the group centers, which will be treated as
    distribution transformer locations. Secondary network is build by building two dimensional
    grid within the bouding box formed by individual group points and then building steiner
    tree from it to connect only the nodes nearest to group points.
    """

    def build_secondary_network(self, group: GroupModel) -> nx.Graph:
        """Internal method to build secondary network.

        Parameters
        ----------
        group: GroupModel
            Group for which the secondary network is to be built.

        Returns
        -------
        nx.Graph

        """
        if len(group.points) == 1:
            sec_graph = nx.Graph()
            node_name = str(uuid.uuid4())
            sec_graph.add_node(node_name, x=group.center[0], y=group.center[1])
            return sec_graph

        minx, miny, maxx, maxy = MultiPoint([Point(*point) for point in group.points]).bounds
        sec_network = get_mesh_network(
            lower_left=GeoLocation(minx, miny),
            upper_right=GeoLocation(maxx, maxy),
            spacing=Distance(50, "m"),
        )
        return self._get_steiner_tree(
            sec_network,
            self._get_nearest_nodes(sec_network, group.points),
        )

    def build_primary_network(self) -> nx.Graph:
        """Internal method for building primary network.

        Returns
        -------
        nx.Graph
        """
        points = [point for group in self.groups for point in group.points]
        road_network_ = get_road_network(get_polygon_from_points(points, self.buffer))
        road_network = split_network_edges(road_network_, split_length=Distance(150, "m"))
        nearest_nodes = self._get_nearest_nodes(
            road_network, [c.center for c in self.groups] + [self.source_location]
        )
        return self._get_steiner_tree(
            road_network,
            nearest_nodes,
        )
