# Quick Start Guide for Developers

Get up and running with NREL-shift development in minutes!

## 🚀 Quick Setup (5 minutes)

### 1. Clone and Install
```bash
# Clone the repository
git clone https://github.com/NREL-Distribution-Suites/shift.git
cd shift

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,doc]"
```

### 2. Verify Installation
```bash
# Run tests to verify everything works
pytest

# Should see all tests passing ✓
```

### 3. Your First Change

Edit a file, then verify your changes:
```bash
# Run linter
ruff check .

# Run tests
pytest

# Check coverage
pytest --cov=shift
```

## 🎯 Common Tasks

### Run Tests
```bash
# All tests
pytest

# Specific file
pytest tests/test_graph.py

# With coverage
pytest --cov=shift --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
```

### Code Quality
```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Build Documentation
```bash
cd docs
make html
# Open docs/_build/html/index.html
```

## 📝 Making Changes

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Edit code
- Add tests
- Update docs

### 3. Test Your Changes
```bash
# Run tests
pytest

# Check coverage
pytest --cov=shift

# Lint code
ruff check .
```

### 4. Commit and Push
```bash
git add .
git commit -m "Add feature: description"
git push origin feature/your-feature-name
```

### 5. Create Pull Request
Go to GitHub and create a PR!

## 🔍 Project Structure Quick Reference

```
shift/
├── src/shift/           # Source code
│   ├── __init__.py      # Main exports
│   ├── data_model.py    # Data models
│   ├── parcel.py        # Parcel fetching
│   ├── graph/           # Graph classes
│   ├── mapper/          # Equipment/phase/voltage mappers
│   └── utils/           # Utility functions
├── tests/               # Test files
├── docs/                # Documentation
├── pyproject.toml       # Project configuration
└── README.md            # Main readme
```

## 📚 Key Files to Know

| File | Purpose |
|------|---------|
| `src/shift/__init__.py` | Main API exports |
| `src/shift/data_model.py` | Core data models |
| `src/shift/graph/distribution_graph.py` | Main graph class |
| `src/shift/mcp_server/` | MCP server implementation |
| `tests/test_*.py` | Test files |
| `pyproject.toml` | Dependencies and config |
| `docs/MCP_SERVER.md` | MCP server documentation |

## 🧪 Test Examples

### Write a Simple Test
```python
# tests/test_myfeature.py
import pytest
from shift import MyClass

def test_my_feature():
    """Test my new feature."""
    obj = MyClass()
    result = obj.my_method()
    assert result == expected_value
```

### Use Fixtures
```python
@pytest.fixture
def sample_graph():
    """Provide a sample graph for testing."""
    graph = DistributionGraph()
    # Setup graph
    return graph

def test_with_fixture(sample_graph):
    """Test using fixture."""
    assert sample_graph.get_nodes() is not None
```

## 💡 Tips

1. **Run tests frequently** - Catch issues early
2. **Check coverage** - Aim for >80% coverage for new code
3. **Write docstrings** - Use NumPy style docstrings
4. **Type hints** - Add type hints to all functions
5. **Small commits** - Make focused, atomic commits

## 🐛 Common Issues

### Import Errors
```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

### Test Failures
```bash
# Run specific test with verbose output
pytest tests/test_file.py::test_name -v
```

### Linting Errors
```bash
# Auto-fix most issues
ruff check --fix .
ruff format .
```

## 📖 Learn More

- [README.md](../README.md) - Project overview
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Detailed guidelines
- [docs/usage/complete_example.md](../docs/usage/complete_example.md) - Full example
- [docs/API_REFERENCE.md](../docs/API_REFERENCE.md) - API reference

## 🤝 Getting Help

- Check existing [Issues](https://github.com/NREL-Distribution-Suites/shift/issues)
- Create a new issue with details
- Read the [documentation](../docs/)

## ✅ Pre-PR Checklist

Before creating a pull request:

- [ ] All tests pass (`pytest`)
- [ ] Code is linted (`ruff check .`)
- [ ] Code is formatted (`ruff format .`)
- [ ] Coverage is maintained/improved
- [ ] Docstrings added/updated
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

## 🎉 You're Ready!

You now have everything you need to contribute to NREL-shift. Start with a small change to get familiar with the workflow, then tackle bigger features!

**Happy Coding!** 🚀
