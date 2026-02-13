# Quick Start for Contributors

Get a development environment running in under five minutes.

## Setup

### 1. Clone and Install

```bash
git clone https://github.com/NREL-Distribution-Suites/shift.git
cd shift

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -e ".[dev,doc]"
```

To also work on the MCP server, install the MCP extras:

```bash
pip install -e ".[dev,doc,mcp]"
```

### 2. Verify Installation

```bash
pytest
```

All tests should pass. If you see import errors, re-run `pip install -e ".[dev]"`.

### 3. Make a Change and Validate

```bash
ruff check .       # Lint
ruff format .      # Format
pytest             # Test
```

## Common Commands

### Testing

```bash
pytest                                 # All tests
pytest tests/test_graph.py             # Single file
pytest tests/test_graph.py::test_name -v  # Single test, verbose
pytest --cov=shift --cov-report=html   # With coverage report
pytest -m "not slow"                   # Skip slow tests
```

### Code Quality

```bash
ruff check .        # Check lint rules
ruff check --fix .  # Auto-fix lint issues
ruff format .       # Format code
```

### Documentation

```bash
cd docs && make html
# Open docs/_build/html/index.html
```

## Development Workflow

1. **Branch** — `git checkout -b feature/your-feature-name`
2. **Code** — Edit source, add tests, update docs
3. **Validate** — `pytest && ruff check .`
4. **Commit** — `git commit -m "Add feature: description"`
5. **Push** — `git push origin feature/your-feature-name`
6. **PR** — Open a pull request on GitHub

## Project Layout

```
shift/
├── src/shift/           # Source code
│   ├── __init__.py      # Public API exports
│   ├── data_model.py    # ParcelModel, NodeModel, EdgeModel, etc.
│   ├── parcel.py        # OpenStreetMap parcel fetching
│   ├── system_builder.py
│   ├── graph/           # DistributionGraph, OpenStreetGraphBuilder, PRSG
│   ├── mapper/          # Phase, voltage, and equipment mappers
│   ├── mcp_server/      # MCP server for LLM agent integration
│   └── utils/           # Clustering, nearest points, mesh networks
├── tests/               # pytest test files (test_*.py)
├── docs/                # Sphinx documentation
│   ├── usage/           # How-to guides
│   └── references/      # Auto-generated API docs
└── pyproject.toml       # Project config, dependencies, tool settings
```

## Key Entry Points

| File | What It Does |
|------|-------------|
| `src/shift/__init__.py` | Defines the public API — start here to see what's exported |
| `src/shift/graph/distribution_graph.py` | Core graph with typed nodes and edges |
| `src/shift/graph/prsgb.py` | Primary/secondary graph builder from road networks |
| `src/shift/mapper/` | Phase, voltage, and equipment assignment |

## Writing Tests

Tests live in `tests/` and follow the pattern `test_<module>.py`.

```python
import pytest
from shift import DistributionGraph, NodeModel
from infrasys import Location

@pytest.fixture
def sample_graph():
    """Provide a graph with one node for testing."""
    graph = DistributionGraph()
    graph.add_node(NodeModel(name="n1", location=Location(x=-97.3, y=32.7)))
    return graph

def test_node_retrieval(sample_graph):
    """Verify nodes can be retrieved by name."""
    node = sample_graph.get_node("n1")
    assert node.name == "n1"
```

## Tips

1. **Run tests often** — catch regressions early
2. **Keep commits small** — one logical change per commit
3. **Add docstrings** — use NumPy-style format (see CONTRIBUTING.md)
4. **Add type hints** — all function signatures should be annotated
5. **Check coverage** — aim for > 80% on new code

## Pre-PR Checklist

- [ ] Tests pass (`pytest`)
- [ ] Lint clean (`ruff check .`)
- [ ] Code formatted (`ruff format .`)
- [ ] Docstrings added/updated
- [ ] CHANGELOG.md updated

## Resources

- [README](./README.md) — Project overview and quick start
- [CONTRIBUTING](./CONTRIBUTING.md) — Full contribution guidelines
- [Complete Example](./docs/usage/complete_example.md) — End-to-end workflow
- [API Reference](./docs/API_REFERENCE.md) — Class and function reference
