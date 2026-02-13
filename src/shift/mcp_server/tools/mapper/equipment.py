"""Equipment mapping tools."""

from __future__ import annotations

import json

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from shift.mcp_server.state import AppContext


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def configure_equipment_mapper(
        ctx: Context[ServerSession, AppContext],
        graph_id: str,
        catalog_path: str,
    ) -> str:
        """Configure equipment mapping using an equipment catalog.

        Maps edges to specific equipment models (conductors, transformers)
        from a catalog file. Requires phase and voltage mappers to be
        configured first.

        Args:
            graph_id: Graph identifier.
            catalog_path: Path to equipment catalog JSON file (DatasetSystem format).

        Returns:
            JSON confirmation.
        """
        try:
            from pathlib import Path
            from shift.mapper.edge_equipment_mapper import EdgeEquipmentMapper
            from gdm.distribution import DistributionSystem as DatasetSystem

            app: AppContext = ctx.request_context.lifespan_context
            graph = app.get_graph(graph_id)

            if graph_id not in app.voltage_mappers:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Voltage mapper must be configured first. "
                        "Use configure_voltage_mapper.",
                    }
                )
            if graph_id not in app.phase_mappers:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Phase mapper must be configured first. "
                        "Use configure_phase_mapper.",
                    }
                )

            catalog_file = Path(catalog_path)
            if not catalog_file.exists():
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Catalog file not found: {catalog_path}",
                    }
                )

            catalog = DatasetSystem.from_json(catalog_file)
            equipment_mapper = EdgeEquipmentMapper(
                graph,
                catalog,
                app.voltage_mappers[graph_id],
                app.phase_mappers[graph_id],
            )
            app.equipment_mappers[graph_id] = equipment_mapper

            return json.dumps(
                {
                    "success": True,
                    "graph_id": graph_id,
                    "catalog_path": str(catalog_path),
                    "message": "Equipment mapper configured. Use get_equipment_mapping to view assignments.",
                }
            )

        except Exception as exc:
            return json.dumps({"success": False, "error": str(exc)})

    @mcp.tool()
    def get_equipment_mapping(
        ctx: Context[ServerSession, AppContext],
        graph_id: str,
    ) -> str:
        """Get equipment assignments for all edges in a distribution graph.

        Args:
            graph_id: Graph identifier.

        Returns:
            JSON dict mapping edge names to equipment details.
        """
        try:
            app: AppContext = ctx.request_context.lifespan_context
            if graph_id not in app.equipment_mappers:
                return json.dumps(
                    {
                        "success": False,
                        "error": f"No equipment mapper configured for graph '{graph_id}'. "
                        "Use configure_equipment_mapper first.",
                    }
                )

            mapper = app.equipment_mappers[graph_id]
            raw = mapper.edge_equipment_mapping
            result = {}
            for edge_name, component in raw.items():
                result[edge_name] = {
                    "type": type(component).__name__,
                    "name": getattr(component, "name", str(component)),
                }

            return json.dumps(
                {
                    "success": True,
                    "mapping": result,
                    "count": len(result),
                }
            )

        except Exception as exc:
            return json.dumps({"success": False, "error": str(exc)})
