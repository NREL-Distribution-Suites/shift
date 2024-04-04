class VsourceNodeAlreadyExists(Exception):
    """Raise this error if vsource node already exists."""


class NodeAlreadyExists(Exception):
    """Raise this error if node already exists."""


class EdgeAlreadyExists(Exception):
    """Raise this error if edge already exists."""


class InvalidAssetPhase(Exception):
    """Raise this error if invalid asset phase is specified."""


class InvalidInputError(Exception):
    """Raise this error if invalid input is passed."""
