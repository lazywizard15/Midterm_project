########################
# History Management    #
########################

from abc import ABC, abstractmethod
import logging
import os
import pandas as pd
from typing import Any, List, Optional
from app.calculation import Calculation
from app.calculator_config import CalculatorConfig


class HistoryObserver(ABC):
    """
    Abstract base class for calculator observers.

    Observers monitor new calculations and react to them.
    """

    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        """
        Handle a new calculation event.

        Args:
            calculation (Calculation): The calculation performed.
        """
        pass


class LoggingObserver(HistoryObserver):
    """
    Observer that logs calculations to a file.
    """

    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        logging.info(
            f"Calculation performed: {calculation.operation} "
            f"({calculation.operand1}, {calculation.operand2}) = {calculation.result}"
        )


class AutoSaveObserver(HistoryObserver):
    """
    Observer that automatically saves calculations to a CSV file.
    """

    def __init__(self, calculator: Any, history_file: Optional[str] = None):
        """
        Initialize the AutoSaveObserver.

        Args:
            calculator (Any): Calculator instance with 'config' and 'history'.
            history_file (Optional[str]): Custom history file name. Defaults to calculator config.
        """
        if not hasattr(calculator, 'config') or not hasattr(calculator, 'history'):
            raise TypeError("Calculator must have 'config' and 'history' attributes")

        self.calculator = calculator
        self.config: CalculatorConfig = calculator.config
        self.history_file = (
            os.path.join(self.config.history_dir, history_file)
            if history_file else str(self.config.history_file)
        )
        os.makedirs(self.config.history_dir, exist_ok=True)

    def update(self, calculation: Calculation) -> None:
        """
        Auto-save calculation history when a new calculation is performed.
        """
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        if self.config.auto_save:
            self.save(self.calculator.history)
            logging.info("History auto-saved")

    def save(self, history: List[Calculation]) -> None:
        """
        Save the calculation history to CSV.

        Args:
            history (List[Calculation]): List of Calculation objects to save.
        """
        df = pd.DataFrame([calc.to_dict() for calc in history])
        if os.path.exists(self.history_file):
            df_existing = pd.read_csv(self.history_file)
            df = pd.concat([df_existing, df], ignore_index=True)
        df.to_csv(self.history_file, index=False)

    def load(self) -> Optional[List[Calculation]]:
        """
        Load the calculation history from CSV.

        Returns:
            Optional[List[Calculation]]: List of Calculation objects or None if file missing.
        """
        if not os.path.exists(self.history_file):
            return None
        df = pd.read_csv(self.history_file)
        return [Calculation.from_dict(row.to_dict()) for _, row in df.iterrows()]
########################
# History Management    #
########################

from abc import ABC, abstractmethod
import logging
import os
import pandas as pd
from typing import Any, List, Optional
from app.calculation import Calculation
from app.calculator_config import CalculatorConfig


class HistoryObserver(ABC):
    """
    Abstract base class for calculator observers.

    Observers monitor new calculations and react to them.
    """

    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        """
        Handle a new calculation event.

        Args:
            calculation (Calculation): The calculation performed.
        """
        pass


class LoggingObserver(HistoryObserver):
    """
    Observer that logs calculations to a file.
    """

    def update(self, calculation: Calculation) -> None:
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        logging.info(
            f"Calculation performed: {calculation.operation} "
            f"({calculation.operand1}, {calculation.operand2}) = {calculation.result}"
        )


class AutoSaveObserver(HistoryObserver):
    """
    Observer that automatically saves calculations to a CSV file.
    """

    def __init__(self, calculator: Any, history_file: Optional[str] = None):
        """
        Initialize the AutoSaveObserver.

        Args:
            calculator (Any): Calculator instance with 'config' and 'history'.
            history_file (Optional[str]): Custom history file name. Defaults to calculator config.
        """
        if not hasattr(calculator, 'config') or not hasattr(calculator, 'history'):
            raise TypeError("Calculator must have 'config' and 'history' attributes")

        self.calculator = calculator
        self.config: CalculatorConfig = calculator.config
        self.history_file = (
            os.path.join(self.config.history_dir, history_file)
            if history_file else str(self.config.history_file)
        )
        os.makedirs(self.config.history_dir, exist_ok=True)

    def update(self, calculation: Calculation) -> None:
        """
        Auto-save calculation history when a new calculation is performed.
        """
        if calculation is None:
            raise AttributeError("Calculation cannot be None")
        if self.config.auto_save:
            self.save(self.calculator.history)
            logging.info("History auto-saved")

    def save(self, history: List[Calculation]) -> None:
        """
        Save the calculation history to CSV.

        Args:
            history (List[Calculation]): List of Calculation objects to save.
        """
        df = pd.DataFrame([calc.to_dict() for calc in history])
        if os.path.exists(self.history_file):
            df_existing = pd.read_csv(self.history_file)
            df = pd.concat([df_existing, df], ignore_index=True)
        df.to_csv(self.history_file, index=False)

    def load(self) -> Optional[List[Calculation]]:
        """
        Load the calculation history from CSV.

        Returns:
            Optional[List[Calculation]]: List of Calculation objects or None if file missing.
        """
        if not os.path.exists(self.history_file):
            return None
        df = pd.read_csv(self.history_file)
        return [Calculation.from_dict(row.to_dict()) for _, row in df.iterrows()]
