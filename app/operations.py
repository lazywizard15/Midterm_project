"""
This module defines operation classes using the Strategy pattern.
"""
from decimal import Decimal, InvalidOperation
from abc import ABC, abstractmethod
from typing import Dict, Type
from app.exceptions import ValidationError, OperationError


class Operation(ABC):
    """Abstract base class for all operations."""

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Execute the operation on two operands."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Return the operation name."""
        pass


class Addition(Operation):
    """Addition operation."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Add two numbers."""
        return a + b

    def __str__(self) -> str:
        return "Addition"


class Subtraction(Operation):
    """Subtraction operation."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Subtract b from a."""
        return a - b

    def __str__(self) -> str:
        return "Subtraction"


class Multiplication(Operation):
    """Multiplication operation."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Multiply two numbers."""
        return a * b

    def __str__(self) -> str:
        return "Multiplication"


class Division(Operation):
    """Division operation."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Divide a by b.
        
        Raises:
            ValidationError: If b is zero.
        """
        if b == 0:
            raise ValidationError("Cannot divide by zero")
        return a / b

    def __str__(self) -> str:
        return "Division"


class Power(Operation):
    """Power operation (a^b)."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Compute a raised to the power of b.
        
        Args:
            a (Decimal): Base.
            b (Decimal): Exponent.
            
        Returns:
            Decimal: Result of a^b.
            
        Raises:
            ValidationError: If the operation is invalid (e.g., negative base with fractional exponent).
        """
        # Check for invalid combinations
        if a < 0 and b % 1 != 0:
            raise ValidationError("Cannot raise negative number to fractional power")
        
        try:
            # Convert to float for calculation, then back to Decimal
            result = float(a) ** float(b)
            return Decimal(str(result))
        except (ValueError, OverflowError) as e:
            raise OperationError(f"Power operation failed: {str(e)}")

    def __str__(self) -> str:
        return "Power"


class Root(Operation):
    """Root operation (nth root of a)."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Compute the bth root of a.
        
        Args:
            a (Decimal): The number to take the root of.
            b (Decimal): The root degree.
            
        Returns:
            Decimal: Result of the bth root of a.
            
        Raises:
            ValidationError: If b is zero or if taking even root of negative number.
        """
        if b == 0:
            raise ValidationError("Cannot take zeroth root")
        
        if a < 0 and b % 2 == 0:
            raise ValidationError("Cannot calculate root of negative number")
        
        try:
            # nth root is equivalent to a^(1/b)
            result = float(a) ** (1 / float(b))
            return Decimal(str(result))
        except (ValueError, OverflowError) as e:
            raise OperationError(f"Root operation failed: {str(e)}")

    def __str__(self) -> str:
        return "Root"


class Modulus(Operation):
    """Modulus operation (remainder)."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Compute a modulo b.
        
        Raises:
            ValidationError: If b is zero.
        """
        if b == 0:
            raise ValidationError("Cannot perform modulo with zero divisor")
        return a % b

    def __str__(self) -> str:
        return "Modulus"


class IntegerDivision(Operation):
    """Integer division operation."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Compute integer division of a by b.
        
        Raises:
            ValidationError: If b is zero.
        """
        if b == 0:
            raise ValidationError("Cannot divide by zero")
        return Decimal(int(a // b))

    def __str__(self) -> str:
        return "IntegerDivision"


class Percentage(Operation):
    """Percentage operation (a% of b)."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Compute a% of b."""
        return (a / Decimal('100')) * b

    def __str__(self) -> str:
        return "Percentage"


class AbsoluteDifference(Operation):
    """Absolute difference operation."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Compute the absolute difference between a and b."""
        return abs(a - b)

    def __str__(self) -> str:
        return "AbsoluteDifference"


class OperationFactory:
    """Factory class for creating operation instances."""

    _operations: Dict[str, Type[Operation]] = {
        'add': Addition,
        'addition': Addition,
        'subtract': Subtraction,
        'subtraction': Subtraction,
        'multiply': Multiplication,
        'multiplication': Multiplication,
        'divide': Division,
        'division': Division,
        'power': Power,
        'root': Root,
        'modulus': Modulus,
        'mod': Modulus,
        'intdiv': IntegerDivision,
        'integerdivision': IntegerDivision,
        'percentage': Percentage,
        'percent': Percentage,
        'absdiff': AbsoluteDifference,
        'absolutedifference': AbsoluteDifference,
    }

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """
        Create an operation instance by name.
        
        Args:
            operation_type (str): Name of the operation (case-insensitive).
            
        Returns:
            Operation: Instance of the requested operation.
            
        Raises:
            ValidationError: If operation name is not recognized.
        """
        operation_name = operation_type.lower().strip()
        operation_class = cls._operations.get(operation_name)
        
        if not operation_class:
            raise ValidationError(f"Unknown operation: {operation_type}")
        
        return operation_class()

    @classmethod
    def register_operation(cls, name: str, operation_class: Type[Operation]) -> None:
        """
        Register a new operation.
        
        Args:
            name (str): Name to register the operation under.
            operation_class (Type[Operation]): The operation class.
            
        Raises:
            ValidationError: If operation_class is not a subclass of Operation.
        """
        if not issubclass(operation_class, Operation):
            raise ValidationError("Operation class must inherit from Operation")
        
        cls._operations[name.lower()] = operation_class

    @classmethod
    def get_available_operations(cls) -> list:
        """
        Get list of available operation names.
        
        Returns:
            list: List of operation names.
        """
        return list(cls._operations.keys())