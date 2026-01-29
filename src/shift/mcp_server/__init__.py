"""MCP Server for NREL-shift Distribution System Builder.

This module provides a Model Context Protocol server that exposes NREL-shift's
distribution system modeling capabilities through structured tools and resources.
"""

from shift.mcp_server.server import create_server, main

__all__ = ["create_server", "main"]
