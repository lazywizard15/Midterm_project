"""
The main 'Calculator' class.
This is the 'Subject' in the Observer pattern.
"""
from typing import Optional
from app.operations import CommandFactory
from app.history import History
from app.calculation import Calculation
from app.exceptions import OperationError
from app.observers import Observer

class Calculator:
    """
    Coordinates calculations, history, and observers.
    This is the 'Subject' (Observable) for the Observer pattern.
    """
    
    def __init__(self, factory: CommandFactory, history_manager: History):
        self._factory = factory
        self._history_manager = history_manager
        self._observers: list[Observer] = []

    # --- Observer Pattern Methods ---

    def attach(self, observer: Observer):
        """Attach an observer."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        """Detach an observer."""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass # pragma: no cover

    def _notify(self, event: str, data: any = None):
        """Notify all observers about an event."""
        for observer in self._observers:
            observer.update(self, event, data)

    # --- Core Functionality ---

    def execute_command(self, command_name: str, a: float, b: float) -> float:
        """
        Executes a calculation, stores it, and notifies observers.
        """
        try:
            command = self._factory.get_command(command_name)
            result = command.execute(a, b)
            
            calc = Calculation(a, b, command, result)
            self._history_manager.add_calculation(calc)
            
            # Notify observers about the new calculation
            self._notify("calculation_performed", data=calc)
            
            return result
        except OperationError as e:
            # Notify observers about the error
            self._notify("error_occurred", data=e)
            raise # Re-raise the exception to be caught by the REPL

    def get_history(self) -> list[Calculation]:
        """Gets the full calculation history."""
        return self._history_manager.get_history()

    def clear_history(self):
        """Clears the calculation history."""
        self._history_manager.clear_history()
        self._notify("history_cleared")

    def undo(self):
        """Undoes the last operation."""
        self._history_manager.undo()
        self._notify("undo")

    def redo(self):
        """Redoes the last undone operation."""
        self._history_manager.redo()
        self._notify("redo")

    def save_history(self):
        """Manually saves the history log."""
        self._history_manager.save_history_to_csv()
        self._notify("history_saved")
        
    def load_history(self):
        """Manually loads the history log."""
        # The history manager needs the factory to rebuild command objects
        self._history_manager.load_history_from_csv(self._factory)
        self._notify("history_loaded")

    def get_available_commands(self) -> list[str]:
        """Gets list of command names from the factory."""
        return self._factory.get_available_commands()

