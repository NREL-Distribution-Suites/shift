"""State management for MCP server sessions."""

import json
from typing import Dict, Optional, Any
from pathlib import Path
from uuid import uuid4
import networkx as nx
from loguru import logger

from shift import DistributionGraph


class StateManager:
    """Manages graph and system state across MCP sessions."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize state manager.

        Parameters
        ----------
        storage_dir : Optional[Path]
            Directory for persistent storage. If None, state is memory-only.
        """
        self.storage_dir = storage_dir
        self.graphs: Dict[str, DistributionGraph] = {}
        self.systems: Dict[str, Any] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

        if storage_dir:
            storage_dir.mkdir(parents=True, exist_ok=True)
            self._load_persisted_state()

    def create_graph(self, name: Optional[str] = None) -> str:
        """Create a new distribution graph.

        Parameters
        ----------
        name : Optional[str]
            Name for the graph. If None, generates a UUID.

        Returns
        -------
        str
            Graph ID
        """
        graph_id = name or f"graph_{uuid4().hex[:8]}"
        self.graphs[graph_id] = DistributionGraph()
        self.metadata[graph_id] = {"type": "graph", "name": name or graph_id, "created": True}
        logger.info(f"Created graph: {graph_id}")
        return graph_id

    def get_graph(self, graph_id: str) -> Optional[DistributionGraph]:
        """Get graph by ID.

        Parameters
        ----------
        graph_id : str
            Graph identifier

        Returns
        -------
        Optional[DistributionGraph]
            Graph instance or None if not found
        """
        return self.graphs.get(graph_id)

    def save_graph(self, graph_id: str, graph: DistributionGraph) -> None:
        """Save or update a graph.

        Parameters
        ----------
        graph_id : str
            Graph identifier
        graph : DistributionGraph
            Graph instance to save
        """
        self.graphs[graph_id] = graph
        if graph_id not in self.metadata:
            self.metadata[graph_id] = {"type": "graph", "name": graph_id}

        if self.storage_dir:
            self._persist_graph(graph_id, graph)

    def list_graphs(self) -> list[Dict[str, Any]]:
        """List all stored graphs.

        Returns
        -------
        list[Dict[str, Any]]
            List of graph metadata
        """
        return [
            {
                "id": gid,
                "name": self.metadata.get(gid, {}).get("name", gid),
                "node_count": len(list(self.graphs[gid].get_nodes())),
                "edge_count": len(list(self.graphs[gid].get_edges())),
            }
            for gid in self.graphs
        ]

    def save_system(self, system_id: str, system: Any) -> None:
        """Save a distribution system.

        Parameters
        ----------
        system_id : str
            System identifier
        system : Any
            DistributionSystem instance
        """
        self.systems[system_id] = system
        self.metadata[system_id] = {"type": "system", "name": system_id}
        logger.info(f"Saved system: {system_id}")

    def get_system(self, system_id: str) -> Optional[Any]:
        """Get system by ID.

        Parameters
        ----------
        system_id : str
            System identifier

        Returns
        -------
        Optional[Any]
            System instance or None if not found
        """
        return self.systems.get(system_id)

    def list_systems(self) -> list[Dict[str, Any]]:
        """List all stored systems.

        Returns
        -------
        list[Dict[str, Any]]
            List of system metadata
        """
        return [
            {"id": sid, "name": self.metadata.get(sid, {}).get("name", sid)}
            for sid in self.systems
        ]

    def delete_graph(self, graph_id: str) -> bool:
        """Delete a graph.

        Parameters
        ----------
        graph_id : str
            Graph identifier

        Returns
        -------
        bool
            True if deleted, False if not found
        """
        if graph_id in self.graphs:
            del self.graphs[graph_id]
            if graph_id in self.metadata:
                del self.metadata[graph_id]
            logger.info(f"Deleted graph: {graph_id}")
            return True
        return False

    def _persist_graph(self, graph_id: str, graph: DistributionGraph) -> None:
        """Persist graph to disk.

        Parameters
        ----------
        graph_id : str
            Graph identifier
        graph : DistributionGraph
            Graph to persist
        """
        if not self.storage_dir:
            return

        file_path = self.storage_dir / f"{graph_id}.json"

        # Serialize using NetworkX node-link format
        nx_graph = graph.get_undirected_graph()

        # Convert NodeModel and EdgeModel to dicts
        for node in nx_graph.nodes():
            node_data = nx_graph.nodes[node]
            if "node_data" in node_data:
                node_data["node_data"] = node_data["node_data"].model_dump(mode="json")

        for u, v in nx_graph.edges():
            edge_data = nx_graph[u][v]
            if "edge_data" in edge_data:
                edge_data["edge_data"] = edge_data["edge_data"].model_dump(mode="json")

        data = nx.node_link_data(nx_graph)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        logger.debug(f"Persisted graph {graph_id} to {file_path}")

    def _load_persisted_state(self) -> None:
        """Load persisted graphs from disk."""
        if not self.storage_dir or not self.storage_dir.exists():
            return

        for file_path in self.storage_dir.glob("*.json"):
            graph_id = file_path.stem
            try:
                with open(file_path) as f:
                    json.load(f)

                # Reconstruct graph (basic implementation)
                # Full reconstruction would need to restore NodeModel/EdgeModel
                logger.info(f"Found persisted graph: {graph_id}")

            except Exception as e:
                logger.error(f"Failed to load graph {graph_id}: {e}")
