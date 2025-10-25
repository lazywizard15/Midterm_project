"""
Unit tests for UndoRedoManager and HistorySnapshot classes.
"""

import pytest
from app.calculator_memento import HistorySnapshot, UndoRedoManager
from app.calculation import Calculation
from app.operations import AddOperation
from app.exceptions import HistoryError


class TestHistorySnapshot:
    """Tests for HistorySnapshot."""

    def test_snapshot_stores_history(self):
        """Ensure snapshot correctly stores a deep copy of history."""
        calc = Calculation(AddOperation(), 5, 3)
        calc.execute()
        history = [calc]

        snapshot = HistorySnapshot(history)
        retrieved = snapshot.retrieve()

        assert len(retrieved) == 1
        assert retrieved[0].result == 8
        assert retrieved is not history  # must be a deep copy


class TestUndoRedoManager:
    """Tests for UndoRedoManager."""

    def test_initialization(self):
        """Verify undo/redo stacks start empty."""
        manager = UndoRedoManager()
        assert not manager.has_undo()
        assert not manager._redo_stack  # internal check

    def test_record_state_adds_snapshot(self):
        """Ensure record_state adds to undo stack."""
        manager = UndoRedoManager()
        calc = Calculation(AddOperation(), 5, 3)
        calc.execute()
        manager.record_state([calc])
        assert manager.has_undo()

    def test_undo_operation(self):
        """Test undo restores previous state and enables redo."""
        manager = UndoRedoManager()
        calc1 = Calculation(AddOperation(), 2, 2)
        calc2 = Calculation(AddOperation(), 3, 3)
        calc1.execute()
        calc2.execute()

        history1 = [calc1]
        history2 = [calc1, calc2]

        manager.record_state(history1)
        restored = manager.undo(history2)

        assert len(restored) == 1
        assert restored[0].result == 4
        assert manager._redo_stack  # redo stack should not be empty

    def test_undo_raises_error_when_empty(self):
        """Ensure undo raises HistoryError when stack empty."""
        manager = UndoRedoManager()
        with pytest.raises(HistoryError, match="No operations to undo"):
            manager.undo([])

    def test_redo_operation(self):
        """Test redo restores next state after undo."""
        manager = UndoRedoManager()
        calc1 = Calculation(AddOperation(), 4, 4)
        calc2 = Calculation(AddOperation(), 5, 5)
        calc1.execute()
        calc2.execute()

        history1 = [calc1]
        history2 = [calc1, calc2]

        manager.record_state(history1)
        manager.undo(history2)
        restored = manager.redo()

        assert len(restored) == 2
        assert restored[1].result == 10

    def test_redo_raises_error_when_empty(self):
        """Ensure redo raises HistoryError when stack empty."""
        manager = UndoRedoManager()
        with pytest.raises(HistoryError, match="No operations to redo"):
            manager.redo()

    def test_record_state_clears_redo_stack(self):
        """Recording new state should clear redo stack."""
        manager = UndoRedoManager()
        calc = Calculation(AddOperation(), 5, 3)
        calc.execute()

        manager.record_state([calc])
        manager.undo([calc])
        assert manager._redo_stack

        manager.record_state([calc])
        assert not manager._redo_stack

    def test_reset_clears_all(self):
        """Reset should clear both stacks."""
        manager = UndoRedoManager()
        calc = Calculation(AddOperation(), 6, 2)
        calc.execute()
        manager.record_state([calc])
        manager.reset()
        assert not manager.has_undo()
        assert not manager._redo_stack
