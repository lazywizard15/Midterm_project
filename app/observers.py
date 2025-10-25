"""
Defines the Observer Design Pattern components.
"""
from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol
from app.exceptions import HistoryError
from app.calculation import Calculation

if TYPE_CHECKING:
    from app.calculation import Calculation
    from app.history import History

# --- Protocol for Subject ---
# This defines what an Observer can expect from the Subject
class Observable(Protocol):
    """Protocol for the Subject (Observable) side of the pattern."""
    
    def attach(self, observer: Observer):
        """Attach an observer."""
        ... # pragma: no cover

    def detach(self, observer: Observer):
        """Detach an observer."""
        ... # pragma: no cover

    def notify(self, event: str, data: any = None):
        """Notify all observers about an event."""
        ... # pragma: no cover

# --- Observer Interface ---
class Observer(ABC):
    """
    The Observer abstract base class.
    """
    @abstractmethod
    def update(self, subject: Observable, event: str, data: any = None):
        """
        Receive update from subject.
        """
        pass # pragma: no cover

# --- Concrete Implementations ---

class LoggingObserver(Observer):
    """
    An observer that logs events, especially new calculations.
    """
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def update(self, subject: Observable, event: str, data: any = None):
        """Logs the event."""
        if event == "calculation_performed" and isinstance(data, Calculation):
            self._logger.info(f"New Calculation: {data}")
        elif event == "error_occurred" and isinstance(data, Exception):
            self._logger.warning(f"Operation Error: {data}")
        elif event == "history_cleared":
            self._logger.info("Calculation history cleared.")
        elif event == "history_loaded":
            self._logger.info("Calculation history loaded from file.")
        elif event == "history_saved":
            self._logger.info("Calculation history saved to file.")
        elif event == "undo":
            self._logger.info("Undo operation performed.")
        elif event == "redo":
            self._logger.info("Redo operation performed.")

class AutoSaveObserver(Observer):
    """
    An observer that auto-saves the history to CSV.
    """
    def __init__(self, history_manager: History):
        self._history_manager = history_manager

    def update(self, subject: Observable, event: str, data: any = None):
        """Saves history on relevant events."""
        # We only care about events that modify the history
        if event in ("calculation_performed", "history_loaded", "undo", "redo"):
            try:
                self._history_manager.save_history_to_csv()
            except HistoryError as e:
                # We should not crash the app if auto-save fails
                # Log this error (ideally using the logger, but print for safety)
                print(f"[AutoSave Error] Failed to auto-save history: {e}") # pragma: no cover