"""Tests for exception classes."""

import pytest

from shift.exceptions import (
    ShiftException,
    GraphError,
    MapperError,
    EquipmentError,
    SystemBuildError,
    EdgeAlreadyExists,
    EdgeDoesNotExist,
    NodeAlreadyExists,
    NodeDoesNotExist,
    VsourceNodeAlreadyExists,
    VsourceNodeDoesNotExist,
    VsourceNodeDoesNotExists,  # backward-compatible alias
    InvalidInputError,
    InvalidAssetPhase,
    EmptyGraphError,
    InvalidNodeDataError,
    InvalidEdgeDataError,
    EquipmentNotFoundError,
    WrongEquipmentAssigned,
    AllocationMappingError,
    InvalidPhaseAllocationMethod,
    MissingTransformerMapping,
    UnsupportedTransformerType,
    MissingVoltageMappingError,
    UnsupportedBranchEquipmentType,
    UnsupportedEdgeTypeError,
    WindingMismatchError,
    InvalidSplitPhaseWindingError,
)


class TestExceptionMessages:
    """Test that each exception preserves its message."""

    @pytest.mark.parametrize(
        "exc_cls,message",
        [
            (EdgeAlreadyExists, "Edge already exists"),
            (EdgeDoesNotExist, "Edge not found"),
            (NodeAlreadyExists, "Node already exists"),
            (NodeDoesNotExist, "Node not found"),
            (VsourceNodeAlreadyExists, "Vsource already exists"),
            (VsourceNodeDoesNotExist, "Vsource not found"),
            (InvalidInputError, "Invalid input provided"),
            (InvalidAssetPhase, "Bad phase combo"),
            (EmptyGraphError, "Graph is empty"),
            (InvalidNodeDataError, "Bad node data"),
            (InvalidEdgeDataError, "Bad edge data"),
            (EquipmentNotFoundError, "Equipment not found"),
            (WrongEquipmentAssigned, "Wrong equipment"),
            (AllocationMappingError, "Allocation failed"),
            (InvalidPhaseAllocationMethod, "Bad method"),
            (MissingTransformerMapping, "Missing mapping"),
            (UnsupportedTransformerType, "Unsupported type"),
            (MissingVoltageMappingError, "Missing voltages"),
            (UnsupportedBranchEquipmentType, "Unsupported branch"),
            (UnsupportedEdgeTypeError, "Unsupported edge"),
            (WindingMismatchError, "Winding mismatch"),
            (InvalidSplitPhaseWindingError, "Bad split phase"),
        ],
    )
    def test_message_preserved(self, exc_cls, message):
        with pytest.raises(exc_cls, match=message):
            raise exc_cls(message)


class TestExceptionHierarchy:
    """Test that exceptions form a proper hierarchy rooted at ShiftException."""

    def test_all_inherit_from_shift_exception(self):
        for cls in [
            GraphError,
            MapperError,
            EquipmentError,
            SystemBuildError,
            EdgeAlreadyExists,
            EdgeDoesNotExist,
            NodeAlreadyExists,
            NodeDoesNotExist,
            VsourceNodeAlreadyExists,
            VsourceNodeDoesNotExist,
            EmptyGraphError,
            InvalidNodeDataError,
            InvalidEdgeDataError,
            InvalidInputError,
            InvalidAssetPhase,
            AllocationMappingError,
            InvalidPhaseAllocationMethod,
            MissingTransformerMapping,
            UnsupportedTransformerType,
            MissingVoltageMappingError,
            UnsupportedBranchEquipmentType,
            EquipmentNotFoundError,
            WrongEquipmentAssigned,
            UnsupportedEdgeTypeError,
            WindingMismatchError,
            InvalidSplitPhaseWindingError,
        ]:
            assert issubclass(cls, ShiftException), f"{cls.__name__} must inherit ShiftException"

    def test_graph_errors(self):
        for cls in [
            NodeAlreadyExists,
            NodeDoesNotExist,
            EdgeAlreadyExists,
            EdgeDoesNotExist,
            VsourceNodeAlreadyExists,
            VsourceNodeDoesNotExist,
            EmptyGraphError,
            InvalidNodeDataError,
            InvalidEdgeDataError,
        ]:
            assert issubclass(cls, GraphError), f"{cls.__name__} must inherit GraphError"

    def test_mapper_errors(self):
        for cls in [
            AllocationMappingError,
            InvalidPhaseAllocationMethod,
            MissingTransformerMapping,
            UnsupportedTransformerType,
            MissingVoltageMappingError,
            UnsupportedBranchEquipmentType,
        ]:
            assert issubclass(cls, MapperError), f"{cls.__name__} must inherit MapperError"

    def test_equipment_errors(self):
        for cls in [EquipmentNotFoundError, WrongEquipmentAssigned]:
            assert issubclass(cls, EquipmentError), f"{cls.__name__} must inherit EquipmentError"

    def test_system_build_errors(self):
        for cls in [UnsupportedEdgeTypeError, WindingMismatchError, InvalidSplitPhaseWindingError]:
            assert issubclass(
                cls, SystemBuildError
            ), f"{cls.__name__} must inherit SystemBuildError"

    def test_input_validation_errors(self):
        assert issubclass(InvalidAssetPhase, InvalidInputError)

    def test_backward_compatible_alias(self):
        """VsourceNodeDoesNotExists (old spelling) must still work."""
        assert VsourceNodeDoesNotExists is VsourceNodeDoesNotExist

    def test_catch_all_shift_errors(self):
        """A single except ShiftException should catch any shift error."""
        with pytest.raises(ShiftException):
            raise NodeAlreadyExists("test")
        with pytest.raises(ShiftException):
            raise AllocationMappingError("test")
        with pytest.raises(ShiftException):
            raise EquipmentNotFoundError("test")
        with pytest.raises(ShiftException):
            raise WindingMismatchError("test")
