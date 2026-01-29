"""Tests for exception classes."""

import pytest

from shift.exceptions import (
    EdgeAlreadyExists,
    EdgeDoesNotExist,
    NodeAlreadyExists,
    NodeDoesNotExist,
    VsourceNodeAlreadyExists,
    VsourceNodeDoesNotExists,
    InvalidInputError,
    EmptyGraphError,
    EquipmentNotFoundError,
)


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_edge_already_exists(self):
        """Test EdgeAlreadyExists exception."""
        with pytest.raises(EdgeAlreadyExists) as exc_info:
            raise EdgeAlreadyExists("Edge already exists")
        assert "Edge already exists" in str(exc_info.value)

    def test_edge_does_not_exist(self):
        """Test EdgeDoesNotExist exception."""
        with pytest.raises(EdgeDoesNotExist) as exc_info:
            raise EdgeDoesNotExist("Edge not found")
        assert "Edge not found" in str(exc_info.value)

    def test_node_already_exists(self):
        """Test NodeAlreadyExists exception."""
        with pytest.raises(NodeAlreadyExists) as exc_info:
            raise NodeAlreadyExists("Node already exists")
        assert "Node already exists" in str(exc_info.value)

    def test_node_does_not_exist(self):
        """Test NodeDoesNotExist exception."""
        with pytest.raises(NodeDoesNotExist) as exc_info:
            raise NodeDoesNotExist("Node not found")
        assert "Node not found" in str(exc_info.value)

    def test_vsource_node_already_exists(self):
        """Test VsourceNodeAlreadyExists exception."""
        with pytest.raises(VsourceNodeAlreadyExists) as exc_info:
            raise VsourceNodeAlreadyExists("Vsource already exists")
        assert "Vsource already exists" in str(exc_info.value)

    def test_vsource_node_does_not_exist(self):
        """Test VsourceNodeDoesNotExists exception."""
        with pytest.raises(VsourceNodeDoesNotExists) as exc_info:
            raise VsourceNodeDoesNotExists("Vsource not found")
        assert "Vsource not found" in str(exc_info.value)

    def test_invalid_input_error(self):
        """Test InvalidInputError exception."""
        with pytest.raises(InvalidInputError) as exc_info:
            raise InvalidInputError("Invalid input provided")
        assert "Invalid input provided" in str(exc_info.value)

    def test_empty_graph_error(self):
        """Test EmptyGraphError exception."""
        with pytest.raises(EmptyGraphError) as exc_info:
            raise EmptyGraphError("Graph is empty")
        assert "Graph is empty" in str(exc_info.value)

    def test_equipment_not_found_error(self):
        """Test EquipmentNotFoundError exception."""
        with pytest.raises(EquipmentNotFoundError) as exc_info:
            raise EquipmentNotFoundError("Equipment not found")
        assert "Equipment not found" in str(exc_info.value)

    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from Exception."""
        assert issubclass(EdgeAlreadyExists, Exception)
        assert issubclass(EdgeDoesNotExist, Exception)
        assert issubclass(NodeAlreadyExists, Exception)
        assert issubclass(NodeDoesNotExist, Exception)
        assert issubclass(VsourceNodeAlreadyExists, Exception)
        assert issubclass(VsourceNodeDoesNotExists, Exception)
        assert issubclass(InvalidInputError, Exception)
        assert issubclass(EmptyGraphError, Exception)
        assert issubclass(EquipmentNotFoundError, Exception)
