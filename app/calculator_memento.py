"""
Defines the Memento class for saving the calculator's state.
Part of the Memento Design Pattern.
"""
from __future__ import annotations
import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.calculation import Calculation

class CalculatorMemento:
    """
    The Memento class.
    It stores a snapshot of the History's state (the list of calculations).
    """
    def __init__(self, history: list[Calculation]):
        # Use deepcopy to ensure the state is fully independent
        self._state = copy.deepcopy(history)

    def get_state(self) -> list[Calculation]:
        """Returns the stored state."""
        # Return a deepcopy to prevent mutation of the stored state
        return copy.deepcopy(self._state)