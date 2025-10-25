"""
Validation routines for calculator inputs.
"""

from app.exceptions import ValidationError


def ensure_numeric(val, name="value") -> float:
    """
    Confirm that the provided value can be interpreted as a number.
    
    Args:
        val: Input to check
        name: Name of the parameter for error messages
    
    Returns:
        Value as float
    
    Raises:
        ValidationError if conversion fails
    """
    try:
        return float(val)
    except (TypeError, ValueError):
        raise ValidationError(f"Parameter '{name}' must be numeric, received '{val}'")


def ensure_within_limit(val: float, maximum: float, name="value") -> None:
    """
    Ensure that the absolute value does not exceed the maximum allowed.
    
    Args:
        val: Value to check
        maximum: Maximum allowed absolute value
        name: Name of the parameter for error messages
    
    Raises:
        ValidationError if value is out of range
    """
    if abs(val) > maximum:
        raise ValidationError(f"{name} cannot exceed {maximum}, got {val}")


def ensure_nonzero(val: float, name="value") -> None:
    """
    Confirm that a number is not zero.
    
    Raises:
        ValidationError if value is zero
    """
    if val == 0:
        raise ValidationError(f"{name} cannot be zero")


def ensure_positive(val: float, name="value") -> None:
    """
    Confirm that a number is strictly positive.
    
    Raises:
        ValidationError if value is zero or negative
    """
    if val <= 0:
        raise ValidationError(f"{name} must be positive, got {val}")
