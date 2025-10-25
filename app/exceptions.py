"""
Custom exception hierarchy for the calculator system.
"""

class CalcBaseError(Exception):
    """Generic base exception for calculator-related errors."""
    pass


class CalcOpError(CalcBaseError):
    """Raised when an arithmetic operation fails."""
    pass


class CalcValidationError(CalcBaseError):
    """Raised when input validation fails."""
    pass


class CalcHistoryError(CalcBaseError):
    """Raised for errors in history operations (undo/redo/save/load)."""
    pass


class CalcConfigError(CalcBaseError):
    """Raised when configuration settings fail to load or are invalid."""
    pass
