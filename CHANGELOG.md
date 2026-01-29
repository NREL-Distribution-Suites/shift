# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive README with installation, usage, and examples
- CONTRIBUTING.md with development guidelines
- Complete example documentation in docs/usage/
- pytest configuration with coverage reporting
- GitHub Actions CI/CD workflow
- Additional test files for data models and exceptions
- Enhanced docstrings for utility functions
- Support for multiple test markers (slow, integration, unit)
- **MCP Server** - Model Context Protocol server for AI assistant integration
  - 7 MCP tools: fetch_parcels, cluster_parcels, create_graph, add_node, add_edge, query_graph, list_resources
  - State management with optional file persistence
  - Comprehensive MCP server documentation (docs/MCP_SERVER.md)
  - Example client script demonstrating all tools
  - Claude Desktop configuration example
  - CLI entry point: `shift-mcp-server`
  - 15+ unit tests for MCP functionality
- API Quick Reference guide (docs/API_REFERENCE.md)
- QUICKSTART.md for new developers

### Changed
- Updated pyproject.toml with pytest and coverage configurations
- Enhanced documentation structure in docs/usage/index.md
- Improved test coverage for graph operations
- Added MCP dependencies as optional install: `pip install -e ".[mcp]"`
- Added loguru as core dependency for logging

### Fixed
- Fixed exception test imports to match actual exception hierarchy
- Fixed test filter functions to match correct signatures
- Added missing Distance import in EdgeModel tests

### Known Issues
- MCP server has pydantic version conflict with grid-data-models (MCP requires 2.12.x, GDM requires 2.10.x)

## [0.6.1] - 2026-01-29

### Changed
- Updated dependencies to support Python 3.10+
- Improved error handling in graph operations

## [0.6.0] - Previous Release

### Added
- Initial public release
- Core distribution graph functionality
- OpenStreetMap integration
- Phase and voltage mapping
- Equipment mapping
- Distribution system builder

[Unreleased]: https://github.com/NREL-Distribution-Suites/shift/compare/v0.6.1...HEAD
[0.6.1]: https://github.com/NREL-Distribution-Suites/shift/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/NREL-Distribution-Suites/shift/releases/tag/v0.6.0
