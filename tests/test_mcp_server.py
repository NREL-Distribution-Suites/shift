"""Tests for MCP server functionality."""

import pytest
from unittest.mock import patch

from shift.mcp_server.config import MCPServerConfig
from shift.mcp_server.state import StateManager
from shift.mcp_server.tools import (
    fetch_parcels_tool,
    cluster_parcels_tool,
    create_graph_tool,
    add_node_tool,
    add_edge_tool,
    query_graph_tool,
    list_resources_tool,
)
from shift import GeoLocation, ParcelModel


class TestStateManager:
    """Test StateManager functionality."""

    def test_create_graph(self, tmp_path):
        """Test creating a new graph."""
        manager = StateManager(storage_dir=None)
        graph_id = manager.create_graph("test_graph")

        assert graph_id == "test_graph"
        assert graph_id in manager.graphs
        assert manager.get_graph(graph_id) is not None

    def test_list_graphs(self):
        """Test listing graphs."""
        manager = StateManager()
        graph_id1 = manager.create_graph("graph1")
        graph_id2 = manager.create_graph("graph2")

        graphs = manager.list_graphs()
        assert len(graphs) == 2
        graph_ids = [g["id"] for g in graphs]
        assert graph_id1 in graph_ids
        assert graph_id2 in graph_ids

    def test_delete_graph(self):
        """Test deleting a graph."""
        manager = StateManager()
        graph_id = manager.create_graph("to_delete")

        assert manager.delete_graph(graph_id) is True
        assert manager.get_graph(graph_id) is None
        assert manager.delete_graph(graph_id) is False


class TestMCPTools:
    """Test MCP tool functions."""

    @pytest.fixture
    def state_manager(self):
        """Fixture providing a StateManager."""
        return StateManager()

    @patch("shift.mcp_server.tools.parcels_from_location")
    def test_fetch_parcels_tool_with_string(self, mock_fetch, state_manager):
        """Test fetching parcels with address string."""
        # Mock parcel data
        mock_parcels = [
            ParcelModel(
                name="parcel_0",
                geometry=GeoLocation(-97.33, 32.75),
                building_type="residential",
                city="Fort Worth",
                state="TX",
                postal_address="76102",
            )
        ]
        mock_fetch.return_value = mock_parcels

        result = fetch_parcels_tool(state_manager, location="Fort Worth, TX", distance_meters=500)

        assert result["success"] is True
        assert result["parcel_count"] == 1
        assert len(result["parcels"]) == 1
        mock_fetch.assert_called_once()

    @patch("shift.mcp_server.tools.parcels_from_location")
    def test_fetch_parcels_tool_with_coords(self, mock_fetch, state_manager):
        """Test fetching parcels with coordinates."""
        mock_fetch.return_value = []

        result = fetch_parcels_tool(
            state_manager, location={"longitude": -97.33, "latitude": 32.75}, distance_meters=500
        )

        assert result["success"] is True
        assert result["parcel_count"] == 0

    def test_fetch_parcels_tool_distance_limit(self, state_manager):
        """Test distance limit enforcement."""
        result = fetch_parcels_tool(
            state_manager,
            location="Test, TX",
            distance_meters=10000,  # Exceeds max
        )

        assert result["success"] is False
        assert "exceeds maximum" in result["error"]

    @patch("shift.mcp_server.tools.get_kmeans_clusters")
    def test_cluster_parcels_tool(self, mock_cluster, state_manager):
        """Test clustering parcels."""
        # Mock cluster data
        from shift.data_model import GroupModel

        mock_clusters = [
            GroupModel(center=GeoLocation(-97.33, 32.75), points=[GeoLocation(-97.33, 32.75)])
        ]
        mock_cluster.return_value = mock_clusters

        parcels = [{"name": "parcel_0", "geometry": {"longitude": -97.33, "latitude": 32.75}}]

        result = cluster_parcels_tool(state_manager, parcels, num_clusters=1)

        assert result["success"] is True
        assert result["cluster_count"] == 1

    def test_create_graph_tool(self, state_manager):
        """Test creating a graph via tool."""
        result = create_graph_tool(state_manager, name="test_graph")

        assert result["success"] is True
        assert "graph_id" in result
        assert result["graph_id"] == "test_graph"

    def test_add_node_tool(self, state_manager):
        """Test adding a node to a graph."""
        # Create graph first
        graph_id = state_manager.create_graph("test")

        result = add_node_tool(
            state_manager,
            graph_id=graph_id,
            node_name="node1",
            longitude=-97.33,
            latitude=32.75,
            assets=["DistributionLoad"],
        )

        assert result["success"] is True
        assert "node1" in result["message"]

    def test_add_node_tool_graph_not_found(self, state_manager):
        """Test adding node to non-existent graph."""
        result = add_node_tool(
            state_manager,
            graph_id="nonexistent",
            node_name="node1",
            longitude=-97.33,
            latitude=32.75,
        )

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_add_edge_tool(self, state_manager):
        """Test adding an edge to a graph."""
        # Create graph and nodes
        graph_id = state_manager.create_graph("test")
        graph = state_manager.get_graph(graph_id)

        from shift import NodeModel
        from infrasys import Location

        graph.add_node(NodeModel(name="n1", location=Location(x=-97.33, y=32.75)))
        graph.add_node(NodeModel(name="n2", location=Location(x=-97.32, y=32.76)))
        state_manager.save_graph(graph_id, graph)

        result = add_edge_tool(
            state_manager,
            graph_id=graph_id,
            from_node="n1",
            to_node="n2",
            edge_name="line1",
            edge_type="DistributionBranchBase",
            length_meters=100,
        )

        assert result["success"] is True

    def test_query_graph_tool_summary(self, state_manager):
        """Test querying graph summary."""
        graph_id = state_manager.create_graph("test")

        result = query_graph_tool(state_manager, graph_id, query_type="summary")

        assert result["success"] is True
        assert "node_count" in result
        assert "edge_count" in result

    def test_query_graph_tool_nodes(self, state_manager):
        """Test querying graph nodes."""
        graph_id = state_manager.create_graph("test")
        add_node_tool(state_manager, graph_id, "n1", -97.33, 32.75)

        result = query_graph_tool(state_manager, graph_id, query_type="nodes")

        assert result["success"] is True
        assert "nodes" in result
        assert len(result["nodes"]) == 1

    def test_list_resources_tool(self, state_manager):
        """Test listing resources."""
        state_manager.create_graph("graph1")
        state_manager.create_graph("graph2")

        result = list_resources_tool(state_manager, resource_type="graphs")

        assert result["success"] is True
        assert "graphs" in result
        assert len(result["graphs"]) == 2


class TestMCPServerConfig:
    """Test configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        cfg = MCPServerConfig()

        assert cfg.server_name == "nrel-shift-mcp-server"
        assert cfg.default_search_distance_m == 500.0
        assert cfg.max_search_distance_m == 5000.0
        assert cfg.log_level == "INFO"

    def test_config_validation(self):
        """Test configuration with custom values."""
        cfg = MCPServerConfig(server_name="custom-server", default_search_distance_m=1000.0)

        assert cfg.server_name == "custom-server"
        assert cfg.default_search_distance_m == 1000.0
