class VsourceNodeAlreadyExists(Exception):
    """Raise this error if vsource node already exists."""


class VsourceNodeDoesNotExists(Exception):
    """Raise this error if vsource node already exists."""


class NodeAlreadyExists(Exception):
    """Raise this error if node already exists."""


class EdgeAlreadyExists(Exception):
    """Raise this error if edge already exists."""


class InvalidAssetPhase(Exception):
    """Raise this error if invalid asset phase is specified."""


class InvalidInputError(Exception):
    """Raise this error if invalid input is passed."""


class NodeDoesNotExist(Exception):
    """Raise this error if node does not exist in the graph."""


class EdgeDoesNotExist(Exception):
    """Raise this error if you are querying edge that does not exist."""


class AllocationMappingError(Exception):
    """Raise this error of allocation mapping is incorrect."""


class EquipmentNotFoundError(Exception):
    """Raise this error if equipment is not found."""


class WrongEquipmentAssigned(Exception):
    """Raise this error of wrong equipment is assigned."""


class EmptyGraphError(Exception):
    """Raise this error if graph is empty."""
