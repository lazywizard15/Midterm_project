########################
# Calculator Memento    #
########################

from dataclasses import dataclass, field
import datetime
from typing import Any, Dict, List

from app.calculation import Calculation


class Memento:
    """Stores a snapshot of the calculator state."""

    def __init__(self, state: List[Calculation]):
        self.state = state.copy()


class Caretaker:
    """Manages undo and redo stacks for calculator history."""

    def __init__(self):
        self.undo_stack: List[Memento] = []
        self.redo_stack: List[Memento] = []

    def save(self, state: List[Calculation]) -> None:
        """Save current state to undo stack and clear redo stack."""
        self.undo_stack.append(Memento(state))
        self.redo_stack.clear()

    def undo(self, current_state: List[Calculation]) -> List[Calculation]:
        """Undo the last action and return previous state."""
        if not self.undo_stack:
            return current_state
        memento = self.undo_stack.pop()
        self.redo_stack.append(Memento(current_state.copy()))
        return memento.state

    def redo(self, current_state: List[Calculation]) -> List[Calculation]:
        """Redo the last undone action and return next state."""
        if not self.redo_stack:
            return current_state
        memento = self.redo_stack.pop()
        self.undo_stack.append(Memento(current_state.copy()))
        return memento.state


@dataclass
class CalculatorMemento:
    """
    Stores calculator state for undo/redo functionality.

    Allows the Calculator to save its current history so that it can be restored later.
    """
    history: List[Calculation]
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the memento into a dictionary."""
        return {
            'history': [calc.to_dict() for calc in self.history],
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalculatorMemento':
        """Deserialize a dictionary to recreate a CalculatorMemento instance."""
        return cls(
            history=[Calculation.from_dict(calc) for calc in data['history']],
            timestamp=datetime.datetime.fromisoformat(data['timestamp'])
        )
