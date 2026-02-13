"""Server configuration — loaded from YAML file, env vars, or defaults."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class ServerConfig(BaseModel):
    """Configuration model for the shift MCP server."""

    server_name: str = "nrel-shift-mcp-server"
    server_version: str = "0.1.0"

    # data-acquisition defaults
    default_search_distance_m: float = 500.0
    max_search_distance_m: float = 5000.0
    default_cluster_count: int = 5

    # documentation path (auto-detected if None)
    docs_path: Optional[str] = None

    # logging
    log_level: str = "INFO"

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ServerConfig":
        import yaml

        with open(path) as fh:
            data = yaml.safe_load(fh) or {}
        return cls(**data)

    @classmethod
    def load(cls, config_path: str | None = None) -> "ServerConfig":
        """Load config from explicit path, env var, or defaults."""
        path = config_path or os.environ.get("SHIFT_MCP_CONFIG")
        if path and Path(path).exists():
            return cls.from_yaml(path)
        return cls()

    def resolve_docs_path(self) -> Path:
        """Return the absolute path to the docs/ folder."""
        if self.docs_path:
            return Path(self.docs_path).resolve()
        # walk up from this file to find the repo root
        candidate = Path(__file__).resolve().parent.parent / "docs"
        if candidate.exists():
            return candidate
        return Path.cwd() / "docs"
