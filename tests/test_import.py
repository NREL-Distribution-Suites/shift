import pkg_resources


def test_shift_version():
    """Prints shifts version."""
    print(pkg_resources.get_distribution("NREL-shift").version)
