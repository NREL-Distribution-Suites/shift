"""Tests for AppContext state management and ServerConfig."""

import pytest

from shift.mcp_server.state import AppContext, GraphMeta
from shift.graph.distribution_graph import DistributionGraph


class TestGraphMeta:
    def test_defaults(self):
        meta = GraphMeta(name="g1", created_at="2026-01-01")
        assert meta.node_count == 0
        assert meta.edge_count == 0


class TestAppContext:
    def test_generate_id_unique(self):
        ids = {AppContext.generate_id() for _ in range(100)}
        assert len(ids) == 100

    def test_generate_id_length(self):
        assert len(AppContext.generate_id()) == 12

    def test_get_graph_success(self, app_context):
        graph = DistributionGraph()
        app_context.graphs["abc"] = graph
        assert app_context.get_graph("abc") is graph

    def test_get_graph_missing_raises(self, app_context):
        with pytest.raises(KeyError, match="No graph found"):
            app_context.get_graph("nonexistent")

    def test_refresh_graph_meta(self, populated_context):
        app, gid = populated_context
        # Add a node so counts change
        from shift.data_model import NodeModel
        from infrasys import Location

        app.graphs[gid].add_node(NodeModel(name="extra", location=Location(x=0, y=0)))
        app.refresh_graph_meta(gid)
        assert app.graph_meta[gid].node_count == 4  # 3 original + 1
        assert app.graph_meta[gid].edge_count == 2

    def test_empty_context_defaults(self):
        ctx = AppContext()
        assert ctx.graphs == {}
        assert ctx.phase_mappers == {}
        assert ctx.voltage_mappers == {}
        assert ctx.equipment_mappers == {}
        assert ctx.systems == {}
        assert ctx.docs_index == {}


class TestServerConfig:
    def test_defaults(self):
        from shift.mcp_server.config import ServerConfig

        cfg = ServerConfig()
        assert cfg.server_name == "nrel-shift-mcp-server"
        assert cfg.default_search_distance_m == 500.0
        assert cfg.max_search_distance_m == 5000.0
        assert cfg.default_cluster_count == 5
        assert cfg.log_level == "INFO"

    def test_load_defaults(self):
        from shift.mcp_server.config import ServerConfig

        cfg = ServerConfig.load()
        assert cfg.server_name == "nrel-shift-mcp-server"

    def test_load_nonexistent_path(self):
        from shift.mcp_server.config import ServerConfig

        cfg = ServerConfig.load("/nonexistent/path.yaml")
        assert cfg.server_name == "nrel-shift-mcp-server"

    def test_resolve_docs_path(self):
        from shift.mcp_server.config import ServerConfig

        cfg = ServerConfig()
        path = cfg.resolve_docs_path()
        assert path.is_absolute()

    def test_custom_docs_path(self, tmp_path):
        from shift.mcp_server.config import ServerConfig

        cfg = ServerConfig(docs_path=str(tmp_path))
        assert cfg.resolve_docs_path() == tmp_path
