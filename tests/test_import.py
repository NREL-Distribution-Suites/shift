import importlib.metadata


def test_shift_version():
    """Prints shifts version."""
    print(importlib.metadata.version("NREL-shift"))
