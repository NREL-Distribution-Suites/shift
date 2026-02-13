"""Entry point for the NREL-shift MCP server.

Usage:
    python -m shift.mcp_server
"""

from shift.mcp_server.server import create_server


def main() -> None:
    mcp = create_server()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
