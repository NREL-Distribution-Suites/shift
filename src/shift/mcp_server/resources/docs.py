"""Documentation resources — expose docs via MCP resource URIs."""

from __future__ import annotations

import json

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from shift.mcp_server.state import AppContext


def register(mcp: FastMCP) -> None:
    """Register documentation resources."""

    @mcp.resource("shift://docs")
    def list_all_docs(ctx: Context[ServerSession, AppContext]) -> str:
        """List all available documentation files."""
        app: AppContext = ctx.request_context.lifespan_context
        docs = []
        for key in sorted(app.docs_index.keys()):
            desc = app.docs_descriptions.get(key, "")
            docs.append({"name": key, "description": desc, "uri": f"shift://docs/{key}"})
        return json.dumps({"docs": docs, "count": len(docs)})

    @mcp.resource("shift://docs/{doc_name}")
    def read_doc_resource(doc_name: str, ctx: Context[ServerSession, AppContext]) -> str:
        """Read a specific documentation file by name.

        URI pattern: shift://docs/{doc_name}
        Example: shift://docs/readme, shift://docs/usage/complete_example
        """
        app: AppContext = ctx.request_context.lifespan_context
        if doc_name not in app.docs_index:
            return json.dumps(
                {
                    "error": f"Document '{doc_name}' not found",
                    "available": sorted(app.docs_index.keys()),
                }
            )
        return app.docs_index[doc_name]

    @mcp.resource("shift://graphs")
    def list_graphs_resource(ctx: Context[ServerSession, AppContext]) -> str:
        """List all in-memory distribution graphs."""
        app: AppContext = ctx.request_context.lifespan_context
        graphs = []
        for gid, meta in app.graph_meta.items():
            graphs.append(
                {
                    "id": gid,
                    "name": meta.name,
                    "node_count": meta.node_count,
                    "edge_count": meta.edge_count,
                    "created_at": meta.created_at,
                }
            )
        return json.dumps({"graphs": graphs, "count": len(graphs)})
