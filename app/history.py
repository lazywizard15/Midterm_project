"""
Manages the history of calculations, including undo/redo and CSV persistence.
This class acts as the 'Caretaker' and 'Originator' in the Memento pattern.
"""
import pandas as pd
from pathlib import Path
from typing import Optional
from app.calculator_config import ConfigLoader
from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento
from app.exceptions import HistoryError, OperationError
from app.operations import CommandFactory # Needed for loading from CSV

class History:
    """
    Manages calculation history, undo/redo stacks, and CSV persistence.
    Acts as the 'Caretaker' (Memento) and 'Originator' (Memento)
    by creating and restoring its own state.
    """
    
    def __init__(self, config: ConfigLoader):
        self._config = config
        self._history: list[Calculation] = []
        self._undo_stack: list[CalculatorMemento] = []
        self._redo_stack: list[CalculatorMemento] = []
        self._max_history_size = int(config.get_setting('CALCULATOR_MAX_HISTORY_SIZE', 20))
        self._history_file_path = config.get_history_file_path()
        self._encoding = config.get_setting('CALCULATOR_DEFAULT_ENCODING', 'utf-8')

    def add_calculation(self, calc: Calculation):
        """Adds a new calculation, saves state for undo, and clears redo."""
        # Save current state for undo
        self._undo_stack.append(self.create_memento())
        
        # Add new calculation
        self._history.append(calc)
        
        # Enforce max history size
        if len(self._history) > self._max_history_size:
            self._history.pop(0) # Remove the oldest entry
            
        # A new action clears the redo stack
        self._redo_stack.clear()

    def get_history(self) -> list[Calculation]:
        """Returns a copy of the current history."""
        return self.create_memento().get_state()

    def clear_history(self):
        """Clears all history, saving state for undo."""
        if not self._history:
            return # Nothing to clear
            
        self._undo_stack.append(self.create_memento())
        self._history.clear()
        self._redo_stack.clear()

    # --- Memento Pattern Methods ---

    def create_memento(self) -> CalculatorMemento:
        """Saves the current history list into a memento."""
        return CalculatorMemento(self._history)

    def restore_memento(self, memento: CalculatorMemento):
        """Restores the history list from a memento."""
        self._history = memento.get_state()

    def undo(self):
        """Performs an undo operation."""
        if not self._undo_stack:
            raise HistoryError("Nothing to undo.")
        
        # Save current state for redo
        self._redo_stack.append(self.create_memento())
        
        # Restore previous state from undo stack
        self.restore_memento(self._undo_stack.pop())

    def redo(self):
        """Performs a redo operation."""
        if not self._redo_stack:
            raise HistoryError("Nothing to redo.")
            
        # Save current state for undo
        self._undo_stack.append(self.create_memento())
        
        # Restore next state from redo stack
        self.restore_memento(self._redo_stack.pop())

    # --- Persistence Methods (Pandas) ---

    def save_history_to_csv(self):
        """Saves the current calculation history to a CSV file using pandas."""
        if not self._history:
            # If history is empty, we should write an empty file (or empty the existing one)
            # This ensures that loading an empty history works correctly.
            empty_df = pd.DataFrame(columns=["Timestamp", "OperandA", "OperandB", "Command", "Result"])
            try:
                self._history_file_path.parent.mkdir(parents=True, exist_ok=True)
                empty_df.to_csv(self._history_file_path, index=False, encoding=self._encoding)
            except (IOError, OSError) as e:
                raise HistoryError(f"Failed to save empty history to CSV: {e}")
            return

        try:
            # Convert list of Calculation objects to list of dicts
            data = [calc.to_dict() for calc in self._history]
            df = pd.DataFrame(data)
            
            # Ensure directory exists
            self._history_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(self._history_file_path, index=False, encoding=self._encoding)
            
        except (pd.errors.EmptyDataError, IOError, OSError) as e:
            raise HistoryError(f"Failed to save history to CSV: {e}")

    def load_history_from_csv(self, command_factory: CommandFactory):
        """Loads calculation history from a CSV file using pandas."""
        if not self._history_file_path.exists():
            # If the file doesn't exist, just start with an empty history.
            self._history = []
            return

        try:
            df = pd.read_csv(self._history_file_path, encoding=self._encoding)
            
            if df.empty:
                self._history = []
                return

            new_history = []
            for _, row in df.iterrows():
                try:
                    command = command_factory.get_command(row["Command"])
                    calc = Calculation(
                        operand_a=float(row["OperandA"]),
                        operand_b=float(row["OperandB"]),
                        command=command,
                        result=float(row["Result"]),
                        timestamp=pd.to_datetime(row["Timestamp"]).to_pydatetime()
                    )
                    new_history.append(calc)
                except (ValueError, OperationError):
                    # Skip malformed data rows, but let file-level errors (like KeyError) bubble up
                    continue # pragma: no cover

            # Save current state for undo, then load
            self._undo_stack.append(self.create_memento())
            self._history = new_history
            self._redo_stack.clear()
            
        except pd.errors.EmptyDataError:
            # File is empty, just start with empty history
            self._history = []
        except (pd.errors.ParserError, KeyError) as e:
            raise HistoryError(f"Failed to parse history file (malformed CSV?): {e}")
        except Exception as e:
            raise HistoryError(f"An unexpected error occurred while loading history: {e}")