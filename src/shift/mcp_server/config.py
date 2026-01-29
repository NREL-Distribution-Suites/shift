"""Configuration for NREL-shift MCP server."""

from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    """Configuration for the MCP server."""

    server_name: str = Field(default="nrel-shift-mcp-server", description="Name of the MCP server")

    server_version: str = Field(default="0.1.0", description="Version of the MCP server")

    default_search_distance_m: float = Field(
        default=500.0, description="Default search distance in meters for data fetching"
    )

    max_search_distance_m: float = Field(
        default=5000.0, description="Maximum allowed search distance in meters"
    )

    default_cluster_count: int = Field(
        default=5, description="Default number of clusters for parcel grouping"
    )

    state_storage_dir: Optional[Path] = Field(
        default=None,
        description="Directory for storing graph/system state (None = in-memory only)",
    )

    enable_visualization: bool = Field(default=True, description="Enable visualization tools")

    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    max_concurrent_fetches: int = Field(
        default=3, description="Maximum concurrent OpenStreetMap fetches"
    )


# Global configuration instance
config = MCPServerConfig()


def load_config(config_path: Optional[Path] = None) -> MCPServerConfig:
    """Load configuration from file or use defaults.

    Parameters
    ----------
    config_path : Optional[Path]
        Path to configuration file (YAML or JSON)

    Returns
    -------
    MCPServerConfig
        Loaded configuration
    """
    if config_path and config_path.exists():
        import yaml

        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        return MCPServerConfig(**config_data)
    return MCPServerConfig()
