"""
Defines custom exceptions for the calculator application.
"""

class CalculatorError(Exception):
    """Base exception class for the calculator."""
    pass

class OperationError(CalculatorError):
    """Raised for errors during an arithmetic operation (e.g., division by zero)."""
    pass

class InputValidationError(CalculatorError):
    """Raised when user input is invalid (e.g., not a number, out of range)."""
    pass

class ConfigError(CalculatorError):
    """Raised for errors related to loading or accessing configuration."""
    pass

class HistoryError(CalculatorError):
    """Raised for errors related to history operations (e.g., save/load failed)."""
    pass