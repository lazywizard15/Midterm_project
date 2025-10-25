"""
Main calculator application with REPL interface.
Uses Observer pattern and Undo/Redo functionality.
"""

from abc import ABC, abstractmethod
from typing import List
from app.calculation import Calculation
from app.operations import OperationFactory
from app.history import CalculationHistory
from app.calculator_memento import UndoRedoManager
from app.calculator_config import CalculatorConfig
from app.logger import Logger
from app.input_validators import validate_number, validate_in_range
from app.exceptions import OperationError, ValidationError, HistoryError


# ---------------- Observer Pattern ---------------- #

class CalculationWatcher(ABC):
    """Abstract base for any calculation observer."""

    @abstractmethod
    def notify(self, calc: Calculation) -> None:
        """Called whenever a new calculation occurs."""
        pass


class LogWatcher(CalculationWatcher):
    """Logs each calculation to the logger."""

    def __init__(self, logger: Logger):
        self.logger = logger

    def notify(self, calc: Calculation) -> None:
        operation_name = calc.operation.__class__.__name__.replace("Operation", "").lower()
        self.logger.log_calculation(operation_name, calc.operand_a, calc.operand_b, calc.result)


class AutoSaveWatcher(CalculationWatcher):
    """Automatically saves history to CSV after each calculation."""

    def __init__(self, history: CalculationHistory, file_path: str):
        self.history = history
        self.file_path = file_path

    def notify(self, calc: Calculation) -> None:
        if self.history.get_count() > 0:
            try:
                self.history.save_to_csv(self.file_path)
            except HistoryError:
                pass  # Silently ignore save errors


# ---------------- Calculator Core ---------------- #

class CalculatorApp:
    """Core calculator class with REPL interface."""

    def __init__(self):
        """Initialize calculator components."""
        self.config = CalculatorConfig()
        self.logger = Logger()
        self.history = CalculationHistory(max_size=self.config.max_history_size)
        self.undo_manager = UndoRedoManager()
        self.watchers: List[CalculationWatcher] = []

        # Register default observers
        self.register_watcher(LogWatcher(self.logger))
        if self.config.auto_save:
            self.register_watcher(AutoSaveWatcher(self.history, self.config.history_file))

        self.logger.info("Calculator initialized")

    # ---------------- Observer Methods ---------------- #

    def register_watcher(self, watcher: CalculationWatcher) -> None:
        """Attach a new watcher to receive calculation notifications."""
        self.watchers.append(watcher)

    def notify_watchers(self, calc: Calculation) -> None:
        """Notify all attached watchers about a calculation."""
        for watcher in self.watchers:
            watcher.notify(calc)

    # ---------------- Calculation Methods ---------------- #

    def execute_operation(self, op_name: str, a: float, b: float) -> float:
        """
        Execute an operation and update history.

        Args:
            op_name: Operation name
            a: First operand
            b: Second operand

        Returns:
            Computed result
        """
        a = validate_number(a, "operand_a")
        b = validate_number(b, "operand_b")
        validate_in_range(a, self.config.max_input_value, "operand_a")
        validate_in_range(b, self.config.max_input_value, "operand_b")

        # Save current history for undo
        self.undo_manager.record_state(self.history.get_history())

        operation = OperationFactory.create_operation(op_name)
        calc = Calculation(operation, a, b)
        result = calc.execute()
        calc.result = round(result, self.config.precision)
        self.history.add_calculation(calc)
        self.notify_watchers(calc)

        return calc.result

    # ---------------- Undo/Redo ---------------- #

    def undo(self) -> None:
        """Undo last calculation."""
        try:
            restored_history = self.undo_manager.undo(self.history.get_history())
            self.history._history = restored_history
            self.logger.info("Undo performed")
        except HistoryError as e:
            print(f"Error: {e}")

    def redo(self) -> None:
        """Redo last undone calculation."""
        try:
            restored_history = self.undo_manager.redo()
            self.history._history = restored_history
            self.logger.info("Redo performed")
        except HistoryError as e:
            print(f"Error: {e}")

    # ---------------- History Management ---------------- #

    def show_history(self) -> None:
        print("\n" + str(self.history))

    def clear_history(self) -> None:
        self.history.clear_history()
        self.undo_manager.reset()
        self.logger.info("History cleared")
        print("History cleared")

    def save_history(self) -> None:
        try:
            self.history.save_to_csv(self.config.history_file)
            self.logger.info(f"History saved to {self.config.history_file}")
            print(f"History saved to {self.config.history_file}")
        except HistoryError as e:
            print(f"Error: {e}")

    def load_history(self) -> None:
        try:
            self.history.load_from_csv(self.config.history_file)
            self.logger.info(f"History loaded from {self.config.history_file}")
            print(f"History loaded from {self.config.history_file}")
        except HistoryError as e:
            print(f"Error: {e}")

    # ---------------- REPL & Help ---------------- #

    def show_help(self) -> None:
        help_text = """
Available Commands:
------------------
Operations:
  add <a> <b>, subtract <a> <b>, multiply <a> <b>, divide <a> <b>
  power <a> <b>, root <a> <b>, modulus <a> <b>, int_divide <a> <b>
  percent <a> <b>, abs_diff <a> <b>

History:
  history - show history
  clear   - clear history
  undo    - undo last
  redo    - redo last
  save    - save to CSV
  load    - load from CSV

Other:
  help - show this help
  exit - exit calculator
        """
        print(help_text)

    def repl(self) -> None:
        """Start Read-Eval-Print Loop interface."""
        print("Calculator REPL - Type 'help' for commands")
        self.logger.info("REPL started")

        while True:
            try:
                raw_input = input("> ").strip().lower()
                if not raw_input:
                    continue

                tokens = raw_input.split()
                cmd = tokens[0]

                if cmd == "exit":
                    print("Goodbye!")
                    self.logger.info("Calculator exiting")
                    break
                elif cmd == "help":
                    self.show_help()
                elif cmd == "history":
                    self.show_history()
                elif cmd == "clear":
                    self.clear_history()
                elif cmd == "undo":
                    self.undo()
                    print("Undo successful")
                    self.show_history()
                elif cmd == "redo":
                    self.redo()
                    print("Redo successful")
                    self.show_history()
                elif cmd == "save":
                    self.save_history()
                elif cmd == "load":
                    self.load_history()
                elif cmd in OperationFactory.get_available_operations():
                    if len(tokens) != 3:
                        print(f"Error: {cmd} requires exactly 2 numbers")
                        continue
                    try:
                        result = self.execute_operation(cmd, tokens[1], tokens[2])
                        print(f"Result: {result}")
                    except (OperationError, ValidationError) as e:
                        print(f"Error: {e}")
                        self.logger.error(str(e))
                else:
                    print(f"Unknown command: {cmd}")
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Unexpected error: {e}")
                self.logger.error(f"Unexpected error: {e}")


# ---------------- Entry Point ---------------- #

def main():
    calc = CalculatorApp()
    calc.repl()


if __name__ == "__main__":
    main()
