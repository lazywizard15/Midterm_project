########################
# Calculator Class      #
########################

from decimal import Decimal
import logging
from pathlib import Path
from typing import Any, List, Optional, Union

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver, LoggingObserver, AutoSaveObserver
from app.input_validators import InputValidator
from app.operations import Operation, OperationFactory

Number = Union[int, float, Decimal]
CalculationResult = Union[Number, str]


class Calculator:
    """
    Main calculator class implementing Strategy, Observer, Memento patterns.
    Supports undo/redo, logging, autosave, dynamic help menu, and history management.
    """

    def __init__(self, config: Optional[CalculatorConfig] = None):
        if config is None:
            project_root = Path(__file__).parent.parent
            config = CalculatorConfig(base_dir=project_root)

        self.config = config
        self.config.validate()

        self.history: List[Calculation] = []
        self.operation_strategy: Optional[Operation] = None
        self.observers: List[HistoryObserver] = []

        self.undo_stack: List[CalculatorMemento] = []
        self.redo_stack: List[CalculatorMemento] = []

        self._setup_directories()
        self._setup_logging()

        # Auto-register Logging and AutoSave observers
        self.add_observer(LoggingObserver())
        self.add_observer(AutoSaveObserver(self))

        try:
            self.load_history()
        except Exception as e:
            logging.warning(f"Could not load existing history: {e}")

        logging.info("Calculator initialized with configuration")

    def _setup_logging(self) -> None:
        try:
            log_file = self.config.log_file.resolve()
            logging.basicConfig(
                filename=str(log_file),
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                force=True
            )
            logging.info(f"Logging initialized at: {log_file}")
        except Exception as e:
            print(f"Error setting up logging: {e}")
            raise

    def _setup_directories(self) -> None:
        self.config.history_dir.mkdir(parents=True, exist_ok=True)
        self.config.log_dir.mkdir(parents=True, exist_ok=True)

    # Observer methods
    def add_observer(self, observer: HistoryObserver) -> None:
        self.observers.append(observer)
        logging.info(f"Added observer: {observer.__class__.__name__}")

    def remove_observer(self, observer: HistoryObserver) -> None:
        if observer in self.observers:
            self.observers.remove(observer)
            logging.info(f"Removed observer: {observer.__class__.__name__}")

    def notify_observers(self, calculation: Calculation) -> None:
        for observer in self.observers:
            observer.update(calculation)

    # Strategy pattern
    def set_operation(self, operation: Union[Operation, str]) -> None:
        """
        Set the current operation strategy.
        Can pass either an Operation instance or a string operation name.
        """
        if isinstance(operation, str):
            self.operation_strategy = OperationFactory.create_operation(operation)
        elif isinstance(operation, Operation):
            self.operation_strategy = operation
        else:
            raise TypeError("Operation must be an Operation instance or a string")
        logging.info(f"Set operation: {self.operation_strategy}")

    def perform_operation(self, a: Union[str, Number], b: Union[str, Number]) -> Decimal:
        if not self.operation_strategy:
            raise OperationError("No operation set")

        try:
            validated_a = InputValidator.validate_number(a, self.config)
            validated_b = InputValidator.validate_number(b, self.config)

            result = self.operation_strategy.execute(validated_a, validated_b)

            calculation = Calculation(
                operation=str(self.operation_strategy),
                operand1=validated_a,
                operand2=validated_b,
                result=result
            )

            # Save undo state
            self.undo_stack.append(CalculatorMemento(self.history.copy()))
            self.redo_stack.clear()

            # Update history
            self.history.append(calculation)
            if len(self.history) > self.config.max_history_size:
                self.history.pop(0)

            self.notify_observers(calculation)
            return result

        except ValidationError as e:
            logging.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Operation failed: {str(e)}")
            raise OperationError(f"Operation failed: {str(e)}")

    # Undo/redo methods
    def undo(self) -> bool:
        if not self.undo_stack:
            logging.info("Undo stack empty, cannot undo")
            return False
        memento = self.undo_stack.pop()
        self.redo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        logging.info("Undo performed")
        return True

    def redo(self) -> bool:
        if not self.redo_stack:
            logging.info("Redo stack empty, cannot redo")
            return False
        memento = self.redo_stack.pop()
        self.undo_stack.append(CalculatorMemento(self.history.copy()))
        self.history = memento.history.copy()
        logging.info("Redo performed")
        return True

    # History management
    def show_history(self) -> List[str]:
        return [f"{calc.operation}({calc.operand1}, {calc.operand2}) = {calc.result}" for calc in self.history]

    def clear_history(self) -> None:
        self.history.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        logging.info("History cleared")

    def save_history(self) -> None:
        for observer in self.observers:
            if isinstance(observer, AutoSaveObserver):
                observer.save(self.history)

    def load_history(self) -> None:
        for observer in self.observers:
            if isinstance(observer, AutoSaveObserver):
                loaded = observer.load()
                if loaded is not None:
                    self.history = loaded

    # Dynamic help menu
    def get_available_operations(self) -> List[str]:
        """
        Returns a list of all available operations dynamically from the OperationFactory.
        """
        return OperationFactory.list_operations()
