"""
Memento implementation for calculator undo/redo functionality.
"""

from copy import deepcopy
from typing import List
from app.calculation import Calculation
from app.exceptions import HistoryError


class HistorySnapshot:
    """Stores a snapshot of the calculation history."""

    def __init__(self, records: List[Calculation]):
        """
        Save a deep copy of calculation records.

        Args:
            records: List of Calculation objects to snapshot
        """
        self._snapshot = deepcopy(records)

    def retrieve(self) -> List[Calculation]:
        """Return a deep copy of the stored history snapshot."""
        return deepcopy(self._snapshot)


class UndoRedoManager:
    """Handles undo and redo operations using history snapshots."""

    def __init__(self):
        """Initialize empty stacks for undo and redo actions."""
        self._undo_stack: List[HistorySnapshot] = []
        self._redo_stack: List[HistorySnapshot] = []

    # ------------------ Core Operations ------------------

    def undo(self, current_history: List[Calculation]) -> List[Calculation]:
        """
        Revert to the previous history state.

        Args:
            current_history: Current calculation history

        Returns:
            Previous state of the history

        Raises:
            HistoryError: If no previous state exists
        """
        if not self._undo_stack:
            raise HistoryError("No operations to undo")

        # Save current state to redo stack
        self._redo_stack.append(HistorySnapshot(current_history))

        # Restore previous state
        previous = self._undo_stack.pop()
        return previous.retrieve()

    def redo(self) -> List[Calculation]:
        """
        Reapply the last undone operation.

        Returns:
            Restored history after redo

        Raises:
            HistoryError: If no redo state exists
        """
        if not self._redo_stack:
            raise HistoryError("No operations to redo")

        next_state = self._redo_stack.pop()
        self._undo_stack.append(next_state)
        return next_state.retrieve()

    def record_state(self, current_history: List[Calculation]) -> None:
        """
        Record current history state to the undo stack.
        Clears redo stack whenever a new state is recorded.

        Args:
            current_history: Current calculation history
        """
        snapshot = HistorySnapshot(current_history)
        self._undo_stack.append(snapshot)
        self._redo_stack.clear()

    # ------------------ Utility Methods ------------------

    def reset(self):
        """Clear all undo and redo states."""
        self._undo_stack.clear()
        self._redo_stack.clear()

    def has_undo(self) -> bool:
        """Return True if undo is possible."""
        return
