class ShiftException(Exception):
    """Base exception for all NREL-shift errors.

    All custom exceptions in the shift package inherit from this class,
    allowing callers to catch any shift-related error with a single
    ``except ShiftException`` clause.
    """


# ---------------------------------------------------------------------------
# Graph errors
# ---------------------------------------------------------------------------


class GraphError(ShiftException):
    """Base class for graph-related errors."""


class NodeAlreadyExists(GraphError):
    """Raised when attempting to add a node that already exists in the graph."""


class NodeDoesNotExist(GraphError):
    """Raised when a referenced node does not exist in the graph."""


class EdgeAlreadyExists(GraphError):
    """Raised when attempting to add an edge that already exists in the graph."""


class EdgeDoesNotExist(GraphError):
    """Raised when a referenced edge does not exist in the graph."""


class VsourceNodeAlreadyExists(GraphError):
    """Raised when a voltage-source node is added but one already exists."""


class VsourceNodeDoesNotExist(GraphError):
    """Raised when the voltage-source node is required but has not been added."""


class EmptyGraphError(GraphError):
    """Raised when an operation requires a non-empty graph but the graph has no nodes."""


class InvalidNodeDataError(GraphError):
    """Raised when node data is missing or has an unexpected type."""


class InvalidEdgeDataError(GraphError):
    """Raised when edge data is missing or has an unexpected type."""


# ---------------------------------------------------------------------------
# Input / validation errors
# ---------------------------------------------------------------------------


class InvalidInputError(ShiftException):
    """Raised when an invalid input value is provided."""


class InvalidAssetPhase(InvalidInputError):
    """Raised when an invalid asset phase combination is specified."""


# ---------------------------------------------------------------------------
# Mapper errors
# ---------------------------------------------------------------------------


class MapperError(ShiftException):
    """Base class for mapper-related errors."""


class AllocationMappingError(MapperError):
    """Raised when phase allocation produces an incomplete or inconsistent mapping."""


class InvalidPhaseAllocationMethod(MapperError):
    """Raised when an unsupported phase-allocation method is requested."""


class MissingTransformerMapping(MapperError):
    """Raised when transformer entries are missing from a mapper configuration."""


class UnsupportedTransformerType(MapperError):
    """Raised when a transformer type is not supported by the mapper."""


class MissingVoltageMappingError(MapperError):
    """Raised when voltage mapping entries are missing for one or more transformers."""


class UnsupportedBranchEquipmentType(MapperError):
    """Raised when a branch equipment type is not supported by the equipment mapper."""


# ---------------------------------------------------------------------------
# Equipment errors
# ---------------------------------------------------------------------------


class EquipmentError(ShiftException):
    """Base class for equipment-related errors."""


class EquipmentNotFoundError(EquipmentError):
    """Raised when a required equipment catalogue entry cannot be found."""


class WrongEquipmentAssigned(EquipmentError):
    """Raised when the assigned equipment type does not match the expected edge type."""


# ---------------------------------------------------------------------------
# System builder errors
# ---------------------------------------------------------------------------


class SystemBuildError(ShiftException):
    """Base class for errors during distribution system construction."""


class UnsupportedEdgeTypeError(SystemBuildError):
    """Raised when an edge type is not supported by the system builder."""


class WindingMismatchError(SystemBuildError):
    """Raised when transformer winding buses/voltages cannot be resolved."""


class InvalidSplitPhaseWindingError(SystemBuildError):
    """Raised when split-phase winding configuration is invalid."""


# ---------------------------------------------------------------------------
# Backward-compatible alias (deprecated spelling)
# ---------------------------------------------------------------------------

#: .. deprecated:: Use :class:`VsourceNodeDoesNotExist` instead.
VsourceNodeDoesNotExists = VsourceNodeDoesNotExist
